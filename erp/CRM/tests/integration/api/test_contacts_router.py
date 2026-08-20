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


@pytest.mark.asyncio
async def test_contacts_promoters_and_company_people_flow(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _auth_headers(app)

        create_promoter = await client.post(
            "/api/v1/contacts/promoters",
            json={"name": "Referral Partner", "phone": "+52 81 5555 0000"},
            headers=headers,
        )
        promoter = create_promoter.json()

        create_company = await client.post(
            "/api/v1/contacts/",
            json={
                "type": "COMPANY",
                "name": "Acme Solar",
                "promoter_id": promoter["id"],
                "city": "Monterrey",
                "industry": "Manufacturing",
                "company_people": [
                    {
                        "name": "Jane Manager",
                        "phone": "+52 81 5555 0101",
                        "email": "JANE@ACME.example",
                        "position": "Facility Manager",
                    }
                ],
            },
            headers=headers,
        )
        company = create_company.json()

        list_people = await client.get(
            f"/api/v1/contacts/{company['id']}/people",
            headers=headers,
        )
        existing_person = list_people.json()[0]
        add_person = await client.post(
            f"/api/v1/contacts/{company['id']}/people",
            json={
                "name": "John CFO",
                "phone": "+52 81 5555 0202",
                "position": "CFO",
            },
            headers=headers,
        )
        added_person = add_person.json()
        update_person = await client.patch(
            f"/api/v1/contacts/{company['id']}/people/{added_person['id']}",
            json={"position": "Finance Director"},
            headers=headers,
        )
        delete_person = await client.delete(
            f"/api/v1/contacts/{company['id']}/people/{existing_person['id']}",
            headers=headers,
        )
        delete_last_person = await client.delete(
            f"/api/v1/contacts/{company['id']}/people/{added_person['id']}",
            headers=headers,
        )

        create_person = await client.post(
            "/api/v1/contacts/",
            json={
                "type": "INDIVIDUAL",
                "name": "Carlos Rivera",
                "email": "CARLOS.RIVERA@example.com",
                "phone": "+52 55 5555 0202",
                "promoter_id": promoter["id"],
                "city": "Ciudad de Mexico",
            },
            headers=headers,
        )
        person = create_person.json()

        list_response = await client.get("/api/v1/contacts/", headers=headers)
        read_response = await client.get(
            f"/api/v1/contacts/{person['id']}",
            headers=headers,
        )
        update_response = await client.patch(
            f"/api/v1/contacts/{person['id']}",
            json={"phone": "+52 55 1234 5678"},
            headers=headers,
        )
        delete_response = await client.delete(
            f"/api/v1/contacts/{person['id']}",
            headers=headers,
        )
        read_deleted_response = await client.get(
            f"/api/v1/contacts/{person['id']}",
            headers=headers,
        )
        delete_linked_promoter = await client.delete(
            f"/api/v1/contacts/promoters/{promoter['id']}",
            headers=headers,
        )

    assert create_promoter.status_code == 201
    assert promoter["name"] == "Referral Partner"

    assert create_company.status_code == 201
    assert company["promoter_id"] == promoter["id"]
    assert company["email"] is None
    assert company["phone"] is None

    assert list_people.status_code == 200
    assert existing_person["email"] == "jane@acme.example"
    assert add_person.status_code == 201
    assert update_person.status_code == 200
    assert update_person.json()["position"] == "Finance Director"
    assert delete_person.status_code == 204
    assert delete_last_person.status_code == 422

    assert create_person.status_code == 201
    assert person["email"] == "carlos.rivera@example.com"

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [
        person["id"],
        company["id"],
    ]

    assert read_response.status_code == 200
    assert read_response.json()["name"] == "Carlos Rivera"

    assert update_response.status_code == 200
    assert update_response.json()["phone"] == "+52 55 1234 5678"

    assert delete_response.status_code == 204
    assert read_deleted_response.status_code == 404
    assert delete_linked_promoter.status_code == 422


@pytest.mark.asyncio
async def test_contacts_require_authentication(app: FastAPI) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/contacts/")

    assert response.status_code == 401
