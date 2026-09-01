from __future__ import annotations

import argparse
from pathlib import Path

from .csv_io import read_unique_brands, write_results
from .discovery import SearchProvider, SerperProvider, discover_candidates
from .normalizer import normalize_brand
from .scorer import score_candidate
from .validator import validate_site
from .providers import StaticProvider


def resolve_brand(brand: str, provider: SearchProvider) -> dict:
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


def run(input_csv: Path | None, output_csv: Path | None, provider: SearchProvider, brand_column: str, limit: int = 0) -> None:
    if input_csv is None:
        raise ValueError("An input CSV is required unless --demo is used.")
    brands = read_unique_brands(input_csv, brand_column)
    if limit:
        brands = brands[:limit]

    results = []
    for i, brand in enumerate(brands, 1):
        print(f"[{i}/{len(brands)}] {brand}")
        try:
            results.append(resolve_brand(brand, provider))
        except Exception as exc:
            results.append({
                "brand": brand, "brand_normalized": normalize_brand(brand),
                "domain": "", "confidence": 0, "status": "ERROR",
                "source": "", "reason": str(exc),
                "evidence_urls": "", "candidate_count": 0,
            })
    write_results(output_csv, results)
    print(f"Wrote {len(results)} results to {output_csv}")


def demo() -> None:
    data = {
        '"Chefman" official website': [SearchResult("Chefman | Kitchen Appliances", "https://chefman.com/", "Official Chefman kitchen appliances")],
        '"Chefman" Amazon brand website': [SearchResult("Chefman Amazon", "https://www.amazon.com/stores/Chefman", "Chefman brand")],
        '"Chefman" company website': [SearchResult("Chefman", "https://chefman.com/", "Kitchen products")],
    }
    result = resolve_brand("Chefman", StaticProvider(data))
    print(result)


if __name__ == "__main__":
    from .discovery import SearchResult

    parser = argparse.ArgumentParser(description="SalesDuo domain resolver")
    parser.add_argument("input_csv", nargs="?", type=Path)
    parser.add_argument("output_csv", nargs="?", type=Path)
    parser.add_argument("--brand-column", default="Brand")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--demo", action="store_true", help="Run the offline smoke test; no API key required")
    args = parser.parse_args()

    if args.demo:
        demo()
    else:
        run(args.input_csv, args.output_csv, SerperProvider(), args.brand_column, args.limit)
