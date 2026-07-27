"""Pipeline stage registry."""

from collections.abc import Callable

from app.core.errors import TemplateValidationError
from app.domain.templates.models import TemplateDefinition
from app.engine.stages import PipelineStage

StageFactory = Callable[[str], PipelineStage]


class PipelineRegistry:
    """Register and resolve pipeline stages by configured name."""

    def __init__(self) -> None:
        self._factories: dict[str, StageFactory] = {}

    def register(self, stage_name: str, factory: StageFactory) -> None:
        """Register a pipeline stage factory."""
        if stage_name in self._factories:
            raise TemplateValidationError(
                f"Pipeline stage is already registered: {stage_name}",
                details={"stage": stage_name},
            )
        self._factories[stage_name] = factory

    def resolve(self, stage_name: str) -> PipelineStage:
        """Create a stage instance for a configured stage name."""
        try:
            factory = self._factories[stage_name]
        except KeyError as exc:
            raise TemplateValidationError(
                f"Unknown pipeline stage: {stage_name}",
                details={"stage": stage_name},
            ) from exc
        return factory(stage_name)

    def available_stages(self) -> set[str]:
        """Return all registered stage names."""
        return set(self._factories)

    def validate_template(self, template: TemplateDefinition) -> None:
        """Ensure every configured template stage is registered."""
        unknown_stages = [
            stage_name
            for stage_name in template.pipeline.steps
            if stage_name not in self._factories
        ]
        if unknown_stages:
            raise TemplateValidationError(
                "Template references unregistered pipeline stages",
                details={"template_id": template.id, "stages": unknown_stages},
            )
