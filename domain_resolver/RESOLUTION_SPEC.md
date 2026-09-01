# SalesDuo Domain Resolver — Resolution Specification

## Objective
Convert a SmartScout Amazon brand into the correct official company domain with enough evidence to safely pass the domain to the existing stakeholder-enrichment tool.

This module stops at a verified domain. It does not find people.

## Resolution waterfall

1. **Normalize** the SmartScout brand while preserving the raw value.
2. **Discover candidates** using existing company/domain data first, then web search, Amazon/product evidence, and trademark/company records for ambiguous brands.
3. **Validate candidates** against brand identity, products/category, company/legal information, Amazon/storefront evidence, and independent corroboration.
4. **Score confidence** and retain the evidence used.
5. **Accept only high-confidence domains** for automatic downstream enrichment.

## Initial scoring model

Positive evidence:
- +30 exact brand/company identity on official site
- +20 product/category match
- +15 legal/company-name match
- +15 Amazon/storefront cross-reference
- +10 independent company/social corroboration
- +10 domain/company consistency

Negative evidence:
- -40 ambiguous generic name with weak evidence
- -50 evidence indicates another company

Cap at 0–100. Hard contradictions override the numeric score.

## Decision thresholds

- **90–100:** ACCEPTED — safe for downstream enrichment
- **75–89:** REVIEW — plausible but needs stronger evidence/manual review
- **<75:** REJECTED / NOT_FOUND — do not pass downstream

## Output fields

`brand_raw`, `brand_normalized`, `company_name`, `domain`, `status`, `confidence`, `source`, `reason`, `evidence_urls`, `review_required`

## Edge cases

- Brand name may differ from legal/company name.
- Parent companies may own consumer brands.
- Generic names such as Frontline require stronger evidence.
- Marketplace/private-label brands may have no independent website.
- Country-specific domains are valid when evidence supports them.
- Never invent or infer an email address here; this module only resolves domains.

## Downstream rule

Only `ACCEPTED` domains automatically enter the existing domain-to-stakeholder workflow. `REVIEW` records remain separate.
