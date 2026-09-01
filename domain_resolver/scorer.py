from __future__ import annotations

import re

from .models import BrandContext, CandidateDomain


def _terms(value: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9]+", (value or "").lower()) if len(x) > 2}


def score_candidate(
    candidate: CandidateDomain,
    brand: str,
    site_evidence: dict | None = None,
    context: BrandContext | None = None,
) -> CandidateDomain:
    """Conservative identity scoring using site evidence and SmartScout context."""
    site_evidence = site_evidence or {}
    context = context or BrandContext(brand=brand)
    score = 0
    signals: list[str] = []
    contradictions: list[str] = []

    brand_terms = _terms(brand)
    title_terms = _terms(site_evidence.get("title", ""))
    text_terms = _terms(site_evidence.get("text", ""))
    domain_terms = _terms(candidate.domain.replace(".", " ").replace("-", " "))
    combined = title_terms | text_terms

    if brand_terms and brand_terms.issubset(title_terms):
        score += 30
        signals.append("brand_in_title")
    elif brand_terms & title_terms:
        score += 12
        signals.append("partial_brand_in_title")

    if brand_terms and brand_terms.issubset(text_terms):
        score += 20
        signals.append("brand_in_page_text")
    elif brand_terms & text_terms:
        score += 8
        signals.append("partial_brand_in_page_text")

    if brand_terms and brand_terms.issubset(domain_terms):
        score += 15
        signals.append("brand_in_domain")

    if site_evidence.get("reachable"):
        score += 10
        signals.append("website_reachable")
    else:
        score -= 15
        contradictions.append("website_not_reachable")

    evidence_text = " ".join(candidate.evidence).lower()
    if "official" in evidence_text:
        score += 10
        signals.append("official_search_evidence")

    category_terms = _terms(context.category)
    subcategory_terms = _terms(context.subcategory)
    category_hits = len(category_terms & combined)
    subcategory_hits = len(subcategory_terms & combined)
    if category_hits:
        score += min(10, category_hits * 3)
        signals.append("category_match")
    if subcategory_hits:
        score += min(8, subcategory_hits * 4)
        signals.append("subcategory_match")

    unrelated_markers = {"software", "realty", "insurance", "law", "university", "church"}
    if category_terms and not (category_terms & combined) and (unrelated_markers & combined):
        score -= 25
        contradictions.append("site_appears_unrelated_to_smartscout_category")

    candidate.score = min(100, max(0, score))
    candidate.signals = signals
    candidate.contradictions = contradictions
    if candidate.score >= 90:
        candidate.reason = "High-confidence candidate based on multiple identity signals."
    elif candidate.score >= 75:
        candidate.reason = "Plausible candidate; additional corroboration or review required."
    else:
        candidate.reason = "Insufficient evidence to safely accept this domain."
    return candidate
