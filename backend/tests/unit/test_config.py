from app.core.config import Settings


def test_settings_normalizes_neon_url_for_psycopg_driver() -> None:
    settings = Settings(
        database_url=(
            "postgresql://user:password@ep-test-pooler.us-east-2.aws.neon.tech/"
            "neondb?sslmode=require"
        )
    )

    assert settings.sqlalchemy_database_url.startswith("postgresql+psycopg://")
    assert settings.environment == "development"
