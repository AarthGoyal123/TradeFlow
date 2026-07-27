"""Pipeline stage contracts and foundational no-op stages."""

from typing import Protocol

from app.engine.context import ProcessingContext


class PipelineStage(Protocol):
    """Executable processing stage."""

    name: str

    def run(self, context: ProcessingContext) -> ProcessingContext:
        """Run the stage against a processing context."""
        ...


class NoOpStage:
    """Placeholder stage that establishes pipeline wiring without business logic."""

    def __init__(self, name: str) -> None:
        self.name = name

    def run(self, context: ProcessingContext) -> ProcessingContext:
        """Return context unchanged."""
        return context


def default_stage_factories() -> dict[str, type[NoOpStage]]:
    """Return built-in stage factories for foundation-only execution."""
    return {
        "validation": NoOpStage,
        "column_removal": NoOpStage,
        "normalization": NoOpStage,
        "keyword_rules": NoOpStage,
        "regex_rules": NoOpStage,
        "fuzzy_matching": NoOpStage,
        "confidence_scoring": NoOpStage,
        "output_generation": NoOpStage,
    }

