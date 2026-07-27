# Architecture

TradeFlow is designed as a template-driven processing platform.

## Logical Layers

1. Frontend application for upload, template selection, job status, and downloads.
2. FastAPI backend for API orchestration.
3. Processing engine for validation, transformation, rules, scoring, and output generation.
4. Template and rule configuration for dataset-specific behavior.
5. SQLite persistence for jobs, reports, and future learned decisions.

## Core Flow

```text
Excel Upload
-> Validation
-> Column Removal
-> Normalization
-> Keyword Engine
-> Regex Engine
-> RapidFuzz Matching
-> Confidence Scoring
-> Needs Review
-> Output Generation
```

## Configuration Boundary

Dataset-specific logic belongs in `templates/` and `rules/`.
Application code should provide reusable engine modules only.

## Repository Layout

```text
backend/     Python FastAPI API and processing engine.
frontend/    React, Vite, TypeScript, Tailwind UI.
templates/   Dataset templates and template-specific rule packs.
rules/       Shared rule packs planned for reuse across templates.
engine/      Product-level engine documentation or future package boundary.
config/      Product-level configuration.
knowledge/   Long-term project memory.
```

## Backend Boundaries

```text
backend/app/api/             HTTP routes, API schemas, and error mapping.
backend/app/application/     Use-case orchestration.
backend/app/domain/          Framework-independent domain models and ports.
backend/app/engine/          Pipeline context, registry, plugins, metrics, and executor.
backend/app/infrastructure/  Filesystem, template loading, persistence, and adapters.
backend/app/core/            Settings, structured logging, and shared errors.
```

Dependency direction:

```text
api -> application -> domain
application -> engine
application -> infrastructure through domain ports
engine -> domain
infrastructure -> domain
domain -> no FastAPI, filesystem, Pandas, SQLAlchemy, or frontend dependencies
```

## Processing Foundation

Pipeline stages are plugin-registered and resolved through `PipelineRegistry`.
Each stage receives a shared `ProcessingContext` and returns the updated context.
`PipelineExecutor` instruments every configured stage with:

- stage name
- duration in milliseconds
- status
- row count before and after when available
- error code when a stage fails

The current built-in stages are no-op placeholders. They establish extension points only and do not implement importer detection, Excel cleaning, or classification.

## Current Implementation

- Backend has a minimal FastAPI application factory in `backend/app/main.py`.
- Backend exposes `GET /health`.
- Backend includes typed settings, structured logging, and a project error hierarchy.
- Backend includes typed template models and a filesystem template repository.
- Backend includes plugin-based pipeline registration, processing context, and stage metrics.
- Frontend has a minimal Vite/React/Tailwind shell.
- `templates/indian_rice_exports/` contains starter configuration files.
