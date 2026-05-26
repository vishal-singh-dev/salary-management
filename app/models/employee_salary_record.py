from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.exchange_rate import ExchangeRate


class EmployeeSalaryRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "employee_salary_records"
    __table_args__ = (
        CheckConstraint("base_amount > 0", name="positive_base_amount"),
        CheckConstraint("variable_amount >= 0", name="non_negative_variable_amount"),
        CheckConstraint("hra_allowance_amount >= 0", name="non_negative_hra_allowance_amount"),
        CheckConstraint("pf_amount >= 0", name="non_negative_pf_amount"),
        CheckConstraint("gratuity_amount >= 0", name="non_negative_gratuity_amount"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="valid_effective_period",
        ),
        Index(
            "uq_employee_salary_records_current_employee",
            "employee_id",
            unique=True,
            postgresql_where=text("effective_to IS NULL"),
        ),
        Index(
            "ix_employee_salary_records_employee_effective_from", "employee_id", "effective_from"
        ),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    variable_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    hra_allowance_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    pf_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    gratuity_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    exchange_rate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exchange_rates.id"), nullable=False
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    employee: Mapped[Employee] = relationship(back_populates="salary_records")
    exchange_rate: Mapped[ExchangeRate] = relationship(back_populates="salary_records")
