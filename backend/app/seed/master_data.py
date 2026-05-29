from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import MasterData
from app.seed.generator import COUNTRIES, DEPARTMENTS, TITLES

MASTER_DATA_NAMESPACE = uuid.UUID("f4a42ace-64f7-4ef0-9d26-ec77d3cf32b6")

COUNTRY_CATEGORY = "country"
DEPARTMENT_CATEGORY = "department"
JOB_TITLE_CATEGORY = "job_title"

COUNTRY_LABELS = {
    "IN": "INDIA",
    "US": "UNITED STATES",
    "GB": "UNITED KINGDOM",
    "DE": "GERMANY",
    "CA": "CANADA",
    "AU": "AUSTRALIA",
}

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


@dataclass(frozen=True)
class FixedMasterData:
    id: uuid.UUID
    category: str
    description: str
    value: str


def fixed_master_data() -> list[FixedMasterData]:
    records: list[FixedMasterData] = []
    records.extend(
        _records_from_pairs(
            category=COUNTRY_CATEGORY,
            pairs=[
                (COUNTRY_LABELS.get(country.code, country.code), country.code)
                for country in COUNTRIES
            ],
        )
    )
    records.extend(
        _records_from_pairs(
            category=DEPARTMENT_CATEGORY,
            pairs=[(department, DEPARTMENT_VALUES[department]) for department in DEPARTMENTS],
        )
    )
    records.extend(
        _records_from_pairs(
            category=JOB_TITLE_CATEGORY,
            pairs=[(title, JOB_TITLE_VALUES[title]) for title in TITLES],
        )
    )
    return records


def seed_fixed_master_data(session: Session) -> int:
    values = [record.__dict__ for record in fixed_master_data()]
    statement = insert(MasterData).values(values)
    session.execute(
        statement.on_conflict_do_nothing(
            index_elements=[MasterData.category, MasterData.description],
        )
    )
    return len(values)


def _records_from_pairs(
    *,
    category: str,
    pairs: list[tuple[str, str]],
) -> list[FixedMasterData]:
    return [
        FixedMasterData(
            id=uuid.uuid5(MASTER_DATA_NAMESPACE, f"{category}:{value}"),
            category=category,
            description=description,
            value=value,
        )
        for description, value in pairs
    ]
