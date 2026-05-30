"""master data config and employee name columns

Revision ID: 20260530_0004
Revises: 20260530_0003
Create Date: 2026-05-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260530_0004"
down_revision: str | None = "20260530_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_master_data_category", table_name="master_data")
    op.drop_table("master_data")

    op.create_table(
        "master_data_config",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("category_name", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("parent_category_name", sa.String(length=100), nullable=True),
        sa.Column("parent_code", sa.String(length=100), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_master_data_config")),
        sa.UniqueConstraint("category_name", "code", name="uq_master_data_config_category_code"),
    )
    op.create_index(
        "ix_master_data_config_category",
        "master_data_config",
        ["category_name"],
        unique=False,
    )
    op.create_index(
        "ix_master_data_config_parent",
        "master_data_config",
        ["parent_category_name", "parent_code"],
        unique=False,
    )

    op.add_column("employees", sa.Column("first_name", sa.String(length=200), nullable=True))
    op.add_column("employees", sa.Column("last_name", sa.String(length=200), nullable=True))
    op.add_column("employees", sa.Column("gender", sa.String(length=10), nullable=True))
    op.execute(
        """
        UPDATE employees
        SET
            first_name = COALESCE(NULLIF(split_part(full_name, ' ', 1), ''), full_name),
            last_name = COALESCE(
                NULLIF(trim(substr(full_name, length(split_part(full_name, ' ', 1)) + 1)), ''),
                split_part(full_name, ' ', 1)
            )
        """
    )
    op.alter_column("employees", "first_name", nullable=False)
    op.alter_column("employees", "last_name", nullable=False)
    op.alter_column(
        "employees",
        "country_code",
        existing_type=sa.String(length=2),
        type_=sa.String(length=3),
        existing_nullable=False,
    )
    op.drop_column("employees", "full_name")


def downgrade() -> None:
    op.add_column("employees", sa.Column("full_name", sa.String(length=200), nullable=True))
    op.execute(
        """
        UPDATE employees
        SET full_name = trim(first_name || ' ' || last_name)
        """
    )
    op.alter_column("employees", "full_name", nullable=False)
    op.alter_column(
        "employees",
        "country_code",
        existing_type=sa.String(length=3),
        type_=sa.String(length=2),
        existing_nullable=False,
    )
    op.drop_column("employees", "gender")
    op.drop_column("employees", "last_name")
    op.drop_column("employees", "first_name")

    op.drop_index("ix_master_data_config_parent", table_name="master_data_config")
    op.drop_index("ix_master_data_config_category", table_name="master_data_config")
    op.drop_table("master_data_config")

    op.create_table(
        "master_data",
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("value", sa.String(length=80), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_master_data")),
        sa.UniqueConstraint("category", "description", name="uq_master_data_category_description"),
        sa.UniqueConstraint("category", "value", name="uq_master_data_category_value"),
    )
    op.create_index("ix_master_data_category", "master_data", ["category"], unique=False)
