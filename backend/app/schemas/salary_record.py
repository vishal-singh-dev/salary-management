from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SalaryCreate(BaseModel):
    currency_code: str = Field(min_length=3, max_length=3)
    base_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    variable_amount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    hra_allowance_amount: Decimal = Field(
        default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2
    )
    pf_amount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    gratuity_amount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    effective_from: date


class SalaryRead(SalaryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    exchange_rate_id: UUID
    effective_to: date | None
    created_at: datetime
    total_amount: Decimal
    base_amount_usd: Decimal
    total_amount_usd: Decimal
