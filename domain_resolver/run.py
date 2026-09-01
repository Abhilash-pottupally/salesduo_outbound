from __future__ import annotations

import argparse
from pathlib import Path

from .csv_io import read_unique_rows, write_clean_rows, write_results
from .discovery import SearchProvider, SearchResult, SerperProvider, discover_candidates
from .models import BrandContext
from .normalizer import normalize_brand
from .scorer import score_candidate
from .validator import validate_site
from .providers import StaticProvider


def context_from_row(row: dict, brand_column: str = "Brand") -> BrandContext:
    return BrandContext(
        brand=(row.get(brand_column) or "").strip(),
        category=(row.get("Category") or "").strip(),
        subcategory=(row.get("Primary Subcategory") or "").strip(),
        monthly_revenue=(row.get("Monthly Revenue") or "").strip(),
        total_ad_spend=(row.get("Total Ad Spend") or "").strip(),
        placement_gap=(row.get("Placement Gap") or "").strip(),
        heavy_advertiser=(row.get("Heavy Advertiser") or "").strip(),
        video_intent=(row.get("Video Intent") or "").strip(),
        multi_format=(row.get("Multi-format") or "").strip(),
        high_ad_spend_ratio=(row.get("High Ad Spend Ratio") or "").strip(),
        primary_campaign=(row.get("Primary Campaign") or "").strip(),
    )


def resolve_brand(brand: str, provider: SearchProvider, context: BrandContext | None = None) -> dict:
    context = context or BrandContext(brand=brand)
    candidates = discover_candidates(brand, provider, context=context)
    scored = []
    for candidate in candidates:
        site = validate_site(candidate.domain, brand)
        candidate = score_candidate(candidate, brand, site, context)
        scored.append((candidate, site))
    scored.sort(key=lambda x: x[0].score, reverse=True)

    if not scored:
        return {
            "brand": brand, "brand_normalized": normalize_brand(brand), "domain": "",
            "confidence": 0, "status": "NOT_FOUND", "source": "",
            "reason": "No candidate domains discovered.", "evidence_urls": "", "candidate_count": 0,
            "signals": "", "contradictions": "",
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
        "signals": ";".join(winner.signals),
        "contradictions": ";".join(winner.contradictions),
    }


def run(input_csv: Path, output_csv: Path, provider: SearchProvider, brand_column: str, limit: int = 0) -> None:
    rows, _ = read_unique_rows(input_csv, brand_column, limit)
    results = []
    for i, row in enumerate(rows, 1):
        brand = (row.get(brand_column) or "").strip()
        print(f"[{i}/{len(rows)}] {brand}")
        try:
            results.append(resolve_brand(brand, provider, context_from_row(row, brand_column)))
        except Exception as exc:
            results.append({
                "brand": brand, "brand_normalized": normalize_brand(brand), "domain": "",
                "confidence": 0, "status": "ERROR", "source": "", "reason": str(exc),
                "evidence_urls": "", "candidate_count": 0, "signals": "", "contradictions": str(exc),
            })
    write_results(output_csv, results)
    print(f"Wrote {len(results)} results to {output_csv}")


def parse_only(input_csv: Path, output_csv: Path, brand_column: str, limit: int = 0) -> None:
    rows, fields = read_unique_rows(input_csv, brand_column, limit)
    write_clean_rows(output_csv, rows, fields)
    print(f"Parsed {len(rows)} unique brands from {input_csv}")
    print(f"Wrote clean SmartScout data to {output_csv}")


def demo() -> None:
    data = {
        '"Chefman" official website': [SearchResult("Chefman | Kitchen Appliances", "https://chefman.com/", "Official Chefman kitchen appliances")],
        '"Chefman" Amazon brand website': [SearchResult("Chefman Amazon", "https://www.amazon.com/stores/Chefman", "Chefman brand")],
        '"Chefman" company website': [SearchResult("Chefman", "https://chefman.com/", "Kitchen products")],
    }
    print(resolve_brand("Chefman", StaticProvider(data), BrandContext(brand="Chefman", category="Kitchen & Dining", subcategory="Air Fryers")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SalesDuo domain resolver")
    parser.add_argument("input_csv", nargs="?", type=Path)
    parser.add_argument("output_csv", nargs="?", type=Path)
    parser.add_argument("--brand-column", default="Brand")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--demo", action="store_true", help="Run offline smoke test")
    parser.add_argument("--parse-only", action="store_true", help="Clean and deduplicate SmartScout CSV without any API")
    args = parser.parse_args()

    if args.demo:
        demo()
    elif args.parse_only:
        if args.input_csv is None or args.output_csv is None:
            parser.error("--parse-only requires input_csv and output_csv")
        parse_only(args.input_csv, args.output_csv, args.brand_column, args.limit)
    else:
        if args.input_csv is None or args.output_csv is None:
            parser.error("input_csv and output_csv are required unless --demo is used")
        run(args.input_csv, args.output_csv, SerperProvider(), args.brand_column, args.limit)
