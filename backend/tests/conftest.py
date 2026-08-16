import os

import pytest

# Set default DB URL to SQLite if not provided by environment (e.g. CI)
os.environ.setdefault("TRADEFLOW_DATABASE_URL", "sqlite:///./tradeflow.sqlite")


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the test database schema before running any tests."""
    from app.infrastructure.database.base import Base
    from app.infrastructure.database.session import get_engine

    engine = get_engine()
    # Drop all and recreate to ensure clean state
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
