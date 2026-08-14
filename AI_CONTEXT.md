# TradeFlow Project Context

## What We Are Building

A Workbook Intelligence Platform for global trade data. Process any trade Excel workbook into clean, validated, categorized output with minimal user configuration.

## Current Phase

Phase 9A — Production Hardening (COMPLETED)
Next: Phase 9B

## Architecture

Clean Architecture (api → application → domain ← infrastructure).
The Intelligence Engine sits at the core. Job execution uses a local `SynchronousJobExecutor` by default to avoid heavy dependencies (Celery/Redis are supported via configuration but NOT required locally).

## Key Files

| File | Purpose |
|---|---|
| `docs/README.md` | Primary documentation index |
| `ROADMAP.md` | Phase tracking |
| `knowledge/architecture_decisions.md` | Architectural history |
| `docs/product-ux.md` | Phase 8 UX flows and browser testing docs |

## Benchmark

The benchmark workbook is at `backend/samples/1006 ALL EXPORT JULY 25.xlsx`.
- Input rows: 19,967
- Clean_Data.xlsx: 8,701
- Removed_Rows.xlsx: 11,266
- Needs_Review.xlsx: 0
- TO ORDER removals: 10,565
- Bank removals: 701

## Test Suite

Run with: `.\.venv\Scripts\python.exe -m pytest`
Ensure the golden regression test (`tests/test_benchmark_regression.py`) always passes exactly as shown above.

## Permanent Project Constraints

1. **ZERO PAID SERVICES**: TradeFlow must remain entirely usable without paid APIs, Auth0, Clerk, Firebase, AWS, or paid DBs. Google OAuth is used strictly as an Identity Provider.
2. **ZERO HEAVY LOCAL DEPS**: Do NOT introduce Docker, WSL, PostgreSQL, Redis, MinIO, or Playwright locally unless explicitly requested.
3. **RESPECT DISK SPACE**: The `C:` drive has limited space. Prefer existing `D:` drive environments. Avoid unnecessary local downloads/installations.
4. **GOLDEN BENCHMARK PRESERVATION**: The exact benchmark row counts (19967/8701/10565/701) MUST NEVER change. Any refactor or feature must preserve this behavior.
5. **NEVER BREAK BACKWARD COMPATIBILITY**: Keep existing tests green. 
6. **DOCUMENTATION**: Maintain and update `docs/` and `knowledge/` diligently. Write the actual architectural reasoning so future agents understand WHY a solution was chosen.