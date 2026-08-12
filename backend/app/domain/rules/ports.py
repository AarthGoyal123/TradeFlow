"""Ports for rule pack access."""

from typing import Protocol

from app.domain.rules.models import RulePackDefinition


class RulePackRepository(Protocol):
    """Load rule packs for templates."""

    def list_rule_packs(self, template_id: str) -> tuple[RulePackDefinition, ...]:
        """Return all rule packs available for a template."""
        ...
