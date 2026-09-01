# SalesDuo Domain Resolver

First-stage lead intelligence for SalesDuo outbound.

## Goal

Convert SmartScout Amazon brand exports into domains that are safe to pass to the existing domain-to-stakeholder enrichment workflow.

## Current status

This is V0.1. The resolver currently contains:

- brand normalization
- candidate-domain data models
- basic website reachability/content validation
- initial confidence scoring
- a 10-brand benchmark

It does **not** yet perform automated search or call Apollo. Those integrations come after the benchmark and validation logic are proven.

## Planned pipeline

```text
SmartScout CSV
  -> normalize brands
  -> candidate discovery
  -> website/company validation
  -> evidence scoring
  -> ACCEPTED / REVIEW / NOT_FOUND
  -> domains.csv
  -> existing stakeholder tool
```

## Safety principle

A missing domain is preferable to a wrong domain. A wrong domain can produce the wrong company and therefore the wrong decision makers.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
