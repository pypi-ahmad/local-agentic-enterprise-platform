import os

import pytest

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_laep.db"
os.environ["BREAK_GLASS_PASSWORD"] = "change-me-now"

pytestmark = pytest.mark.skip(
    reason="Integration tests require async DB driver capabilities not available in this sandbox"
)


def test_liveness_endpoint() -> None:
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_local_login_and_memory_cycle() -> None:
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "local-admin", "password": "change-me-now"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    write = client.post(
        "/api/v1/memory/",
        json={"scope": "test", "key": "sample", "value": {"ok": True}},
        headers=headers,
    )
    assert write.status_code == 200

    read = client.get("/api/v1/memory/", headers=headers)
    assert read.status_code == 200
    assert len(read.json()) >= 1
