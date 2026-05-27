from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

EMPLOYEE_NAMESPACE = uuid.UUID("29727d52-03d6-4b41-847e-b490952646cd")
SALARY_NAMESPACE = uuid.UUID("68783ba3-cbb0-4974-8334-bd3cf2382bb5")
MONEY_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class CountryProfile:
    code: str
    currency_code: str
    minimum_base: int
    maximum_base: int
    hra_percent: Decimal
    pf_percent: Decimal
    gratuity_percent: Decimal


@dataclass(frozen=True)
class SeedEmployeeRecord:
    id: uuid.UUID
    employee_id: str
    full_name: str
    title: str
    department: str
    country_code: str
    from_date: date
    to_date: None = None


@dataclass(frozen=True)
class SeedSalaryRecord:
    id: uuid.UUID
    employee_id: uuid.UUID
    currency_code: str
    base_amount: Decimal
    variable_amount: Decimal
    hra_allowance_amount: Decimal
    pf_amount: Decimal
    gratuity_amount: Decimal
    exchange_rate_id: uuid.UUID
    effective_from: date
    effective_to: None = None


@dataclass(frozen=True)
class GeneratedSeedData:
    employees: list[SeedEmployeeRecord]
    salaries: list[SeedSalaryRecord]
    currencies_used: set[str]


COUNTRIES = (
    CountryProfile("IN", "INR", 500_000, 6_000_000, Decimal("20"), Decimal("12"), Decimal("4.81")),
    CountryProfile("US", "USD", 55_000, 240_000, Decimal("0"), Decimal("4"), Decimal("0")),
    CountryProfile("GB", "GBP", 38_000, 150_000, Decimal("0"), Decimal("5"), Decimal("0")),
    CountryProfile("DE", "EUR", 45_000, 170_000, Decimal("0"), Decimal("4"), Decimal("0")),
    CountryProfile("CA", "CAD", 55_000, 190_000, Decimal("0"), Decimal("4"), Decimal("0")),
    CountryProfile("AU", "AUD", 65_000, 220_000, Decimal("0"), Decimal("4"), Decimal("0")),
)
TITLES = (
    "Software Engineer",
    "Senior Software Engineer",
    "Product Manager",
    "Data Analyst",
    "HR Business Partner",
    "Finance Manager",
    "Sales Executive",
    "Support Specialist",
)
DEPARTMENTS = (
    "Engineering",
    "Product",
    "Data",
    "Human Resources",
    "Finance",
    "Sales",
    "Support",
)


def load_names(path: Path) -> list[str]:
    if not path.exists():
        raise ValueError(f"Name fixture file was not found: {path}")
    names = [
        value.strip()
        for value in path.read_text(encoding="utf-8").splitlines()
        if value.strip()
    ]
    if not names:
        raise ValueError(f"Name fixture file is empty: {path}")
    return names


def required_currencies() -> set[str]:
    return {country.currency_code for country in COUNTRIES}


def generate_seed_records(
    count: int,
    random_seed: int,
    first_names: list[str],
    last_names: list[str],
    exchange_rate_ids: dict[str, uuid.UUID],
) -> GeneratedSeedData:
    if count <= 0:
        raise ValueError("Employee count must be greater than zero.")
    if not first_names or not last_names:
        raise ValueError("First and last names must not be empty.")
    missing_rates = sorted(required_currencies() - exchange_rate_ids.keys())
    if missing_rates:
        raise ValueError(
            f"Missing current exchange rates for currencies: {', '.join(missing_rates)}"
        )

    rng = random.Random(random_seed)
    employees: list[SeedEmployeeRecord] = []
    salaries: list[SeedSalaryRecord] = []
    currencies_used: set[str] = set()
    employment_start = date(2015, 1, 1)

    for sequence in range(1, count + 1):
        business_id = f"SEED-{sequence:06d}"
        employee_uuid = uuid.uuid5(EMPLOYEE_NAMESPACE, business_id)
        country = rng.choice(COUNTRIES)
        currencies_used.add(country.currency_code)
        from_date = employment_start + timedelta(days=rng.randrange(0, 4018))
        base_amount = Decimal(
            rng.randrange(country.minimum_base, country.maximum_base + 1, 100)
        ).quantize(MONEY_QUANTUM)
        variable_percent = Decimal(rng.choice((0, 5, 10, 15, 20)))

        employee = SeedEmployeeRecord(
            id=employee_uuid,
            employee_id=business_id,
            full_name=f"{rng.choice(first_names)} {rng.choice(last_names)}",
            title=rng.choice(TITLES),
            department=rng.choice(DEPARTMENTS),
            country_code=country.code,
            from_date=from_date,
        )
        salary = SeedSalaryRecord(
            id=uuid.uuid5(SALARY_NAMESPACE, business_id),
            employee_id=employee_uuid,
            currency_code=country.currency_code,
            base_amount=base_amount,
            variable_amount=_percentage_amount(base_amount, variable_percent),
            hra_allowance_amount=_percentage_amount(base_amount, country.hra_percent),
            pf_amount=_percentage_amount(base_amount, country.pf_percent),
            gratuity_amount=_percentage_amount(base_amount, country.gratuity_percent),
            exchange_rate_id=exchange_rate_ids[country.currency_code],
            effective_from=from_date,
        )
        employees.append(employee)
        salaries.append(salary)

    return GeneratedSeedData(
        employees=employees, salaries=salaries, currencies_used=currencies_used
    )


def _percentage_amount(amount: Decimal, percent: Decimal) -> Decimal:
    return (amount * percent / Decimal("100")).quantize(MONEY_QUANTUM)
