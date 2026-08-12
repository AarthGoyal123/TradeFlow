"""Processing result and progress models."""

from dataclasses import dataclass

from app.domain.datasets.models import IntermediateDataset
from app.domain.outputs.models import ProcessingSummary
from app.domain.rules.models import RuleExecutionReport


@dataclass(frozen=True, slots=True)
class ProcessingProgress:
    """Progress entry for a processing stage."""

    stage: str
    status: str
    message: str


@dataclass(frozen=True, slots=True)
class ProcessingIssue:
    """Structured processing issue."""

    code: str
    message: str
    details: dict[str, object]


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    """Result of synchronous processing to the intermediate dataset."""

    job_id: str
    template_id: str
    dataset: IntermediateDataset | None
    progress: tuple[ProcessingProgress, ...]
    rule_report: RuleExecutionReport | None = None
    summary: ProcessingSummary | None = None
    errors: tuple[ProcessingIssue, ...] = ()
