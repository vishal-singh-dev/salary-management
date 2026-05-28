import uuid
from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.main import create_app
from app.models import Employee, EmployeeSalaryRecord, ExchangeRate

pytestmark = pytest.mark.integration


@pytest.fixture()
def client(database_session: Session) -> Generator[TestClient, None, None]:
    # Intent: analytics API tests execute aggregate SQL against PostgreSQL.
    app = create_app()

    def override_session() -> Generator[Session, None, None]:
        yield database_session

    app.dependency_overrides[get_session] = override_session
    _add_salary_fixture_data(database_session)

    yield TestClient(app)
    app.dependency_overrides.clear()


def test_salary_analytics_filters(client: TestClient) -> None:
    # Intent: salary analytics supports country and department filters with mean/median/mode.
    response = client.get(
        "/api/v1/analytics/salaries",
        params={"country_code": "IN", "department": "Engineering"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 3
    assert body["currency_code"] == "INR"
    assert body["min_base_salary"] == "1000000.00"
    assert body["max_base_salary"] == "3000000.00"
    assert body["mean_base_salary"] == "2000000.00"
    assert body["median_base_salary"] == "2000000.00"
    assert body["mode_base_salary"] == "1000000.00"


def test_salary_analytics_excludes_inactive_by_default(client: TestClient) -> None:
    # Intent: inactive employees are excluded unless include_inactive is explicitly true.
    active_response = client.get(
        "/api/v1/analytics/salaries",
        params={"country_code": "IN", "department": "Finance"},
    )
    inactive_response = client.get(
        "/api/v1/analytics/salaries",
        params={"country_code": "IN", "department": "Finance", "include_inactive": True},
    )

    assert active_response.json()["employee_count"] == 0
    assert inactive_response.json()["employee_count"] == 1


def test_salary_analytics_requires_country_for_local_currency(client: TestClient) -> None:
    # Intent: local-currency metrics cannot mix countries with different currencies.
    response = client.get("/api/v1/analytics/salaries")

    assert response.status_code == 422


def test_salary_analytics_usd_basis(client: TestClient) -> None:
    # Intent: USD basis supports cross-country salary comparison.
    response = client.get(
        "/api/v1/analytics/salaries",
        params={"currency_basis": "usd", "department": "Engineering"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 4
    assert body["currency_code"] == "USD"
    assert body["mean_base_salary"] == "55500.00"


def _add_salary_fixture_data(session: Session) -> None:
    inr_rate = ExchangeRate(
        id=uuid.uuid4(),
        source_currency_code="INR",
        target_currency_code="USD",
        rate_to_usd=Decimal("0.01200000"),
        effective_from=date(2026, 1, 1),
        rate_source="TEST_FIXED_RATE",
    )
    usd_rate = ExchangeRate(
        id=uuid.uuid4(),
        source_currency_code="USD",
        target_currency_code="USD",
        rate_to_usd=Decimal("1.00000000"),
        effective_from=date(2026, 1, 1),
        rate_source="TEST_FIXED_RATE",
    )
    session.add_all([inr_rate, usd_rate])
    session.flush()

    _add_employee_salary(
        session, "EMP-001", "IN", "Engineering", "Engineer", "INR", 1_000_000, inr_rate.id
    )
    _add_employee_salary(
        session, "EMP-002", "IN", "Engineering", "Engineer", "INR", 1_000_000, inr_rate.id
    )
    _add_employee_salary(
        session, "EMP-003", "IN", "Engineering", "Manager", "INR", 3_000_000, inr_rate.id
    )
    _add_employee_salary(
        session, "EMP-004", "US", "Engineering", "Engineer", "USD", 150_000, usd_rate.id
    )
    _add_employee_salary(
        session,
        "EMP-005",
        "IN",
        "Finance",
        "Analyst",
        "INR",
        9_000_000,
        inr_rate.id,
        to_date=date(2026, 5, 1),
    )
    session.commit()


def _add_employee_salary(
    session: Session,
    employee_id: str,
    country_code: str,
    department: str,
    title: str,
    currency_code: str,
    base_amount: int,
    exchange_rate_id: uuid.UUID,
    to_date: date | None = None,
) -> None:
    employee = Employee(
        id=uuid.uuid4(),
        employee_id=employee_id,
        full_name=f"{employee_id} Test",
        title=title,
        department=department,
        country_code=country_code,
        from_date=date(2026, 1, 1),
        to_date=to_date,
    )
    employee.salary_records.append(
        EmployeeSalaryRecord(
            id=uuid.uuid4(),
            currency_code=currency_code,
            base_amount=Decimal(base_amount),
            variable_amount=Decimal("0"),
            hra_allowance_amount=Decimal("0"),
            pf_amount=Decimal("0"),
            gratuity_amount=Decimal("0"),
            exchange_rate_id=exchange_rate_id,
            effective_from=date(2026, 1, 1),
        )
    )
    session.add(employee)
