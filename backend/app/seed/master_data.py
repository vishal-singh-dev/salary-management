from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import MasterData
from app.seed.generator import EmployeeMasterHierarchy

COUNTRY_CATEGORY = "Country"
DEPARTMENT_CATEGORY = "Department"
JOB_TITLE_CATEGORY = "JobTitle"
CURRENCY_CATEGORY = "Currency"


@dataclass(frozen=True)
class FixedMasterData:
    category_name: str
    display_name: str
    code: str
    parent_category_name: str | None
    parent_code: str | None
    sort_order: int


MD = FixedMasterData

COUNTRY_RECORDS = (
    MD(COUNTRY_CATEGORY, "India", "IN", None, None, 1),
    MD(COUNTRY_CATEGORY, "China", "CHN", None, None, 2),
    MD(COUNTRY_CATEGORY, "Australia", "AUS", None, None, 3),
    MD(COUNTRY_CATEGORY, "United States", "US", None, None, 4),
    MD(COUNTRY_CATEGORY, "United Kingdom", "GB", None, None, 5),
    MD(COUNTRY_CATEGORY, "Germany", "DE", None, None, 6),
    MD(COUNTRY_CATEGORY, "Canada", "CA", None, None, 7),
)

DEPARTMENT_RECORDS = (
    MD(DEPARTMENT_CATEGORY, "HR", "HR", COUNTRY_CATEGORY, "IN", 1),
    MD(DEPARTMENT_CATEGORY, "Finance", "FIN", COUNTRY_CATEGORY, "IN", 2),
    MD(DEPARTMENT_CATEGORY, "Support", "SP", COUNTRY_CATEGORY, "CHN", 3),
    MD(DEPARTMENT_CATEGORY, "Labour", "LAB", COUNTRY_CATEGORY, "CHN", 4),
    MD(DEPARTMENT_CATEGORY, "Engineering", "ENG", COUNTRY_CATEGORY, "AUS", 5),
    MD(DEPARTMENT_CATEGORY, "Product", "PROD", COUNTRY_CATEGORY, "AUS", 6),
    MD(DEPARTMENT_CATEGORY, "Engineering", "US_ENG", COUNTRY_CATEGORY, "US", 7),
    MD(DEPARTMENT_CATEGORY, "Sales", "US_SALES", COUNTRY_CATEGORY, "US", 8),
    MD(DEPARTMENT_CATEGORY, "Operations", "GB_OPS", COUNTRY_CATEGORY, "GB", 9),
    MD(DEPARTMENT_CATEGORY, "Finance", "GB_FIN", COUNTRY_CATEGORY, "GB", 10),
    MD(DEPARTMENT_CATEGORY, "Engineering", "DE_ENG", COUNTRY_CATEGORY, "DE", 11),
    MD(DEPARTMENT_CATEGORY, "Data", "DE_DATA", COUNTRY_CATEGORY, "DE", 12),
    MD(DEPARTMENT_CATEGORY, "Support", "CA_SUPPORT", COUNTRY_CATEGORY, "CA", 13),
    MD(DEPARTMENT_CATEGORY, "HR", "CA_HR", COUNTRY_CATEGORY, "CA", 14),
)

