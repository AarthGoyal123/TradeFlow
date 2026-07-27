"""Template API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_template_service
from app.api.schemas.templates import TemplateSummaryResponse
from app.application.templates.service import TemplateService

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

