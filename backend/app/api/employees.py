from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_session
from app.models import AuditEvent, Employee, EmployeeSalaryRecord, ExchangeRate
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeList,
    EmployeeNextId,
    EmployeeRead,
    EmployeeUpdate,
)

router = APIRouter(prefix="/employees", tags=["employees"])
SessionDep = Annotated[Session, Depends(get_session)]
EMPLOYEE_ID_PREFIX = "EMP-"
EMPLOYEE_ID_WIDTH = 6
EMPLOYEE_ID_NUMBER_PATTERN = re.compile(r"(\d+)$")


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, session: SessionDep) -> EmployeeRead:
    exchange_rate = _current_exchange_rate(session, payload.initial_salary.currency_code)
    employee = Employee(
        employee_id=payload.employee_id,
        full_name=payload.full_name,
        title=payload.title,
        department=payload.department,
        country_code=payload.country_code,
        from_date=payload.from_date,
        to_date=payload.to_date,
    )
    salary = EmployeeSalaryRecord(
        employee=employee,
        currency_code=payload.initial_salary.currency_code,
        base_amount=payload.initial_salary.base_amount,
        variable_amount=payload.initial_salary.variable_amount,
        hra_allowance_amount=payload.initial_salary.hra_allowance_amount,
        pf_amount=payload.initial_salary.pf_amount,
        gratuity_amount=payload.initial_salary.gratuity_amount,
        exchange_rate_id=exchange_rate.id,
        effective_from=payload.initial_salary.effective_from,
        effective_to=None,
    )
    employee.salary_records.append(salary)
    try:
        session.add(employee)
        session.flush()
        session.add(
            AuditEvent(
                event_type="employee.created",
                entity_type="employee",
                entity_id=employee.id,
                employee_id=employee.id,
                initiated_by="api",
                summary=f"Created employee {employee.employee_id}.",
                details={"employee_id": employee.employee_id},
            )
        )
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee identifier already exists.",
        ) from error
    session.refresh(employee)
    return _employee_with_current_salary(session, employee.id)


@router.get("", response_model=EmployeeList)
def list_employees(
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    include_inactive: bool = False,
) -> EmployeeList:
    filters = [] if include_inactive else [Employee.to_date.is_(None)]
    total = session.scalar(select(func.count()).select_from(Employee).where(*filters)) or 0
    employees = (
        session.scalars(
            select(Employee)
            .options(selectinload(Employee.salary_records))
            .where(*filters)
            .order_by(Employee.employee_id)
            .limit(limit)
            .offset(offset)
        )
        .unique()
        .all()
    )
    return EmployeeList(
        items=[_to_employee_read(employee) for employee in employees],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/next-id", response_model=EmployeeNextId)
def get_next_employee_id(session: SessionDep) -> EmployeeNextId:
    employee_ids = session.scalars(select(Employee.employee_id)).all()
    max_number = 0
    max_width = EMPLOYEE_ID_WIDTH

    for employee_id in employee_ids:
        match = EMPLOYEE_ID_NUMBER_PATTERN.search(employee_id)
        if not match:
            continue
        number_text = match.group(1)
        max_number = max(max_number, int(number_text))
        max_width = max(max_width, len(number_text))

    next_number = max_number + 1
    return EmployeeNextId(employee_id=f"{EMPLOYEE_ID_PREFIX}{next_number:0{max_width}d}")


@router.get("/{employee_uuid}", response_model=EmployeeRead)
def get_employee(employee_uuid: uuid.UUID, session: SessionDep) -> EmployeeRead:
    return _to_employee_read(_employee_with_current_salary(session, employee_uuid))


@router.patch("/{employee_uuid}", response_model=EmployeeRead)
def update_employee(
    employee_uuid: uuid.UUID,
    payload: EmployeeUpdate,
    session: SessionDep,
) -> EmployeeRead:
    employee = _employee_with_current_salary(session, employee_uuid)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(employee, field, value)
    session.add(
        AuditEvent(
            event_type="employee.updated",
            entity_type="employee",
            entity_id=employee.id,
            employee_id=employee.id,
            initiated_by="api",
            summary=f"Updated employee {employee.employee_id}.",
            details={"changed_fields": sorted(updates)},
        )
    )
    session.commit()
    return _to_employee_read(_employee_with_current_salary(session, employee_uuid))


@router.delete("/{employee_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_uuid: uuid.UUID, session: SessionDep) -> None:
    employee = _employee_with_current_salary(session, employee_uuid)
    if employee.to_date is None:
        employee.to_date = datetime.now(UTC).date()
    session.add(
        AuditEvent(
            event_type="employee.deleted",
            entity_type="employee",
            entity_id=employee.id,
            employee_id=employee.id,
            initiated_by="api",
            summary=f"Ended employee {employee.employee_id}.",
            details={"to_date": employee.to_date.isoformat()},
        )
    )
    session.commit()


def _current_exchange_rate(session: Session, currency_code: str) -> ExchangeRate:
    exchange_rate = session.scalar(
        select(ExchangeRate).where(
            ExchangeRate.source_currency_code == currency_code,
            ExchangeRate.effective_to.is_(None),
        )
    )
    if not exchange_rate:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No current exchange rate exists for {currency_code}.",
        )
    return exchange_rate


def _employee_with_current_salary(session: Session, employee_uuid: uuid.UUID) -> Employee:
    employee = session.scalar(
        select(Employee)
        .options(selectinload(Employee.salary_records))
        .where(Employee.id == employee_uuid)
    )
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
    return employee


def _to_employee_read(employee: Employee) -> EmployeeRead:
    current_salary = next(
        (salary for salary in employee.salary_records if salary.effective_to is None),
        None,
    )
    return EmployeeRead.model_validate(
        {
            "id": employee.id,
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "title": employee.title,
            "department": employee.department,
            "country_code": employee.country_code,
            "from_date": employee.from_date,
            "to_date": employee.to_date,
            "created_at": employee.created_at,
            "current_salary": current_salary,
        }
    )
