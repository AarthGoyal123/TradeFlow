# AI Context

This file helps future AI-assisted development sessions continue consistently.

## Project Summary

TradeFlow is a production-grade, configurable Excel processing platform for trade/export shipment data.

The MVP targets Indian export shipment data and must reduce manual cleaning from 1-2 hours to under 30 seconds.

## Key Constraints

- Do not hardcode business rules.
- Use templates and rule packs for dataset-specific behavior.
- No paid APIs.
- Prefer deterministic processing before optional AI enhancements.
- Unknown cases go to `Needs_Review`.
- Every removal needs a reason.
- No automatic duplicate removal in MVP.

## Required Habit

Before implementing a feature, review:

- `knowledge/client_requirements.md`
- `knowledge/business_rules.md`
- `knowledge/excel_format.md`
- `knowledge/architecture_decisions.md`

If a new requirement affects implementation, update the relevant knowledge file before code.

