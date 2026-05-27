from collections.abc import Generator
from os import environ

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base


@pytest.fixture()
def database_session() -> Generator[Session, None, None]:
    database_url = environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests.")
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            yield session
            session.rollback()
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()

