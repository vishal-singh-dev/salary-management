import uuid
from unittest.mock import Mock

import pytest

from app.models import AuditEvent
from app.seed.generator import generate_seed_records, required_currencies
from app.seed.persistence import (
    SeedPreconditionError,
    assert_empty_employee_dataset,
    persist_seed_data,
)


def test_seed_initial_load_guard() -> None:
    # Intent: the seed workflow refuses to mutate a database that already has employees.
    session = Mock()
    session.scalar.return_value = 1

    with pytest.raises(SeedPreconditionError, match="initial-load only"):
        assert_empty_employee_dataset(session)


def test_seed_batch_persistence() -> None:
    # Intent: seed persistence batches inserts and writes one audit summary event.
    rates = {
        currency: uuid.uuid5(uuid.NAMESPACE_DNS, currency) for currency in required_currencies()
    }
    seed_data = generate_seed_records(3, 2026, ["Asha"], ["Patel"], rates)
    session = Mock()

    persist_seed_data(session, seed_data, random_seed=2026, batch_size=2)

    assert session.execute.call_count == 4
    session.add.assert_called_once()
    audit_event = session.add.call_args.args[0]
    assert isinstance(audit_event, AuditEvent)
    assert audit_event.event_type == "seed.employees_created"
    assert audit_event.details["employee_count"] == 3
    assert audit_event.details["random_seed"] == 2026
