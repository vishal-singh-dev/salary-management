from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.employee_salary_record import EmployeeSalaryRecord


class ExchangeRate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        CheckConstraint("target_currency_code = 'USD'", name="target_currency_is_usd"),
        CheckConstraint("rate_to_usd > 0", name="positive_rate_to_usd"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="valid_effective_period",
        ),
        Index(
            "uq_exchange_rates_current_source_currency",
            "source_currency_code",
            unique=True,
            postgresql_where=text("effective_to IS NULL"),
        ),
        Index("ix_exchange_rates_source_effective_from", "source_currency_code", "effective_from"),
    )

    source_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    target_currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    rate_to_usd: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    rate_source: Mapped[str] = mapped_column(String(100), nullable=False)

    salary_records: Mapped[list[EmployeeSalaryRecord]] = relationship(
        back_populates="exchange_rate"
    )
