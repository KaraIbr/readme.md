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
from core.security import create_access_token
from fastapi import FastAPI
from helpers import create_iam_user, grant_iam_crm_service_access
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr


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


async def _register_and_login(
    app: FastAPI,
    client: AsyncClient,
    *,
    email: str,
    creator_headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str]]:
    async with app.state.session_factory() as session:
        user = await create_iam_user(
            session,
            email=email,
            crm_service_access=False,
        )
        assert user.id is not None
        await grant_iam_crm_service_access(session, user_id=user.id)
        user_id = user.id

    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    if creator_headers is None:
        await client.post(
            f"/api/v1/permissions/users/{user_id}/role",
            json={"role": "admin"},
            headers=headers,
        )
    return user_id, headers


async def _create_sales_lead(
    client: AsyncClient,
    headers: dict[str, str],
) -> tuple[int, int]:
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
    return contact_response.json()["id"], lead_response.json()["id"]


@pytest.mark.asyncio
async def test_sales_assignment_and_tech_proposal_scope(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        _admin_id, admin_headers = await _register_and_login(
            app,
            client,
            email="admin@example.com",
        )
        sales_a_id, sales_a_headers = await _register_and_login(
            app,
            client,
            email="sales-a@example.com",
            creator_headers=admin_headers,
        )
        sales_b_id, sales_b_headers = await _register_and_login(
            app,
            client,
            email="sales-b@example.com",
            creator_headers=admin_headers,
        )
        tech_id, tech_headers = await _register_and_login(
            app,
            client,
            email="tech@example.com",
            creator_headers=admin_headers,
        )
        sales_a_role_response = await client.post(
            f"/api/v1/permissions/users/{sales_a_id}/role",
            json={"role": "sales"},
            headers=admin_headers,
        )
        sales_b_role_response = await client.post(
            f"/api/v1/permissions/users/{sales_b_id}/role",
            json={"role": "sales"},
            headers=admin_headers,
        )
        role_response = await client.post(
            f"/api/v1/permissions/users/{tech_id}/role",
            json={"role": "tech"},
            headers=admin_headers,
        )

        contact_id, lead_id = await _create_sales_lead(client, sales_a_headers)
        assignment_response = await client.post(
            f"/api/v1/leads/{lead_id}/assignment",
            json={"user_id": sales_b_id},
            headers=sales_a_headers,
        )
        previous_sales_lead_response = await client.get(
            f"/api/v1/leads/{lead_id}",
            headers=sales_a_headers,
        )
        previous_sales_contact_response = await client.get(
            f"/api/v1/contacts/{contact_id}",
            headers=sales_a_headers,
        )
        current_sales_lead_response = await client.get(
            f"/api/v1/leads/{lead_id}",
            headers=sales_b_headers,
        )
        current_sales_contact_response = await client.get(
            f"/api/v1/contacts/{contact_id}",
            headers=sales_b_headers,
        )
        await client.post(
            f"/api/v1/leads/{lead_id}/interactions",
            json={
                "interaction_type": "NEGOTIATION",
                "title": "Initial negotiation",
                "notes": "Customer asked for phased delivery.",
                "interaction_date": "2026-06-15T16:30:00",
            },
            headers=sales_b_headers,
        )

        proposal_response = await client.post(
            "/api/v1/proposals/",
            json={
                "lead_id": lead_id,
                "name": "Acme technical option",
                "total_price": "250000.00",
            },
            headers=admin_headers,
        )
        proposal_id = proposal_response.json()["id"]
        proposal_assignment_response = await client.post(
            f"/api/v1/proposals/{proposal_id}/assignments",
            json={"user_id": tech_id},
            headers=admin_headers,
        )
        tech_lead_response = await client.get(
            f"/api/v1/leads/{lead_id}",
            headers=tech_headers,
        )
        tech_contact_response = await client.get(
            f"/api/v1/contacts/{contact_id}",
            headers=tech_headers,
        )
        tech_interactions_response = await client.get(
            f"/api/v1/leads/{lead_id}/interactions",
            headers=tech_headers,
        )
        tech_proposal_update_response = await client.patch(
            f"/api/v1/proposals/{proposal_id}",
            json={"name": "Acme technical option updated"},
            headers=tech_headers,
        )
        tech_price_update_response = await client.patch(
            f"/api/v1/proposals/{proposal_id}",
            json={"total_price": "245000.00"},
            headers=tech_headers,
        )

    assert sales_a_role_response.status_code == 200
    assert sales_b_role_response.status_code == 200
    assert role_response.status_code == 200
    assert role_response.json()["role"] == "tech"
    assert assignment_response.status_code == 200
    assert assignment_response.json() == {"lead_id": lead_id, "user_id": sales_b_id}
    assert previous_sales_lead_response.status_code == 403
    assert previous_sales_contact_response.status_code == 403
    assert current_sales_lead_response.status_code == 200
    assert current_sales_contact_response.status_code == 200

    assert proposal_response.status_code == 201
    assert proposal_assignment_response.status_code == 200
    assert proposal_assignment_response.json() == {
        "proposal_id": proposal_id,
        "user_id": tech_id,
    }
    assert tech_lead_response.status_code == 200
    assert tech_contact_response.status_code == 200
    assert tech_interactions_response.status_code == 403
    assert tech_proposal_update_response.status_code == 200
    assert tech_proposal_update_response.json()["name"] == "Acme technical option updated"
    assert tech_price_update_response.status_code == 403
    assert sales_a_id != sales_b_id
