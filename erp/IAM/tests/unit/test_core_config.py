"""Unit coverage for IAM runtime configuration."""

import pytest
from iam.core.config import Settings, get_settings
from pydantic import ValidationError


def _minimal_settings(**overrides: object) -> Settings:
    defaults: dict[str, object] = {
        "environment": "testing",
        "database_url": "sqlite+aiosqlite:///:memory:",
        "jwt_secret_key": "unit-test-secret-key-for-iam",
        "dev_bootstrap_enabled": False,
    }
    defaults.update(overrides)
    return Settings(**defaults)


def test_defaults_with_explicit_secret() -> None:
    settings = _minimal_settings()
    assert settings.app_name == "verp-iam"
    assert settings.environment == "testing"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_minutes == 60 * 24 * 7
    assert settings.dev_bootstrap_enabled is False
    assert settings.database_echo is False
    assert settings.cors_origins == []


def test_missing_secret_generates_temporary_key() -> None:
    with pytest.warns(UserWarning, match="Generated a temporary key"):
        settings = Settings(
            jwt_secret_key=None,
            environment="testing",
            database_url="sqlite+aiosqlite:///:memory:",
            dev_bootstrap_enabled=False,
        )
    assert settings.jwt_secret_key is not None
    assert len(settings.jwt_secret_key.get_secret_value()) >= 32


@pytest.mark.parametrize(
    "insecure_secret",
    ["change-me-in-local-development", "changeme", "secret", "default"],
)
def test_known_insecure_secrets_are_rejected(insecure_secret: str) -> None:
    with pytest.raises(ValueError, match="known to be insecure"):
        _minimal_settings(jwt_secret_key=insecure_secret)


def test_cors_origins_parses_comma_separated_values() -> None:
    settings = _minimal_settings(
        cors_origins="https://app.example.com, https://admin.example.com ",
    )
    assert settings.cors_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_cors_origins_empty_and_list_passthrough() -> None:
    assert _minimal_settings(cors_origins="").cors_origins == []
    assert _minimal_settings(cors_origins=None).cors_origins == []
    assert _minimal_settings(
        cors_origins=["https://app.example.com"],
    ).cors_origins == ["https://app.example.com"]


def test_log_level_is_normalized_to_upper_case() -> None:
    assert _minimal_settings(log_level="info").log_level == "INFO"


def test_environment_helpers() -> None:
    assert _minimal_settings(environment="testing").is_testing is True
    assert _minimal_settings(environment="development").is_development is True
    assert _minimal_settings(environment="production").is_production is True
    assert _minimal_settings(environment="testing").is_production is False


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _minimal_settings(environment="nope")


def test_non_positive_access_token_expiry_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _minimal_settings(access_token_expire_minutes=0)


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
