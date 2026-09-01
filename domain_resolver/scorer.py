from .models import CandidateDomain


def score_candidate(candidate: CandidateDomain, brand: str, site_evidence: dict | None = None) -> CandidateDomain:
    """Apply the initial evidence rubric from RESOLUTION_SPEC.md."""
    score = candidate.score
    evidence = " ".join(candidate.evidence).lower()
    brand_norm = brand.lower().strip()
    title = (site_evidence or {}).get("title", "").lower()
    text = (site_evidence or {}).get("text", "").lower()

    if brand_norm and brand_norm in title:
        score += 30
    if brand_norm and brand_norm in text:
        score += 20
    if (site_evidence or {}).get("reachable"):
        score += 10
    if "official" in evidence:
        score += 10

    candidate.score = min(100, max(0, score))
    if candidate.score >= 90:
        candidate.reason = "High-confidence candidate based on accumulated identity evidence."
    elif candidate.score >= 75:
        candidate.reason = "Plausible candidate; additional corroboration or review required."
    else:
        candidate.reason = "Insufficient evidence to safely accept this domain."
    return candidate
