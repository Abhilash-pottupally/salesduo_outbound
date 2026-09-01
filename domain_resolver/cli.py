from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .discovery import SerperProvider, discover_candidates
from .normalizer import normalize_brand
from .scorer import score_candidate
from .validator import validate_site


def resolve_brand(brand: str, provider: SerperProvider) -> dict:
    candidates = discover_candidates(brand, provider)
    scored = []
    for candidate in candidates:
        evidence = validate_site(candidate.domain, brand)
        candidate = score_candidate(candidate, brand, evidence)
        scored.append((candidate, evidence))

    scored.sort(key=lambda pair: pair[0].score, reverse=True)
    if not scored:
        return {
            "brand": brand,
            "brand_normalized": normalize_brand(brand),
            "domain": "",
            "confidence": 0,
            "status": "NOT_FOUND",
            "source": "",
            "reason": "No candidate domains discovered.",
            "evidence_urls": "",
        }

    winner, evidence = scored[0]
    if winner.score >= 90:
        status = "ACCEPTED"
    elif winner.score >= 75:
        status = "REVIEW"
    else:
        status = "NOT_FOUND"

    return {
        "brand": brand,
        "brand_normalized": normalize_brand(brand),
        "domain": winner.domain if status != "NOT_FOUND" else "",
        "confidence": winner.score,
        "status": status,
        "source": winner.source,
        "reason": winner.reason,
        "evidence_urls": evidence.get("url", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve SmartScout brands to verified domains")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--brand-column", default="Brand")
    args = parser.parse_args()

    provider = SerperProvider()
    with args.input_csv.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    brands = []
    seen = set()
    for row in rows:
        brand = (row.get(args.brand_column) or "").strip()
        key = normalize_brand(brand)
        if brand and key not in seen:
            seen.add(key)
            brands.append(brand)

    results = [resolve_brand(brand, provider) for brand in brands]
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=results[0].keys() if results else ["brand"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()
