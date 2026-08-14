"""HTTP exception mapping for expected TradeFlow errors."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.errors import JobNotFoundError, TemplateNotFoundError, TradeFlowError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register API exception handlers."""

    @app.exception_handler(TradeFlowError)
    async def handle_tradeflow_error(_: Request, exc: TradeFlowError) -> JSONResponse:
        from app.core.errors import (
            BusinessRuleError,
            StorageError,
            SystemError,
            ValidationError,
        )

        # Base status mapping
        if isinstance(exc, TemplateNotFoundError | JobNotFoundError):
            status_code = 404
        elif isinstance(exc, ValidationError):
            status_code = 400
        elif isinstance(exc, BusinessRuleError):
            status_code = 422
        elif isinstance(exc, StorageError | SystemError):
            status_code = 500
        else:
            status_code = 400

        # Prevent data leakage for infrastructure errors
        if isinstance(exc, StorageError | SystemError):
            logger.error("System/Storage Error: %s %s", exc.message, exc.details)
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": exc.code,
                        "message": "An internal system error occurred.",
                        "details": {},
                    }
                },
            )

        # Safe business/validation errors
        # Sanitize known sensitive keys just in case
        safe_details = {
            k: v
            for k, v in exc.details.items()
            if "path" not in k.lower() and "file" not in k.lower()
        }

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": safe_details,
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            content = exc.detail
        else:
            content = {"detail": exc.detail}
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled API exception")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An internal error occurred",
                    "details": {},
                }
            },
        )
