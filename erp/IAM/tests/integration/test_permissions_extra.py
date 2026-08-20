"""Integration coverage for IAM permission overrides beyond the happy paths."""

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


async def test_permission_catalog_requires_iam_permissions_read(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    await _create_user(client, email="limited@example.com", token=owner_access)
    limited_access = await _login(client, email="limited@example.com")

    catalog = await client.get(
        "/api/v1/permissions/",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert catalog.status_code == 200
    keys = [entry["key"] for entry in catalog.json()]
    assert keys == sorted(keys)
    assert "iam.users.create" in keys
    assert "iam.permissions.manage" in keys

    denied = await client.get(
        "/api/v1/permissions/",
        headers={"Authorization": f"Bearer {limited_access}"},
    )
    assert denied.status_code == 403


async def test_deny_override_blocks_permission(client: AsyncClient) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_access = await _login(client, email="target@example.com")
    target_id = int(target["id"])

    blocked = await client.post(
        "/api/v1/users/",
        json={"email": "other@example.com", "password": "correct-password"},
        headers={"Authorization": f"Bearer {target_access}"},
    )
    assert blocked.status_code == 403

    denied = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": [], "deny": ["iam.users.create"], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert denied.status_code == 200
    assert "iam.users.create" in denied.json()["denials"]
    assert "iam.users.create" not in denied.json()["effective_permissions"]

    still_blocked = await client.post(
        "/api/v1/users/",
        json={"email": "other@example.com", "password": "correct-password"},
        headers={"Authorization": f"Bearer {target_access}"},
    )
    assert still_blocked.status_code == 403


async def test_grant_then_clear_removes_override(client: AsyncClient) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_access = await _login(client, email="target@example.com")
    target_id = int(target["id"])

    granted = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": ["iam.users.read"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert granted.status_code == 200
    assert "iam.users.read" in granted.json()["effective_permissions"]

    read = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {target_access}"},
    )
    assert read.status_code == 200
    assert read.json()["email"] == "target@example.com"

    cleared = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": [], "deny": [], "clear": ["iam.users.read"]},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert cleared.status_code == 200
    assert "iam.users.read" not in cleared.json()["effective_permissions"]
    assert cleared.json()["grants"] == []


async def test_grant_and_deny_same_permission_is_rejected(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_id = int(target["id"])

    response = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": ["iam.users.read"], "deny": ["iam.users.read"], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert response.status_code == 422
    assert "grant and deny" in response.json()["error"]["message"]


async def test_permission_patch_rejects_unknown_permissions(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_id = int(target["id"])

    response = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": ["iam.bogus.read"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_operation"


async def test_changing_override_effect_from_grant_to_deny(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="owner@example.com")
    owner_access = await _login(client, email="owner@example.com")
    target = await _create_user(client, email="target@example.com", token=owner_access)
    target_id = int(target["id"])

    granted = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": ["iam.users.read"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert granted.status_code == 200

    flipped = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": [], "deny": ["iam.users.read"], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert flipped.status_code == 200
    assert "iam.users.read" in flipped.json()["denials"]
    assert "iam.users.read" not in flipped.json()["effective_permissions"]


async def test_permission_overrides_reject_inactive_target(
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

    patch = await client.patch(
        f"/api/v1/permissions/users/{target_id}",
        json={"grant": ["iam.users.read"], "deny": [], "clear": []},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert patch.status_code == 403

    read = await client.get(
        f"/api/v1/permissions/users/{target_id}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    assert read.status_code == 403
    assert "inactive" in read.json()["error"]["message"]
