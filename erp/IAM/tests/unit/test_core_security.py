"""Unit coverage for IAM password hashing and JWT helpers."""

from datetime import UTC, datetime, timedelta

import pytest
from iam.core.config import Settings
from iam.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from jose import jwt


def _settings() -> Settings:
    return Settings(
        environment="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key="unit-test-secret-key-for-iam",
        dev_bootstrap_enabled=False,
    )


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("correct-password")
    assert hashed != "correct-password"
    assert verify_password("correct-password", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_token_without_secret_raises_runtime_error() -> None:
    settings = Settings.model_construct(jwt_secret_key=None)
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY is not configured"):
        create_token("1", token_type="access", settings=settings)


def test_access_token_roundtrip() -> None:
    settings = _settings()
    token = create_access_token("42", settings=settings)
    payload = decode_token(token, expected_type="access", settings=settings)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["jti"]
    assert abs(int(payload["exp"]) - int(payload["iat"])) - 1800 <= 1


def test_refresh_token_default_expiry() -> None:
    settings = _settings()
    token = create_refresh_token("7", settings=settings)
    payload = decode_token(token, expected_type="refresh", settings=settings)
    assert payload["sub"] == "7"
    assert payload["type"] == "refresh"
    assert abs(int(payload["exp"]) - int(payload["iat"])) - 604800 <= 1


def test_custom_expiry_and_additional_claims() -> None:
    settings = _settings()
    token = create_token(
        "user@example.com",
        token_type="access",
        settings=settings,
        expires_delta=timedelta(minutes=5),
        additional_claims={"scope": ["iam.users.read"], "locale": "en"},
    )
    payload = decode_token(token, settings=settings)
    assert int(payload["exp"]) - int(payload["iat"]) == 300
    assert payload["scope"] == ["iam.users.read"]
    assert payload["locale"] == "en"
    assert payload["sub"] == "user@example.com"


def test_integer_subject_is_stored_as_string() -> None:
    settings = _settings()
    token = create_access_token(123, settings=settings)
    assert decode_token(token, settings=settings)["sub"] == "123"


def test_decode_rejects_garbage_token() -> None:
    with pytest.raises(InvalidTokenError, match="Invalid or expired token"):
        decode_token("not-a-valid-jwt", settings=_settings())


def test_decode_rejects_wrong_token_type() -> None:
    settings = _settings()
    access_token = create_access_token("42", settings=settings)
    with pytest.raises(InvalidTokenError, match="Expected refresh token"):
        decode_token(access_token, expected_type="refresh", settings=settings)


def test_decode_rejects_expired_token() -> None:
    settings = _settings()
    token = create_access_token(
        "42",
        settings=settings,
        expires_delta=-timedelta(minutes=1),
    )
    with pytest.raises(InvalidTokenError, match="Invalid or expired token"):
        decode_token(token, settings=settings)


def test_decode_rejects_missing_subject() -> None:
    settings = _settings()
    now = datetime.now(UTC)
    payload = {
        "type": "access",
        "jti": "fixed-jti",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=30),
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(InvalidTokenError, match="subject is missing"):
        decode_token(token, settings=settings)
