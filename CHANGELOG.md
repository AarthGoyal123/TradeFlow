# Changelog

All notable project changes will be documented here.

## 2026-08-14

- **Phase 9A Completed**: Production Hardening.
  - Implemented `CleanupService` to securely purge old job artifacts from disk based on a configurable retention policy, preserving job metadata in the database.
  - Implemented rigorous environment variable validation for production (`AUTH_SECRET` entropy, wildcard CORS block, secure cookies enforcement).
  - Designed minimal self-hosted production deployment architecture via ADR-015 (SQLite WAL, Single Node, Caddy Reverse Proxy).

- **Phase 8 Completed**: Production Hardening & Core Product UX.
  - Fixed logout logic to correctly clear `access_token` and `csrf_token` cookies via `path="/"`.
  - Implemented global session expiry handling, capturing `401 Unauthorized` via Axios interceptors and safely routing the user to `/login` without redirect loops.
  - Upgraded polling to use an exponential backoff strategy for queued/processing jobs to protect backend load.
  - Redesigned `job-detail.tsx` with discrete UI states for queued, processing, and failed.
  - Redesigned `settings.tsx` to surface authentication provider and read-only profile data.
  - Fixed a critical UI bug where the 30-second Axios timeout would suppress navigation for large files because the backend executes synchronously. The fix immediately routes users to the detail page, uncoupling navigation from processing time.
  - Verified Golden Benchmark matches original constraints perfectly.

- **Phase 7 Completed**: Authentication & Multi-Tenancy.
  - Implemented Google OAuth / OIDC architecture.
  - Built out secure `httpOnly`, `Secure`, `SameSite=lax` cookie-based sessions.
  - Implemented Double Submit Cookie pattern for CSRF protection on mutation endpoints.
  - Added Role-Based Access Control (RBAC) foundation.
  - Migrated database architecture to SQLAlchemy to support tenant-isolation.

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
- Added synchronous processing workflow from uploaded job to normalized intermediate dataset with job status updates and progress entries.
- Added rule engine foundation with typed rule definitions, built-in operators, row classifications, cell transformations, validation findings, and execution reports.
- Fixed processing service instantiation in regression tests by injecting `DataCleaningService`.
- Ensured `DatasetRow` fields (`row_number` and `confidence`) remain mutable to be explicitly preserved across processing stages.
- Broadened `TO ORDER` variations regex detection and updated frontend to display "Indian Rice Exports" cleanly.
- Validated real business logic against benchmark workbook `1006 ALL EXPORT JULY 25.xlsx`, correctly rejecting 10,565 rows for "to order" variations and 701 rows for "consignee_bank" entities.
- Completed Phase 0.5: Established golden regression protection and GitHub Actions CI workflow to ensure the benchmark baseline (19,967 input -> 8,701 clean / 11,266 removed) remains protected.
- Completed full production architecture audit and created `ARCHITECTURE_V2.md` proposal outlining migration to Celery, Redis, PostgreSQL, and object storage.
