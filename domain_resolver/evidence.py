from __future__ import annotations

import re
from urllib.parse import urlparse

GENERIC_HOSTS = {
    "amazon.com", "amazon.in", "walmart.com", "ebay.com", "etsy.com",
    "facebook.com", "instagram.com", "linkedin.com", "youtube.com",
    "tiktok.com", "google.com", "wikipedia.org",
}


def domain_root(url: str) -> str:
    host = urlparse(url).netloc.lower().split(":", 1)[0]
    return host[4:] if host.startswith("www.") else host


def normalized_tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (value or "").lower()))


def identity_evidence(brand: str, site: dict) -> dict:
    """Turn fetched-site observations into explicit evidence signals.

    This does not declare ownership. It produces signals for the scorer.
    """
    brand_tokens = normalized_tokens(brand)
    title_tokens = normalized_tokens(site.get("title", ""))
    text = (site.get("text") or "").lower()
    domain = domain_root(site.get("url", "")) if site.get("url") else ""

    overlap = len(brand_tokens & title_tokens) / max(1, len(brand_tokens))
    product_match = bool(brand_tokens and any(token in text for token in brand_tokens))

    return {
        "reachable": bool(site.get("reachable")),
        "title_brand_overlap": round(overlap, 3),
        "brand_in_page_text": product_match,
        "domain": domain,
        "generic_host": domain in GENERIC_HOSTS,
        "final_domain": site.get("final_domain", domain),
    }
