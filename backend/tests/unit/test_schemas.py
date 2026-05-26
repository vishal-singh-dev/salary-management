from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.audit_event import AuditEventRead
from app.schemas.employee import EmployeeCreate
from app.schemas.salary_record import SalaryCreate


def test_employee_create_requires_valid_initial_salary() -> None:
    employee = EmployeeCreate(
        employee_id="EMP-000001",
        full_name="Asha Patel",
        title="HR Manager",
        department="Human Resources",
        country_code="IN",
        from_date=date(2024, 1, 1),
        initial_salary=SalaryCreate(
            currency_code="INR",
            base_amount=Decimal("1200000.00"),
            variable_amount=Decimal("100000.00"),
            hra_allowance_amount=Decimal("240000.00"),
            pf_amount=Decimal("144000.00"),
            gratuity_amount=Decimal("58000.00"),
            effective_from=date(2026, 1, 1),
        ),
    )

    assert employee.initial_salary.base_amount == Decimal("1200000.00")


def test_salary_record_rejects_non_positive_base_salary() -> None:
    with pytest.raises(ValidationError):
        SalaryCreate(
            currency_code="USD",
            base_amount=Decimal("0"),
            effective_from=date(2026, 1, 1),
        )


def test_audit_event_schema_exposes_mvp_business_event_fields() -> None:
    event = AuditEventRead(
        id=uuid4(),
        occurred_at=datetime.now(UTC),
        event_type="employee.created",
        entity_id=uuid4(),
        entity_type="employee",
        employee_id=None,
        initiated_by="hr_ui",
        summary="Employee created.",
        details={"changed_fields": ["full_name"]},
    )

    assert event.event_type == "employee.created"
    assert event.initiated_by == "hr_ui"
