"""store employee department and title master values

Revision ID: 20260530_0003
Revises: 20260529_0002
Create Date: 2026-05-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260530_0003"
down_revision: str | None = "20260529_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEPARTMENT_VALUES = {
    "Engineering": "ENG",
    "Product": "PROD",
    "Data": "DATA",
    "Human Resources": "HR",
    "Finance": "FIN",
    "Sales": "SALES",
    "Support": "SUPPORT",
}

JOB_TITLE_VALUES = {
    "Software Engineer": "SWE",
    "Senior Software Engineer": "SR_SWE",
    "Product Manager": "PM",
    "Data Analyst": "DA",
    "HR Business Partner": "HRBP",
    "Finance Manager": "FIN_MGR",
    "Sales Executive": "SALES_EXEC",
    "Support Specialist": "SUPPORT_SPEC",
}


def upgrade() -> None:
    connection = op.get_bind()
    for description, value in DEPARTMENT_VALUES.items():
        connection.execute(
            sa.text("UPDATE employees SET department = :value WHERE department = :description"),
            {"value": value, "description": description},
        )
    for description, value in JOB_TITLE_VALUES.items():
        connection.execute(
            sa.text("UPDATE employees SET title = :value WHERE title = :description"),
            {"value": value, "description": description},
        )


def downgrade() -> None:
    connection = op.get_bind()
    for description, value in DEPARTMENT_VALUES.items():
        connection.execute(
            sa.text("UPDATE employees SET department = :description WHERE department = :value"),
            {"value": value, "description": description},
        )
    for description, value in JOB_TITLE_VALUES.items():
        connection.execute(
            sa.text("UPDATE employees SET title = :description WHERE title = :value"),
            {"value": value, "description": description},
        )
