from app.seed.generator import COUNTRIES, COUNTRY_DEPARTMENTS, DEPARTMENT_TITLES
from app.seed.master_data import (
    COUNTRY_CATEGORY,
    CURRENCY_CATEGORY,
    DEPARTMENT_CATEGORY,
    JOB_TITLE_CATEGORY,
    fixed_master_data,
)


def test_fixed_master_data_contains_hierarchical_values() -> None:
    # Intent: dropdown masters include country, dependent department/title, and currency values.
    records = fixed_master_data()

    countries = [record for record in records if record.category_name == COUNTRY_CATEGORY]
    departments = [record for record in records if record.category_name == DEPARTMENT_CATEGORY]
    titles = [record for record in records if record.category_name == JOB_TITLE_CATEGORY]
    currencies = [record for record in records if record.category_name == CURRENCY_CATEGORY]

    assert {record.code for record in countries} == {country.code for country in COUNTRIES}
    assert {record.code for record in currencies} >= {
        country.currency_code for country in COUNTRIES
    }
    assert all(record.parent_category_name is None for record in countries + currencies)
    assert all(record.parent_code is None for record in countries + currencies)
    assert {
        (record.parent_code, record.code)
        for record in departments
    } == {
        (country_code, department)
        for country_code, department_codes in COUNTRY_DEPARTMENTS.items()
        for department in department_codes
    }
    assert {
        (record.parent_code, record.code)
        for record in titles
    } == {
        (department_code, title)
        for department_code, title_codes in DEPARTMENT_TITLES.items()
        for title in title_codes
    }


def test_fixed_master_data_uses_unique_codes_per_category() -> None:
    # Intent: each master category can be upserted by category/code.
    records = fixed_master_data()

    for category_name in {record.category_name for record in records}:
        category_records = [
            record for record in records if record.category_name == category_name
        ]
        assert len({record.code for record in category_records}) == len(category_records)


def test_fixed_master_data_keeps_currency_independent() -> None:
    # Intent: salary currency choices are not filtered by country, department, or title.
    currencies = [
        record
        for record in fixed_master_data()
        if record.category_name == CURRENCY_CATEGORY
    ]

    assert {record.code for record in currencies} >= {"INR", "CNY", "AUD", "USD"}
    assert all(record.parent_category_name is None for record in currencies)
    assert all(record.parent_code is None for record in currencies)
