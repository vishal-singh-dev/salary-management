Problem Statement
=================

Build a minimal but usable salary management tool for an organisation with 10,000 employees.
The first user persona is an HR manager who needs to manage employee records and understand salary
distribution across countries, departments, and job titles.

The backend must support:

- Employee create, read, update, and delete operations.
- Salary records connected to employees.
- Salary insights such as minimum, maximum, average, median, and mode.
- Country and department based analytics.
- Deterministic seed data generation for 10,000 employees.
- A relational database schema that can evolve beyond the MVP.
- Unit and integration tests developed with a TDD approach.

Backend Scope
=============

The backend is implemented as a FastAPI service using PostgreSQL. Neon PostgreSQL is the intended
hosted database, with connection strings supplied through environment variables.

Implemented backend scope:

- Configuration loading from environment variables.
- SQLAlchemy database engine and session setup.
- Alembic migrations.
- Employee, salary, exchange-rate, and audit models.
- Filter master-data model for country, department, and job title values.
- Pydantic schemas for API validation and serialization.
- Health check endpoint.
- Employee CRUD API.
- Salary analytics API.
- Deterministic seed generation for employee and salary data.
- Fixed exchange-rate master seeding.
- Unit tests for core logic.
- Integration tests against a disposable PostgreSQL database.

Data Model Plan
===============

The database is intentionally normalized so employee identity, salary history, currency conversion,
and audit events can evolve independently.

Tables:

| Table | Purpose |
| --- | --- |
| `employees` | Stores employee profile and employment period |
| `employee_salary_records` | Stores effective-dated salary records |
| `exchange_rates` | Stores current and historical FX rates to USD |
| `master_data` | Stores fixed filter values used by dashboard and employee screens |
| `audit_events` | Stores MVP audit events for important backend actions |

Employee design:

- `id` is the internal database UUID and is used by API detail routes.
- `employee_id` is the HR-facing identifier and must be unique.
- `full_name`, `title`, `department`, and `country_code` support HR workflows and analytics.
- `from_date` and `to_date` represent employment period.
- `to_date IS NULL` means the employee is active.
- Delete is implemented as soft delete by setting `to_date`.

Salary design:

- Salary is stored separately from employee profile data.
- Each salary record is effective dated with `effective_from` and `effective_to`.
- `effective_to IS NULL` means the salary record is current.
- `base_amount` is the primary salary metric for analytics.
- Allowances and statutory components are stored separately for future reporting.
- `currency_code` stores local salary currency.
- `exchange_rate_id` links the salary record to the FX rate used for USD comparison.

Exchange-rate design:

- Exchange rates are stored in a separate table instead of hardcoded in application logic.
- Rates are modeled from source currency to USD.
- Current rows have `effective_to IS NULL`.
- The MVP seed inserts fixed master rows for INR, USD, GBP, EUR, CAD, and AUD.

Master-data design:

- Country, department, and job title filter values are stored in `master_data`.
- `category` identifies the filter group, such as `country`, `department`, or `job_title`.
- `description` stores the display value used by the user.
- `value` stores a stable numeric code for each description inside a category.
- Seed values come from `app.seed.generator` so filters match generated employees.

Audit design:

- Auditing is intentionally functional and minimal for MVP.
- It records business events that matter for traceability, such as employee create, update, delete,
  and seed completion.
- The audit table is not a full enterprise audit log yet.
- This keeps the feature useful without overbuilding schema fields that the product does not use.

API Plan
========

The API is versioned under `/api/v1`.

Health:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Confirms the API process is running |

Employee CRUD:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/employees` | Create employee with one initial salary record |
| GET | `/api/v1/employees` | List employees with pagination |
| GET | `/api/v1/employees/{employee_uuid}` | Read employee by internal UUID |
| PATCH | `/api/v1/employees/{employee_uuid}` | Update employee profile fields |
| DELETE | `/api/v1/employees/{employee_uuid}` | Soft delete employee |

Salary analytics:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/analytics/salaries` | Return salary metrics with optional filters |

