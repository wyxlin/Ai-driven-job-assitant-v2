import os

# Must be set before any project import so config.py loads .env.test
os.environ["ENV_FILE"] = ".env.test"

import pytest
from sqlalchemy import create_engine

from core.models import Base, init_db


@pytest.fixture(scope="session", autouse=True)
def db_engine():
    """Single in-memory SQLite DB for the entire test session."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    init_db(engine)
    yield engine


@pytest.fixture(autouse=True)
def reset_db(db_engine):
    """Truncate all tables after each test to ensure isolation."""
    yield
    with db_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
