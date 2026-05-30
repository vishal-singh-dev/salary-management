from app.seed.generator import COUNTRIES
from app.seed.master_data import (
    COUNTRY_CATEGORY,
    DEPARTMENT_CATEGORY,
    DEPARTMENT_DESCRIPTIONS,
    DEPARTMENT_VALUES,
    JOB_TITLE_CATEGORY,
    JOB_TITLE_DESCRIPTIONS,
    JOB_TITLE_VALUES,
    fixed_master_data,
)


def test_fixed_master_data_contains_filter_values() -> None:
    # Intent: ensure dashboard filter masters are generated from the same values used by seeding.
    records = fixed_master_data()

    assert len(records) == (
        len(COUNTRIES) + len(DEPARTMENT_DESCRIPTIONS) + len(JOB_TITLE_DESCRIPTIONS)
    )
    assert {record.value for record in records if record.category == COUNTRY_CATEGORY} == {
        country.code for country in COUNTRIES
    }
    department_descriptions = {
        record.description for record in records if record.category == DEPARTMENT_CATEGORY
    }
    assert department_descriptions == set(DEPARTMENT_DESCRIPTIONS)
    assert {record.value for record in records if record.category == DEPARTMENT_CATEGORY} == set(
        DEPARTMENT_VALUES.values()
    )
    title_descriptions = {
        record.description for record in records if record.category == JOB_TITLE_CATEGORY
    }
    assert title_descriptions == set(JOB_TITLE_DESCRIPTIONS)
    assert {record.value for record in records if record.category == JOB_TITLE_CATEGORY} == set(
        JOB_TITLE_VALUES.values()
    )


def test_fixed_master_data_uses_unique_values_per_category() -> None:
    # Intent: each category should have stable unique query values for UI filters.
    records = fixed_master_data()

    for category in {record.category for record in records}:
        category_records = [record for record in records if record.category == category]
        assert len({record.value for record in category_records}) == len(category_records)
        assert len({record.id for record in category_records}) == len(category_records)


def test_fixed_master_data_country_uses_display_label_and_query_value() -> None:
    # Intent: UI displays country description but sends the seeded employee country code.
    germany = next(
        record
        for record in fixed_master_data()
        if record.category == COUNTRY_CATEGORY and record.description == "GERMANY"
    )

    assert germany.value == "DE"


def test_fixed_master_data_department_and_title_use_short_query_values() -> None:
    # Intent: query values should be compact codes without spaces, while descriptions stay readable.
    records = fixed_master_data()
    engineering = next(
        record
        for record in records
        if record.category == DEPARTMENT_CATEGORY and record.description == "Engineering"
    )
    senior_engineer = next(
        record
        for record in records
        if (
            record.category == JOB_TITLE_CATEGORY
            and record.description == "Senior Software Engineer"
        )
    )

    assert engineering.value == "ENG"
    assert senior_engineer.value == "SR_SWE"
    assert " " not in engineering.value
    assert " " not in senior_engineer.value
