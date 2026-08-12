"""Job API schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.domain.jobs.models import JobStatus


class JobUploadResponse(BaseModel):
    """Response returned when a file upload is accepted."""

    job_id: str
    status: JobStatus
    template_id: str
    filename: str


class JobDetailsResponse(BaseModel):
    """Persisted job metadata returned by the API."""

    job_id: str
    template_id: str
    original_filename: str
    stored_filename: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime


class ProcessingProgressResponse(BaseModel):
    """Progress entry for a processing stage."""

    stage: str
    status: str
    message: str


class ProcessingIssueResponse(BaseModel):
    """Structured processing issue."""

    code: str
    message: str
    details: dict[str, object]


class ProcessingResponse(BaseModel):
    """Response returned when processing is triggered."""

    job_id: str
    template_id: str
    status: JobStatus
    progress: list[ProcessingProgressResponse]
    errors: list[ProcessingIssueResponse] = []


class OutputArtifactResponse(BaseModel):
    """Generated output workbook metadata."""

    output_type: str
    filename: str
    path: str


class JobReportResponse(BaseModel):
    """Processing summary with output metadata and statistics."""

    job_id: str
    template_id: str
    status: str
    total_rows: int
    clean_rows: int
    removed_rows: int
    needs_review_rows: int
    rule_matches: int
    validation_findings: int
    outputs: list[OutputArtifactResponse]
    created_at: str | None = None


class ColumnMappingExplanationResponse(BaseModel):
    """How a single column was mapped (or why it failed)."""

    field: str
    required: bool
    matched: bool
    source_header: str | None = None
    column_number: int | None = None
    confidence: float = 0.0
    detection_method: str = "none"
    searched_aliases: list[str] = []
    closest_matches: list[dict[str, object]] = []
    suggested_fix: str | None = None


class StructureAnalysisResponse(BaseModel):
    """Workbook structure analysis summary."""

    detected_header_row: int | None = None
    header_confidence: float = 0.0
    total_sheets: int = 0
    total_columns: int = 0
    total_data_rows: int = 0
    structure_confidence: float = 0.0
    anomalies: list[str] = []


class DetectedFieldResponse(BaseModel):
    """Field detected by semantic analysis."""

    label: str
    column: int
    sample: str
    confidence: float
    reason: str


class SemanticAnalysisResponse(BaseModel):
    """Semantic value analysis summary."""

    total_fields_detected: int = 0
    fields: list[DetectedFieldResponse] = []


class DataQualityResponse(BaseModel):
    """Data quality indicators."""

    missing_cells: int = 0
    empty_rows: int = 0
    blank_columns: list[str] = []


class IntelligenceReportResponse(BaseModel):
    """Full workbook intelligence report."""

    structure: StructureAnalysisResponse
    semantic: SemanticAnalysisResponse
    data_quality: DataQualityResponse
    column_mappings: list[ColumnMappingExplanationResponse]
    overall_confidence: float = 0.0

