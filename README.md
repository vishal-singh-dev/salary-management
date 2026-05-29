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
| Filter master-data schema | Implemented |
| Audit event schema | Implemented |
| Fixed FX master seed | Implemented |
| Filter master-data seed | Implemented |
| 10,000 employee seed | Implemented |
| Unit tests | Implemented |
| PostgreSQL integration test | Implemented |
| Next.js frontend | Implemented |
| Deployed app | Render deployment config implemented |
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
|   +-- plan.md
+-- frontend/
|   +-- app/
|   +-- components/
|   +-- lib/
|   +-- tests/
|   +-- .env.example
|   +-- package.json
+-- docker-compose.yml
+-- .gitattributes
+-- .gitignore
+-- README.md
+-- render.yaml
```

Backend Data Model
==================

The backend uses normalized tables:

| Table | Purpose |
| --- | --- |
| `employees` | Employee profile, title, department, country, and employment period |
| `employee_salary_records` | Effective-dated salary structure for each employee |
| `exchange_rates` | Current and historical currency-to-USD rates |
| `master_data` | Filter master values for country, department, and job title |
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

Docker Compose Setup
====================

The repository includes Docker setup for PostgreSQL, the FastAPI backend, the Next.js frontend,
database migrations, fixed master data, and the initial 10,000-employee demo seed.

Start the full stack:

```powershell
cd C:\Users\Vishal\salary-management
docker compose up --build
```

Open:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API docs: http://localhost:8000/docs
```

The backend container runs Alembic migrations, seeds exchange rates and filter master data, and
creates the 10,000 employee salary dataset when the employee table is empty. On later restarts, it
keeps existing employees and only ensures fixed master data is present.

Stop the stack:

```powershell
docker compose down
```

Remove the local PostgreSQL Docker volume:

```powershell
docker compose down -v
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

Filter Master Data
==================

Dashboard and employee filters use fixed master-data rows for:

- country
- department
- job title

Insert the fixed MVP filter master rows:

```powershell
uv run python -m app.seed.master_data_cli
```

This command is idempotent. It inserts values from `app.seed.generator` and leaves existing rows
alone.

Employee And Salary Seeding
===========================

Run employee and salary seeding only after migrations, FX master setup, and filter master setup.

Recommended one-command setup:

```powershell
uv run salary-seed-all --count 10000 --random-seed 2026
```

Equivalent module command:

```powershell
uv run python -m app.seed.all_cli --count 10000 --random-seed 2026
```

This combined command runs these steps in order:

- fixed FX master seed
- filter master-data seed
- employee and salary seed

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

Run The Frontend
================

Install frontend dependencies:

```powershell
cd C:\Users\Vishal\salary-management\frontend
npm install
```

Create frontend environment file:

```powershell
Copy-Item .env.example .env.local
```

Set the backend URL in `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```powershell
npm run dev
```

Open:

```text
http://localhost:3000
```

Frontend routes:

| Route | Purpose |
| --- | --- |
| `/dashboard` | Salary insights dashboard with filters |
| `/employees` | Employee list and pagination |
| `/employees/new` | Create employee with initial salary |
| `/employees/{id}` | Employee details and profile update |
| `/employees/{id}/salary` | Read-only current salary details |

Frontend validation commands:

```powershell
npm run test
npm run lint
npm run build
```

Deploy The Backend
==================

The backend is configured for Render using the root `render.yaml` file.

Render service configuration:

| Setting | Value |
| --- | --- |
| Service type | Web Service |
| Runtime | Python |
| Root directory | `backend` |
| Build command | `uv sync --frozen --no-dev` |
| Start command | `uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/health` |

Required Render environment variables:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | `[]` until the frontend URL exists |
| `SQL_ECHO` | `false` |
| `PYTHON_VERSION` | `3.12.7` |

Deployment steps:

1. Push the repository to GitHub.
2. Create a new Render Web Service from the GitHub repository.
3. Let Render detect the root `render.yaml` blueprint, or manually copy the settings above.
4. Add `DATABASE_URL` in Render as a secret environment variable.
5. Deploy the service.
6. Open the public health endpoint:

```text
https://<render-service-name>.onrender.com/health
```

Expected production response:

```json
{
  "status": "ok",
  "environment": "production"
}
```

