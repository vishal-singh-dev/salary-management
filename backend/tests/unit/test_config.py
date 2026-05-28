from app.core.config import Settings


def test_postgres_connection() -> None:
    # Intent: Neon-style Postgres URLs should use the psycopg SQLAlchemy driver.
    settings = Settings(
        database_url=(
            "postgresql://user:password@ep-test-pooler.us-east-2.aws.neon.tech/"
            "neondb?sslmode=require"
        )
    )

    assert settings.sqlalchemy_database_url.startswith("postgresql+psycopg://")
    assert settings.environment == "development"
