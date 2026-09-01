# SalesDuo Domain Resolver

The first-stage lead-intelligence engine for SalesDuo outbound.

## Goal

Convert a SmartScout Amazon brand export into domains that are safe to pass to the existing domain-to-stakeholder enrichment workflow.

**This module stops at the domain. It does not find people.**

## Current architecture

```text
SmartScout CSV
  -> normalize + deduplicate brands
  -> candidate discovery provider
  -> candidate filtering
  -> website validation
  -> identity/evidence extraction
  -> confidence scoring
  -> ACCEPTED / REVIEW / NOT_FOUND
  -> resolved_domains.csv
  -> existing stakeholder tool
```

## Provider strategy

The resolver uses a provider interface. Serper is the first live implementation, but it is intentionally not hard-coded into the rest of the engine. This lets us add or replace search/data providers without rewriting validation or scoring.

An offline `StaticProvider` is included so the pipeline can be developed and tested without an API key.

## Live run

Create a local `.env` containing `SERPER_API_KEY` (never commit it), install dependencies, then:

```bash
python -m domain_resolver.run path/to/smartscout.csv output/resolved_domains.csv
```

For a 10-brand test:

```bash
python -m domain_resolver.run path/to/smartscout.csv output/test_10.csv --limit 10
```

The input defaults to a `Brand` column; use `--brand-column` if your export uses another name.

## Offline test

```bash
python -m domain_resolver.demo
```

This exercises discovery -> validation/scoring -> final resolution without calling an external API.

## Safety principle

A missing domain is preferable to a wrong domain. A wrong domain can produce the wrong company and therefore the wrong decision makers.

## Status

V0.1: core pipeline and provider abstraction are implemented.

Next hardening work before large-scale use:

- richer search evidence
- Amazon/storefront evidence
- company/legal-name corroboration
- parent-company detection
- generic-brand handling
- stronger scoring and contradiction rules
- retry/rate-limit handling
- structured review queue
- automated benchmark tests