Open the public API documentation:

```text
https://<render-service-name>.onrender.com/docs
```

The Render start command runs Alembic migrations before starting Uvicorn. This keeps the MVP
deployment simple and ensures the database schema is current after each deploy.

When the frontend is deployed, update `CORS_ORIGINS` to a JSON list containing the public frontend
origin, for example `["https://salary-management-ui.onrender.com"]`.

One-Time Production Seed
========================

Run production seed commands only after the first successful deployment and migration.

Use Render Shell from the deployed backend service:

```bash
uv run python -m app.seed.exchange_rate_cli
uv run python -m app.seed.master_data_cli
uv run python -m app.seed.cli --count 10000 --random-seed 2026
```

Seed notes:

- Run the FX master seed first.
- Run the filter master-data seed before employee seed.
- Run the employee seed once for the demo database.
- The employee seed refuses to run when employees already exist.
- Do not put seed commands in the Render start command because that would execute them on every
  deploy.

Post-deploy checks:

```text
GET /health
GET /docs
GET /api/v1/employees?limit=10&offset=0
GET /api/v1/analytics/salaries?country_code=IN&department=Engineering
GET /api/v1/analytics/salaries?currency_basis=usd&department=Engineering
```

API Reference
=============

Interactive OpenAPI documentation is available when the backend is running:

```text
http://127.0.0.1:8000/docs
```

API conventions:

- All request and response bodies use JSON.
- Dates use ISO format, for example `2026-01-01`.
- Money values are represented as decimal strings in API examples to avoid floating point ambiguity.
- Employee detail routes use the database UUID field named `id`.
- The HR-facing employee identifier is stored separately as `employee_id`.
- Mutating employee endpoints write an MVP audit event to `audit_events`.

Health
------

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Confirms the API process is running |

Employee CRUD
-------------

Base path:

```text
/api/v1/employees
```

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/employees` | Create an employee with one initial salary record |
| GET | `/api/v1/employees` | List employees with pagination |
| GET | `/api/v1/employees/{employee_uuid}` | Read one employee by database UUID |
| PATCH | `/api/v1/employees/{employee_uuid}` | Update employee profile fields |
| DELETE | `/api/v1/employees/{employee_uuid}` | Soft delete an employee by setting `to_date` |

Expected status codes:

| Operation | Success | Common validation or business errors |
| --- | --- | --- |
| Create employee | `201 Created` | `400 Bad Request` for missing FX rate, `409 Conflict` for duplicate `employee_id`, `422 Unprocessable Entity` for invalid payload |
| List employees | `200 OK` | `422 Unprocessable Entity` for invalid query parameters |
| Read employee | `200 OK` | `404 Not Found` when the UUID does not exist |
| Update employee | `200 OK` | `404 Not Found` when the UUID does not exist, `422 Unprocessable Entity` for invalid payload |
| Delete employee | `204 No Content` | `404 Not Found` when the UUID does not exist |

Create employee request:

```json
{
  "employee_id": "EMP-000001",
  "full_name": "Asha Patel",
  "title": "HR Manager",
  "department": "Human Resources",
  "country_code": "US",
  "from_date": "2026-01-01",
  "initial_salary": {
    "currency_code": "USD",
    "base_amount": "120000.00",
    "variable_amount": "10000.00",
    "hra_allowance_amount": "0.00",
    "pf_amount": "4800.00",
    "gratuity_amount": "0.00",
    "effective_from": "2026-01-01"
  }
}
```

Create employee notes:

- `employee_id` is the HR-facing identifier.
- API detail, update, and delete routes use the database UUID returned as `id`.
- The salary currency must have a current row in `exchange_rates`.
- Duplicate `employee_id` returns `409 Conflict`.

List employees query parameters:

| Parameter | Default | Notes |
| --- | --- | --- |
| `limit` | `50` | Minimum `1`, maximum `100` |
| `offset` | `0` | Zero-based row offset |
| `include_inactive` | `false` | When false, only employees where `to_date IS NULL` are returned |

Example list request:

```text
GET /api/v1/employees?limit=25&offset=0
```

Example list response:

```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000000",
      "employee_id": "EMP-000001",
      "full_name": "Asha Patel",
      "title": "HR Manager",
      "department": "Human Resources",
      "country_code": "US",
      "from_date": "2026-01-01",
      "to_date": null,
      "created_at": "2026-05-28T10:00:00Z",
      "current_salary": {
        "id": "00000000-0000-0000-0000-000000000001",
        "employee_id": "00000000-0000-0000-0000-000000000000",
        "currency_code": "USD",
        "base_amount": "120000.00",
        "variable_amount": "10000.00",
        "hra_allowance_amount": "0.00",
        "pf_amount": "4800.00",
        "gratuity_amount": "0.00",
        "effective_from": "2026-01-01",
        "effective_to": null,
        "exchange_rate_id": "00000000-0000-0000-0000-000000000002",
        "created_at": "2026-05-28T10:00:00Z"
      }
    }
  ],
  "total": 1,
  "limit": 25,
  "offset": 0
}
```

Update employee request:

```text
PATCH /api/v1/employees/00000000-0000-0000-0000-000000000000
```

```json
{
  "title": "Senior HR Manager",
  "department": "People Operations",
  "country_code": "US"
}
```

Update notes:

- Only employee profile fields are updated by this endpoint.
- Salary changes should be handled as separate effective-dated salary records in a later salary API.
- Fields omitted from the request are left unchanged.

Delete employee request:

```text
DELETE /api/v1/employees/00000000-0000-0000-0000-000000000000
```

Delete notes:

- Delete is a soft delete.
- The employee row remains in the database for auditability.
- The API sets `employees.to_date` and hides the employee from default list and analytics results.

Master Data
-----------

Base path:

```text
/api/v1/master-data
```

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/master-data` | List all dropdown master values |
| GET | `/api/v1/master-data?category=department` | List values for one category |

