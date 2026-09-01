# SalesDuo Outbound

SalesDuo outbound automation workspace.

## Current project

### Domain Resolver

Convert SmartScout brand exports into verified company domains. The resolved domains will later be passed to the existing domain-to-stakeholder enrichment workflow.

## Pipeline

SmartScout CSV → brand extraction → domain candidate discovery → domain validation → confidence scoring → resolved domains CSV → stakeholder enrichment.

The first milestone is a 10-brand benchmark before scaling to the full SmartScout dataset.
