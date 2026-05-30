from collections.abc import Generator

from fastapi.testclient import TestClient

from app.api.dependencies import get_session
from app.main import create_app


class _ScalarResult:
    def all(self) -> list[str]:
        return ["EMP-000001", "EMP-000010"]


class _Session:
    def scalars(self, _statement: object) -> _ScalarResult:
        return _ScalarResult()


def test_employee_next_id_route_is_not_captured_by_uuid_path() -> None:
    # Intent: static next-id route must resolve before employee UUID detail routes.
    app = create_app()

    def override_session() -> Generator[_Session, None, None]:
        yield _Session()

    app.dependency_overrides[get_session] = override_session
    response = TestClient(app).get("/api/v1/employees/next-id")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"employee_id": "EMP-000011"}
