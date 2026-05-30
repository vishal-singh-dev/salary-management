import uuid
from decimal import Decimal
from pathlib import Path

import pytest

from app.seed.generator import (
    COUNTRY_DEPARTMENTS,
    DEPARTMENT_TITLES,
    generate_seed_records,
    load_names,
    required_currencies,
)


def exchange_rate_ids() -> dict[str, uuid.UUID]:
    return {
        currency: uuid.uuid5(uuid.NAMESPACE_DNS, currency) for currency in required_currencies()
    }


def test_seed_name_file_validation(tmp_path: Path) -> None:
    # Intent: seed input files must contain at least one usable name.
    path = tmp_path / "names.txt"
    path.write_text("\n", encoding="utf-8")

    with pytest.raises(ValueError, match="is empty"):
        load_names(path)


def test_seed_data_generation() -> None:
    # Intent: generated employees and salary rows are deterministic and relationally linked.
    first_names = ["Asha", "Maya"]
    last_names = ["Patel", "Singh"]
    rates = exchange_rate_ids()

    first_run = generate_seed_records(10, 2026, first_names, last_names, rates)
    second_run = generate_seed_records(10, 2026, first_names, last_names, rates)

    assert first_run == second_run
    assert first_run.employees[0].employee_id == "SEED-000001"
    assert first_run.employees[-1].employee_id == "SEED-000010"
    assert len(first_run.employees) == len(first_run.salaries) == 10
    assert {salary.employee_id for salary in first_run.salaries} == {
        employee.id for employee in first_run.employees
    }
    assert all(
        employee.first_name in first_names and employee.last_name in last_names
        for employee in first_run.employees
    )
    assert all(
        employee.department in COUNTRY_DEPARTMENTS[employee.country_code]
        for employee in first_run.employees
    )
    assert all(
        employee.title in DEPARTMENT_TITLES[employee.department]
        for employee in first_run.employees
    )
    assert all(salary.base_amount > Decimal("0") for salary in first_run.salaries)


def test_fx_rates_prerequisites() -> None:
    # Intent: seed generation requires a complete set of current exchange rates.
    with pytest.raises(ValueError, match="Missing current exchange rates"):
        generate_seed_records(1, 2026, ["Asha"], ["Patel"], {"INR": uuid.uuid4()})
