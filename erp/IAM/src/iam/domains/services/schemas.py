"""IAM service-access request and response DTOs."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_service_key(value: str) -> str:
    """Normalize a service key used by IAM."""

    return value.strip().lower()


class ServiceRead(BaseModel):
    """Known VERP service catalog entry."""

    key: str
    description: str


class ServiceAccessCreate(BaseModel):
    """Request body for granting access to one service."""

    service_key: str = Field(min_length=1, max_length=80)

    @field_validator("service_key")
    @classmethod
    def normalize_service_key(cls, value: str) -> str:
        return normalize_service_key(value)


class ServiceAccessRead(BaseModel):
    """Public service-access representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    service_key: str
    is_active: bool
    granted_by: int
