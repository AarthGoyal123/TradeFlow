# Architecture Decisions

This file records major technical decisions, rationale, rejected alternatives, trade-offs, and future improvements.

## ADR-001 - Build TradeFlow as a Template-Driven Processing Platform

Date: 2026-07-28

Status: accepted.

### Decision

TradeFlow will be built as a reusable, template-driven Excel processing platform.
Dataset-specific behavior belongs in templates and rule packs rather than hardcoded application logic.

### Rationale

- The long-term goal is to support new Excel formats by adding templates.
- This avoids creating a brittle one-off script for the first client.
- Templates can be versioned, reviewed, tested, and reused.

### Rejected Alternatives

- One Python script per client format.
- Hardcoded if/else branches for specific source columns or business rules.

### Trade-Offs

- More upfront structure is required.
- Template validation becomes important.
- The initial MVP may take slightly longer, but future dataset support becomes cheaper and safer.

### Future Improvements

- Add a template editor UI.
- Add template schema validation with detailed diagnostics.
- Add a template test runner with fixture workbooks.

## ADR-002 - Keep AI Optional and Avoid Paid APIs in MVP

Date: 2026-07-28

Status: accepted.

### Decision

The MVP will use deterministic rules, regex, and RapidFuzz matching.
Paid APIs will not be used.
LLMs and embeddings are optional future enhancements only.

### Rationale

- The client requires fast, local processing.
- Deterministic rules are easier to audit.
- Avoiding paid APIs keeps costs predictable.

### Rejected Alternatives

- Calling paid LLM APIs during processing.
- Making embeddings mandatory for importer identification.

### Trade-Offs

- Some ambiguous cases will go to manual review.
- Rule packs need careful maintenance.

### Future Improvements

- Optional local embeddings for similarity search.
- Human feedback loop for learned decisions.
- Configurable ML module enabled per template.

## ADR-003 - Use a Knowledge Base as Project Memory

Date: 2026-07-28

Status: accepted.

### Decision

The project will maintain a `knowledge/` folder containing long-term client requirements, business rules, Excel format knowledge, and architecture decisions.

### Rationale

- Future implementation sessions must preserve context.
- Requirements and decisions need chronological traceability.
- Conflicts should be surfaced before architecture changes.

### Rejected Alternatives

- Keeping project memory only in chat history.
- Keeping requirements scattered across code comments and tickets.

### Trade-Offs

- Documentation must be updated as part of normal development.
- The team must review knowledge files before feature work.

### Future Improvements

- Add decision IDs referenced from code and tests where useful.
- Add a lightweight release checklist that includes knowledge-base review.

## ADR-004 - Use a Monorepo with Separate Backend and Frontend Apps

Date: 2026-07-28

Status: accepted.

### Decision

TradeFlow will use a single Git repository with separate `backend/` and `frontend/` application roots.
Top-level `templates/`, `rules/`, `engine/`, and `config/` folders will be kept for product-level configuration and future packaging decisions.

### Rationale

- The MVP needs tight coordination between API contracts, templates, and UI workflow.
- A monorepo keeps documentation, fixtures, templates, and application code versioned together.
- Separate app roots keep Python and TypeScript tooling clean.

### Rejected Alternatives

- Separate repositories for backend and frontend during MVP.
- A single mixed application folder containing both Python and TypeScript code.

### Trade-Offs

- CI must understand both Python and Node workflows.
- Shared contracts need discipline until generated types are introduced.

### Future Improvements

- Add OpenAPI-based TypeScript client generation.
- Add workspace-level CI that runs backend and frontend checks independently.

## ADR-005 - Use Pragmatic Clean Architecture Backend Boundaries

Date: 2026-07-28

Status: accepted.

### Decision

The backend will be organized around explicit boundaries:

- `api` for HTTP routes, request/response schemas, and API dependencies.
- `application` for use-case orchestration.
- `domain` for framework-independent business models and contracts.
- `engine` for reusable processing pipeline infrastructure.
- `infrastructure` for filesystem, template loading, persistence, and other external systems.
- `core` for settings, logging, and shared error handling.

