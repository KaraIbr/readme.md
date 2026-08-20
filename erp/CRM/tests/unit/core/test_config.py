from core.config import Settings
from pydantic import SecretStr


def test_settings_parse_comma_separated_cors_origins() -> None:
    settings = Settings(cors_origins="https://one.example, https://two.example")

    assert settings.cors_origins == [
        "https://one.example",
        "https://two.example",
    ]


def test_settings_expose_environment_helpers() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key=SecretStr("super-secret-for-tests"),
    )

    assert settings.is_production is True
    assert settings.is_development is False
    assert settings.is_testing is False
