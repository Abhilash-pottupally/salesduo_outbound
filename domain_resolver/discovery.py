from __future__ import annotations

import os
import re
from dataclasses import dataclass

import httpx

from .models import BrandContext, CandidateDomain
from .normalizer import normalize_brand


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""


class SearchProvider:
    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        raise NotImplementedError


class SerperProvider(SearchProvider):
    """Google-results provider using SERPER_API_KEY."""

    endpoint = "https://google.serper.dev/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY is required for SerperProvider")

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        response = httpx.post(
            self.endpoint,
            headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
            json={"q": query, "num": min(limit, 10)},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return [
            SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
            for item in data.get("organic", [])
            if item.get("link")
        ]


def _domain_from_url(url: str) -> str | None:
    match = re.match(r"https?://(?:www\.)?([^/]+)", url.lower())
    return match.group(1) if match else None


def _blocked_domain(domain: str) -> bool:
    blocked = (
        "google.com", "amazon.com", "wikipedia.org", "facebook.com",
        "instagram.com", "linkedin.com", "youtube.com", "tiktok.com",
        "pinterest.com", "x.com", "twitter.com", "reddit.com",
    )
    return domain == "amazon.com" or domain.endswith(blocked)


def discover_candidates(
    brand: str,
    provider: SearchProvider,
    context: BrandContext | None = None,
    limit: int = 5,
) -> list[CandidateDomain]:
    """Discover candidates using independent identity and category searches."""
    context = context or BrandContext(brand=brand)
    queries = [
        f'"{brand}" official website',
        f'"{brand}" company website',
        f'"{brand}" Amazon brand website',
    ]
    if context.category or context.subcategory:
        category_hint = " ".join(x for x in [context.category, context.subcategory] if x)
        queries.append(f'"{brand}" "{category_hint}"')

    seen: dict[str, CandidateDomain] = {}
    brand_norm = normalize_brand(brand)

    for query in queries:
        for result in provider.search(query, limit=limit):
            domain = _domain_from_url(result.url)
            if not domain or _blocked_domain(domain):
                continue
            candidate = seen.setdefault(domain, CandidateDomain(domain=domain, source="search", evidence=[]))
            candidate.evidence.append(f"{query}: {result.title} — {result.snippet}")
            if brand_norm and brand_norm in normalize_brand(result.title):
                candidate.score += 15
                candidate.signals.append("brand_in_search_title")

    return list(seen.values())