### Rationale

- TradeFlow must remain a reusable processing engine, not a FastAPI-bound script.
- Clear dependency direction keeps future CLI, background worker, and SaaS paths open.
- Domain and engine code should be testable without HTTP, SQLite, or frontend concerns.

### Rejected Alternatives

- Keeping broad folders such as `services`, `models`, and `database` as primary boundaries.
- Letting FastAPI route handlers call processing code directly.
- Implementing a heavy enterprise architecture with excessive abstractions before the MVP.

### Trade-Offs

- Slightly more files and ceremony in the initial scaffold.
- Developers must respect import direction.
- The payoff is better long-term maintainability and easier testing.

### Future Improvements

- Add import-lint rules if boundaries begin to drift.
- Generate TypeScript API clients from OpenAPI once API contracts stabilize.

## ADR-006 - Use Plugin-Based Pipeline Steps with a Shared Processing Context

Date: 2026-07-28

Status: accepted.

### Decision

Processing will be implemented as dynamically registered pipeline stages.
Each stage receives and returns a shared `ProcessingContext`.
A `PipelineRegistry` maps configured stage names to stage implementations.
The pipeline executor records metrics for every stage.

### Rationale

- Templates need to control which processing stages run and in what order.
- New modules should plug into the engine without rewriting orchestration logic.
- Stage metrics are required to prove the under-30-second MVP goal and diagnose failures.

### Rejected Alternatives

- Hardcoded sequential function calls in a single processor.
- One processor class per client template.
- Runtime package discovery for external plugins before the MVP needs it.

### Trade-Offs

- Stage contracts must be stable.
- Template validation must reject unknown stage names.
- Dynamic registration adds a little indirection, but keeps extension points clean.

### Future Improvements

- Add external plugin discovery through Python entry points if TradeFlow becomes a broader platform.
- Add per-stage retry or skip policies for non-critical future modules.

## ADR-007 - Use Lightweight SQLite Job Tracking Before Processing Execution

Date: 2026-07-28

Status: accepted.

### Decision

The API foundation will persist upload jobs in SQLite before workbook processing exists.
Job persistence will be implemented behind a repository interface and accessed through application services.

### Rationale

- Upload, retrieval, and future processing status APIs need stable job identifiers.
- SQLite is required for the MVP and is sufficient for local client workflows.
- Keeping persistence behind a repository preserves the existing architecture boundary.

### Rejected Alternatives

- In-memory job tracking, because job state would be lost on restart.
- Direct SQL calls from API routes, because that violates the established dependency direction.
- A full migration framework immediately, because the current schema is intentionally small.

### Trade-Offs

- Manual table initialization is acceptable for MVP foundation but may need migrations later.
- SQLite write concurrency is limited, but acceptable before background processing and SaaS scale.

### Future Improvements

- Add Alembic migrations when schema evolution accelerates.
- Add job event history and output tracking tables.
- Move to PostgreSQL if SaaS concurrency requires it.

## ADR-008 - Keep Excel-Specific Workbook Access in Infrastructure

Date: 2026-07-28

Status: accepted.

### Decision

OpenPyXL access will live in infrastructure adapters.
Application and domain code will depend on workbook abstractions and ports rather than OpenPyXL objects.

### Rationale

- The processing engine should not be coupled directly to one Excel library.
- Workbook validation and column mapping should be testable with in-memory workbook abstractions.
- Future support for alternate readers or streaming strategies should not require API or domain rewrites.

### Rejected Alternatives

- Passing OpenPyXL worksheets into application services.
- Reading all Excel data directly inside API routes.
- Implementing Pandas-based loading before structural workbook validation exists.

### Trade-Offs

- A small abstraction layer is added before full processing exists.
- The adapter must preserve enough worksheet behavior for efficient future processing.

### Future Improvements

- Add streaming row readers for very large workbooks.
- Add `.xls` conversion or reader support if client files require legacy Excel parsing.
- Add fixture-based performance tests once representative files are available.

## ADR-009 - Use a Domain Intermediate Dataset Between Workbook Reading and Rules

Date: 2026-07-28

Status: accepted.

