# Testing

TradeFlow testing should focus on correctness, auditability, and regression safety.

## Planned Test Types

- Unit tests for engine modules.
- Template validation tests.
- Rule engine tests.
- Excel fixture regression tests.
- API tests for upload and download flows.
- Frontend workflow tests after UI implementation.

## Quality Gates

- Business rules must have tests when implemented.
- Output workbook generation must be validated with representative fixtures.
- `Needs_Review` routing must be tested for ambiguous data.

## Current Tests

- `backend/tests/test_health.py` verifies the FastAPI health endpoint.
- `backend/tests/test_template_api.py` verifies `GET /templates` response shape.
- `backend/tests/test_template_details_api.py` verifies `GET /templates/{template_id}` and missing-template behavior.
- `backend/tests/test_template_service.py` verifies application-level template listing.
- `backend/tests/test_template_loading.py` verifies starter template loading and missing-template errors.
- `backend/tests/test_pipeline_foundation.py` verifies registry behavior and per-stage pipeline metrics.
- `backend/tests/test_job_api.py` verifies upload-only job creation, extension errors, missing template errors, upload directory creation, max size errors, and job retrieval.
- `backend/tests/test_sqlite_job_repository.py` verifies SQLite job persistence and missing-job errors.
- `backend/tests/test_openpyxl_workbook_loader.py` verifies OpenPyXL-backed workbook loading, header extraction, row numbers, and empty cell handling.
- `backend/tests/test_workbook_validation_service.py` verifies template-based sheet selection, column mapping, missing required columns, and unreadable workbook validation results.
- `backend/tests/test_processing_stages.py` verifies column removal and normalization stages.
- `backend/tests/test_processing_service.py` verifies synchronous processing from uploaded job to normalized intermediate dataset and failed-job handling.
- `backend/tests/test_rule_operators.py` verifies built-in rule operators.
- `backend/tests/test_rule_evaluator.py` verifies row classification, cell transformation, validation finding, and disabled-rule behavior.
- `backend/tests/test_rule_evaluation_service.py` verifies deterministic rule evaluation reports over intermediate datasets.
- `backend/tests/test_benchmark_regression.py` validates the end-to-end processing pipeline, including rule preservation (`confidence`, `row_number`), correct routing of `TO ORDER` and `BANK` consignees, and accurate final output formats.


## Current Verification Note

The backend test suite passes with pytest cache disabled, which is configured in `backend/pyproject.toml`.
This avoids local cache/bytecode permission issues observed in the current Windows workspace.
Mypy should be run with a writable cache directory in this environment, for example under `$env:TEMP`.

## CI Quality Gate

The project uses a GitHub Actions CI pipeline to protect the golden regression baseline.

What can block a PR?
- test failure
- benchmark regression (e.g. Clean_Data row counts change)
- output schema change (e.g. columns reordered or removed)
- lint failure (ruff or eslint)
- type-check failure (mypy)
- frontend build failure

### CI Checks

**Backend:**
- `pytest` (including golden regression against Indian Rice Exports benchmark)
- `ruff check .`
- `mypy app`

**Frontend:**
- `npm run lint`
- `npm run build`

**Golden Regression:**
The Indian Rice Exports benchmark workbook is committed safely to the repository (`backend/samples/`) and used in the CI pipeline to run end-to-end regression validation. It ensures the exact required 8,701 clean / 11,266 removed row counts and explicit outputs are generated.
