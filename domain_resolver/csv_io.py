from __future__ import annotations

import csv
from pathlib import Path

from .normalizer import normalize_brand


def read_unique_brands(path: Path, brand_column: str = "Brand") -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or brand_column not in reader.fieldnames:
            raise ValueError(f"Column '{brand_column}' not found. Columns: {reader.fieldnames}")
        seen: set[str] = set()
        brands: list[str] = []
        for row in reader:
            raw = (row.get(brand_column) or "").strip()
            key = normalize_brand(raw)
            if raw and key and key not in seen:
                seen.add(key)
                brands.append(raw)
        return brands


def read_unique_rows(path: Path, brand_column: str = "Brand", limit: int = 0) -> tuple[list[dict], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or brand_column not in reader.fieldnames:
            raise ValueError(f"Column '{brand_column}' not found. Columns: {reader.fieldnames}")
        rows: list[dict] = []
        seen: set[str] = set()
        for row in reader:
            brand = (row.get(brand_column) or "").strip()
            key = normalize_brand(brand)
            if not brand or not key or key in seen:
                continue
            seen.add(key)
            row["brand_normalized"] = key
            rows.append(row)
            if limit and len(rows) >= limit:
                break
        return rows, list(reader.fieldnames) + ["brand_normalized"]


def write_clean_rows(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [f for f in fields if f and not f.startswith("Unnamed")]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_results(path: Path, results: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "brand", "brand_normalized", "domain", "confidence", "status",
        "source", "reason", "evidence_urls", "candidate_count",
        "signals", "contradictions",
        "category", "subcategory", "monthly_revenue", "total_ad_spend",
        "placement_gap", "heavy_advertiser", "video_intent", "multi_format",
        "high_ad_spend_ratio", "primary_campaign",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
