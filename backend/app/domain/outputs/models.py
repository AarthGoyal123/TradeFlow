"""Output artifact domain models."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class OutputType(StrEnum):
    """Supported output workbook types."""

    CLEAN_DATA = "clean_data"
    REMOVED_ROWS = "removed_rows"
    NEEDS_REVIEW = "needs_review"
    PROCESSING_REPORT = "processing_report"


@dataclass(frozen=True, slots=True)
class OutputArtifact:
    """Generated output workbook metadata."""

    output_type: OutputType
    filename: str
    path: Path


@dataclass(frozen=True, slots=True)
class ProcessingSummary:
    """Processing summary persisted and returned by report APIs."""

    job_id: str
    template_id: str
    total_rows: int
    clean_rows: int
    removed_rows: int
    needs_review_rows: int
    rule_matches: int
    validation_findings: int
    outputs: tuple[OutputArtifact, ...]

