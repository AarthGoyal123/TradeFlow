from pathlib import Path

import pytest

from app.core.errors import TemplateValidationError
from app.engine.bootstrap import build_default_pipeline_registry
from app.engine.context import ProcessingContext
from app.engine.pipeline import PipelineExecutor
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository


def test_pipeline_records_metrics_for_each_configured_stage() -> None:
    repository = FileSystemTemplateRepository(Path("../templates"))
    template = repository.get_template("indian_rice_exports")
    registry = build_default_pipeline_registry()
    registry.validate_template(template)
    context = ProcessingContext(template=template, job_id="test-job")

    result = PipelineExecutor(registry).execute(context)

    assert [metric.stage for metric in result.metrics] == template.pipeline.steps
    assert all(metric.status == "succeeded" for metric in result.metrics)
    assert all(metric.duration_ms >= 0 for metric in result.metrics)


def test_registry_rejects_unknown_stage() -> None:
    registry = build_default_pipeline_registry()

    with pytest.raises(TemplateValidationError):
        registry.resolve("unknown_stage")
