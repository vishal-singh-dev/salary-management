import uuid
from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.main import create_app
from app.models import ExchangeRate

pytestmark = pytest.mark.integration


@pytest.fixture()
def client(database_session: Session) -> Generator[TestClient, None, None]:
    # Intent: employee API tests use the configured PostgreSQL test database.
    def override_session() -> Generator[Session, None, None]:
        yield database_session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    database_session.add(
        ExchangeRate(
            id=uuid.uuid4(),
            source_currency_code="USD",
            target_currency_code="USD",
            rate_to_usd=Decimal("1.00000000"),
            effective_from=date(2026, 1, 1),
            rate_source="TEST_FIXED_RATE",
        )
    )
    database_session.commit()

    yield TestClient(app)
    app.dependency_overrides.clear()


def employee_payload(employee_id: str = "EMP-000001") -> dict[str, object]:
    return {
        "employee_id": employee_id,
        "full_name": "Asha Patel",
        "title": "HR Manager",
        "department": "Human Resources",
        "country_code": "US",
        "from_date": "2026-01-01",
        "initial_salary": {
            "currency_code": "USD",
            "base_amount": "120000.00",
            "variable_amount": "10000.00",
            "hra_allowance_amount": "0.00",
            "pf_amount": "4800.00",
            "gratuity_amount": "0.00",
            "effective_from": "2026-01-01",
        },
    }


def test_employee_create_api(client: TestClient) -> None:
    # Intent: employee creation persists profile data with one current salary record.
    response = client.post("/api/v1/employees", json=employee_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["employee_id"] == "EMP-000001"
    assert body["current_salary"]["base_amount"] == "120000.00"


def test_employee_duplicate_api(client: TestClient) -> None:
    # Intent: duplicate HR-facing employee identifiers return a conflict.
    assert client.post("/api/v1/employees", json=employee_payload()).status_code == 201

    response = client.post("/api/v1/employees", json=employee_payload())

    assert response.status_code == 409


def test_employee_list_api(client: TestClient) -> None:
    # Intent: employee listing returns active employees with pagination metadata.
    client.post("/api/v1/employees", json=employee_payload())

    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["employee_id"] == "EMP-000001"


def test_employee_next_id_api(client: TestClient) -> None:
    # Intent: employee creation forms can request the next HR-facing employee identifier.
    client.post("/api/v1/employees", json=employee_payload("EMP-000001"))
    client.post("/api/v1/employees", json=employee_payload("EMP-000010"))

    response = client.get("/api/v1/employees/next-id")

    assert response.status_code == 200
    assert response.json() == {"employee_id": "EMP-000011"}


def test_employee_get_update_delete_api(client: TestClient) -> None:
    # Intent: employee detail, profile update, and soft delete work through the API.
    created = client.post("/api/v1/employees", json=employee_payload()).json()
    employee_uuid = created["id"]

    detail = client.get(f"/api/v1/employees/{employee_uuid}")
    assert detail.status_code == 200
    assert detail.json()["full_name"] == "Asha Patel"

    updated = client.patch(
        f"/api/v1/employees/{employee_uuid}",
        json={"title": "Senior HR Manager"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Senior HR Manager"

    deleted = client.delete(f"/api/v1/employees/{employee_uuid}")
    assert deleted.status_code == 204

    active_list = client.get("/api/v1/employees")
    assert active_list.json()["total"] == 0

    all_list = client.get("/api/v1/employees?include_inactive=true")
    assert all_list.json()["total"] == 1
