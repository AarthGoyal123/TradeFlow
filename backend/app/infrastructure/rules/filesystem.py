"""Filesystem JSON rule pack repository."""

import json
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.core.errors import RulePackValidationError
from app.domain.rules.models import (
    RuleCondition,
    RuleDefinition,
    RuleOperatorName,
    RulePackDefinition,
    RuleSeverity,
    RuleType,
)
from app.domain.rules.ports import RulePackRepository
from app.domain.templates.models import TemplateDefinition
from app.domain.templates.ports import TemplateRepository
from app.domain.workbooks.models import CellValue


class FileSystemRulePackRepository(RulePackRepository):
    """Load typed rule packs from template-local JSON files."""

    def __init__(self, *, template_root: Path, template_repository: TemplateRepository) -> None:
        self._template_root = template_root
        self._template_repository = template_repository

    def list_rule_packs(self, template_id: str) -> tuple[RulePackDefinition, ...]:
        """Return all enabled and disabled rule packs available for a template."""
        template = self._template_repository.get_template(template_id)
        rules_dir = self._template_root / template_id / "rules"
        if not rules_dir.exists():
            return ()
        return tuple(
            self._load_rule_pack(path=path, template=template)
            for path in sorted(rules_dir.glob("*.json"))
        )

    def _load_rule_pack(self, *, path: Path, template: TemplateDefinition) -> RulePackDefinition:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            schema = _RulePackSchema.model_validate(payload)
            rule_pack = schema.to_domain(default_pack_id=path.stem)
            self._validate_rule_pack(rule_pack=rule_pack, template=template, path=path)
            return rule_pack
        except json.JSONDecodeError as exc:
            raise RulePackValidationError(
                "Rule pack JSON is malformed",
                details={"path": str(path), "error": str(exc)},
            ) from exc
        except ValidationError as exc:
            raise RulePackValidationError(
                "Rule pack schema is invalid",
                details={"path": str(path), "errors": exc.errors()},
            ) from exc

    def _validate_rule_pack(
        self,
        *,
        rule_pack: RulePackDefinition,
        template: TemplateDefinition,
        path: Path,
    ) -> None:
        seen_rule_ids: set[str] = set()
        valid_fields = {
            column.field
            for column in [*template.columns.required_fields, *template.columns.optional_fields]
        }
        for rule in rule_pack.rules:
            if rule.rule_id in seen_rule_ids:
                raise RulePackValidationError(
                    "Rule pack contains duplicate rule id",
                    details={"path": str(path), "rule_id": rule.rule_id},
                )
            seen_rule_ids.add(rule.rule_id)
            if rule.condition.field not in valid_fields:
                raise RulePackValidationError(
                    "Rule references an unknown template field",
                    details={
                        "path": str(path),
                        "rule_id": rule.rule_id,
                        "field": rule.condition.field,
                    },
                )
            if rule.condition.operator == RuleOperatorName.REGEX:
                self._validate_regex(rule=rule, path=path)

    @staticmethod
    def _validate_regex(*, rule: RuleDefinition, path: Path) -> None:
        try:
            re.compile(str(rule.condition.expected_value))
        except re.error as exc:
            raise RulePackValidationError(
                "Rule contains an invalid regex pattern",
                details={"path": str(path), "rule_id": rule.rule_id, "error": str(exc)},
            ) from exc


class _RulePackSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pack_id: str | None = None
    name: str | None = None
    version: str = Field(min_length=1, default="0.1.0")
    enabled: bool = True
    rules: list["_RuleSchema"] = Field(default_factory=list)

    def to_domain(self, *, default_pack_id: str) -> RulePackDefinition:
        pack_id = self.pack_id or default_pack_id
        return RulePackDefinition(
            pack_id=pack_id,
            name=self.name or pack_id,
            version=self.version,
            enabled=self.enabled,
            rules=tuple(rule.to_domain() for rule in self.rules),
        )


class _ConditionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1)
    operator: RuleOperatorName
    expected_value: CellValue = None
    expected_values: list[CellValue] = Field(default_factory=list)
    case_sensitive: bool = False
    threshold: float | None = Field(default=None, ge=0.0, le=100.0)

    def to_domain(self) -> RuleCondition:
        return RuleCondition(
            field=self.field,
            operator=self.operator,
            expected_value=self.expected_value,
            expected_values=tuple(self.expected_values),
            case_sensitive=self.case_sensitive,
            threshold=self.threshold,
        )


class _RuleSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    rule_type: RuleType
    condition: _ConditionSchema
    enabled: bool = True
    priority: int = 100
    classification: str | None = None
    transform_to: CellValue = None
    severity: RuleSeverity = RuleSeverity.INFO
    message: str = ""
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("classification must not be blank")
        return value

    def to_domain(self) -> RuleDefinition:
        return RuleDefinition(
            rule_id=self.rule_id,
            name=self.name,
            rule_type=self.rule_type,
            condition=self.condition.to_domain(),
            enabled=self.enabled,
            priority=self.priority,
            classification=self.classification,
            transform_to=self.transform_to,
            severity=self.severity,
            message=self.message,
            metadata=self.metadata,
        )
