"""Pipeline executor."""

import logging
from time import perf_counter

from app.core.errors import ProcessingError, TradeFlowError
from app.core.logging import log_extra
from app.engine.context import ProcessingContext
from app.engine.metrics import StageMetric
from app.engine.registry import PipelineRegistry

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Execute configured pipeline stages with metrics and structured logs."""

    def __init__(self, registry: PipelineRegistry) -> None:
        self._registry = registry

    def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Run every configured stage in order."""
        for stage_name in context.template.pipeline.steps:
            stage = self._registry.resolve(stage_name)
            rows_in = self._row_count(context)
            started = perf_counter()
            logger.info(
                "pipeline_stage_started",
                extra=log_extra(
                    job_id=context.job_id,
                    template_id=context.template_id,
                    stage=stage_name,
                ),
            )
            try:
                context = stage.run(context)
            except TradeFlowError as exc:
                duration_ms = self._duration_ms(started)
                context.add_metric(
                    StageMetric(
                        stage=stage_name,
                        duration_ms=duration_ms,
                        status="failed",
                        rows_in=rows_in,
                        rows_out=self._row_count(context),
                        error_code=exc.code,
                    )
                )
                logger.exception(
                    "pipeline_stage_failed",
                    extra=log_extra(
                        job_id=context.job_id,
                        template_id=context.template_id,
                        stage=stage_name,
                        duration_ms=duration_ms,
                    ),
                )
                raise
            except Exception as exc:
                duration_ms = self._duration_ms(started)
                context.add_metric(
                    StageMetric(
                        stage=stage_name,
                        duration_ms=duration_ms,
                        status="failed",
                        rows_in=rows_in,
                        rows_out=self._row_count(context),
                        error_code=ProcessingError.code,
                    )
                )
                logger.exception(
                    "pipeline_stage_failed",
                    extra=log_extra(
                        job_id=context.job_id,
                        template_id=context.template_id,
                        stage=stage_name,
                        duration_ms=duration_ms,
                    ),
                )
                raise ProcessingError(
                    f"Pipeline stage failed: {stage_name}",
                    details={"stage": stage_name},
                ) from exc

            duration_ms = self._duration_ms(started)
            context.add_metric(
                StageMetric(
                    stage=stage_name,
                    duration_ms=duration_ms,
                    status="succeeded",
                    rows_in=rows_in,
                    rows_out=self._row_count(context),
                )
            )
            logger.info(
                "pipeline_stage_completed",
                extra=log_extra(
                    job_id=context.job_id,
                    template_id=context.template_id,
                    stage=stage_name,
                    duration_ms=duration_ms,
                ),
            )
        return context

    @staticmethod
    def _duration_ms(started: float) -> float:
        return round((perf_counter() - started) * 1000, 3)

    @staticmethod
    def _row_count(context: ProcessingContext) -> int | None:
        data = context.data
        if data is None:
            return None
        if hasattr(data, "__len__"):
            return len(data)
        return None

