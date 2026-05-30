from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import ExchangeRate

EXCHANGE_RATE_NAMESPACE = uuid.UUID("0b82b8d4-a4cc-4b44-bd78-c3ac2c49a8d5")
FIXED_RATE_SOURCE = "MVP_FIXED_RATE_TABLE"


@dataclass(frozen=True)
class FixedExchangeRate:
    id: uuid.UUID
    source_currency_code: str
    target_currency_code: str
    rate_to_usd: Decimal
    effective_from: date
    effective_to: None
    rate_source: str


def fixed_exchange_rates() -> list[FixedExchangeRate]:
    effective_from = date(2026, 1, 1)
    rates = {
        "INR": Decimal("0.01200000"),
        "CNY": Decimal("0.14000000"),
        "USD": Decimal("1.00000000"),
        "GBP": Decimal("1.26000000"),
        "EUR": Decimal("1.08000000"),
        "CAD": Decimal("0.74000000"),
        "AUD": Decimal("0.66000000"),
    }
    return [
        FixedExchangeRate(
            id=uuid.uuid5(EXCHANGE_RATE_NAMESPACE, currency),
            source_currency_code=currency,
            target_currency_code="USD",
            rate_to_usd=rate,
            effective_from=effective_from,
            effective_to=None,
            rate_source=FIXED_RATE_SOURCE,
        )
        for currency, rate in rates.items()
    ]


def seed_fixed_exchange_rates(session: Session) -> int:
    values = [rate.__dict__ for rate in fixed_exchange_rates()]
    statement = insert(ExchangeRate).values(values)
    session.execute(
        statement.on_conflict_do_nothing(
            index_elements=[ExchangeRate.source_currency_code],
            index_where=ExchangeRate.effective_to.is_(None),
        )
    )
    return len(values)
