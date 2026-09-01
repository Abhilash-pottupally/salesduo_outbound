from __future__ import annotations

from urllib.parse import urlparse

from .models import CandidateDomain

BLOCKED_DOMAINS = {
    "amazon.com", "amazon.in", "walmart.com", "ebay.com", "etsy.com",
    "facebook.com", "instagram.com", "linkedin.com", "youtube.com",
    "tiktok.com", "google.com", "wikipedia.org",
}


def extract_domain(url: str) -> str | None:
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        host = parsed.netloc.lower().split(":", 1)[0]
        if host.startswith("www."):
            host = host[4:]
        return host or None
    except Exception:
        return None


def merge_candidate(existing: CandidateDomain | None, domain: str, source: str, evidence: str) -> CandidateDomain:
    if existing is None:
        return CandidateDomain(domain=domain, source=source, evidence=[evidence])
    if evidence not in existing.evidence:
        existing.evidence.append(evidence)
    return existing


def is_allowed_candidate(domain: str) -> bool:
    return bool(domain) and domain not in BLOCKED_DOMAINS and not any(domain.endswith("." + x) for x in BLOCKED_DOMAINS)
