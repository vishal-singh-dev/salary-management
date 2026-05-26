from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExchangeRateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_currency_code: str = Field(min_length=3, max_length=3)
    target_currency_code: str = Field(min_length=3, max_length=3)
    rate_to_usd: Decimal
    effective_from: date
    effective_to: date | None
    rate_source: str
    created_at: datetime
