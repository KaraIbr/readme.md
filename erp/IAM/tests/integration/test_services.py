"""Integration coverage for IAM service access."""

from httpx import AsyncClient


async def _create_user(
    client: AsyncClient,
    *,
    email: str,
    token: str | None = None,
) -> dict[str, object]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "password": "correct-password",
            "full_name": email.split("@", maxsplit=1)[0].title(),
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _login(client: AsyncClient, *, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "correct-password"},
    )
    assert response.status_code == 200, response.text
    return str(response.json()["access_token"])


async def test_service_access_can_be_granted_listed_and_revoked(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    user = await _create_user(
        client,
        email="crm.user@example.com",
        token=owner_access,
    )

    catalog_response = await client.get(
        "/api/v1/services/",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert catalog_response.status_code == 200
    assert catalog_response.json() == [
        {"key": "crm", "description": "Renewable-energy CRM service"},
    ]

    grant_response = await client.post(
        f"/api/v1/services/users/{user['id']}/access",
        json={"service_key": "CRM"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert grant_response.status_code == 201
    assert grant_response.json()["service_key"] == "crm"
    assert grant_response.json()["is_active"] is True

    list_response = await client.get(
        f"/api/v1/services/users/{user['id']}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert list_response.status_code == 200
    assert list_response.json()[0]["service_key"] == "crm"
    assert list_response.json()[0]["is_active"] is True

    revoke_response = await client.delete(
        f"/api/v1/services/users/{user['id']}/access/crm",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert revoke_response.status_code == 204

    after_revoke = await client.get(
        f"/api/v1/services/users/{user['id']}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert after_revoke.status_code == 200
    assert after_revoke.json()[0]["service_key"] == "crm"
    assert after_revoke.json()[0]["is_active"] is False


async def test_service_access_requires_iam_service_permissions(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    user = await _create_user(
        client,
        email="limited@example.com",
        token=owner_access,
    )
    limited_access = await _login(client, email="limited@example.com")

    denied_response = await client.get(
        f"/api/v1/services/users/{user['id']}",
        headers={"Authorization": f"Bearer {limited_access}"},
    )
    assert denied_response.status_code == 403

    unknown_response = await client.post(
        f"/api/v1/services/users/{user['id']}/access",
        json={"service_key": "billing"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert unknown_response.status_code == 422
