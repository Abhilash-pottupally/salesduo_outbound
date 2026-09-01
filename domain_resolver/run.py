from __future__ import annotations

import argparse
from pathlib import Path

from .csv_io import read_unique_brands, write_results
from .discovery import SerperProvider, discover_candidates
from .normalizer import normalize_brand
from .scorer import score_candidate
from .validator import validate_site


def resolve_brand(brand: str, provider: SerperProvider) -> dict:
    candidates = discover_candidates(brand, provider)
    scored = []
    for candidate in candidates:
        site = validate_site(candidate.domain, brand)
        candidate = score_candidate(candidate, brand, site)
        scored.append((candidate, site))
    scored.sort(key=lambda x: x[0].score, reverse=True)

    if not scored:
        return {
            "brand": brand, "brand_normalized": normalize_brand(brand),
            "domain": "", "confidence": 0, "status": "NOT_FOUND",
            "source": "", "reason": "No candidate domains discovered.",
            "evidence_urls": "", "candidate_count": 0,
        }

    winner, site = scored[0]
    status = "ACCEPTED" if winner.score >= 90 else "REVIEW" if winner.score >= 75 else "NOT_FOUND"
    return {
        "brand": brand,
        "brand_normalized": normalize_brand(brand),
        "domain": winner.domain if status != "NOT_FOUND" else "",
        "confidence": winner.score,
        "status": status,
        "source": winner.source,
        "reason": winner.reason,
        "evidence_urls": site.get("url", ""),
        "candidate_count": len(scored),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve SmartScout brands to official domains")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--brand-column", default="Brand")
    parser.add_argument("--limit", type=int, default=0, help="Resolve only the first N unique brands (0 = all)")
    args = parser.parse_args()

    provider = SerperProvider()
    brands = read_unique_brands(args.input_csv, args.brand_column)
    if args.limit:
        brands = brands[:args.limit]

    results = []
    for i, brand in enumerate(brands, 1):
        print(f"[{i}/{len(brands)}] {brand}")
        try:
            results.append(resolve_brand(brand, provider))
        except Exception as exc:
            results.append({
                "brand": brand,
                "brand_normalized": normalize_brand(brand),
                "domain": "", "confidence": 0, "status": "ERROR",
                "source": "", "reason": str(exc),
                "evidence_urls": "", "candidate_count": 0,
            })

    write_results(args.output_csv, results)
    print(f"Wrote {len(results)} results to {args.output_csv}")


if __name__ == "__main__":
    main()
