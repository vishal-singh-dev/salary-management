from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.employees import router as employees_router
from app.api.master_data import router as master_data_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="0.1.0")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    application.include_router(analytics_router, prefix="/api/v1")
    application.include_router(employees_router, prefix="/api/v1")
    application.include_router(master_data_router, prefix="/api/v1")

    return application


app = create_app()
