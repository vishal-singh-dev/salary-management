from app.models import Base


def test_normalized_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "employees",
        "employee_salary_records",
        "exchange_rates",
        "audit_events",
    }
