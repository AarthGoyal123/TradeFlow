"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.routes.jobs import router as jobs_router
from app.api.routes.system import router as system_router
from app.api.routes.templates import router as templates_router
from app.core.logging import configure_logging
from app.core.settings import get_settings


def create_app() -> FastAPI:
    """Create and configure the TradeFlow API application."""
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="TradeFlow API",
        version="0.1.0",
        description="Template-driven Excel processing API for trade shipment data.",
    )

    register_exception_handlers(app)
    app.include_router(system_router)
    app.include_router(templates_router)
    app.include_router(jobs_router)

    return app


app = create_app()
