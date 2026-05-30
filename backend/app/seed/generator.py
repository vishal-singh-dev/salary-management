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
    first_name: str
    last_name: str
    gender: str | None
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


@dataclass(frozen=True)
class EmployeeMasterHierarchy:
    country_departments: dict[str, tuple[str, ...]]
    department_titles: dict[str, tuple[str, ...]]


COUNTRIES = (
    CountryProfile("IN", "INR", 500_000, 6_000_000, Decimal("20"), Decimal("12"), Decimal("4.81")),
    CountryProfile("CHN", "CNY", 90_000, 1_400_000, Decimal("0"), Decimal("5"), Decimal("0")),
    CountryProfile("AUS", "AUD", 65_000, 220_000, Decimal("0"), Decimal("4"), Decimal("0")),
    CountryProfile("US", "USD", 55_000, 240_000, Decimal("0"), Decimal("4"), Decimal("0")),
    CountryProfile("GB", "GBP", 38_000, 150_000, Decimal("0"), Decimal("5"), Decimal("0")),
    CountryProfile("DE", "EUR", 45_000, 170_000, Decimal("0"), Decimal("4"), Decimal("0")),
    CountryProfile("CA", "CAD", 55_000, 190_000, Decimal("0"), Decimal("4"), Decimal("0")),
)
COUNTRY_DEPARTMENTS = {
    "IN": ("HR", "FIN"),
    "CHN": ("SP", "LAB"),
    "AUS": ("ENG", "PROD"),
    "US": ("US_ENG", "US_SALES"),
    "GB": ("GB_OPS", "GB_FIN"),
    "DE": ("DE_ENG", "DE_DATA"),
    "CA": ("CA_SUPPORT", "CA_HR"),
}
DEPARTMENT_TITLES = {
    "HR": ("HRF", "HRO"),
    "FIN": ("FIN_MGR", "PAYROLL"),
    "SP": ("CS", "GS"),
    "LAB": ("LAB_SUP", "LAB_COORD"),
    "ENG": ("SWE", "SR_SWE"),
    "PROD": ("PM", "PA"),
    "US_ENG": ("US_PE", "US_EM"),
    "US_SALES": ("US_SE", "US_AM"),
    "GB_OPS": ("GB_OM", "GB_PA"),
    "GB_FIN": ("GB_FA", "GB_CTRL"),
    "DE_ENG": ("DE_SE", "DE_AE"),
    "DE_DATA": ("DE_DA", "DE_DE"),
    "CA_SUPPORT": ("CA_CSS", "CA_SL"),
    "CA_HR": ("CA_HRBP", "CA_TP"),
}
GENDERS = ("Female", "Male", "Other")
DEFAULT_EMPLOYEE_MASTER_HIERARCHY = EmployeeMasterHierarchy(
    country_departments=COUNTRY_DEPARTMENTS,
    department_titles=DEPARTMENT_TITLES,
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
    hierarchy: EmployeeMasterHierarchy | None = None,
) -> GeneratedSeedData:
    if count <= 0:
        raise ValueError("Employee count must be greater than zero.")
    if not first_names or not last_names:
        raise ValueError("First and last names must not be empty.")
    hierarchy = hierarchy or DEFAULT_EMPLOYEE_MASTER_HIERARCHY
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
        country = rng.choice(_countries_with_job_titles(hierarchy))
        department = rng.choice(_departments_with_job_titles(hierarchy, country.code))
        first_name = rng.choice(first_names)
        last_name = rng.choice(last_names)
        currencies_used.add(country.currency_code)
        from_date = employment_start + timedelta(days=rng.randrange(0, 4018))
        base_amount = Decimal(
            rng.randrange(country.minimum_base, country.maximum_base + 1, 100)
        ).quantize(MONEY_QUANTUM)
        variable_percent = Decimal(rng.choice((0, 5, 10, 15, 20)))

        employee = SeedEmployeeRecord(
            id=employee_uuid,
            employee_id=business_id,
            first_name=first_name,
            last_name=last_name,
            gender=rng.choice(GENDERS),
            title=rng.choice(hierarchy.department_titles[department]),
            department=department,
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


def _countries_with_job_titles(hierarchy: EmployeeMasterHierarchy) -> tuple[CountryProfile, ...]:
    countries = tuple(
        country
        for country in COUNTRIES
        if any(
            department in hierarchy.department_titles
            for department in hierarchy.country_departments.get(country.code, ())
        )
    )
    if not countries:
        raise ValueError(
            "Master data does not contain any country with departments and job titles."
        )
    return countries


def _departments_with_job_titles(
    hierarchy: EmployeeMasterHierarchy,
    country_code: str,
) -> tuple[str, ...]:
    departments = tuple(
        department
        for department in hierarchy.country_departments.get(country_code, ())
        if department in hierarchy.department_titles
    )
    if not departments:
        raise ValueError(f"Master data does not contain job-title departments for {country_code}.")
    return departments
