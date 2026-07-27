# Changelog

All notable project changes will be documented here.

## 2026-07-28

- Created initial project knowledge base.
- Created baseline project documentation.
- Added monorepo scaffold with `backend/` and `frontend/` roots.
- Added minimal FastAPI application shell with `GET /health`.
- Added initial Vite, React, TypeScript, and Tailwind frontend shell.
- Added starter `indian_rice_exports` processing template and empty rule packs.
- Added `.env.example` for local development defaults.
- Introduced backend boundaries for API, application, domain, engine, infrastructure, and core modules.
- Added typed settings, structured logging, and TradeFlow error hierarchy.
- Added typed template models and filesystem template repository.
- Added plugin-based pipeline registry, shared `ProcessingContext`, pipeline executor, and per-stage metrics.
- Added foundation tests for template loading and pipeline execution.
- Added `GET /templates` API endpoint returning filesystem template summaries.
- Added `GET /templates/{template_id}` API endpoint returning template details.
- Added upload-only `POST /jobs` API endpoint with extension and size validation.
- Added `GET /jobs/{job_id}` API endpoint returning persisted job metadata.
- Added lightweight SQLite job repository and local upload storage.
- Added workbook processing foundation with OpenPyXL-backed loading, sheet reading, template column mapping, and structured validation results.
