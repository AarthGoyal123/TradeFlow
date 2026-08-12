"""Ports for output generation and persistence."""

from pathlib import Path
from typing import Protocol

from app.domain.datasets.models import IntermediateDataset
from app.domain.outputs.models import OutputArtifact, OutputType, ProcessingSummary
from app.domain.rules.models import RuleExecutionReport


class OutputStorage(Protocol):
    """Store generated output files."""

    def output_path(self, *, job_id: str, output_type: OutputType, filename: str) -> Path:
        """Return a safe output path for one job output."""
        ...

    def get_output(self, *, job_id: str, output_type: OutputType) -> OutputArtifact:
        """Return persisted output metadata."""
        ...


class OutputWorkbookBuilder(Protocol):
    """Build output workbooks from processed data."""

    def build(
        self,
        *,
        job_id: str,
        dataset: IntermediateDataset,
        rule_report: RuleExecutionReport,
        output_storage: OutputStorage,
    ) -> tuple[OutputArtifact, ...]:
        """Build all output workbooks and return generated artifacts."""
        ...


class ProcessingReportRepository(Protocol):
    """Persist and retrieve processing summaries."""

    def save_summary(self, summary: ProcessingSummary) -> ProcessingSummary:
        """Persist a processing summary."""
        ...

    def get_summary(self, job_id: str) -> ProcessingSummary:
        """Return a processing summary by job id."""
        ...
