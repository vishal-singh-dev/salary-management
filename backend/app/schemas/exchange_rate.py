from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FXRates(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    src_crncy_id: str = Field(min_length=3, max_length=3)
    target_crncy_id: str = Field(min_length=3, max_length=3)
    target_rate: Decimal
