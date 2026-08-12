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


# --- Base Categories ---

class ValidationError(TradeFlowError):
    """Base for all validation errors."""
    code = "validation_error"


class BusinessRuleError(TradeFlowError):
    """Base for business rule and state errors."""
    code = "business_rule_error"


class StorageError(TradeFlowError):
    """Base for storage and persistence errors."""
    code = "storage_error"


class SystemError(TradeFlowError):
    """Base for infrastructure and unexpected errors."""
    code = "system_error"


# --- Specific Errors ---

class InvalidStateTransitionError(BusinessRuleError):
    """Raised when attempting an invalid job state transition."""
    code = "invalid_state_transition"


class TemplateNotFoundError(ValidationError):
    """Raised when a requested template does not exist."""
    code = "template_not_found"


class JobNotFoundError(ValidationError):
    """Raised when a requested job does not exist."""
    code = "job_not_found"


class TemplateValidationError(ValidationError):
    """Raised when template files fail structural validation."""
    code = "template_validation_error"


class WorkbookValidationError(ValidationError):
    """Raised when an uploaded workbook fails validation."""
    code = "workbook_validation_error"


class ProcessingError(BusinessRuleError):
    """Raised when pipeline execution fails."""
    code = "processing_error"


class OutputGenerationError(SystemError):
    """Raised when output workbook generation fails."""
    code = "output_generation_error"


class UploadValidationError(ValidationError):
    """Raised when an uploaded file is rejected before processing."""
    code = "upload_validation_error"


class RulePackValidationError(ValidationError):
    """Raised when a rule pack cannot be loaded or validated."""
    code = "rule_pack_validation_error"
