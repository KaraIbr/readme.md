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


async def _contact_id(app: FastAPI, headers: dict[str, str]) -> int:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        promoter_resp = await client.post(
            "/api/v1/contacts/promoters",
            json={"name": "Partner", "phone": "+52 81 5555 0000"},
            headers=headers,
        )
        contact_resp = await client.post(
            "/api/v1/contacts/",
            json={
                "type": "COMPANY",
                "name": "Acme Solar",
                "promoter_id": promoter_resp.json()["id"],
                "industry": "Manufacturing",
                "company_people": [
                    {"name": "Jane", "phone": "+52 81 5555 0101", "position": "Manager"}
                ],
            },
            headers=headers,
        )
        return contact_resp.json()["id"]


@pytest.mark.asyncio
async def test_opportunities_lifecycle_flow(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        _, headers = await auth_headers(app)
        contact_id = await _contact_id(app, headers)

        create_response = await client.post(
            "/api/v1/opportunities/",
            json={
                "name": "Solar Project - Acme",
                "contact_id": contact_id,
                "value": 50000.0,
                "currency": "MXN",
            },
            headers=headers,
        )
        opp = create_response.json()

        list_response = await client.get("/api/v1/opportunities/", headers=headers)
        read_response = await client.get(f"/api/v1/opportunities/{opp['id']}", headers=headers)
        update_response = await client.patch(
            f"/api/v1/opportunities/{opp['id']}",
            json={"name": "Updated Project"},
            headers=headers,
        )
        stage_response = await client.post(
            f"/api/v1/opportunities/{opp['id']}/stage",
            json={"stage": "QUALIFIED"},
            headers=headers,
        )
        close_response = await client.post(
            f"/api/v1/opportunities/{opp['id']}/close",
            json={"outcome": "LOST", "notes": "No budget"},
            headers=headers,
        )

    assert create_response.status_code == 201
    assert opp["current_stage"] == "PROSPECTING"
    assert opp["value"] == 50000.0

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [opp["id"]]

    assert read_response.status_code == 200
    assert read_response.json()["name"] == "Solar Project - Acme"

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Project"

    assert stage_response.status_code == 200
    assert stage_response.json()["current_stage"] == "QUALIFIED"

    assert close_response.status_code == 200
    assert close_response.json()["current_stage"] == "CLOSED_LOST"
    assert close_response.json()["closed_at"] is not None


@pytest.mark.asyncio
async def test_opportunities_require_authentication(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/opportunities/")

    assert response.status_code == 401
