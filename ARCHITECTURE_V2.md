# TradeFlow Architecture Audit & Proposal (V2)

This document serves as the formal architecture review and proposed target architecture for TradeFlow, evolving it from a local processing script/MVP into a production-grade SaaS platform while strictly preserving its golden regression baseline.

## 1. Current Architecture
TradeFlow is currently built as a monolithic, synchronously processing web application. It follows Clean Architecture principles logically (API → Application → Domain ← Infrastructure) but executes all operations synchronously in the HTTP request lifecycle. The system is heavily coupled to the local filesystem for storage and SQLite for persistence.

## 2. Current Technology Stack
- **Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, Pandas, OpenPyXL, RapidFuzz.
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form.
- **Database:** SQLite (local file-backed).
- **Storage:** Local filesystem (`./data/uploads`, `./data/outputs`).

## 3. Current Processing Flow
1. **Upload:** Client uploads an Excel file via `POST /jobs`. The file is saved locally, and an SQLite `jobs` record is created.
2. **Analysis:** Client requests `/intelligence`, which synchronously reads the file, detects sheets, headers, and column mappings via `WorkbookIntelligenceService`.
3. **Processing:** Client triggers `POST /jobs/{id}/process`. The FastAPI worker synchronously:
   - Validates the workbook.
   - Loads the dataset via OpenPyXL.
   - Removes columns & normalizes data.
   - Evaluates rules & transforms cells.
   - Routes rows (Clean/Removed/Needs Review).
   - Generates output Excel workbooks to the local filesystem.
   - Saves a summary report to SQLite.
4. **Download:** Client downloads the generated files via `GET /jobs/{id}/outputs/{type}`.

## 4. Current Database/Storage Design
- **Database:** SQLite stores minimal job states and processing summaries. Entities like Users, Organizations, or Tenants do not exist.
- **Storage:** Uploads and outputs are stored directly in the local filesystem, posing major scalability and security risks (no persistence across ephemeral containers, path traversal risks, storage exhaustion).

## 5. Current Frontend Architecture
- Built with React and Vite.
- Communicates directly with the backend REST API using TanStack Query for state management.
- Polling is manually emulated or absent during long processing steps.
- UI components are functional but treat the system as a single-tenant utility rather than a secure multi-tenant SaaS.

## 6. Current Template Architecture
Templates are defined in the filesystem (e.g., `templates/indian_rice_exports/`) as a collection of JSON configuration files (`config.json`, `columns.json`, `pipeline.json`, `output.json`) and rule packs. This makes them highly extensible but hard to manage dynamically via API or database.

## 7. Current Security Posture
- **Authentication/Authorization:** None. Any user can upload and process data.
- **Tenant Isolation:** None.
- **Storage:** Files are stored locally. While UUIDs are used, there are no strict access controls on the generated artifacts.
- **File Validation:** Basic extension and size limits exist, but no deep MIME or macro scanning.

## 8. Current Scalability Limitations
- **Synchronous Processing:** Processing 20,000+ rows synchronously blocks the FastAPI worker, leading to HTTP timeouts (as observed during verification).
- **Memory:** Pandas and OpenPyXL can consume significant memory for large workbooks.
- **Storage/DB:** SQLite and local storage prevent horizontal scaling (running multiple backend instances).

## 9. Current SOLID Violations / Architectural Smells
- **DIP (Dependency Inversion):** While ports/adapters are used, the synchronous execution flow limits the scalability of the application layer. The API directly triggers heavy domain logic.
- **SRP (Single Responsibility):** The `ProcessingService` orchestrates validation, datasets, rules, outputs, and database updates in one massive synchronous function.

## 10. Current Technical Debt
- Lack of background task processing.
- Missing database migrations (Alembic).
- No staging/production environment separation.
- Frontend polling/timeout issues during long HTTP requests.

## 11. Current Testing Coverage
- 55 automated backend tests using pytest.
- Strong domain logic and rule engine tests.
- E2E testing relies on the benchmark workbook (`1006 ALL EXPORT JULY 25.xlsx`).
- Frontend tests (Playwright) are currently missing/failing due to local storage constraints.

