from app.models import Base


def test_schema_tables() -> None:
    # Intent: all normalized SQLAlchemy tables are registered for migrations and tests.
    assert set(Base.metadata.tables) == {
        "employees",
        "employee_salary_records",
        "exchange_rates",
        "audit_events",
    }
