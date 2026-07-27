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
- `backend/tests/test_template_loading.py` verifies starter template loading and missing-template errors.
- `backend/tests/test_pipeline_foundation.py` verifies registry behavior and per-stage pipeline metrics.

## Current Verification Note

The backend test suite passes with pytest cache disabled, which is configured in `backend/pyproject.toml`.
This avoids local cache/bytecode permission issues observed in the current Windows workspace.
