"""Integration coverage for IAM authentication flows and token handling."""

from httpx import AsyncClient
from iam.core.config import Settings


async def _create_user(client: AsyncClient, *, email: str) -> dict[str, object]:
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "password": "correct-password",
            "full_name": email.split("@", maxsplit=1)[0].title(),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_login_with_wrong_password_is_rejected(client: AsyncClient) -> None:
    await _create_user(client, email="user@example.com")

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_failed"

    unknown = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever-password"},
    )
    assert unknown.status_code == 401


async def test_account_locks_after_five_failed_attempts(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="user@example.com")

    for _ in range(5):
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "user@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401

    locked = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "correct-password"},
    )
    assert locked.status_code == 401
    assert "locked" in locked.json()["error"]["message"]


async def test_refresh_token_validation_and_missing_token(
    client: AsyncClient,
) -> None:
    await _create_user(client, email="user@example.com")
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "correct-password"},
    )
    assert login.status_code == 200
    token_pair = login.json()

    invalid = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not-a-valid-jwt"},
    )
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "authentication_failed"

    wrong_type = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_pair["access_token"]},
    )
    assert wrong_type.status_code == 401

    client.cookies.clear()
    missing = await client.post("/api/v1/auth/refresh", json={})
    assert missing.status_code == 401
    assert missing.json()["error"]["message"] == "Refresh token missing"


async def test_refresh_via_http_only_cookie(client: AsyncClient) -> None:
    await _create_user(client, email="user@example.com")
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "correct-password"},
    )
    assert login.status_code == 200
    refresh_cookie = client.cookies.get("verp_refresh_token")
    assert refresh_cookie

    refreshed = await client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json()["token_type"] == "bearer"
    assert refreshed.cookies.get("verp_access_token")


async def test_logout_revokes_access_token(client: AsyncClient) -> None:
    await _create_user(client, email="user@example.com")
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "correct-password"},
    )
    assert login.status_code == 200
    access_token = login.json()["access_token"]
    access_cookie = client.cookies.get("verp_access_token")
    assert access_cookie

    me_before = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_before.status_code == 200

    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    me_after = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_after.status_code == 401
    assert me_after.json()["error"]["message"] == "Token has been revoked"


async def test_refresh_rejects_untrusted_origin(
    client: AsyncClient,
    monkeypatch,
) -> None:
    await _create_user(client, email="user@example.com")
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "correct-password"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    settings = Settings(
        environment="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key="test-secret-key-for-iam",
        dev_bootstrap_enabled=False,
        cors_origins=["https://app.example.com"],
    )
    monkeypatch.setattr("iam.domains.auth.router.get_settings", lambda: settings)

    evil_origin = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
        headers={"Origin": "https://evil.example.com"},
    )
    assert evil_origin.status_code == 403
    assert evil_origin.json()["error"]["message"] == "Origin not allowed"

    trusted_origin = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
        headers={"Origin": "https://app.example.com"},
    )
    assert trusted_origin.status_code == 200