### Decision

Processing will convert a validated workbook into a domain-owned intermediate dataset before rule execution or output generation.
The intermediate dataset will preserve source row numbers, mapped template fields, retained source headers, and normalized values.

### Rationale

- Rule execution and output generation need a stable input that is not tied to OpenPyXL.
- Preserving source row numbers keeps future reports auditable.
- Separating dataset creation, column removal, and normalization makes each processing stage testable.

### Rejected Alternatives

- Passing worksheet readers directly into future rule-engine code.
- Using Pandas DataFrames as the domain model before core processing semantics are defined.
- Running normalization directly in infrastructure while reading Excel rows.

### Trade-Offs

- The intermediate model adds a small translation step before full processing exists.
- Large files may require a streaming dataset implementation later.

### Future Improvements

- Add chunked processing for very large workbooks.
- Add dataset persistence or snapshots if report generation requires it.
- Add rule-engine evidence collections against intermediate rows.

## ADR-010 - Implement Rule Engine Foundation as Domain/Application Logic

Date: 2026-07-28

Status: accepted.

### Decision

The rule engine foundation will live in domain and application layers.
Domain code defines rule models, operators, outcomes, and reports.
Application code orchestrates rule evaluation over the intermediate dataset.

### Rationale

- Rules are business behavior and must not be hidden in API or infrastructure code.
- Rule execution should consume the domain intermediate dataset instead of Excel-specific objects.
- Future custom rule packs need stable extension points without changing orchestration.

### Rejected Alternatives

- Implementing rule execution directly inside processing service.
- Evaluating rules inside infrastructure adapters.
- Adding public rule APIs before internal rule semantics are stable.

### Trade-Offs

- The foundation adds internal models before full client rule packs exist.
- Conflict resolution remains intentionally conservative until routing/output behavior is implemented.

### Future Improvements

- Load rule definitions from template rule-pack JSON files.
- Add RapidFuzz-backed operators.
- Add conflict resolution and final row routing.
- Persist rule execution reports for processing reports and audit trails.

## ADR-011 - Migrate Persistence to SQLAlchemy and Alembic

Date: 2026-08-13

Status: accepted.

### Decision

TradeFlow will use SQLAlchemy 2.0 and Alembic for its persistence layer. The JobRepository and ProcessingReportRepository interfaces will be backed by a new SQLAlchemyJobRepository. SQLite will remain the default database for local development and testing, while PostgreSQL will be supported for staging and production via environment configuration.

### Rationale

- **Database Agnosticism:** Raw sqlite3 queries coupled the application tightly to SQLite. Using SQLAlchemy provides an abstraction over the database engine.
- **Production Readiness:** SQLite is not suitable for a production SaaS architecture. SQLAlchemy allows seamless transition to PostgreSQL in production environments.
- **Migration Management:** As the domain model evolves, schema migrations need to be version-controlled and reproducible. Alembic provides this capability.
- **Synchronous Design (For Now):** The existing application and file processing logic are strictly synchronous. Introducing asynchronous database drivers (syncpg) would require an extensive and risky rewrite of the entire API and worker architecture without immediate benefit. Therefore, synchronous SQLAlchemy and psycopg are used.

### Rejected Alternatives

- **Asyncpg/SQLAlchemy Async:** Rejected because the application processing is inherently synchronous and CPU-bound. Transitioning the entire API layer to async just to support an async DB driver would be premature optimization and risky.
- **Raw PostgreSQL Queries:** Rejected because it sacrifices local development velocity. Running a PostgreSQL container locally consumes significant disk space and slows down the feedback loop. We need SQLite for local dev.

### Trade-offs

- The SQLiteJobRepository is temporarily marked as legacy but kept to demonstrate a clean fallback path.
- The use of synchronous database operations might become a bottleneck under extremely high concurrent web traffic, though background processing (Celery) is the actual scaling dimension for TradeFlow.

### Future Improvements

- Fully deprecate and remove SQLiteJobRepository once PostgreSQL production behavior is deeply established.
- Add connection pooling for PostgreSQL (already handled transparently by SQLAlchemy engine).
