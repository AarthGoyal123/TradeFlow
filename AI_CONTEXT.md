# TradeFlow Project Context

## What We Are Building

A Workbook Intelligence Platform for global trade data. Process any trade Excel workbook into clean, validated, categorized output with minimal user configuration.

## Current Phase

Phase 1 — Architecture Hardening (IN PROGRESS)

## Architecture

Clean Architecture (api → application → domain ← infrastructure).

The Intelligence Engine sits at the core. Job execution is currently synchronous but prepared for async. SQLite is used for persistence. Local filesystem for outputs.

## Key Files

| File | Purpose |
|---|---|
| `docs/README.md` | Primary documentation index |
| `domain/workbooks/intelligence.py` | All intelligence domain models |
| `application/processing/service.py` | Processing pipeline orchestrator |
| `domain/jobs/models.py` | Job state machine |
| `templates/indian_rice_exports/columns.json` | Reference template (20 business fields) |

## Benchmark

The benchmark workbook is at `backend/samples/1006 ALL EXPORT JULY 25.xlsx`.
- Input rows: 19,967
- Clean_Data.xlsx: 8,701
- Removed_Rows.xlsx: 11,266
- Needs_Review.xlsx: 0
- TO ORDER removals: 10,565
- Bank removals: 701

## Test Suite

Run with: `python -m pytest`
Ensure the golden regression test (`tests/test_benchmark_regression.py`) always passes.

## Rules

1. NEVER break backward compatibility.
2. ALL existing tests must pass.
3. Benchmark workbook must never be modified — fix the code instead.
4. Golden benchmark row counts MUST remain strictly identical.
5. All documentation MUST be kept up to date (`/docs/`).

## What NOT To Build Yet

- Multi-tenant architecture (planned Phase 6)
- PostgreSQL migration (planned Phase 3)
- Celery/Redis/async processing (planned Phase 4)
- S3 integration (planned Phase 5)