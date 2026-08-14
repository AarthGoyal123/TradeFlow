# TradeFlow

TradeFlow is a **Workbook Intelligence Platform** for global trade data processing.

It ingests trade/export Excel workbooks, automatically detects business fields, maps them to a processing template, validates data quality, and generates cleaned output workbooks — all with explainable confidence scores.

The first reference implementation is Indian Rice Export Shipments, but the architecture is designed for any trade industry.

## Philosophy

TradeFlow is **not** a template validator.

TradeFlow is a **Workbook Intelligence Platform**.

The system should never ask "Is there a column named Consignee?"
Instead it asks "Where is the consignee information in this workbook?"

That distinction drives the entire architecture.

## Core Flow

```
Excel Upload
  ↓
Workbook Intelligence Engine
  ├── Structure Analysis (sheets, header row, columns, data rows)
  ├── Semantic Detection (countries, ports, HS codes, dates, currency)
  ├── Column Mapping (exact → normalized → synonym → fuzzy → semantic)
  └── Confidence Scoring (per-field + overall)
  ↓
Validation Report (explainable, non-blocking)
  ↓
Processing Pipeline
  ├── Dataset Building
  ├── Column Removal
  ├── Normalization
  ├── Rule Evaluation
  └── Output Generation
  ↓
Download (Clean Data, Removed Rows, Needs Review, Report)
```

## Current Status

- Phase 1 — Architecture Hardening — COMPLETE
- Phase 2 — Async/Celery Architecture — COMPLETE
- Phase 3 — SQLAlchemy/Alembic — COMPLETE
- Phase 5 — Zero-Cost Object Storage Architecture — COMPLETE
- Phase 6 — Authentication/Tenant Security — COMPLETE
- Phase 6.5 — Auth Integration/Test Restoration — COMPLETE
- Phase 7A — Google OAuth — COMPLETE
- Phase 7B — Browser Authentication Forensic Fixes — COMPLETE
- Phase 8 — Production UX — COMPLETE
- Phase 9A — Production Hardening — COMPLETE
- Phase 9B — NOT STARTED

## Permanent Project Constraints

1. **ZERO PAID SERVICES**: TradeFlow must remain entirely usable without paid APIs, Auth0, Clerk, Firebase, AWS, or paid DBs. Google OAuth is used strictly as an Identity Provider.
2. **ZERO HEAVY LOCAL DEPS**: Do NOT introduce Docker, WSL, PostgreSQL, Redis, MinIO, or Playwright locally unless explicitly requested. Local storage uses standard disk; local execution is purely synchronous.
3. **RESPECT DISK SPACE**: The `C:` drive has limited space. Prefer existing `D:` drive environments.
4. **GOLDEN BENCHMARK PRESERVATION**: The exact benchmark row counts (19967/8701/10565/701) MUST NEVER change. Any refactor or feature must preserve this behavior.
5. **NEVER BREAK BACKWARD COMPATIBILITY**: Keep existing tests green.

## Planned Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, OpenPyXL, RapidFuzz
- **Frontend:** React, Vite, TypeScript, Tailwind CSS, shadcn/ui

## Development Commands

Backend:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

Tests:
```bash
cd backend
python -m pytest tests/ -v
```