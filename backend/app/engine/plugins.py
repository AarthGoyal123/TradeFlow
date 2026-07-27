"""Plugin contracts for pipeline stage registration."""

from typing import Protocol

from app.engine.registry import PipelineRegistry
from app.engine.stages import default_stage_factories


class PipelinePlugin(Protocol):
    """A plugin that contributes one or more pipeline stages."""

    name: str

    def register(self, registry: PipelineRegistry) -> None:
        """Register plugin-provided stages with the pipeline registry."""
        ...


class BuiltInPipelinePlugin:
    """Register built-in foundation stages."""

    name = "built_in_pipeline"

    def register(self, registry: PipelineRegistry) -> None:
        """Register built-in no-op stage placeholders."""
        for stage_name, factory in default_stage_factories().items():
            registry.register(stage_name, factory)
