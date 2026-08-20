"""Integration coverage for IAM central-user administration."""

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


async def test_list_users_returns_all_with_role_field(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)

    anonymous = await client.get("/api/v1/users/")
    assert anonymous.status_code == 200
    anonymous_emails = [u["email"] for u in anonymous.json()]
    assert "owner@example.com" in anonymous_emails
    assert "target@example.com" in anonymous_emails

    authenticated = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert authenticated.status_code == 200
    rows = authenticated.json()
    target_row = next(r for r in rows if r["email"] == "target@example.com")
    assert target_row["id"] == int(target["id"])
    assert target_row["full_name"] == "Target"
    assert target_row["is_active"] is True
    assert target_row["role"] is None


async def test_read_user_enforces_permission_and_not_found(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    await _create_user(client, email="limited@example.com", token=owner_access)
    limited_access = await _login(client, email="limited@example.com")

    target_id = int(target["id"])

    allowed = await client.get(
        f"/api/v1/users/{target_id}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["email"] == "target@example.com"

    denied = await client.get(
        f"/api/v1/users/{target_id}",
        headers={"Authorization": f"Bearer {limited_access}"},
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "authorization_failed"

    missing = await client.get(
        "/api/v1/users/999999",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "not_found"


async def test_update_user_enforces_permission_and_conflicts(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    await _create_user(client, email="taken@example.com", token=owner_access)
    await _create_user(client, email="limited@example.com", token=owner_access)
    limited_access = await _login(client, email="limited@example.com")

    target_id = int(target["id"])

    denied = await client.patch(
        f"/api/v1/users/{target_id}",
        json={"full_name": "Hacked"},
        headers={"Authorization": f"Bearer {limited_access}"},
    )
    assert denied.status_code == 403

    renamed = await client.patch(
        f"/api/v1/users/{target_id}",
        json={"full_name": "Renamed"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["full_name"] == "Renamed"

    conflict = await client.patch(
        f"/api/v1/users/{target_id}",
        json={"email": "taken@example.com"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "conflict"

    me = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert me.status_code == 200
    self_deactivate = await client.patch(
        f"/api/v1/users/{me.json()['id']}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert self_deactivate.status_code == 403
    assert "deactivate their own account" in self_deactivate.json()["error"]["message"]


async def test_deactivated_user_cannot_login_and_can_be_reactivated(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_id = int(target["id"])

    deactivated = await client.post(
        f"/api/v1/users/{target_id}/deactivate",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    blocked_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "target@example.com", "password": "correct-password"},
    )
    assert blocked_login.status_code == 403
    assert blocked_login.json()["error"]["code"] == "authorization_failed"

    reactivated = await client.post(
        f"/api/v1/users/{target_id}/activate",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert reactivated.status_code == 200
    assert reactivated.json()["is_active"] is True

    working_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "target@example.com", "password": "correct-password"},
    )
    assert working_login.status_code == 200


async def test_delete_user_permanently_and_self_delete_forbidden(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    me = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    owner_id = int(me.json()["id"])

    self_delete = await client.delete(
        f"/api/v1/users/{owner_id}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert self_delete.status_code == 403
    assert "delete their own account" in self_delete.json()["error"]["message"]

    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_id = int(target["id"])

    deleted = await client.delete(
        f"/api/v1/users/{target_id}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert deleted.status_code == 200
    assert deleted.json()["id"] == target_id

    after = await client.get(
        f"/api/v1/users/{target_id}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert after.status_code == 404


async def test_delete_user_with_active_service_access_is_rejected(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_id = int(target["id"])

    grant = await client.post(
        f"/api/v1/services/users/{target_id}/access",
        json={"service_key": "crm"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert grant.status_code == 201

    deleted = await client.delete(
        f"/api/v1/users/{target_id}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert deleted.status_code == 422
    assert "cannot be permanently deleted" in deleted.json()["error"]["message"]
