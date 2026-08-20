from datetime import datetime

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
    monkeypatch.setenv("DOCUMENT_STORAGE_PATH", str(tmp_path / "uploads"))
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


async def _auth_headers(app: FastAPI) -> dict[str, str]:
    _user_id, headers = await auth_headers(app)
    return headers


async def _create_lead(client: AsyncClient, headers: dict[str, str]) -> int:
    promoter_response = await client.post(
        "/api/v1/contacts/promoters",
        json={"name": "Referral Partner", "phone": "+52 81 5555 0000"},
        headers=headers,
    )
    contact_response = await client.post(
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
    lead_response = await client.post(
        "/api/v1/leads/",
        json={
            "contact_id": contact_response.json()["id"],
            "title": "Solar 8kW - Acme",
            "interest_type": "Photovoltaic",
        },
        headers=headers,
    )
    return lead_response.json()["id"]


@pytest.mark.asyncio
async def test_technical_visit_and_proposal_link_flow(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _auth_headers(app)
        lead_id = await _create_lead(client, headers)

        requirement_response = await client.post(
            f"/api/v1/leads/{lead_id}/technical-visit-requirement",
            json={"requirement": "REQUIRED"},
            headers=headers,
        )
        create_visit_response = await client.post(
            f"/api/v1/leads/{lead_id}/technical-visits",
            json={
                "scheduled_at": datetime(2026, 6, 20, 16, 30).isoformat(),
                "receiver_name": "Jane Manager",
                "receiver_phone": "+52 81 5555 0101",
                "notes": "Access through loading dock.",
                "assignees": [{"name": "Engineer One"}],
            },
            headers=headers,
        )
        visit = create_visit_response.json()
        attachment_response = await client.post(
            f"/api/v1/technical-visits/{visit['id']}/attachments",
            data={"title": "Inspection report", "file_kind": "DOCUMENT"},
            files={
                "file": (
                    "inspection.pdf",
                    b"technical visit report",
                    "application/pdf",
                )
            },
            headers=headers,
        )
        complete_response = await client.post(
            f"/api/v1/technical-visits/{visit['id']}/complete",
            headers=headers,
        )
        list_visits_response = await client.get(
            f"/api/v1/leads/{lead_id}/technical-visits",
            headers=headers,
        )
        proposal_response = await client.post(
            "/api/v1/proposals/",
            json={"lead_id": lead_id, "name": "Acme PV v1"},
            headers=headers,
        )
        proposal = proposal_response.json()
        link_response = await client.post(
            f"/api/v1/proposals/{proposal['id']}/technical-visits",
            json={
                "technical_visit_id": visit["id"],
                "relationship_type": "BASED_ON",
                "notes": "Proposal version uses field measurements.",
            },
            headers=headers,
        )
        links_response = await client.get(
            f"/api/v1/proposals/{proposal['id']}/technical-visits",
            headers=headers,
        )
        unauthenticated_response = await client.get("/api/v1/technical-visits/")

    assert requirement_response.status_code == 200
    assert requirement_response.json()["technical_visit_requirement"] == "REQUIRED"

    assert create_visit_response.status_code == 201
    assert visit["status"] == "SCHEDULED"
    assert visit["receiver_name"] == "Jane Manager"
    assert [item["name"] for item in visit["assignees"]] == ["Engineer One"]

    assert attachment_response.status_code == 201
    assert attachment_response.json()["file_kind"] == "DOCUMENT"

    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "COMPLETED"
    assert complete_response.json()["completed_at"] is not None

    assert list_visits_response.status_code == 200
    assert [item["id"] for item in list_visits_response.json()] == [visit["id"]]

    assert proposal_response.status_code == 201
    assert link_response.status_code == 201
    assert link_response.json()["technical_visit_id"] == visit["id"]
    assert links_response.status_code == 200
    assert [item["id"] for item in links_response.json()] == [link_response.json()["id"]]
    assert unauthenticated_response.status_code == 401
