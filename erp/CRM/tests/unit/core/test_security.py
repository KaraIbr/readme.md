from datetime import timedelta

import pytest
from core.config import Settings
from core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from pydantic import SecretStr


def test_password_hashing_round_trip() -> None:
    hashed = hash_password("correct horse battery staple")

    assert hashed != "correct horse battery staple"
    assert verify_password("correct horse battery staple", hashed) is True
    assert verify_password("wrong password", hashed) is False


def test_access_token_round_trip() -> None:
    settings = Settings(jwt_secret_key=SecretStr("super-secret-for-tests"))

    token = create_access_token(
        42,
        settings=settings,
        additional_claims={"role": "admin"},
    )
    payload = decode_token(token, expected_type="access", settings=settings)

    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["role"] == "admin"


def test_decode_token_rejects_wrong_type() -> None:
    settings = Settings(jwt_secret_key=SecretStr("super-secret-for-tests"))
    token = create_refresh_token(
        42,
        settings=settings,
        expires_delta=timedelta(minutes=5),
    )

    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type="access", settings=settings)
