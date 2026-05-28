from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.employees import router as employees_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="0.1.0")

    @application.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    application.include_router(analytics_router, prefix="/api/v1")
    application.include_router(employees_router, prefix="/api/v1")

    return application


app = create_app()
