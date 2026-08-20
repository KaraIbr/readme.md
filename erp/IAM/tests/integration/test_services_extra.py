"""Additional integration coverage for IAM service access management."""

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


async def test_grant_reactivates_previously_revoked_access(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    user = await _create_user(
        client,
        email="crm.user@example.com",
        token=owner_access,
    )

    grant = await client.post(
        f"/api/v1/services/users/{user['id']}/access",
        json={"service_key": "crm"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert grant.status_code == 201
    assert grant.json()["is_active"] is True

    revoke = await client.delete(
        f"/api/v1/services/users/{user['id']}/access/crm",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert revoke.status_code == 204

    after_revoke = await client.get(
        f"/api/v1/services/users/{user['id']}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert after_revoke.status_code == 200
    assert after_revoke.json()[0]["is_active"] is False
    row_id = after_revoke.json()[0]["id"]

    regrant = await client.post(
        f"/api/v1/services/users/{user['id']}/access",
        json={"service_key": "crm"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert regrant.status_code == 201
    assert regrant.json()["is_active"] is True
    assert regrant.json()["id"] == row_id


async def test_list_access_for_user_without_grants_is_empty(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    user = await _create_user(
        client,
        email="crm.user@example.com",
        token=owner_access,
    )

    response = await client.get(
        f"/api/v1/services/users/{user['id']}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_grant_to_inactive_user_is_rejected(client: AsyncClient) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    user = await _create_user(
        client,
        email="crm.user@example.com",
        token=owner_access,
    )

    deactivated = await client.post(
        f"/api/v1/users/{user['id']}/deactivate",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert deactivated.status_code == 200

    grant = await client.post(
        f"/api/v1/services/users/{user['id']}/access",
        json={"service_key": "crm"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert grant.status_code == 403

    revoke = await client.delete(
        f"/api/v1/services/users/{user['id']}/access/crm",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert revoke.status_code == 403

    listing = await client.get(
        f"/api/v1/services/users/{user['id']}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert listing.status_code == 403
    assert "inactive" in listing.json()["error"]["message"]


async def test_revoke_unknown_service_returns_error(client: AsyncClient) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    user = await _create_user(
        client,
        email="crm.user@example.com",
        token=owner_access,
    )

    response = await client.delete(
        f"/api/v1/services/users/{user['id']}/access/billing",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_operation"


async def test_grant_service_access_permission_required(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    user = await _create_user(
        client,
        email="crm.user@example.com",
        token=owner_access,
    )
    await _create_user(client, email="limited@example.com", token=owner_access)
    limited_access = await _login(client, email="limited@example.com")

    denied = await client.post(
        f"/api/v1/services/users/{user['id']}/access",
        json={"service_key": "crm"},
        headers={"Authorization": f"Bearer {limited_access}"},
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "authorization_failed"
