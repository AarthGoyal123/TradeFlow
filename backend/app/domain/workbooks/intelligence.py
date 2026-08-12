"""Domain models for the Workbook Intelligence Engine."""

from dataclasses import dataclass, field
from pathlib import Path

# ── Analysis Models ──────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class FileMetadata:
    size_bytes: int
    filename: str
    extension: str
    sheet_count: int


@dataclass(frozen=True, slots=True)
class SheetInfo:
    name: str
    row_count: int
    column_count: int
    is_hidden: bool = False
    is_likely_data_sheet: bool = False
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class HeaderAnalysis:
    detected_row: int
    confidence: float
    cells: tuple[str, ...]
    detection_method: str  # "row_1", "heuristic", "content_based"


@dataclass(frozen=True, slots=True)
class DataSampleAnalysis:
    column_count: int
    estimated_data_rows: int
    estimated_empty_rows: int
    has_title_rows: bool
    title_row_count: int
    column_types: dict[str, str]  # column_name -> inferred type


@dataclass(frozen=True, slots=True)
class StructureAnalysis:
    file_metadata: FileMetadata
    sheets: tuple[SheetInfo, ...]
    likely_data_sheet: SheetInfo | None
    header: HeaderAnalysis
    data_sample: DataSampleAnalysis
    has_merged_cells: bool = False
    has_hidden_sheets: bool = False
    structure_confidence: float = 0.0


# ── Column Mapping Explanation ────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ColumnMappingExplanation:
    """Explain how a single business field was resolved (or why it wasn't)."""

    field: str
    required: bool
    matched: bool
    source_header: str | None = None
    column_number: int | None = None
    method: str = "none"
    confidence: float = 0.0
    searched_aliases: tuple[str, ...] = ()
    closest_matches: tuple[dict[str, object], ...] = ()


@dataclass(frozen=True, slots=True)
class DetectedFieldInfo:
    """A field detected by semantic analysis of cell values."""

    label: str
    column: int
    sample: str
    confidence: float
    reason: str


# ── Semantic Detection ────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class DetectedPattern:
    pattern_type: str  # "country", "hs_code", "port", "currency", "date", "numeric"
    column_name: str
    sample_values: tuple[str, ...]
    confidence: float


@dataclass(frozen=True, slots=True)
class BusinessEntity:
    business_concept: str          # "consignee", "port", "country", "hs_code"
    workbook_header: str | None    # actual header found
    detection_method: str          # "exact", "synonym", "fuzzy", "semantic", "missing"
    confidence: float
    sample_values: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SemanticAnalysis:
    detected_entities: tuple[BusinessEntity, ...] = ()
    detected_patterns: tuple[DetectedPattern, ...] = ()
    has_country_data: bool = False
    has_hs_code_data: bool = False
    has_port_data: bool = False
    has_currency_data: bool = False
    total_fields_detected: int = 0
    fields: tuple[DetectedFieldInfo, ...] = ()


# ── Data Quality ──────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ColumnQuality:
    column_name: str
    completeness_pct: float
    null_count: int
    total_count: int
    has_duplicates: bool = False
    duplicate_count: int = 0
    has_invalid_values: bool = False
    invalid_value_count: int = 0
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DataQualityAnalysis:
    columns: tuple[ColumnQuality, ...]
    overall_quality_pct: float
    warning_count: int
    critical_count: int


# ── Workbook Classification ────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class WorkbookClassification:
    workbook_type: str | None  # "Rice Export Register", "General Trade", etc.
    confidence: float
    reason: str
    detected_features: tuple[str, ...]  # features that drove classification
    recommended_template_id: str | None = None


# ── Template Match ─────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class MappingExplanation:
    business_field: str
    workbook_header: str | None
    status: str  # "matched", "suggested", "missing"
    detection_method: str  # "exact", "case_insensitive", "normalized", "synonym", "fuzzy", "semantic", "none"
    confidence: float
    searched_aliases: tuple[str, ...] = ()
    closest_matches: tuple[tuple[str, float], ...] = ()
    suggested_fix: str = ""


@dataclass(frozen=True, slots=True)
class TemplateMatchResult:
    template_id: str
    template_name: str
    mappings: tuple[MappingExplanation, ...]
    match_confidence: float
    missing_required: tuple[str, ...] = ()
    missing_optional: tuple[str, ...] = ()
    suggested_mappings: tuple[MappingExplanation, ...] = ()
    warnings: tuple[str, ...] = ()


# ── Confidence Engine ──────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ConfidenceReport:
    overall: float = 0.0
    structure_confidence: float = 0.0
    header_confidence: float = 0.0
    mapping_confidence: float = 0.0
    mapping_coverage: float = 0.0
    template_match_confidence: float = 0.0
    header_detection_confidence: float = 0.0
    data_quality_confidence: float = 0.0
    overall_workbook_health: float = 0.0
    warning_count: int = 0
    critical_error_count: int = 0


# ── Learning Alias Store ──────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class LearnedAlias:
    workbook_header: str
    business_field: str
    count: int  # number of times this mapping was confirmed
    last_confirmed: str | None = None  # ISO date


# ── Complete Intelligence Report ───────────────────────────────────


@dataclass(frozen=True, slots=True)
class WorkbookIntelligenceReport:
    structure: StructureAnalysis
    semantic: SemanticAnalysis = field(default_factory=SemanticAnalysis)
    mapping_explanations: tuple[ColumnMappingExplanation, ...] = ()
    confidence: ConfidenceReport = field(default_factory=ConfidenceReport)
    sheets: tuple[str, ...] = ()
    template_id: str = ""
    workbook_path: Path | None = None
    classification: WorkbookClassification | None = None
    template_match: TemplateMatchResult | None = None
    data_quality: DataQualityAnalysis | None = None
    raw_header: tuple[str, ...] = ()
    detected_columns: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()