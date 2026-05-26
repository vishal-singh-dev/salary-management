"""Create employee, salary, exchange rate, and audit event tables.

Revision ID: 20260527_0001
Revises:
Create Date: 2026-05-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260527_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", sa.String(length=30), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("from_date", sa.Date(), nullable=False),
        sa.Column("to_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "to_date IS NULL OR to_date >= from_date",
            name="valid_employment_period",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_employees"),
        sa.UniqueConstraint("employee_id", name="uq_employees_employee_id"),
    )
    op.create_index("ix_employees_country_code", "employees", ["country_code"])
    op.create_index("ix_employees_department", "employees", ["department"])
    op.create_index("ix_employees_employee_id", "employees", ["employee_id"])
    op.create_index("ix_employees_title", "employees", ["title"])
    op.create_index("ix_employees_current_country", "employees", ["to_date", "country_code"])
    op.create_index("ix_employees_current_department", "employees", ["to_date", "department"])

    op.create_table(
        "exchange_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_currency_code", sa.String(length=3), nullable=False),
        sa.Column("target_currency_code", sa.String(length=3), nullable=False),
        sa.Column("rate_to_usd", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("rate_source", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("rate_to_usd > 0", name="positive_rate_to_usd"),
        sa.CheckConstraint("target_currency_code = 'USD'", name="target_currency_is_usd"),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="valid_effective_period",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_exchange_rates"),
    )
    op.create_index(
        "ix_exchange_rates_source_effective_from",
        "exchange_rates",
        ["source_currency_code", "effective_from"],
    )
    op.create_index(
        "uq_exchange_rates_current_source_currency",
        "exchange_rates",
        ["source_currency_code"],
        unique=True,
        postgresql_where=sa.text("effective_to IS NULL"),
    )

    op.create_table(
        "employee_salary_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.Column("base_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("variable_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("hra_allowance_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("pf_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("gratuity_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("exchange_rate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "base_amount > 0",
            name="positive_base_amount",
        ),
        sa.CheckConstraint(
            "variable_amount >= 0",
            name="non_negative_variable_amount",
        ),
        sa.CheckConstraint(
            "hra_allowance_amount >= 0",
            name="non_negative_hra_allowance_amount",
        ),
        sa.CheckConstraint(
            "pf_amount >= 0",
            name="non_negative_pf_amount",
        ),
        sa.CheckConstraint(
            "gratuity_amount >= 0",
            name="non_negative_gratuity_amount",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="valid_effective_period",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name="fk_employee_salary_records_employee_id_employees",
        ),
        sa.ForeignKeyConstraint(
            ["exchange_rate_id"],
            ["exchange_rates.id"],
            name="fk_employee_salary_records_exchange_rate_id_exchange_rates",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_employee_salary_records"),
    )
    op.create_index(
        "ix_employee_salary_records_employee_id", "employee_salary_records", ["employee_id"]
    )
    op.create_index(
        "ix_employee_salary_records_employee_effective_from",
        "employee_salary_records",
        ["employee_id", "effective_from"],
    )
    op.create_index(
        "uq_employee_salary_records_current_employee",
        "employee_salary_records",
        ["employee_id"],
        unique=True,
        postgresql_where=sa.text("effective_to IS NULL"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("initiated_by", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.String(length=250), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_audit_events_employee_id_employees"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
    )
    op.create_index(
        "ix_audit_events_employee_occurred_at", "audit_events", ["employee_id", "occurred_at"]
    )
    op.create_index(
        "ix_audit_events_event_type_occurred_at", "audit_events", ["event_type", "occurred_at"]
    )
    op.create_index("ix_audit_events_entity", "audit_events", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("employee_salary_records")
    op.drop_table("exchange_rates")
    op.drop_table("employees")