## 12. Current Documentation Gaps
- Lack of detailed deployment strategies.
- No defined API versioning strategy.
- Missing schema documentation for adding new templates natively.

## 13. What Should Remain Unchanged
- The core **Domain Logic** (rules, matching, normalization, intelligence).
- The **Golden Regression Baseline** for `indian_rice_exports` (19,967 input -> 8,701 clean, 11,266 removed).
- The Clean Architecture module boundaries (`api/`, `application/`, `domain/`, `infrastructure/`).

## 14. What Should Be Redesigned
- **Processing Execution:** Move from synchronous API calls to asynchronous background workers (e.g., Celery/Redis).
- **Persistence:** Move from SQLite to PostgreSQL.
- **Storage:** Move from local filesystem to S3-compatible object storage.
- **Template Management:** Migrate templates from local JSON files to the database (or a hybrid cached model) to support dynamic UI-driven template creation.

## 15. Proposed Production Architecture
```text
[ React Frontend ] -> (HTTPS/WAF) -> [ Load Balancer ] -> [ FastAPI API Nodes ]
                                                                 |
                                                                 +-> [ PostgreSQL ] (Metadata, Jobs, Users)
                                                                 +-> [ Redis ] (Message Broker, Cache)
                                                                 +-> [ S3 Object Storage ] (Uploads, Outputs)
                                                                 |
                                                          [ Celery/Worker Nodes ] (Heavy Excel Processing)
```

## 16. Proposed Technology Stack
- **Frontend:** React, Vite, Tailwind CSS, TanStack Query (unchanged, highly effective).
- **Backend API:** FastAPI, Pydantic, SQLAlchemy, Alembic (migration added).
- **Database:** PostgreSQL (for relational integrity, multi-tenancy, concurrent access).
- **Async Workers:** Celery + Redis (standard, mature Python background processing).
- **Storage:** MinIO (local dev) / AWS S3 (production).

## 17. Migration Plan (Phased Approach)
- **Phase 0:** Architecture Audit (Current Phase).
- **Phase 1:** Harden current architecture (type checks, strict validation).
- **Phase 2:** Production Job Model (State machine for jobs: `UPLOADED` -> `PROCESSING` -> `COMPLETED`).
- **Phase 3:** PostgreSQL + Alembic migrations.
- **Phase 4:** Redis + Background Workers (move processing out of FastAPI).
- **Phase 5:** S3 Object Storage adapter.
- **Phase 6:** Authentication & Authorization (JWT/OIDC).
- **Phase 7:** Frontend UX overhaul (WebSockets/Polling for job status).
- **Phase 8:** Observability (Prometheus, structured logging).
- **Phase 9:** Docker + CI/CD.
- **Phase 10:** Production Deployment.

## 18. Risk Analysis
- **Timeout Risks:** High if Phase 4 is delayed. Large files currently timeout the HTTP request.
- **Memory Risks:** Large Excel files (100k+ rows) might OOM workers. We must ensure streaming reads/writes where possible.
- **Regression Risks:** Refactoring the engine to use workers might inadvertently change data routing. Strict golden regression tests must be run on every commit.

## 19. Estimated Implementation Phases
- Phases 1-3: 1-2 weeks. Focus on data modeling and state management.
- Phases 4-5: 2 weeks. Infrastructure shift to distributed processing.
- Phases 6-7: 2 weeks. Security and UX polish.
- Phases 8-10: 1 week. DevOps and launch.

## 20. Golden Regression Requirements
Before merging any change to the processing pipeline or infrastructure adapters, the following exact benchmark MUST be verified automatically:

**Input:** `1006 ALL EXPORT JULY 25.xlsx`
**Total Rows:** 19,967
**Clean_Data.xlsx:** 8,701 rows
**Removed_Rows.xlsx:** 11,266 rows (10,565 TO ORDER, 701 bank)
**Needs_Review.xlsx:** 0 rows
**Clean Columns Order:** exporter_name, exporter_address, exporter_city_state, consignee_name, country, port, date, description, quantity, uqc, unit_rate, currency, fob.
**Metadata constraints:** Clean output MUST NOT contain `route`, `confidence`, `job_id`, or other internal fields. Removed rows must be FULL original rows.
