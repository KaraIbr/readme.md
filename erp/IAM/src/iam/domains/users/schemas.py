"""IAM user request and response DTOs."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_email(value: str) -> str:
    """Normalize an email value used for identity and login."""

    return value.strip().lower()


class UserCreate(BaseModel):
    """Request body for creating a central VERP user."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = normalize_email(value)
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Invalid email address")
        return normalized

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class UserUpdate(BaseModel):
    """Request body for updating central user profile fields."""

    email: str | None = Field(default=None, min_length=3, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = Field(default=None)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = normalize_email(value)
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Invalid email address")
        return normalized

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class UserRead(BaseModel):
    """Public central user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None
    is_active: bool


class AdminUserRead(BaseModel):
    """Admin-oriented user representation with optional CRM role."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None
    is_active: bool
    role: str | None = None
    last_login: str | None = None
    created_at: str
