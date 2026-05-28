Salary Management
=================

A salary management backend for an HR manager to manage employee records and salary data for an
organisation-scale dataset of 10,000 employees.

The project currently contains the FastAPI backend foundation, PostgreSQL schema, deterministic
employee seeding, salary seeding, fixed exchange-rate master setup, and backend tests. The frontend
will be added as a separate Next.js application under this repository.

Project Requirements
====================

Functional requirements
-----------------------

| Area | Requirement |
| --- | --- |
| Employee management | Add, view, update, and delete employees through the final UI |
| Employee fields | Full name, job title, country, salary, and other meaningful HR data |
| Salary insights | Minimum, maximum, and average salary by country |
| Salary insights | Average salary for a job title within a country |
| Scale | Seed and support 10,000 employees |
| Seeding | Generate full names from `first_names.txt` and `last_names.txt` |
| Backend | Fully functional API and relational database |
| UI | React or Next.js frontend |
| Tests | Fast, deterministic unit tests and meaningful integration tests |
| Delivery | Deployed software and video demo |
| Git history | Incremental commits showing solution evolution |

Current implementation status
-----------------------------

| Component | Status |
| --- | --- |
| FastAPI backend | Implemented |
| PostgreSQL connection | Implemented |
| Alembic setup | Implemented |
| Employee schema | Implemented |
| Salary schema | Implemented |
| Exchange-rate master schema | Implemented |
| Audit event schema | Implemented |
| Fixed FX master seed | Implemented |
| 10,000 employee seed | Implemented |
| Unit tests | Implemented |
| PostgreSQL integration test | Implemented |
| Next.js frontend | Pending |
| Deployed app | Pending |
| Video demo | Pending |

Tech Stack
==========

| Layer | Technology |
| --- | --- |
| Backend | Python, FastAPI |
| Database | PostgreSQL, Neon compatible |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Dependency management | uv |
| Testing | pytest |
| Linting | Ruff |

Repository Structure
====================

```text
salary-management/
+-- backend/
|   +-- alembic/
|   +-- app/
|   |   +-- core/
|   |   +-- models/
|   |   +-- schemas/
|   |   +-- seed/
|   +-- data/
|   |   +-- first_names.txt
|   |   +-- last_names.txt
|   +-- tests/
|   |   +-- integration/
|   |   +-- unit/
|   +-- .env.example
|   +-- alembic.ini
|   +-- pyproject.toml
|   +-- README.md
+-- docker-compose.yml
+-- .gitattributes
+-- .gitignore
+-- README.md
```

Backend Data Model
==================

The backend uses normalized tables:

| Table | Purpose |
| --- | --- |
| `employees` | Employee profile, title, department, country, and employment period |
| `employee_salary_records` | Effective-dated salary structure for each employee |
| `exchange_rates` | Current and historical currency-to-USD rates |
| `audit_events` | MVP audit trail for business events |

Salary records include:

- `base_amount`
- `variable_amount`
- `hra_allowance_amount`
- `pf_amount`
- `gratuity_amount`
- `currency_code`
- `exchange_rate_id`
- `effective_from`
- `effective_to`

Salary insights should use `base_amount` as the core salary metric.

Prerequisites
=============

Install:

- Python 3.12 or newer
- uv
- Git
- PostgreSQL or a Neon PostgreSQL database

Check local tools:

```powershell
python --version
uv --version
git --version
```

Setup
=====

Clone the repository:

```powershell
git clone https://github.com/vishal-singh-dev/SalaryManagement.git
cd SalaryManagement
```

Install backend dependencies:

```powershell
cd backend
uv sync --dev
```

Create environment file:

```powershell
Copy-Item .env.example .env
```

Update `backend/.env`:

```dotenv
ENVIRONMENT=development
DATABASE_URL=postgresql://username:password@host/database?sslmode=require&channel_binding=require
CORS_ORIGINS=["http://localhost:3000"]
SQL_ECHO=false
```

The application accepts a standard Neon `postgresql://` connection string and internally uses the
SQLAlchemy `psycopg` driver.

Local PostgreSQL Option
=======================

If you do not want to use Neon for local development, start PostgreSQL with Docker:

```powershell
cd C:\Users\Vishal\salary-management
docker compose up -d postgres
```

Use this local connection string in `backend/.env`:

