"""Integration coverage for IAM users, auth, and permission guardrails."""

from httpx import AsyncClient


async def _create_user(
    client: AsyncClient,
    *,
    email: str,
    password: str = "correct-password",
    token: str | None = None,
) -> dict[str, object]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "password": password,
            "full_name": email.split("@", maxsplit=1)[0].title(),
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _login(
    client: AsyncClient,
    *,
    email: str,
    password: str = "correct-password",
) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["token_type"] == "bearer"
    return payload


async def test_bootstrap_user_can_login_refresh_and_read_permissions(
    client: AsyncClient,
) -> None:
    owner = await _create_user(client, email="owner@example.com")
    owner_id = int(owner["id"])

    token_pair = await _login(client, email="owner@example.com")
    access_token = token_pair["access_token"]

    me_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "owner@example.com"

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_pair["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["token_type"] == "bearer"

    permissions_response = await client.get(
        f"/api/v1/permissions/users/{owner_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert permissions_response.status_code == 200
    effective = permissions_response.json()["effective_permissions"]
    assert "iam.users.create" in effective
    assert "iam.permissions.manage" in effective
    assert "iam.services.manage" in effective


async def test_user_creation_requires_permission_after_bootstrap(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_tokens = await _login(client, email="owner@example.com")
    owner_access = owner_tokens["access_token"]

    anonymous_response = await client.post(
        "/api/v1/users/",
        json={
            "email": "anonymous@example.com",
            "password": "correct-password",
            "full_name": "Anonymous User",
        },
    )
    assert anonymous_response.status_code == 401

    limited_user = await _create_user(
        client,
        email="limited@example.com",
        token=owner_access,
    )
    limited_tokens = await _login(client, email="limited@example.com")

    denied_response = await client.post(
        "/api/v1/users/",
        json={
            "email": "denied@example.com",
            "password": "correct-password",
            "full_name": "Denied User",
        },
        headers={"Authorization": f"Bearer {limited_tokens['access_token']}"},
    )
    assert denied_response.status_code == 403

    grant_response = await client.patch(
        f"/api/v1/permissions/users/{limited_user['id']}",
        json={"grant": ["iam.users.create"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert grant_response.status_code == 200
    assert "iam.users.create" in grant_response.json()["effective_permissions"]

    allowed_response = await client.post(
        "/api/v1/users/",
        json={
            "email": "allowed@example.com",
            "password": "correct-password",
            "full_name": "Allowed User",
        },
        headers={"Authorization": f"Bearer {limited_tokens['access_token']}"},
    )
    assert allowed_response.status_code == 201


async def test_permission_management_guardrails(
    client: AsyncClient,
) -> None:
    owner = await _create_user(client, email="owner@example.com")
    owner_tokens = await _login(client, email="owner@example.com")
    owner_access = owner_tokens["access_token"]

    self_change = await client.patch(
        f"/api/v1/permissions/users/{owner['id']}",
        json={"grant": ["iam.users.create"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert self_change.status_code == 403

    limited_user = await _create_user(
        client,
        email="limited@example.com",
        token=owner_access,
    )
    target_user = await _create_user(
        client,
        email="target@example.com",
        token=owner_access,
    )
    grant_manage = await client.patch(
        f"/api/v1/permissions/users/{limited_user['id']}",
        json={"grant": ["iam.permissions.manage"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert grant_manage.status_code == 200

    limited_tokens = await _login(client, email="limited@example.com")
    escalation = await client.patch(
        f"/api/v1/permissions/users/{target_user['id']}",
        json={"grant": ["iam.users.update"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {limited_tokens['access_token']}"},
    )
    assert escalation.status_code == 403
    assert (
        escalation.json()["error"]["message"]
        == "Cannot grant IAM permissions the actor does not have"
    )

    unknown = await client.patch(
        f"/api/v1/permissions/users/{target_user['id']}",
        json={"grant": ["iam.unknown"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert unknown.status_code == 422
