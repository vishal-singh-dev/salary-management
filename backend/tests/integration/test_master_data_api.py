from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.main import create_app
from app.seed.master_data import seed_fixed_master_data

pytestmark = pytest.mark.integration


@pytest.fixture()
def client(database_session: Session) -> Generator[TestClient, None, None]:
    # Intent: master-data API tests verify dropdown values are read from PostgreSQL.
    app = create_app()

    def override_session() -> Generator[Session, None, None]:
        yield database_session

    app.dependency_overrides[get_session] = override_session
    seed_fixed_master_data(database_session)
    database_session.commit()

    yield TestClient(app)
    app.dependency_overrides.clear()


def test_master_data_lists_all_categories(client: TestClient) -> None:
    # Intent: frontend can retrieve all active dropdown values in one call.
    response = client.get("/api/v1/master-data")

    assert response.status_code == 200
    body = response.json()
    assert {"Country", "Department", "JobTitle", "Currency"} <= {
        record["category_name"] for record in body
    }
    assert "id" not in body[0]


def test_master_data_filters_department_by_country(client: TestClient) -> None:
    # Intent: department dropdown values can be filtered by selected country.
    response = client.get(
        "/api/v1/master-data",
        params={"category": "Department", "parent_code": "IN"},
    )

    assert response.status_code == 200
    body = response.json()
    assert {record["code"] for record in body} == {"HR", "FIN"}
    assert all(record["parent_code"] == "IN" for record in body)


def test_master_data_filters_job_title_by_department(client: TestClient) -> None:
    # Intent: job title dropdown values can be filtered by selected department.
    response = client.get(
        "/api/v1/master-data",
        params={"category": "JobTitle", "parent_code": "HR"},
    )

    assert response.status_code == 200
    body = response.json()
    assert {record["code"] for record in body} == {"HRF", "HRO"}
    assert all(record["parent_category_name"] == "Department" for record in body)


def test_master_data_currency_is_independent(client: TestClient) -> None:
    # Intent: currency choices are available without parent filters.
    response = client.get("/api/v1/master-data", params={"category": "Currency"})

    assert response.status_code == 200
    body = response.json()
    assert {"INR", "CNY", "AUD", "USD"} <= {record["code"] for record in body}
    assert all(record["parent_code"] is None for record in body)
