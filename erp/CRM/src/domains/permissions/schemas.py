"""CRM permissions request and response DTOs."""

from domains.permissions.models import CRMUserPermissionEffect, UserRole
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PermissionRead(BaseModel):
    """Catalog entry for one CRM permission."""

    key: str
    description: str


class PermissionOverrideRead(BaseModel):
    """Public representation of a user-specific permission override."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    permission: str
    effect: CRMUserPermissionEffect
    changed_by: int | None


class UserPermissionsRead(BaseModel):
    """CRM authorization state for one user."""

    user_id: int
    role: UserRole | None
    role_permissions: list[str]
    grants: list[str]
    denials: list[str]
    effective_permissions: list[str]


class UserPermissionPatch(BaseModel):
    """Grant or deny individual CRM permissions for one user."""

    grant: list[str] = Field(default_factory=list)
    deny: list[str] = Field(default_factory=list)
    clear: list[str] = Field(default_factory=list)

    @field_validator("grant", "deny", "clear")
    @classmethod
    def normalize_permissions(cls, values: list[str]) -> list[str]:
        return sorted({value.strip() for value in values if value.strip()})


class RoleAssignment(BaseModel):
    """Request body for assigning one CRM role template."""

    role: UserRole


class LeadAssignmentCreate(BaseModel):
    """Request body for assigning a Lead to a sales user."""

    user_id: int = Field(gt=0)


class ProposalAssignmentCreate(BaseModel):
    """Request body for assigning a Proposal to a technical user."""

    user_id: int = Field(gt=0)


class LeadAssignmentRead(BaseModel):
    """Public Lead assignment state."""

    lead_id: int
    user_id: int


class ProposalAssignmentRead(BaseModel):
    """Public Proposal assignment state."""

    proposal_id: int
    user_id: int
