"""Engine bootstrap helpers."""

from collections.abc import Iterable

from app.engine.plugins import BuiltInPipelinePlugin, PipelinePlugin
from app.engine.registry import PipelineRegistry


def build_default_pipeline_registry(
    plugins: Iterable[PipelinePlugin] | None = None,
) -> PipelineRegistry:
    """Build the built-in pipeline registry."""
    registry = PipelineRegistry()
    for plugin in [BuiltInPipelinePlugin(), *(plugins or [])]:
        plugin.register(registry)
    return registry
