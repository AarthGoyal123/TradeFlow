from pathlib import Path

from app.application.templates.service import TemplateService
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository


def test_template_service_lists_available_templates() -> None:
    repository = FileSystemTemplateRepository(Path("../templates"))
    service = TemplateService(repository)

    templates = service.list_templates()

    assert [template.id for template in templates] == ["indian_rice_exports"]
