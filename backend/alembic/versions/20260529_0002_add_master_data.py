"""add master data table

Revision ID: 20260529_0002
Revises: 20260527_0001
Create Date: 2026-05-29 07:50:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260529_0002"
down_revision: str | None = "20260527_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.drop_index("ix_master_data_category", table_name="master_data")
    op.drop_table("master_data")
