import pytest
from api.dependencies import get_db_session
from api.v1.router import api_v1
from core.config import Settings, get_settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from core.exceptions import register_exception_handlers
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from integration.api.helpers import auth_headers


@pytest.fixture()
async def app(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "testing")
    get_settings.cache_clear()
    settings = Settings(
        environment="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key=SecretStr("super-secret-for-tests"),
    )
    engine = build_async_engine(settings)
    await create_all(engine)
    session_factory = build_session_factory(engine)

    test_app = FastAPI()
    test_app.state.session_factory = session_factory
    register_exception_handlers(test_app)
    test_app.include_router(api_v1)

    async def override_session():
        async with session_factory() as session:
            yield session

    test_app.dependency_overrides[get_db_session] = override_session

    try:
        yield test_app
    finally:
        await drop_all(engine)
        await engine.dispose()
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_activities_lifecycle_flow(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        _, headers = await auth_headers(app)

        create_response = await client.post(
            "/api/v1/activities/",
            json={
                "activity_type": "CALL",
                "title": "Follow-up call",
                "description": "Check proposal status",
            },
            headers=headers,
        )
        activity = create_response.json()

        list_response = await client.get("/api/v1/activities/", headers=headers)

        read_response = await client.get(f"/api/v1/activities/{activity['id']}", headers=headers)

        update_response = await client.patch(
            f"/api/v1/activities/{activity['id']}",
            json={"title": "Updated call", "description": "Updated notes"},
            headers=headers,
        )

        complete_response = await client.post(
            f"/api/v1/activities/{activity['id']}/complete",
            headers=headers,
        )

    assert create_response.status_code == 201
    assert activity["activity_type"] == "CALL"
    assert activity["title"] == "Follow-up call"
    assert activity["created_by"]

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [activity["id"]]

    assert read_response.status_code == 200
    assert read_response.json()["title"] == "Follow-up call"

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated call"
    assert update_response.json()["description"] == "Updated notes"

    assert complete_response.status_code == 200
    assert complete_response.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_activities_require_authentication(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/activities/")

    assert response.status_code == 401
