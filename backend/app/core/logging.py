"""Structured logging configuration."""

import logging
import sys
from pathlib import Path


def configure_logging(log_level: str) -> None:
    """Configure process-wide structured logging."""
    from logging.handlers import RotatingFileHandler

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_dir / "tradeflow.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    
    stream_handler = logging.StreamHandler(sys.stdout)
    
    logging.basicConfig(
        level=log_level.upper(),
        format=(
            "%(asctime)s %(levelname)s %(name)s "
            "event=%(message)s job_id=%(job_id)s template_id=%(template_id)s "
            "stage=%(stage)s duration_ms=%(duration_ms)s"
        ),
        handlers=[stream_handler, file_handler],
        force=True,
    )
    for handler in logging.getLogger().handlers:
        handler.addFilter(_DefaultContextFilter())


def log_extra(
    *,
    job_id: str | None = None,
    template_id: str | None = None,
    stage: str | None = None,
    duration_ms: float | None = None,
    tenant_id: str | None = None,
) -> dict[str, str | float]:
    """Return common logging fields with stable defaults."""
    return {
        "job_id": job_id or "-",
        "template_id": template_id or "-",
        "stage": stage or "-",
        "duration_ms": duration_ms if duration_ms is not None else -1.0,
        "tenant_id": tenant_id or "-",
    }


class _DefaultContextFilter(logging.Filter):
    """Ensure structured log fields exist for all records."""

    def filter(self, record: logging.LogRecord) -> bool:
        for field, default in {
            "job_id": "-",
            "template_id": "-",
            "stage": "-",
            "duration_ms": -1.0,
        }.items():
            if not hasattr(record, field):
                setattr(record, field, default)
        return True
