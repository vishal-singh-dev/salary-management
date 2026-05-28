Salary Management API
=====================

Backend service for the salary management project. The root README contains the complete project
setup guide. This file keeps backend-only commands close to the API source.

Local Setup
===========

```powershell
uv sync --dev
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

Create a Neon database and set its connection string in `.env` as `DATABASE_URL`. The application
accepts Neon's standard pooled URL, for example:

```dotenv
DATABASE_URL=postgresql://username:password@ep-example-pooler.region.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

The configuration layer selects SQLAlchemy's `psycopg` driver internally. Keep the real Neon
credential only in `.env`; it is excluded from source control.

Database Setup
==============

The employee seed is an initial-load operation. Apply migrations and populate fixed current
`exchange_rates` records first:

```powershell
uv run alembic upgrade head
uv run python -m app.seed.exchange_rate_cli
```

Then run employee and salary seeding against an empty employees table:

```powershell
uv run python -m app.seed.cli --count 10000 --random-seed 2026
```

The command combines names from `data/first_names.txt` and `data/last_names.txt`, generates one
current salary record per employee, inserts data in batches, and records one audit summary event.
It aborts instead of changing data when employees already exist.

Checks
======

```powershell
uv run ruff check .
uv run pytest
```

Integration tests require a disposable PostgreSQL database and never use `DATABASE_URL` by
default:

```powershell
$env:TEST_DATABASE_URL="postgresql://user:password@localhost:5432/salary_management_test"
uv run pytest tests/integration
```
