"""TradeFlow error hierarchy."""

from collections.abc import Mapping
from typing import Any


class TradeFlowError(Exception):
    """Base class for expected TradeFlow application errors."""

    code = "tradeflow_error"

    def __init__(self, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = dict(details or {})


class TemplateNotFoundError(TradeFlowError):
    """Raised when a requested template does not exist."""

    code = "template_not_found"


class JobNotFoundError(TradeFlowError):
    """Raised when a requested job does not exist."""

    code = "job_not_found"


class TemplateValidationError(TradeFlowError):
    """Raised when template files fail structural validation."""

    code = "template_validation_error"


class WorkbookValidationError(TradeFlowError):
    """Raised when an uploaded workbook fails validation."""

    code = "workbook_validation_error"


class ProcessingError(TradeFlowError):
    """Raised when pipeline execution fails."""

    code = "processing_error"


class OutputGenerationError(TradeFlowError):
    """Raised when output workbook generation fails."""

    code = "output_generation_error"


class StorageError(TradeFlowError):
    """Raised when filesystem or persistence operations fail."""

    code = "storage_error"


class UploadValidationError(TradeFlowError):
    """Raised when an uploaded file is rejected before processing."""

    code = "upload_validation_error"
