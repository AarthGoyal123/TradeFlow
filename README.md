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

## Current Status (Phase 1 Complete)

- ✅ Workbook Intelligence Engine — structure analysis, semantic detection, layered column matching
- ✅ Global Trade Synonym Dictionary — 20+ business field groups with real-world header variants
- ✅ Non-fatal validation — missing columns produce warnings, not crashes
- ✅ Intelligence API — `GET /jobs/{id}/intelligence` returns full analysis report
- ✅ Rule Engine with complex regex handling, robust DatasetRow manipulation, and reliable Output creation.
- ✅ Full end-to-end benchmark regression test against realistic trade data (19k+ rows) properly segregating To Order/Bank consignees into `Removed_Rows.xlsx`.
- ✅ React Frontend capable of listing and processing jobs utilizing all backend functionalities.

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