# TradeFlow Project Context

## What We Are Building

A Workbook Intelligence Platform for global trade data. Process any trade Excel workbook into clean, validated, categorized output with minimal user configuration.

## Current Phase

Phase 1 — Workbook Intelligence Engine (COMPLETE)

## Architecture

Clean Architecture (api → application → domain ← infrastructure).

The Intelligence Engine sits at the core:
1. **WorkbookAnalyzer** — detects sheets, header row, counts columns/rows
2. **SemanticDetector** — identifies countries, HS codes, ports by value patterns
3. **TemplateColumnMapper** — 4-stage matching: exact → normalized → synonym → fuzzy
4. **Confidence Engine** — per-field + overall confidence scoring

## Key Files

| File | Purpose |
|---|---|
| `domain/workbooks/intelligence.py` | All intelligence domain models |
| `domain/workbooks/synonyms.py` | Global trade synonym dictionary (20+ fields) |
| `domain/workbooks/analyzer.py` | Structure analysis (sheets, header, sampling) |
| `domain/workbooks/semantic_detector.py` | Value-based field type detection |
| `domain/workbooks/alias_store.py` | User-confirmed mapping learning |
| `application/workbooks/intelligence_service.py` | Orchestrates full intelligence report |
| `application/workbooks/column_mapper.py` | Layered header → business field matching |
| `application/workbooks/validation.py` | Validation with intelligence enrichment |
| `application/processing/service.py` | Processing pipeline (non-fatal validation) |
| `api/routes/jobs.py` | Intelligence API endpoint |
| `frontend/src/features/jobs/components/intelligence-report.tsx` | Intelligence UI component |
| `templates/indian_rice_exports/columns.json` | Reference template (20 business fields) |

## Benchmark

The benchmark workbook is at `backend/samples/1006 ALL EXPORT JULY 25.xlsx`.
- 19 columns, 19,967 data rows
- 20 business fields defined in template (3 required, 17 optional)
- 19/20 mapped (all except shipping_company which isn't in the workbook)
- Overall confidence: 99.75%
- Structure confidence: 95%

## Test Suite

26 tests total (18 pre-existing + 8 benchmark regression tests).
Run with: `cd backend && python -m pytest tests/ -v`

The 4 `PermissionError` failures on temp directory are pre-existing environment issues, not code bugs.

## Rules

1. NEVER break backward compatibility
2. ALL existing tests must pass
3. Benchmark workbook must never be modified — fix the code instead
4. Keep architecture generic — don't overfit to rice exports
5. The intelligence report must always be explainable to business users
6. Validation is advisory, not blocking (except for truly fatal errors)

## What NOT To Build Yet

- Multi-tenant architecture
- PostgreSQL migration
- Celery/Redis/async processing
- Authentication/Auth
- Plugin marketplace
- LLM/AI integrations
- Multiple industries beyond the reference template