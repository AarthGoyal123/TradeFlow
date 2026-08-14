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

## Current Status (Phase 7A Complete)

- ✅ **Authentication & Authorization**: Argon2id passwords, HttpOnly JWT cookies, Double-submit CSRF, Role-Based Access Control (RBAC).
- ✅ **Tenant Isolation**: Secure multi-tenancy ensuring users can only access jobs, outputs, and artifacts belonging to their organization.
- ✅ **Google OAuth (OIDC)**: Direct, Zero-Paid-Service integration with Google for Social Login, including automatic account creation and identity linking, hardened against open redirects and race conditions.
- ✅ **Workbook Intelligence Engine**: Structure analysis, semantic detection, layered column matching, Global Trade Synonym Dictionary.
- ✅ **Processing Pipeline**: Complex regex handling, dataset normalization, robust rule evaluation, and output generation.
- ✅ **Golden Benchmark**: Full end-to-end regression test against realistic trade data (19k+ rows) properly segregating To Order/Bank consignees.

## Planned Stack

- **Backend:** Python 3.12, FastAPI, OpenPyXL, RapidFuzz, SQLite
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