"""Pipeline execution metrics."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StageMetric:
    """Execution metrics captured for one pipeline stage."""

    stage: str
    duration_ms: float
    status: str
    rows_in: int | None = None
    rows_out: int | None = None
    error_code: str | None = None

