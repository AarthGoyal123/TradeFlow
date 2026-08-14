# Roadmap

## Phase 1 — Workbook Intelligence Engine (✅ Complete)

- [x] Clean Architecture foundations (api → application → domain ← infrastructure)
- [x] FastAPI service with health, template, and job endpoints
- [x] OpenPyXL workbook loading with port-based abstraction
- [x] Template system with Pydantic validation
- [x] Processing pipeline (validation → dataset → cleanup → rules → outputs)
- [x] Rule engine (keyword, regex, fuzzy matching operators)
- [x] Frontend shell (upload, job list, job detail, reports)
- [x] SQLite job persistence
- [x] **Workbook Intelligence Engine** — structure analysis, semantic detection, layered column matching
- [x] **Global Trade Synonym Dictionary** — 20+ business fields with real-world header variants
- [x] **Non-fatal validation** — missing columns produce warnings, not crashes
- [x] **Intelligence API** — `GET /jobs/{id}/intelligence` with full analysis report
- [x] **Benchmark workbook** (19 columns, 19,967 rows) processes at 99.75% confidence
- [x] **8 regression tests** covering original/reordered/extra/missing-column scenarios
- [x] **Frontend intelligence report card** wired into Job Detail page
- [x] All pre-existing tests continue to pass

## Phase 2 — Column Intelligence & Template Auto-Detection (Next)

Design for, and partially implement:

- [ ] **Workbook Classifier** — detect workbook type, industry, likely template automatically
- [ ] **Template Auto-Detection** — score each template against workbook, rank candidates
- [ ] **Suggested Template** on upload page — auto-select with user override
- [ ] **LearningAliasStore persistence** — SQLite-backed user-confirmed mappings
- [ ] **Semantic detector improvements** — reduce false positives (FOB→HS code, etc.)
- [ ] **Confidence threshold tuning** — calibrated against real-world data

## Phase 3 — Async Processing & Performance (Planned)

Design for, but do not build yet (wait until user demand):

- [ ] Async processing via background worker
- [ ] WebSocket progress updates
- [ ] Streaming workbook reader for 500K+ row files
- [ ] Template caching for hot reload
- [ ] Performance benchmarks against large workbooks

## Phase 4 — Multi-Tenant Foundation (✅ Complete - Built as Phase 7)

- [x] Tenant isolation in storage and database
- [x] SQLAlchemy migration
- [x] User authentication (Google OAuth) + RBAC
- [x] Cookie-based sessions with CSRF protection

## Phase 5 — Plugin Architecture & AI (Planned)

Design for, but do not build yet:

- [ ] SemanticDetector plugin protocol
- [ ] LLM detector plugin (for ambiguous columns)
- [ ] Plugin registry + configuration

## Phase 6 — Frontend Tests (Planned)

- [ ] Vitest + React Testing Library setup
- [ ] Component tests for 10+ UI components
- [ ] Integration tests for API client hooks
- [ ] E2E test for upload → analyze → process → download flow

## Phase 7 — Authentication & Multi-Tenancy (✅ Complete)
- [x] Google OAuth implementation
- [x] Session cookie and CSRF security architecture
- [x] Tenant-isolated SQLAlchemy Database architecture

## Phase 8 — Production Hardening & Core UX (✅ Complete)
- [x] Settings & Authentication info UI
- [x] Logout mechanics and global 401 interceptors
- [x] Bounded exponential backoff for UI polling
- [x] Decoupled Job detail visual states
- [x] UX Navigation logic refactored for synchronous local endpoints

## Phase 9 — Production Hardening & Deployment (✅ Phase 9A Complete)
- [x] Artifact retention/cleanup service
- [x] Production settings validation
- [x] Caddy reverse proxy template
- [ ] Complete Phase 9B deployments