Analytics query parameters:

- `country_code`
- `department`
- `title`
- `include_inactive`
- `currency_basis`

Analytics behavior:

- Active employees are used by default.
- Current salary records are used by default.
- Local currency analytics require `country_code` to avoid mixing currencies.
- USD analytics use `base_amount * exchange_rates.rate_to_usd`.
- The endpoint returns count, minimum, maximum, mean, median, and mode.

Why query parameters instead of path parameters:

- Salary analytics is a filtered collection query, not a single country or department resource.
- Query parameters make optional filters natural.
- This avoids creating many path variants as the product adds more filters.

Testing Plan
============

The project follows a TDD style where core behavior is expressed through tests before or alongside
implementation.

Unit tests:

- Test configuration behavior.
- Test schema validation.
- Test seed generation logic.
- Keep tests fast and deterministic.
- Avoid database dependency for pure business logic.

Integration tests:

- Use a disposable PostgreSQL database through `TEST_DATABASE_URL`.
- Do not use the application `DATABASE_URL`.
- Create and drop schema around test runs.
- Test API behavior through FastAPI `TestClient`.
- Cover database-backed flows such as employee create/list/update/delete and analytics queries.

End-to-end testing:

- Full browser end-to-end tests are not required for the backend-only MVP.
- They become valuable once the Next.js UI is implemented.
- For the assessment, API integration tests provide better early value because they test the
  database, validation, and endpoint behavior deterministically.

Seeding Plan
============

The seed requirement is to generate 10,000 employees by combining first and last names from text
files.

Seed behavior:

- Read `data/first_names.txt`.
- Read `data/last_names.txt`.
- Combine names deterministically using a random seed.
- Generate employee profile fields such as title, department, country, and employment date.
- Generate one current salary record for each employee.
- Use existing current FX rows from `exchange_rates`.
- Insert records in batches for performance.
- Stop when employees already exist to avoid overwriting real HR data.

The seed script is designed as an initial-load command. Engineers can run it repeatedly, but it
should not duplicate production-like data.

Configuration Plan
==================

Configuration is environment driven.

Important variables:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Application database URL |
| `TEST_DATABASE_URL` | Disposable database URL for integration tests |
| `ENVIRONMENT` | Environment label returned by health check |
| `CORS_ORIGINS` | Allowed frontend origins |
| `SQL_ECHO` | SQLAlchemy SQL logging toggle |

Neon connection strings can be supplied as standard `postgresql://` URLs. The configuration layer
normalizes them for SQLAlchemy's psycopg driver.

Project Structure
=================

```text
backend/
+-- alembic/
+-- app/
|   +-- api/
|   +-- core/
|   +-- models/
|   +-- schemas/
|   +-- seed/
|   +-- main.py
+-- data/
|   +-- first_names.txt
|   +-- last_names.txt
+-- tests/
|   +-- integration/
|   +-- unit/
+-- alembic.ini
+-- pyproject.toml
+-- README.md
+-- plan.md
+-- uv.lock
```

Implementation Order
====================

The backend was planned and built incrementally:

1. Create Python backend project with FastAPI, SQLAlchemy, Alembic, Pydantic, pytest, and Ruff.
2. Add configuration loading and database connection setup.
3. Define normalized models for employees, salary records, exchange rates, and audit events.
4. Add Alembic migration setup.
5. Add Pydantic schemas and validation.
6. Add health endpoint and test.
7. Add deterministic seed generator unit tests and implementation.
8. Add seed persistence and fixed FX master seed.
9. Add fixed filter master-data seed.
10. Add employee CRUD API and integration tests.
11. Add salary analytics API and integration tests.
12. Document setup, commands, and API usage.

MVP Tradeoffs
=============

Intentional MVP choices:

- Salary update APIs are deferred. The current employee create API creates the first salary record.
- Employee delete is soft delete to preserve history.
- Audit logging records functional business events only.
- FX rates are fixed master seed values for the MVP.
- Salary analytics use `base_amount` as the primary metric.
- Authentication and authorization are deferred 
