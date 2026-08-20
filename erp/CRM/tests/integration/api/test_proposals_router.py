from datetime import date, datetime, timedelta

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


def _proposal_payload(lead_id: int, name: str) -> dict[str, object]:
    return {
        "lead_id": lead_id,
        "name": name,
        "version": "1.0",
        "installation_address": {
            "address_line": "Av Solar 123",
            "city": "Monterrey",
            "state": "Nuevo Leon",
            "postal_code": "64000",
        },
        "tariff": "GDMTH",
        "contracted_demand": 120,
        "system_type": "PV",
        "total_price": "250000.00",
        "annual_savings": "78000.00",
        "currency": "MXN",
        "estimated_cost": "180000.00",
        "expected_profit": "70000.00",
        "submitted_at": datetime(2026, 6, 1, 12, 0).isoformat(),
        "valid_until": (date.today() + timedelta(days=30)).isoformat(),
        "pv_system": {
            "panel_count": 16,
            "panel_model": "Jinko 550",
            "panel_power": 550,
            "inverter_model": "INV-8K",
            "inverter_count": 1,
            "inverter_power": 8,
            "type_of_surface": "roof",
            "total_power_ac": 8,
            "system_size_kw": 8.5,
            "oversizing_kw": 0.5,
            "estimated_annual_kwh": 12800,
            "estimated_savings_kw": 7.2,
            "connection_mode": "interconnected",
            "cost_watt": "21.1765",
            "price_watt": "29.4118",
        },
    }


@pytest.mark.asyncio
async def test_proposals_win_flow(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _auth_headers(app)
        lead_id = await _create_lead(client, headers)

        create_winner_response = await client.post(
            "/api/v1/proposals/",
            json=_proposal_payload(lead_id, "Winner"),
            headers=headers,
        )
        winner = create_winner_response.json()
        create_sibling_response = await client.post(
            "/api/v1/proposals/",
            json=_proposal_payload(lead_id, "Sibling"),
            headers=headers,
        )
        sibling = create_sibling_response.json()

        sent_response = await client.post(
            f"/api/v1/proposals/{winner['id']}/stage",
            json={"stage": "SENT"},
            headers=headers,
        )
        list_response = await client.get("/api/v1/proposals/", headers=headers)
        update_response = await client.patch(
            f"/api/v1/proposals/{winner['id']}",
            json={"total_price": "245000.00"},
            headers=headers,
        )
        won_response = await client.post(
            f"/api/v1/proposals/{winner['id']}/won",
            headers=headers,
        )
        sibling_response = await client.get(
            f"/api/v1/proposals/{sibling['id']}",
            headers=headers,
        )
        lead_response = await client.get(f"/api/v1/leads/{lead_id}", headers=headers)

    assert create_winner_response.status_code == 201
    assert winner["current_stage"] == "DRAFT"
    assert winner["is_complete"] is True
    assert winner["installation_address"]["city"] == "Monterrey"
    assert winner["pv_system"]["inverter_model"] == "INV-8K"
    assert winner["pv_system"]["cost_watt"] == "21.1765"
    assert winner["pv_system"]["price_watt"] == "29.4118"
    assert create_sibling_response.status_code == 201

    assert sent_response.status_code == 200
    assert sent_response.json()["current_stage"] == "SENT"
    assert sent_response.json()["proposed_at"] is not None

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [
        sibling["id"],
        winner["id"],
    ]

    assert update_response.status_code == 200
    assert update_response.json()["total_price"] == "245000.00"

    assert won_response.status_code == 200
    assert won_response.json()["current_stage"] == "WON"
    assert sibling_response.json()["current_stage"] == "SUPERSEDED"
    assert lead_response.json()["current_stage"] == "CLOSED_WON"
    assert lead_response.json()["outcome"] == "WON"


@pytest.mark.asyncio
async def test_proposals_require_authentication(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/proposals/")

    assert response.status_code == 401
