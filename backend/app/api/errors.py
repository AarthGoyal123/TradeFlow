"""HTTP exception mapping for expected TradeFlow errors."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import JobNotFoundError, TemplateNotFoundError, TradeFlowError


def register_exception_handlers(app: FastAPI) -> None:
    """Register API exception handlers."""

    @app.exception_handler(TradeFlowError)
    async def handle_tradeflow_error(_: Request, exc: TradeFlowError) -> JSONResponse:
        status_code = 404 if isinstance(exc, TemplateNotFoundError | JobNotFoundError) else 400
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
