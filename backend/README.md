# Salary Management API

## Local setup

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

## Checks

```powershell
uv run ruff check .
uv run pytest
```
