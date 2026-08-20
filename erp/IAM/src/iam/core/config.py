"""IAM service settings loaded from environment variables."""

import secrets
import warnings
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "testing", "staging", "production"]

_KNOWN_INSECURE_SECRETS = {"change-me-in-local-development", "changeme", "secret", "default"}


class Settings(BaseSettings):
    """Typed runtime configuration for the IAM service."""

    model_config = SettingsConfigDict(
        env_file=(".env", "IAM/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="IAM_",
    )

    app_name: str = "verp-iam"
    environment: Environment = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./ventura.db"
    database_echo: bool = False

    jwt_secret_key: SecretStr | None = Field(default=None)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 7, gt=0)

    log_level: str = "INFO"
    log_json: bool = True

    cors_origins: list[str] = Field(default_factory=list)

    dev_bootstrap_enabled: bool = False

    @field_validator("jwt_secret_key", mode="before")
    @classmethod
    def validate_jwt_secret(cls, value: object) -> object:
        if value is None or value == "":
            generated = secrets.token_urlsafe(32)
            warnings.warn(
                f"No IAM_JWT_SECRET_KEY provided. Generated a temporary key: {generated}. "
                "Set IAM_JWT_SECRET_KEY in production.",
                stacklevel=2,
            )
            return SecretStr(generated)
        if isinstance(value, SecretStr):
            raw = value.get_secret_value()
        elif isinstance(value, str):
            raw = value
        else:
            return value
        if raw.lower() in _KNOWN_INSECURE_SECRETS:
            raise ValueError(
                f"The JWT secret '{raw}' is known to be insecure. "
                "Generate a strong random key with: secrets.token_urlsafe(32)"
            )
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str] | None) -> list[str]:
        """Accept either comma-separated env values or already parsed lists."""

        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings for dependency injection."""

    return Settings()
