# Architecture

TradeFlow follows Clean Architecture with strict layer separation:

```
api/ → application/ → domain/ ← infrastructure/
```

Dependencies point inward. Domain has zero external dependencies.

## Layers

### API Layer (`api/`)

FastAPI routes, Pydantic request/response schemas, error handlers, dependency injection.

### Application Layer (`application/`)

Use-case orchestration:
- `jobs/service.py` — upload handling
- `workbooks/validation.py` — workbook validation with intelligence
- `workbooks/column_mapper.py` — layered column matching
- `workbooks/intelligence_service.py` — full intelligence report orchestration
- `processing/service.py` — processing pipeline (validation → dataset → rules → output)
- `rules/service.py` — rule evaluation
- `templates/service.py` — template listing/fetching

### Domain Layer (`domain/`)

Business logic and contracts, no framework dependencies:

- `workbooks/` — models, ports, synonym dictionary, analyzer, semantic detector, alias store, intelligence models
- `templates/` — template definition models and repository port
- `jobs/` — job models and repository port
- `rules/` — rule engine (evaluator, operators, models)
- `datasets/` — intermediate dataset models
- `processing/` — progress/result models
- `outputs/` — output models and storage port

### Infrastructure Layer (`infrastructure/`)

Adapters implementing domain ports:
- `excel/openpyxl_loader.py` — workbook loading
- `excel/output_builder.py` — output workbook generation
- `files/local_uploads.py` — uploaded file storage
- `files/local_outputs.py` — output file storage
- `persistence/sqlite_jobs.py` — job repository
- `rules/filesystem.py` — rule pack loading
- `rules/rapidfuzz_operator.py` — fuzzy matching operator
- `template_store/filesystem.py` — template loading

## Workbook Intelligence Engine

The core innovation — analyzes workbooks before any validation:

```
WorkbookIntelligenceService
├── WorkbookAnalyzer
│   ├── Sheet detection (name, row count, column count)
│   ├── Header row detection
│   └── Data sampling (column types, empty rows)
├── SemanticDetector
│   ├── Country detection (value matching)
│   ├── HS Code detection (pattern matching)
│   ├── Port detection (dictionary lookup)
│   ├── Currency detection (symbol matching)
│   ├── Date detection (pattern matching)
│   └── Numeric detection
├── TemplateColumnMapper
│   ├── Stage 1: Exact match
│   ├── Stage 2: Normalized match (case/spaces/underscores)
│   ├── Stage 3: Synonym match (Global Dictionary)
│   └── Stage 4: Fuzzy match (RapidFuzz, ≥95% auto, ≥85% suggest)
└── Confidence Engine
    ├── Per-field confidence
    ├── Structure confidence
    └── Overall confidence score
```

## Synonym Dictionary Hierarchy

```
Template-specific aliases  (columns.json)
        ↓
Industry Dictionary       (per-industry overrides)
        ↓
Global Trade Dictionary   (20+ business field groups)
        ↓
Fuzzy Matching           (RapidFuzz WRatio)
        ↓
Semantic Detection       (value pattern analysis)
```

## Processing Pipeline

```
Validation → Dataset Building → Column Removal → Normalization
→ Rule Evaluation → Transformations → Output Generation
```

Validation is non-fatal: missing columns produce warnings, not crashes.
Only truly unrecoverable issues (unreadable file, missing required sheet) abort processing.

## Testing

- All tests in `backend/tests/`
- 55 tests including comprehensive backend regression and frontend rendering tests
- Benchmark workbook (`samples/1006 ALL EXPORT JULY 25.xlsx`) is the primary regression dataset
- Tests cover: original workbook, reordered columns, extra columns, missing optional columns

## Template Format

Templates define how a workbook should be interpreted and processed:

```
templates/{template_id}/
├── config.json       — Template metadata, workbook strategy, enabled modules
├── columns.json      — Required/optional field mappings with aliases
├── pipeline.json     — Ordered processing pipeline steps
├── output.json       — Output filenames and review threshold
└── rules/            — Rule packs (keyword, regex, fuzzy matching)
```

The `indian_rice_exports` template is the reference implementation with 20 business fields.