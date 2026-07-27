"""Typed template models for configurable processing."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


StageName = str


class WorkbookConfig(BaseModel):
    """Workbook selection behavior for a template."""

    model_config = ConfigDict(extra="forbid")

    sheet_strategy: Literal["first_sheet", "named_sheet"] = "first_sheet"
    sheet_name: str | None = None

    @model_validator(mode="after")
    def validate_sheet_name(self) -> "WorkbookConfig":
        """Require a sheet name when using named-sheet loading."""
        if self.sheet_strategy == "named_sheet" and not self.sheet_name:
            raise ValueError("sheet_name is required when sheet_strategy is named_sheet")
        return self


class TemplateConfig(BaseModel):
    """Top-level template metadata and enabled module configuration."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, pattern=r"^[a-z0-9_]+$")
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    description: str = ""
    workbook: WorkbookConfig
    enabled_modules: list[StageName] = Field(min_length=1)

    @field_validator("enabled_modules")
    @classmethod
    def validate_enabled_modules(cls, value: list[StageName]) -> list[StageName]:
        """Prevent duplicated or invalid enabled modules."""
        if len(value) != len(set(value)):
            raise ValueError("enabled_modules must not contain duplicates")
        if any(not _is_identifier(stage) for stage in value):
            raise ValueError("enabled_modules must contain lowercase stage identifiers")
        return value


class ColumnMapping(BaseModel):
    """Map one conceptual field to possible source headers."""

    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1, pattern=r"^[a-z0-9_]+$")
    aliases: list[str] = Field(min_length=1)

    @field_validator("aliases")
    @classmethod
    def validate_aliases(cls, value: list[str]) -> list[str]:
        """Require non-empty, unique aliases."""
        cleaned = [alias.strip() for alias in value]
        if any(not alias for alias in cleaned):
            raise ValueError("aliases must not contain blank values")
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("aliases must not contain duplicates")
        return cleaned


class ColumnsConfig(BaseModel):
    """Column mapping and removal configuration."""

    model_config = ConfigDict(extra="forbid")

    required_fields: list[ColumnMapping] = Field(min_length=1)
    optional_fields: list[ColumnMapping] = Field(default_factory=list)
    remove_columns: list[str] = Field(default_factory=list)


class PipelineConfig(BaseModel):
    """Ordered pipeline stage configuration."""

    model_config = ConfigDict(extra="forbid")

    steps: list[StageName] = Field(min_length=1)

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, value: list[StageName]) -> list[StageName]:
        """Prevent duplicated or invalid pipeline steps."""
        if len(value) != len(set(value)):
            raise ValueError("pipeline steps must not contain duplicates")
        if any(not _is_identifier(step) for step in value):
            raise ValueError("pipeline steps must contain lowercase stage identifiers")
        return value


class OutputFiles(BaseModel):
    """Names of generated output workbooks."""

    model_config = ConfigDict(extra="forbid")

    clean_data: str = "Clean_Data.xlsx"
    removed_rows: str = "Removed_Rows.xlsx"
    needs_review: str = "Needs_Review.xlsx"
    processing_report: str = "Processing_Report.xlsx"


class OutputConfig(BaseModel):
    """Output and review routing configuration."""

    model_config = ConfigDict(extra="forbid")

    files: OutputFiles
    review_threshold: float = Field(ge=0.0, le=1.0)


class RulePack(BaseModel):
    """Generic rule pack envelope.

    Rule item schemas will be tightened as each rule engine is implemented.
    """

    model_config = ConfigDict(extra="allow")

    rules: list[dict] = Field(default_factory=list)
    match_sets: list[dict] = Field(default_factory=list)


class TemplateDefinition(BaseModel):
    """Fully loaded and validated processing template."""

    model_config = ConfigDict(extra="forbid")

    config: TemplateConfig
    columns: ColumnsConfig
    pipeline: PipelineConfig
    output: OutputConfig
    keyword_rules: RulePack
    regex_rules: RulePack
    fuzzy_matches: RulePack

    @model_validator(mode="after")
    def validate_pipeline_modules(self) -> "TemplateDefinition":
        """Ensure configured pipeline stages are enabled by the template."""
        enabled = set(self.config.enabled_modules)
        missing = [step for step in self.pipeline.steps if step not in enabled]
        if missing:
            raise ValueError(f"pipeline steps are not enabled modules: {missing}")
        return self

    @property
    def id(self) -> str:
        """Return the stable template identifier."""
        return self.config.id

    @property
    def name(self) -> str:
        """Return the display name."""
        return self.config.name


def _is_identifier(value: str) -> bool:
    return bool(value) and value.replace("_", "").isalnum() and value == value.lower()
