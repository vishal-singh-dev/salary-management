from os import environ

environ.setdefault(
    "DATABASE_URL",
    "postgresql://test:test@localhost:5432/salary_test?sslmode=require",
)
