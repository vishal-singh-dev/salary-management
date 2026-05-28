from decimal import Decimal

from pydantic import BaseModel


class SalaryAnalyticsFilters(BaseModel):
    country_code: str | None
    department: str | None
    title: str | None
    include_inactive: bool
    currency_basis: str


class SalaryAnalytics(BaseModel):
    filters: SalaryAnalyticsFilters
    employee_count: int
    currency_code: str | None
    min_base_salary: Decimal | None
    max_base_salary: Decimal | None
    mean_base_salary: Decimal | None
    median_base_salary: Decimal | None
    mode_base_salary: Decimal | None

