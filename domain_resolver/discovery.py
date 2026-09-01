from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable

import httpx

from .models import CandidateDomain
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
    """Optional Google-results provider using SERPER_API_KEY.

    Kept behind an interface so the resolver is not coupled to one vendor.
    """

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


def discover_candidates(brand: str, provider: SearchProvider, limit: int = 5) -> list[CandidateDomain]:
    """Discover candidate domains from several evidence-oriented queries."""
    queries = [
        f'"{brand}" official website',
        f'"{brand}" Amazon brand website',
        f'"{brand}" company website',
    ]
    seen: dict[str, CandidateDomain] = {}
    brand_norm = normalize_brand(brand)

    for query in queries:
        for result in provider.search(query, limit=limit):
            domain = _domain_from_url(result.url)
            if not domain:
                continue
            # Ignore obvious search/social/marketplace hosts as final candidates.
            if domain.endswith(("google.com", "amazon.com", "wikipedia.org", "facebook.com", "instagram.com", "linkedin.com", "youtube.com")):
                continue
            candidate = seen.setdefault(
                domain,
                CandidateDomain(domain=domain, source="search", evidence=[]),
            )
            candidate.evidence.append(f"{query}: {result.title} — {result.snippet}")
            if brand_norm in normalize_brand(result.title):
                candidate.score += 15

    return list(seen.values())
