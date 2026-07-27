"""Template API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_template_service
from app.api.schemas.templates import (
    TemplateColumnResponse,
    TemplateDetailsResponse,
    TemplateOutputResponse,
    TemplateSummaryResponse,
)
from app.application.templates.service import TemplateService
from app.domain.templates.models import TemplateDefinition

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateSummaryResponse])
def list_templates(
    template_service: Annotated[TemplateService, Depends(get_template_service)],
) -> list[TemplateSummaryResponse]:
    """Return all available processing templates."""
    templates = template_service.list_templates()
    return [
        TemplateSummaryResponse(
            id=template.id,
            name=template.name,
            version=template.config.version,
            description=template.config.description,
        )
        for template in templates
    ]


@router.get("/{template_id}", response_model=TemplateDetailsResponse)
def get_template(
    template_id: str,
    template_service: Annotated[TemplateService, Depends(get_template_service)],
) -> TemplateDetailsResponse:
    """Return detailed processing template metadata."""
    return _to_template_details_response(template_service.get_template(template_id))


def _to_template_details_response(template: TemplateDefinition) -> TemplateDetailsResponse:
    columns = [
        *[
            TemplateColumnResponse(field=column.field, aliases=column.aliases, required=True)
            for column in template.columns.required_fields
        ],
        *[
            TemplateColumnResponse(field=column.field, aliases=column.aliases, required=False)
            for column in template.columns.optional_fields
        ],
    ]
    outputs = [
        TemplateOutputResponse(type=output_type, filename=filename)
        for output_type, filename in template.output.files.model_dump().items()
    ]
    return TemplateDetailsResponse(
        id=template.id,
        name=template.name,
        version=template.config.version,
        description=template.config.description,
        columns=columns,
        pipeline=template.pipeline.steps,
        outputs=outputs,
    )

