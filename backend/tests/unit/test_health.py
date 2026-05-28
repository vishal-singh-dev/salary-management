from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    # Intent: the API exposes a simple readiness endpoint for deployment checks.
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "development"}
