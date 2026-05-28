from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.models import Employee, EmployeeSalaryRecord, ExchangeRate
from app.schemas.analytics import SalaryAnalytics, SalaryAnalyticsFilters

router = APIRouter(prefix="/analytics", tags=["analytics"])
SessionDep = Annotated[Session, Depends(get_session)]
CurrencyBasis = Literal["local", "usd"]


@router.get("/salaries", response_model=SalaryAnalytics)
def get_salary_analytics(
    session: SessionDep,
    country_code: str | None = Query(default=None, min_length=2, max_length=2),
    department: str | None = Query(default=None, min_length=1, max_length=120),
    title: str | None = Query(default=None, min_length=1, max_length=200),
    include_inactive: bool = False,
    currency_basis: CurrencyBasis = "local",
) -> SalaryAnalytics:
    if currency_basis == "local" and not country_code:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="country_code is required when currency_basis is local.",
        )

    salary_value = (
        EmployeeSalaryRecord.base_amount
        if currency_basis == "local"
        else EmployeeSalaryRecord.base_amount * ExchangeRate.rate_to_usd
    )
    filters = [
        EmployeeSalaryRecord.effective_to.is_(None),
        Employee.id == EmployeeSalaryRecord.employee_id,
        ExchangeRate.id == EmployeeSalaryRecord.exchange_rate_id,
    ]
    if not include_inactive:
        filters.append(Employee.to_date.is_(None))
    if country_code:
        filters.append(Employee.country_code == country_code)
    if department:
        filters.append(Employee.department == department)
    if title:
        filters.append(Employee.title == title)

    metrics = session.execute(
        select(
            func.count(Employee.id),
            func.min(salary_value),
            func.max(salary_value),
            func.avg(salary_value),
            func.percentile_cont(0.5).within_group(salary_value),
            func.mode().within_group(salary_value),
            func.min(EmployeeSalaryRecord.currency_code),
            func.max(EmployeeSalaryRecord.currency_code),
        )
        .select_from(Employee)
        .join(EmployeeSalaryRecord, Employee.id == EmployeeSalaryRecord.employee_id)
        .join(ExchangeRate, ExchangeRate.id == EmployeeSalaryRecord.exchange_rate_id)
        .where(*filters)
    ).one()
    (
        employee_count,
        min_salary,
        max_salary,
        mean_salary,
        median_salary,
        mode_salary,
        min_currency,
        max_currency,
    ) = metrics

    currency_code = _currency_code(currency_basis, min_currency, max_currency)
    return SalaryAnalytics(
        filters=SalaryAnalyticsFilters(
            country_code=country_code,
            department=department,
            title=title,
            include_inactive=include_inactive,
            currency_basis=currency_basis,
        ),
        employee_count=employee_count,
        currency_code=currency_code,
        min_base_salary=_decimal_or_none(min_salary),
        max_base_salary=_decimal_or_none(max_salary),
        mean_base_salary=_decimal_or_none(mean_salary),
        median_base_salary=_decimal_or_none(median_salary),
        mode_base_salary=_decimal_or_none(mode_salary),
    )


def _currency_code(
    currency_basis: CurrencyBasis,
    min_currency: str | None,
    max_currency: str | None,
) -> str | None:
    if currency_basis == "usd":
        return "USD"
    if not min_currency:
        return None
    if min_currency != max_currency:
        return None
    return min_currency


def _decimal_or_none(value: object) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"))
