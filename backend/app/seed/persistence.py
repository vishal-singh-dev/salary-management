from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import asdict

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import AuditEvent, Employee, EmployeeSalaryRecord, ExchangeRate
from app.seed.generator import GeneratedSeedData, required_currencies


class SeedPreconditionError(RuntimeError):
    """Raised when initial-load preconditions are not satisfied."""


def current_exchange_rate_ids(session: Session) -> dict[str, uuid.UUID]:
    rows = session.execute(
        select(ExchangeRate.source_currency_code, ExchangeRate.id).where(
            ExchangeRate.effective_to.is_(None)
        )
    ).all()
    exchange_rate_ids = {currency_code: rate_id for currency_code, rate_id in rows}
    missing = sorted(required_currencies() - exchange_rate_ids.keys())
    if missing:
        raise SeedPreconditionError(
            f"Missing current exchange rates for currencies: {', '.join(missing)}"
        )
    return exchange_rate_ids


def assert_empty_employee_dataset(session: Session) -> None:
    existing_count = session.scalar(select(func.count()).select_from(Employee))
    if existing_count:
        raise SeedPreconditionError(
            "Employee seeding is initial-load only; employees already exist in the database."
        )


def persist_seed_data(
    session: Session,
    seed_data: GeneratedSeedData,
    *,
    random_seed: int,
    batch_size: int,
) -> None:
    if batch_size <= 0:
        raise ValueError("Batch size must be greater than zero.")

    for batch in _batches(seed_data.employees, batch_size):
        session.execute(insert(Employee), [asdict(record) for record in batch])
    for batch in _batches(seed_data.salaries, batch_size):
        session.execute(insert(EmployeeSalaryRecord), [asdict(record) for record in batch])

    session.add(
        AuditEvent(
            event_type="seed.employees_created",
            entity_type="employee_seed_batch",
            initiated_by="seed_script",
            summary=(
                f"Created initial employee dataset containing "
                f"{len(seed_data.employees)} employees."
            ),
            details={
                "employee_count": len(seed_data.employees),
                "salary_record_count": len(seed_data.salaries),
                "random_seed": random_seed,
                "batch_size": batch_size,
                "currencies_used": sorted(seed_data.currencies_used),
            },
        )
    )


def _batches[T](records: Sequence[T], batch_size: int) -> list[Sequence[T]]:
    return [records[start : start + batch_size] for start in range(0, len(records), batch_size)]
