import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AuditEvent, Employee, EmployeeSalaryRecord, ExchangeRate
from app.seed.generator import generate_seed_records, required_currencies
from app.seed.persistence import (
    SeedPreconditionError,
    assert_empty_employee_dataset,
    persist_seed_data,
)

pytestmark = pytest.mark.integration


def add_current_exchange_rates(session: Session) -> dict[str, uuid.UUID]:
    rate_ids: dict[str, uuid.UUID] = {}
    for currency in required_currencies():
        rate_id = uuid.uuid5(uuid.NAMESPACE_DNS, currency)
        rate_ids[currency] = rate_id
        session.add(
            ExchangeRate(
                id=rate_id,
                source_currency_code=currency,
                target_currency_code="USD",
                rate_to_usd=Decimal("1.00000000"),
                effective_from=date(2026, 1, 1),
                rate_source="TEST_FIXED_RATES",
            )
        )
    session.flush()
    return rate_ids


def test_seed_database_persistence(database_session: Session) -> None:
    # Intent: seed records persist correctly against PostgreSQL with employee/salary counts.
    rates = add_current_exchange_rates(database_session)
    seed_data = generate_seed_records(25, 2026, ["Asha"], ["Patel"], rates)

    assert_empty_employee_dataset(database_session)
    persist_seed_data(database_session, seed_data, random_seed=2026, batch_size=10)
    database_session.flush()

    assert database_session.scalar(select(func.count()).select_from(Employee)) == 25
    assert database_session.scalar(select(func.count()).select_from(EmployeeSalaryRecord)) == 25
    assert database_session.scalar(select(func.count()).select_from(AuditEvent)) == 1

    with pytest.raises(SeedPreconditionError, match="initial-load only"):
        assert_empty_employee_dataset(database_session)