JOB_TITLE_RECORDS = (
    MD(JOB_TITLE_CATEGORY, "HR Finance", "HRF", DEPARTMENT_CATEGORY, "HR", 1),
    MD(JOB_TITLE_CATEGORY, "HR Operations", "HRO", DEPARTMENT_CATEGORY, "HR", 2),
    MD(JOB_TITLE_CATEGORY, "Finance Manager", "FIN_MGR", DEPARTMENT_CATEGORY, "FIN", 3),
    MD(JOB_TITLE_CATEGORY, "Payroll Specialist", "PAYROLL", DEPARTMENT_CATEGORY, "FIN", 4),
    MD(JOB_TITLE_CATEGORY, "Call Support", "CS", DEPARTMENT_CATEGORY, "SP", 5),
    MD(JOB_TITLE_CATEGORY, "General Support", "GS", DEPARTMENT_CATEGORY, "SP", 6),
    MD(JOB_TITLE_CATEGORY, "Labour Supervisor", "LAB_SUP", DEPARTMENT_CATEGORY, "LAB", 7),
    MD(JOB_TITLE_CATEGORY, "Labour Coordinator", "LAB_COORD", DEPARTMENT_CATEGORY, "LAB", 8),
    MD(JOB_TITLE_CATEGORY, "Software Engineer", "SWE", DEPARTMENT_CATEGORY, "ENG", 9),
    MD(JOB_TITLE_CATEGORY, "Senior Software Engineer", "SR_SWE", DEPARTMENT_CATEGORY, "ENG", 10),
    MD(JOB_TITLE_CATEGORY, "Product Manager", "PM", DEPARTMENT_CATEGORY, "PROD", 11),
    MD(JOB_TITLE_CATEGORY, "Product Analyst", "PA", DEPARTMENT_CATEGORY, "PROD", 12),
    MD(JOB_TITLE_CATEGORY, "Platform Engineer", "US_PE", DEPARTMENT_CATEGORY, "US_ENG", 13),
    MD(JOB_TITLE_CATEGORY, "Engineering Manager", "US_EM", DEPARTMENT_CATEGORY, "US_ENG", 14),
    MD(JOB_TITLE_CATEGORY, "Sales Executive", "US_SE", DEPARTMENT_CATEGORY, "US_SALES", 15),
    MD(JOB_TITLE_CATEGORY, "Account Manager", "US_AM", DEPARTMENT_CATEGORY, "US_SALES", 16),
    MD(JOB_TITLE_CATEGORY, "Operations Manager", "GB_OM", DEPARTMENT_CATEGORY, "GB_OPS", 17),
    MD(JOB_TITLE_CATEGORY, "Process Analyst", "GB_PA", DEPARTMENT_CATEGORY, "GB_OPS", 18),
    MD(JOB_TITLE_CATEGORY, "Finance Analyst", "GB_FA", DEPARTMENT_CATEGORY, "GB_FIN", 19),
    MD(JOB_TITLE_CATEGORY, "Controller", "GB_CTRL", DEPARTMENT_CATEGORY, "GB_FIN", 20),
    MD(JOB_TITLE_CATEGORY, "Systems Engineer", "DE_SE", DEPARTMENT_CATEGORY, "DE_ENG", 21),
    MD(JOB_TITLE_CATEGORY, "Automation Engineer", "DE_AE", DEPARTMENT_CATEGORY, "DE_ENG", 22),
    MD(JOB_TITLE_CATEGORY, "Data Analyst", "DE_DA", DEPARTMENT_CATEGORY, "DE_DATA", 23),
    MD(JOB_TITLE_CATEGORY, "Data Engineer", "DE_DE", DEPARTMENT_CATEGORY, "DE_DATA", 24),
    MD(
        JOB_TITLE_CATEGORY,
        "Customer Support Specialist",
        "CA_CSS",
        DEPARTMENT_CATEGORY,
        "CA_SUPPORT",
        25,
    ),
    MD(JOB_TITLE_CATEGORY, "Support Lead", "CA_SL", DEPARTMENT_CATEGORY, "CA_SUPPORT", 26),
    MD(JOB_TITLE_CATEGORY, "HR Business Partner", "CA_HRBP", DEPARTMENT_CATEGORY, "CA_HR", 27),
    MD(JOB_TITLE_CATEGORY, "Talent Partner", "CA_TP", DEPARTMENT_CATEGORY, "CA_HR", 28),
)

CURRENCY_RECORDS = (
    MD(CURRENCY_CATEGORY, "Indian Rupee", "INR", None, None, 1),
    MD(CURRENCY_CATEGORY, "Chinese Yuan", "CNY", None, None, 2),
    MD(CURRENCY_CATEGORY, "Australian Dollar", "AUD", None, None, 3),
    MD(CURRENCY_CATEGORY, "United States Dollar", "USD", None, None, 4),
    MD(CURRENCY_CATEGORY, "British Pound", "GBP", None, None, 5),
    MD(CURRENCY_CATEGORY, "Euro", "EUR", None, None, 6),
    MD(CURRENCY_CATEGORY, "Canadian Dollar", "CAD", None, None, 7),
)


def fixed_master_data() -> list[FixedMasterData]:
    return [
        *COUNTRY_RECORDS,
        *DEPARTMENT_RECORDS,
        *JOB_TITLE_RECORDS,
        *CURRENCY_RECORDS,
    ]


def seed_fixed_master_data(session: Session) -> int:
    values = [record.__dict__ | {"is_active": True} for record in fixed_master_data()]
    statement = insert(MasterData).values(values)
    session.execute(
        statement.on_conflict_do_update(
            index_elements=[MasterData.category_name, MasterData.code],
            set_={
                "display_name": statement.excluded.display_name,
                "parent_category_name": statement.excluded.parent_category_name,
                "parent_code": statement.excluded.parent_code,
                "sort_order": statement.excluded.sort_order,
                "is_active": True,
            },
        )
    )
    return len(values)


def active_employee_master_hierarchy(session: Session) -> EmployeeMasterHierarchy:
    rows = session.scalars(
        select(MasterData)
        .where(
            MasterData.category_name.in_(
                [COUNTRY_CATEGORY, DEPARTMENT_CATEGORY, JOB_TITLE_CATEGORY]
            ),
            MasterData.is_active.is_(True),
        )
        .order_by(MasterData.sort_order, MasterData.display_name)
    ).all()
    active_country_codes = {
        row.code for row in rows if row.category_name == COUNTRY_CATEGORY
    }
    country_departments: dict[str, list[str]] = {
        country_code: [] for country_code in active_country_codes
    }
    department_titles: dict[str, list[str]] = {}

    for row in rows:
        if (
            row.category_name == DEPARTMENT_CATEGORY
            and row.parent_category_name == COUNTRY_CATEGORY
            and row.parent_code in active_country_codes
        ):
            country_departments.setdefault(row.parent_code, []).append(row.code)

    active_department_codes = {
        department
        for departments in country_departments.values()
        for department in departments
    }
    for row in rows:
        if (
            row.category_name == JOB_TITLE_CATEGORY
            and row.parent_category_name == DEPARTMENT_CATEGORY
            and row.parent_code in active_department_codes
        ):
            department_titles.setdefault(row.parent_code, []).append(row.code)

    return EmployeeMasterHierarchy(
        country_departments={
            country: tuple(departments)
            for country, departments in country_departments.items()
            if departments
        },
        department_titles={
            department: tuple(titles)
            for department, titles in department_titles.items()
            if titles
        },
    )
