# TradeFlow

TradeFlow is a configurable Excel data processing platform for cleaning trade/export shipment datasets and identifying importers.

The first MVP target is Indian export shipment data, where manual Excel cleaning currently takes 1-2 hours. The product goal is to reduce this work to under 30 seconds while preserving auditability and review controls.

## Principles

- Template-driven processing.
- No hardcoded business rules.
- Deterministic rules first.
- Unknown or low-confidence cases go to review.
- Every removal or classification should be explainable.
- Built as a reusable product, not a one-off script.

## Planned Stack

- Backend: Python 3.12, FastAPI, Pandas, OpenPyXL, RapidFuzz, SQLite.
- Frontend: React, Vite, TypeScript, Tailwind CSS, shadcn/ui.

## Project Memory

Long-term project knowledge lives in `knowledge/`.
Review it before implementing new features.

## Current Status

- Project documentation and knowledge base are initialized.
- Backend shell exists with `GET /health`.
- Backend architecture boundaries are established.
- Processing engine foundation exists with plugin-registered no-op stages, shared context, typed template validation, structured logging, and stage metrics.
- Workbook processing foundation exists with OpenPyXL-backed loading, sheet reading, template column mapping, and structured validation results.
- Template listing and template details APIs are implemented.
- Upload-only job APIs are implemented with SQLite job tracking.
- Frontend shell exists with Vite, React, TypeScript, and Tailwind configuration.
- Starter template exists for Indian rice export shipments.

## Development Commands

Backend:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```
