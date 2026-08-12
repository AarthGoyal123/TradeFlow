"""Ports for template access."""

from typing import Protocol

from app.domain.templates.models import TemplateDefinition


class TemplateRepository(Protocol):
    """Read processing templates from a backing store."""

    def list_templates(self) -> list[TemplateDefinition]:
        """Return all templates available to the application."""
        ...

    def get_template(self, template_id: str) -> TemplateDefinition:
        """Return one template by identifier."""
        ...
