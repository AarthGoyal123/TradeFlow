import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the test database schema before running any tests."""
    os.environ["TRADEFLOW_DATABASE_URL"] = "sqlite:///./tradeflow.sqlite"
    
    from app.infrastructure.database.base import Base
    from app.infrastructure.database.session import get_engine
    
    engine = get_engine()
    # Drop all and recreate to ensure clean state
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
