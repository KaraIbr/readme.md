from datetime import date, datetime, timedelta

import pytest
from agent.providers.base import LLMProvider
from agent.providers.factory import get_llm_provider
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
from langchain_core.messages import AIMessage
from pydantic import SecretStr
from unit.agent.helpers import ToolAwareFakeChatModel

from integration.api.helpers import auth_headers


class FakeProvider(LLMProvider):
    def chat_model(self) -> ToolAwareFakeChatModel:
        return ToolAwareFakeChatModel(
            responses=[AIMessage(content="No encontré registros suficientes para responder.")]
        )


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

    def override_provider() -> FakeProvider:
        return FakeProvider()

    test_app.dependency_overrides[get_db_session] = override_session
    test_app.dependency_overrides[get_llm_provider] = override_provider

    try:
        yield test_app
    finally:
        await drop_all(engine)
        await engine.dispose()


async def _auth_headers(app: FastAPI) -> dict[str, str]:
    _user_id, headers = await auth_headers(app)
    return headers


async def _seed_proposal(client: AsyncClient, headers: dict[str, str]) -> None:
    promoter_response = await client.post(
        "/api/v1/contacts/promoters",
        json={"name": "Referral Partner", "phone": "+52 81 5555 0000"},
        headers=headers,
    )
    contact_response = await client.post(
        "/api/v1/contacts/",
        json={
            "type": "COMPANY",
            "name": "Acme Manufacturing",
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
    await client.post(
        "/api/v1/proposals/",
        json={
            "lead_id": lead_response.json()["id"],
            "name": "Acme technical option",
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
        },
        headers=headers,
    )


@pytest.mark.asyncio
async def test_agent_chat_requires_authentication(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agent/chat",
            json={"message": "Qué propuestas hay?"},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_agent_chat_endpoint_returns_agent_response(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _auth_headers(app)
        await _seed_proposal(client, headers)
        response = await client.post(
            "/api/v1/agent/chat",
            json={"message": "Qué inversor tiene Acme?"},
            headers=headers,
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "No encontré registros suficientes para responder."
