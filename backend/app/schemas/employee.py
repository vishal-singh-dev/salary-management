from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.salary_record import SalaryCreate, SalaryRead


class EmployeeBase(BaseModel):
    employee_id: str = Field(min_length=1, max_length=30)
    first_name: str = Field(min_length=1, max_length=200)
    last_name: str = Field(min_length=1, max_length=200)
    gender: str | None = Field(default=None, min_length=1, max_length=10)
    title: str = Field(min_length=1, max_length=200)
    department: str = Field(min_length=1, max_length=120)
    country_code: str = Field(min_length=2, max_length=3)
    from_date: date
    to_date: date | None = None


class EmployeeCreate(EmployeeBase):
    initial_salary: SalaryCreate


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=200)
    last_name: str | None = Field(default=None, min_length=1, max_length=200)
    gender: str | None = Field(default=None, min_length=1, max_length=10)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    department: str | None = Field(default=None, min_length=1, max_length=120)
    country_code: str | None = Field(default=None, min_length=2, max_length=3)
    from_date: date | None = None
    to_date: date | None = None


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    current_salary: SalaryRead | None = None


class EmployeeList(BaseModel):
    items: list[EmployeeRead]
    total: int
    limit: int
    offset: int


class EmployeeNextId(BaseModel):
    employee_id: str