Categories:

- `country`
- `department`
- `job_title`

Example response:

```json
[
  {
    "category": "department",
    "description": "Engineering",
    "value": "ENG"
  }
]
```

Frontend usage:

- Use `description` as the dropdown label.
- Use `value` as the analytics query parameter value.

Salary Analytics
----------------

Base path:

```text
/api/v1/analytics/salaries
```

This endpoint returns base salary distribution metrics for current salary records.

Metrics returned:

- employee count
- minimum base salary
- maximum base salary
- mean base salary
- median base salary
- mode base salary

Query parameters:

| Parameter | Default | Notes |
| --- | --- | --- |
| `country_code` | `null` | Required when `currency_basis=local` |
| `department` | `null` | Optional department filter |
| `title` | `null` | Optional job title filter |
| `include_inactive` | `false` | When false, only employees where `to_date IS NULL` are included |
| `currency_basis` | `local` | `local` or `usd` |

Local currency example:

```text
GET /api/v1/analytics/salaries?country_code=IN&department=Engineering
```

Example response:

```json
{
  "filters": {
    "country_code": "IN",
    "department": "Engineering",
    "title": null,
    "include_inactive": false,
    "currency_basis": "local"
  },
  "employee_count": 420,
  "currency_code": "INR",
  "min_base_salary": "500000.00",
  "max_base_salary": "6000000.00",
  "mean_base_salary": "2185000.00",
  "median_base_salary": "2050000.00",
  "mode_base_salary": "1800000.00"
}
```

USD comparison example:

```text
GET /api/v1/analytics/salaries?currency_basis=usd&department=Engineering
```

Example empty response:

```json
{
  "filters": {
    "country_code": "IN",
    "department": "Legal",
    "title": null,
    "include_inactive": false,
    "currency_basis": "local"
  },
  "employee_count": 0,
  "currency_code": null,
  "min_base_salary": null,
  "max_base_salary": null,
  "mean_base_salary": null,
  "median_base_salary": null,
  "mode_base_salary": null
}
```

Analytics notes:

- Salary metrics use `employee_salary_records.base_amount`.
- Only current salary records are included, meaning `effective_to IS NULL`.
- Active employees are used by default, meaning `employees.to_date IS NULL`.
- `currency_basis=local` requires `country_code` to avoid mixing currencies.
- `currency_basis=usd` uses `base_amount * exchange_rates.rate_to_usd`.

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
The backend deployment configuration is now implemented. The frontend, user-facing CRUD screens,
insights dashboard, public deployment execution, and video demo will follow in later commits.
