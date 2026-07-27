"""Application service for processing templates."""

from app.domain.templates.models import TemplateDefinition
from app.domain.templates.ports import TemplateRepository


class TemplateService:
    """Coordinate template-related application use cases."""

    def __init__(self, template_repository: TemplateRepository) -> None:
        self._template_repository = template_repository

    def list_templates(self) -> list[TemplateDefinition]:
        """Return all available processing templates."""
        return self._template_repository.list_templates()

    def get_template(self, template_id: str) -> TemplateDefinition:
        """Return one processing template by identifier."""
        return self._template_repository.get_template(template_id)