```dotenv
DATABASE_URL=postgresql://salary_app:salary_app@localhost:5432/salary_management
```

Database Setup
==============

Run migrations:

```powershell
cd C:\Users\Vishal\salary-management\backend
uv run alembic upgrade head
```

Check current migration:

```powershell
uv run alembic current
```

Show migration history:

```powershell
uv run alembic history
```

Fixed Exchange-Rate Master Data
===============================

Employee salary seeding requires current FX rows for these currencies:

- INR
- USD
- GBP
- EUR
- CAD
- AUD

Insert the fixed MVP exchange-rate master rows:

```powershell
uv run python -m app.seed.exchange_rate_cli
```

This command is idempotent. It inserts missing current rows and leaves existing current rows alone.

Employee And Salary Seeding
===========================

Run employee and salary seeding only after migrations and FX master setup.

```powershell
uv run python -m app.seed.cli --count 10000 --random-seed 2026
```

What this command does:

- Reads names from `backend/data/first_names.txt`
- Reads names from `backend/data/last_names.txt`
- Generates full names by combining first and last names
- Generates 10,000 employee records
- Generates one current salary record for each employee
- Uses existing current FX rows from `exchange_rates`
- Inserts records in batches
- Writes one audit summary event
- Stops if employees already exist

Optional seed arguments:

```powershell
uv run python -m app.seed.cli `
  --count 10000 `
  --random-seed 2026 `
  --batch-size 1000 `
  --first-names-file data\first_names.txt `
  --last-names-file data\last_names.txt
```

Run The API
===========

Start the backend:

```powershell
cd C:\Users\Vishal\salary-management\backend
uv run uvicorn app.main:app --reload
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "environment": "development"
}
```

Testing
=======

Run all unit tests:

```powershell
cd C:\Users\Vishal\salary-management\backend
uv run pytest tests\unit
```

Run a specific unit test file:

```powershell
uv run pytest tests\unit\test_seed_generator.py
```

Run integration tests:

```powershell
$env:TEST_DATABASE_URL="postgresql://user:password@host/database?sslmode=require"
uv run pytest tests\integration
```

Integration tests use `TEST_DATABASE_URL`, not `DATABASE_URL`. This prevents tests from writing to
the normal development database by accident.

Run lint checks:

```powershell
uv run ruff check .
```

Apply safe lint fixes:

```powershell
uv run ruff check --fix .
```

Format code:

```powershell
uv run ruff format .
```

Recommended validation before commit:

```powershell
uv run ruff check .
uv run pytest tests\unit
```

Useful Development Commands
===========================

Create a new migration after changing SQLAlchemy models:

```powershell
uv run alembic revision --autogenerate -m "describe schema change"
```

Apply migrations:

```powershell
uv run alembic upgrade head
```

Rollback one migration:

```powershell
uv run alembic downgrade -1
```

Check ignored environment files:

```powershell
git check-ignore -v backend\.env
```

Security Notes
==============

- Never commit `backend/.env`.
- Rotate database credentials if a real connection string is pushed to Git history.
- Use `backend/.env.example` only for placeholders.
- Use `TEST_DATABASE_URL` for integration tests.
- Use `DATABASE_URL` for the actual application and seed commands.

Troubleshooting
===============

Missing `pydantic` import
-------------------------

Use the backend virtual environment created by uv:

```powershell
cd C:\Users\Vishal\salary-management\backend
uv sync --dev
uv run python -c "import pydantic; print(pydantic.__version__)"
```

In VS Code, select this interpreter:

```text
C:\Users\Vishal\salary-management\backend\.venv\Scripts\python.exe
```

`employees` table does not exist
--------------------------------

Run migrations:

```powershell
uv run alembic upgrade head
```

Missing exchange rates
----------------------

Seed the fixed FX master data:

```powershell
uv run python -m app.seed.exchange_rate_cli
```

Seed refuses to run
-------------------

The employee seed is initial-load only. It stops when employees already exist so it does not
overwrite real HR data.

Line-ending warnings on Windows
-------------------------------

The repository uses `.gitattributes` to keep source files on LF line endings. If warnings persist,
renormalize once:

```powershell
git add --renormalize .
```

Assessment Notes
================

This project is being built incrementally. Backend foundation and seeding are implemented first.
The frontend, user-facing CRUD screens, insights dashboard, deployment configuration, and video demo
will follow in later commits.
