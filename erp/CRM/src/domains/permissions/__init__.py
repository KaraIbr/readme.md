"""CRM permissions domain."""

from domains.permissions.models import (
    CRMUserPermissionEffect,
    CRMUserPermissionOverride,
    LeadAssignment,
    ProposalAssignment,
)

__all__ = [
    "CRMUserPermissionEffect",
    "CRMUserPermissionOverride",
    "LeadAssignment",
    "ProposalAssignment",
]
