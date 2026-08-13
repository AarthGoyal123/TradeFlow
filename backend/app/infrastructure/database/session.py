"""SQLAlchemy session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings


def get_engine():
    """Create the SQLAlchemy engine from settings."""
    settings = get_settings()
    
    # Enable SQLite foreign keys by default for testing/local
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        
    return create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=False, # Set to True for debugging queries
    )


def get_session_factory(engine=None):
    """Create a thread-safe session factory."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
