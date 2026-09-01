# SalesDuo Outbound

SalesDuo outbound automation workspace.

## Domain Resolver

Convert SmartScout brand exports into candidate company domains, validate the sites, score identity evidence, and later pass high-confidence domains into the existing domain-to-stakeholder workflow.

### Pipeline

SmartScout CSV → unique brands → search candidates → filter junk domains → website validation → SmartScout/category-aware scoring → ACCEPTED / REVIEW / NOT_FOUND → stakeholder enrichment.

### Local setup

```powershell
cd "C:\Users\abhil\salesduo_outbound"
.\.venv\Scripts\Activate.ps1
git pull
```

### Offline CSV test (no API key)

```powershell
python -m domain_resolver.run ".\input\smartscout.csv" ".\output\test_10.csv" --parse-only --limit 10
```

### Offline smoke test

```powershell
python -m domain_resolver.run --demo
```

### Live domain discovery

Set `SERPER_API_KEY` in a local `.env` or environment variable, then run:

```powershell
python -m domain_resolver.run ".\input\smartscout.csv" ".\output\resolved_domains.csv" --limit 10
```

Remove `--limit 10` only after the 10-brand benchmark is reviewed. Never commit `.env` or API keys.

### Output

The resolver writes a CSV containing the brand, normalized brand, chosen domain, confidence, status, source, evidence URL, candidate count, positive signals, and contradictions.

Statuses:

- `ACCEPTED` — high-confidence identity match; eligible for downstream enrichment.
- `REVIEW` — plausible but needs human verification.
- `NOT_FOUND` — insufficient evidence; do not guess a domain.
- `ERROR` — processing/search failure; investigate before retrying.

The first milestone is a 10-brand benchmark before scaling to the full SmartScout dataset.
