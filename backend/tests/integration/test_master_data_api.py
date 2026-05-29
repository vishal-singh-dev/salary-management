import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.main import create_app
from app.models import MasterData

pytestmark = pytest.mark.integration


@pytest.fixture()
def client(database_session: Session) -> Generator[TestClient, None, None]:
    # Intent: master-data API tests verify dropdown values are read from PostgreSQL.
    app = create_app()

    def override_session() -> Generator[Session, None, None]:
        yield database_session

    app.dependency_overrides[get_session] = override_session
    _add_master_data_fixture(database_session)

    yield TestClient(app)
    app.dependency_overrides.clear()


def test_master_data_lists_all_categories(client: TestClient) -> None:
    # Intent: frontend can retrieve all dropdown values in a single call.
    response = client.get("/api/v1/master-data")

    assert response.status_code == 200
    body = response.json()
    assert [record["category"] for record in body] == ["country", "department", "job_title"]
    assert body[0]["description"] == "INDIA"
    assert body[0]["value"] == "IN"
    assert "id" not in body[0]


def test_master_data_filters_by_category(client: TestClient) -> None:
    # Intent: dashboard can request only one filter category when needed.
    response = client.get("/api/v1/master-data", params={"category": "department"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "department"
    assert body[0]["description"] == "Engineering"
    assert body[0]["value"] == "ENG"


def _add_master_data_fixture(session: Session) -> None:
    session.add_all(
        [
            MasterData(
                id=uuid.uuid4(),
                category="country",
                description="INDIA",
                value="IN",
            ),
            MasterData(
                id=uuid.uuid4(),
                category="department",
                description="Engineering",
                value="ENG",
            ),
            MasterData(
                id=uuid.uuid4(),
                category="job_title",
                description="Senior Software Engineer",
                value="SR_SWE",
            ),
        ]
    )
    session.commit()
