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
async def app(monkeypatch):
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


async def _auth_headers(app: FastAPI) -> dict[str, str]:
    _user_id, headers = await auth_headers(app)
    return headers


async def _create_contact(client: AsyncClient, headers: dict[str, str]) -> int:
    promoter_response = await client.post(
        "/api/v1/contacts/promoters",
        json={"name": "Referral Partner", "phone": "+52 81 5555 0000"},
        headers=headers,
    )
    response = await client.post(
        "/api/v1/contacts/",
        json={
            "type": "COMPANY",
            "name": "Acme Solar",
            "promoter_id": promoter_response.json()["id"],
            "industry": "Manufacturing",
            "company_people": [
                {
                    "name": "Jane Manager",
                    "phone": "+52 81 5555 0101",
                    "position": "Facility Manager",
                }
            ],
        },
        headers=headers,
    )
    return response.json()["id"]


@pytest.mark.asyncio
async def test_pipeline_transition_history_endpoint(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _auth_headers(app)
        contact_id = await _create_contact(client, headers)
        create_response = await client.post(
            "/api/v1/leads/",
            json={
                "contact_id": contact_id,
                "title": "Solar 8kW - Acme",
                "interest_type": "Photovoltaic",
            },
            headers=headers,
        )
        lead_id = create_response.json()["id"]
        await client.post(
            f"/api/v1/leads/{lead_id}/stage",
            json={"stage": "QUALIFYING"},
            headers=headers,
        )

        history_response = await client.get(
            "/api/v1/pipeline/transitions",
            params={"entity_type": "lead", "entity_id": lead_id},
            headers=headers,
        )
        summary_response = await client.get(
            f"/api/v1/pipeline/summary/lead/{lead_id}",
            headers=headers,
        )
        unauthenticated_response = await client.get("/api/v1/pipeline/transitions")

    assert history_response.status_code == 200
    assert [
        (item["from_stage"], item["to_stage"]) for item in reversed(history_response.json())
    ] == [(None, "NEW"), ("NEW", "QUALIFYING")]
    assert summary_response.status_code == 200
    assert summary_response.json()["current_stage"] == "QUALIFYING"
    assert summary_response.json()["transition_count"] == 2
    assert unauthenticated_response.status_code == 401
