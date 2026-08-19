import pytest
from app.api.dependencies import get_db_session


def test_sequential_sessions_use_null_pool():
    # If NullPool is active, each session opens and closes a new connection,
    # rather than keeping it open in a QueuePool.
    # We will just verify that we can create sequential sessions without hanging,
    # and verify that the underlying engine uses NullPool.
    # Open 20 sequential sessions
    for _ in range(20):
        generator = get_db_session()
        session = next(generator)
        # Execute a trivial query to ensure connection is opened
        from sqlalchemy import text
        session.execute(text("SELECT 1"))

        # Verify it uses NullPool
        from sqlalchemy.pool import NullPool

        assert isinstance(session.bind.pool, NullPool)

        # Close session
        try:
            next(generator)
        except StopIteration:
            pass

    assert True
