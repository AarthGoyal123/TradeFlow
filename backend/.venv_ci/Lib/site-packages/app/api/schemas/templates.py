"""Template API schemas."""

from pydantic import BaseModel, ConfigDict


class TemplateSummaryResponse(BaseModel):
    """Public template summary returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    version: str
    description: str


class TemplateColumnResponse(BaseModel):
    """Column mapping returned by the template details API."""

    field: str
    aliases: list[str]
    required: bool


class TemplateOutputResponse(BaseModel):
    """Output workbook returned by the template details API."""

    type: str
    filename: str


class TemplateDetailsResponse(TemplateSummaryResponse):
    """Detailed template response returned by the API."""

    columns: list[TemplateColumnResponse]
    pipeline: list[str]
    outputs: list[TemplateOutputResponse]
