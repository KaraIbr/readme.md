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
async def test_leads_lifecycle_flow(app: FastAPI) -> None:
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
                "qualification_score": 72,
            },
            headers=headers,
        )
        lead = create_response.json()
        document_response = await client.post(
            f"/api/v1/leads/{lead['id']}/documents",
            data={"title": "Project requirements"},
            files={
                "file": (
                    "requirements.pdf",
                    b"project document",
                    "application/pdf",
                )
            },
            headers=headers,
        )
        bill_response = await client.post(
            f"/api/v1/leads/{lead['id']}/electricity-bills",
            data={"title": "March CFE receipt"},
            files={"file": ("cfe-march.pdf", b"bill document", "application/pdf")},
            headers=headers,
        )
        interaction_response = await client.post(
            f"/api/v1/leads/{lead['id']}/interactions",
            json={
                "interaction_type": "NEGOTIATION",
                "title": "Initial negotiation",
                "notes": "Customer asked for phased delivery.",
                "interaction_date": "2026-06-15T16:30:00",
            },
            headers=headers,
        )

        stage_response = await client.post(
            f"/api/v1/leads/{lead['id']}/stage",
            json={"stage": "QUALIFYING"},
            headers=headers,
        )
        list_response = await client.get("/api/v1/leads/", headers=headers)
        documents_response = await client.get(
            f"/api/v1/leads/{lead['id']}/documents",
            headers=headers,
        )
        bills_response = await client.get(
            f"/api/v1/leads/{lead['id']}/electricity-bills",
            headers=headers,
        )
        interactions_response = await client.get(
            f"/api/v1/leads/{lead['id']}/interactions",
            headers=headers,
        )
        read_response = await client.get(
            f"/api/v1/leads/{lead['id']}",
            headers=headers,
        )
        update_response = await client.patch(
            f"/api/v1/leads/{lead['id']}",
            json={"notes": "Needs bill review", "qualification_score": 85},
            headers=headers,
        )
        close_response = await client.post(
            f"/api/v1/leads/{lead['id']}/close",
            json={"outcome": "LOST", "notes": "No response"},
            headers=headers,
        )
        close_won_response = await client.post(
            f"/api/v1/leads/{lead['id']}/close",
            json={"outcome": "WON"},
            headers=headers,
        )

    assert create_response.status_code == 201
    assert lead["current_stage"] == "NEW"
    assert lead["owner_id"]
    assert lead["contact_id"] == contact_id
    assert lead["interest_type"] == "Photovoltaic"

    assert document_response.status_code == 201
    assert document_response.json()["title"] == "Project requirements"
    assert bill_response.status_code == 201
    assert bill_response.json()["title"] == "March CFE receipt"
    assert interaction_response.status_code == 201
    assert interaction_response.json()["interaction_type"] == "NEGOTIATION"
    assert interaction_response.json()["interaction_date"] == "2026-06-15T16:30:00"

    assert stage_response.status_code == 200
    assert stage_response.json()["current_stage"] == "QUALIFYING"

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [lead["id"]]
    assert [item["id"] for item in documents_response.json()] == [document_response.json()["id"]]
    assert [item["id"] for item in bills_response.json()] == [bill_response.json()["id"]]
    assert [item["id"] for item in interactions_response.json()] == [
        interaction_response.json()["id"]
    ]

    assert read_response.status_code == 200
    assert read_response.json()["title"] == "Solar 8kW - Acme"

    assert update_response.status_code == 200
    assert update_response.json()["qualification_score"] == 85

    assert close_response.status_code == 200
    assert close_response.json()["current_stage"] == "CLOSED_LOST"
    assert close_response.json()["outcome"] == "LOST"
    assert close_response.json()["closed_at"] is not None

    assert close_won_response.status_code == 422


@pytest.mark.asyncio
async def test_leads_require_authentication(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/leads/")

    assert response.status_code == 401
