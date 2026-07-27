"""FastAPI dependency providers."""

from app.application.templates.service import TemplateService
from app.core.settings import get_settings
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository


def get_template_service() -> TemplateService:
    """Build the template application service."""
    settings = get_settings()
    repository = FileSystemTemplateRepository(settings.resolved_template_root)
    return TemplateService(repository)
