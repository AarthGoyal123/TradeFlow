"""SQLAlchemy session management."""

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings


def get_engine(*args: Any, **kwargs: Any) -> Any:
    """Create the SQLAlchemy engine from settings."""
    settings = get_settings()

    # Enable SQLite foreign keys by default for testing/local
    connect_args = {}
    url = settings.database_url

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return create_engine(
        url,
        connect_args=connect_args,
        echo=False,  # Set to True for debugging queries
    )


def get_session_factory(engine: Any = None) -> Any:
    """Create a thread-safe session factory."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
