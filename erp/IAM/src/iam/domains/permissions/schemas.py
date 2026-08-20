"""IAM permission request and response DTOs."""

from pydantic import BaseModel, Field, field_validator


class PermissionRead(BaseModel):
    """Catalog entry for one IAM permission."""

    key: str
    description: str


class UserPermissionsRead(BaseModel):
    """IAM authorization state for one user."""

    user_id: int
    grants: list[str]
    denials: list[str]
    effective_permissions: list[str]


class UserPermissionPatch(BaseModel):
    """Grant, deny, or clear IAM permissions for one user."""

    grant: list[str] = Field(default_factory=list)
    deny: list[str] = Field(default_factory=list)
    clear: list[str] = Field(default_factory=list)

    @field_validator("grant", "deny", "clear")
    @classmethod
    def normalize_permissions(cls, values: list[str]) -> list[str]:
        return sorted({value.strip() for value in values if value.strip()})
