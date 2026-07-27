"""Filesystem template repository implementation."""

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.core.errors import TemplateNotFoundError, TemplateValidationError
from app.domain.templates.models import (
    ColumnsConfig,
    OutputConfig,
    PipelineConfig,
    RulePack,
    TemplateConfig,
    TemplateDefinition,
)


class FileSystemTemplateRepository:
    """Load processing templates from a directory tree."""

    def __init__(self, template_root: Path) -> None:
        self._template_root = template_root

    def list_templates(self) -> list[TemplateDefinition]:
        """Return all valid templates under the template root."""
        if not self._template_root.exists():
            return []
        templates = [
            self._load_template_from_dir(path)
            for path in sorted(self._template_root.iterdir())
            if path.is_dir()
        ]
        return templates

    def get_template(self, template_id: str) -> TemplateDefinition:
        """Return one template by identifier."""
        template_path = self._template_root / template_id
        if not template_path.exists() or not template_path.is_dir():
            raise TemplateNotFoundError(
                f"Template not found: {template_id}",
                details={"template_id": template_id},
            )
        template = self._load_template_from_dir(template_path)
        if template.id != template_id:
            raise TemplateValidationError(
                "Template directory name must match template id",
                details={"template_id": template.id, "directory": template_id},
            )
        return template

    def _load_template_from_dir(self, template_path: Path) -> TemplateDefinition:
        try:
            return TemplateDefinition(
                config=TemplateConfig.model_validate_json(
                    self._read_required_file(template_path / "config.json")
                ),
                columns=ColumnsConfig.model_validate_json(
                    self._read_required_file(template_path / "columns.json")
                ),
                pipeline=PipelineConfig.model_validate_json(
                    self._read_required_file(template_path / "pipeline.json")
                ),
                output=OutputConfig.model_validate_json(
                    self._read_required_file(template_path / "output.json")
                ),
                keyword_rules=RulePack.model_validate(
                    self._read_optional_json(template_path / "rules" / "keywords.json")
                ),
                regex_rules=RulePack.model_validate(
                    self._read_optional_json(template_path / "rules" / "regex.json")
                ),
                fuzzy_matches=RulePack.model_validate(
                    self._read_optional_json(template_path / "rules" / "fuzzy_matches.json")
                ),
            )
        except ValidationError as exc:
            raise TemplateValidationError(
                f"Invalid template: {template_path.name}",
                details={"template": template_path.name, "errors": exc.errors()},
            ) from exc
        except json.JSONDecodeError as exc:
            raise TemplateValidationError(
                f"Invalid template JSON: {template_path.name}",
                details={"template": template_path.name, "error": str(exc)},
            ) from exc

    @staticmethod
    def _read_required_file(path: Path) -> str:
        if not path.exists():
            raise TemplateValidationError(
                f"Required template file is missing: {path.name}",
                details={"path": str(path)},
            )
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _read_optional_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            content = json.load(file)
        if not isinstance(content, dict):
            raise TemplateValidationError(
                f"Template rule file must contain a JSON object: {path.name}",
                details={"path": str(path)},
            )
        return content

