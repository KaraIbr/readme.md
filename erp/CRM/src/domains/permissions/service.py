"""CRM permission and assignment business logic."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Final, cast

from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from domains.contacts import repository as contacts_repository
from domains.leads import repository as leads_repository
from domains.leads.models import Lead
from domains.permissions import repository
from domains.permissions.models import (
    CRMUserAccess,
    CRMUserPermissionEffect,
    CRMUserPermissionOverride,
    LeadAssignment,
    ProposalAssignment,
    UserRole,
)
from domains.proposals import repository as proposals_repository
from domains.proposals.models import Proposal
from domains.technical_visits.models import TechnicalVisit, TechnicalVisitAssignee
from domains.users import repository as users_repository
from domains.users.models import IAMServiceAccess, User
from domains.users.service import (
    CRM_SERVICE_KEY,
    get_active_user,
    get_user,
    require_crm_service_access,
)
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

PERMISSIONS: Final[dict[str, str]] = {
    "crm.permissions.read": "Read CRM permissions",
    "crm.permissions.manage": "Manage CRM permission overrides",
    "crm.roles.assign": "Assign CRM role templates",
    "crm.contacts.create": "Create contacts",
    "crm.contacts.read": "Read contacts",
    "crm.contacts.update": "Update contacts",
    "crm.contacts.delete": "Delete contacts",
    "crm.leads.create": "Create leads",
    "crm.leads.read": "Read leads",
    "crm.leads.update": "Update leads",
    "crm.leads.delete": "Delete leads",
    "crm.leads.assign": "Assign sales follow-up for leads",
    "crm.leads.stage.update": "Update lead stage",
    "crm.leads.close": "Close leads",
    "crm.leads.documents.create": "Upload lead documents",
    "crm.leads.documents.read": "Read lead documents",
    "crm.leads.documents.delete": "Delete lead documents",
    "crm.leads.electricity_bills.create": "Upload lead electricity bills",
    "crm.leads.electricity_bills.read": "Read lead electricity bills",
    "crm.leads.electricity_bills.delete": "Delete lead electricity bills",
    "crm.leads.interactions.create": "Create lead interactions",
    "crm.leads.interactions.read": "Read lead interactions",
    "crm.leads.interactions.update": "Update lead interactions",
    "crm.leads.interactions.delete": "Delete lead interactions",
    "crm.proposals.create": "Create proposals",
    "crm.proposals.read": "Read proposals",
    "crm.proposals.update": "Update proposals except protected price fields",
    "crm.proposals.delete": "Delete proposals",
    "crm.proposals.assign_tech": "Assign technical proposal work",
    "crm.proposals.stage.update": "Update proposal stage",
    "crm.proposals.mark_won": "Mark proposals won",
    "crm.proposals.mark_lost": "Mark proposals lost",
    "crm.proposals.price.set": "Set empty protected proposal price fields",
    "crm.proposals.price.update": "Change established protected proposal price fields",
    "crm.proposals.commercial_documents.create": "Upload commercial proposal PDFs",
    "crm.proposals.commercial_documents.read": "Read commercial proposal PDFs",
    "crm.proposals.commercial_documents.delete": "Delete commercial proposal PDFs",
    "crm.proposals.documents.create": "Upload proposal documents",
    "crm.proposals.documents.read": "Read proposal documents",
    "crm.proposals.documents.delete": "Delete proposal documents",
    "crm.proposals.technical_visits.link": "Link proposals to technical visits",
    "crm.proposals.technical_visits.read": "Read proposal technical visit links",
    "crm.proposals.technical_visits.unlink": "Unlink proposal technical visits",
    "crm.technical_visits.create": "Create technical visits",
    "crm.technical_visits.read": "Read technical visits",
    "crm.technical_visits.update": "Update technical visits",
    "crm.technical_visits.assign": "Assign technical visit users",
    "crm.technical_visits.complete": "Complete technical visits",
    "crm.technical_visits.cancel": "Cancel technical visits",
    "crm.technical_visits.attachments.create": "Upload technical visit attachments",
    "crm.technical_visits.attachments.read": "Read technical visit attachments",
    "crm.technical_visits.attachments.delete": "Delete technical visit attachments",
    "crm.pipeline.read": "Read pipeline history and summaries",
    "crm.agent.chat": "Use the CRM agent",
    "crm.activities.create": "Create activities",
    "crm.activities.read": "Read activities",
    "crm.activities.update": "Update activities",
    "crm.activities.delete": "Delete activities",
    "crm.opportunities.create": "Create opportunities",
    "crm.opportunities.read": "Read opportunities",
    "crm.opportunities.update": "Update opportunities",
    "crm.opportunities.delete": "Delete opportunities",
    "crm.opportunities.stage.update": "Update opportunity stage",
    "crm.opportunities.close": "Close opportunities",
    "crm.tasks.create": "Create tasks",
    "crm.tasks.read": "Read tasks",
    "crm.tasks.update": "Update tasks",
    "crm.tasks.delete": "Delete tasks",
    "crm.dashboard.read": "Read dashboard stats",
}

ALL_PERMISSIONS: Final[frozenset[str]] = frozenset(PERMISSIONS)
PRICE_PERMISSIONS: Final[frozenset[str]] = frozenset(
    {"crm.proposals.price.set", "crm.proposals.price.update"}
)
TECH_DENIED_DEFAULTS: Final[frozenset[str]] = frozenset(
    {
        "crm.permissions.manage",
        "crm.roles.assign",
        "crm.contacts.create",
        "crm.contacts.update",
        "crm.contacts.delete",
        "crm.leads.create",
        "crm.leads.update",
        "crm.leads.delete",
        "crm.leads.assign",
        "crm.leads.stage.update",
        "crm.leads.close",
        "crm.leads.documents.create",
        "crm.leads.documents.delete",
        "crm.leads.electricity_bills.create",
        "crm.leads.electricity_bills.delete",
        "crm.leads.interactions.create",
        "crm.leads.interactions.read",
        "crm.leads.interactions.update",
        "crm.leads.interactions.delete",
        "crm.proposals.price.set",
        "crm.proposals.price.update",
        "crm.activities.create",
        "crm.activities.update",
        "crm.activities.delete",
        "crm.opportunities.create",
        "crm.opportunities.update",
        "crm.opportunities.delete",
        "crm.opportunities.stage.update",
        "crm.opportunities.close",
    }
)


def role_permissions(role: UserRole) -> set[str]:
    """Return default permission keys for a CRM role."""

    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        return set(ALL_PERMISSIONS)
    if role == UserRole.SALES:
        return {
            key
            for key in ALL_PERMISSIONS
            if key.startswith("crm.contacts.")
            or key.startswith("crm.leads.")
            or key
            in {
                "crm.proposals.read",
                "crm.proposals.commercial_documents.read",
                "crm.proposals.documents.read",
                "crm.proposals.technical_visits.read",
                "crm.technical_visits.read",
                "crm.technical_visits.attachments.read",
                "crm.pipeline.read",
                "crm.agent.chat",
            }
        } - PRICE_PERMISSIONS
    if role == UserRole.TECH:
        return set(ALL_PERMISSIONS) - TECH_DENIED_DEFAULTS
    return set()


async def get_crm_user_access(
    session: AsyncSession,
    user_id: int,
) -> CRMUserAccess | None:
    """Return active CRM access for one active central user, if configured."""

    await require_crm_service_access(session, user_id)
    access = await repository.get_user_access(session, user_id)
    if access is None or not access.is_active:
        return None
    return access


async def require_crm_user_access(
    session: AsyncSession,
    user_id: int,
) -> CRMUserAccess:
    """Return active CRM access or reject the user for CRM actions."""

    access = await get_crm_user_access(session, user_id)
    if access is None:
        raise AuthorizationError("User does not have CRM access")
    return access


async def get_user_crm_role(
    session: AsyncSession,
    user_id: int,
) -> UserRole | None:
    """Return the CRM role assigned to one central user, if any."""

    access = await get_crm_user_access(session, user_id)
    if access is None:
        return None
    return access.role


async def effective_permissions(session: AsyncSession, user_id: int) -> set[str]:
    """Return role permissions plus grants minus denials for one active user."""

    access = await get_crm_user_access(session, user_id)
    permissions = set() if access is None else role_permissions(access.role)
    overrides = await repository.list_user_overrides(session, user_id)
    grants = {
        override.permission
        for override in overrides
        if override.effect == CRMUserPermissionEffect.GRANT
    }
    denials = {
        override.permission
        for override in overrides
        if override.effect == CRMUserPermissionEffect.DENY
    }
    return (permissions | grants) - denials


async def require_permission(
    session: AsyncSession,
    user_id: int,
    permission: str,
) -> None:
    """Raise when a user lacks a CRM permission."""

    if permission not in ALL_PERMISSIONS:
        raise InvalidOperationError(
            "Unknown CRM permission",
            details={"permission": permission},
        )
    permissions = await effective_permissions(session, user_id)
    if permission not in permissions:
        raise AuthorizationError(
            "Missing CRM permission",
            details={"permission": permission},
        )


async def can_manage_user(
    session: AsyncSession,
    *,
    actor_id: int,
    target_user_id: int,
    requested_permissions: set[str] | None = None,
) -> tuple[User, User]:
    """Validate manager/admin guardrails for permission administration."""

    actor = await get_active_user(session, actor_id)
    target = await get_user(session, target_user_id)
    actor_access = await require_crm_user_access(session, actor_id)
    target_access = await get_crm_user_access(session, target_user_id)
    await require_permission(session, actor_id, "crm.permissions.manage")
    if actor.id == target.id:
        raise AuthorizationError("Users cannot modify their own CRM permissions")
    if (
        target_access is not None
        and target_access.role == UserRole.ADMIN
        and actor_access.role != UserRole.ADMIN
    ):
        raise AuthorizationError("Managers cannot modify admin users")
    if requested_permissions:
        actor_permissions = await effective_permissions(session, actor_id)
        missing = sorted(requested_permissions - actor_permissions)
        if missing:
            raise AuthorizationError(
                "Cannot grant permissions the actor does not have",
                details={"permissions": missing},
            )
    return actor, target


async def set_user_permission_overrides(
    session: AsyncSession,
    *,
    actor_id: int,
    target_user_id: int,
    grant: set[str],
    deny: set[str],
    clear: set[str],
) -> None:
    """Apply user-specific CRM permission overrides."""

    unknown = sorted((grant | deny | clear) - ALL_PERMISSIONS)
    if unknown:
        raise InvalidOperationError(
            "Unknown CRM permissions",
            details={"permissions": unknown},
        )
    if grant & deny:
        raise InvalidOperationError("Cannot grant and deny the same permission")
    await can_manage_user(
        session,
        actor_id=actor_id,
        target_user_id=target_user_id,
        requested_permissions=grant,
    )
    now = datetime.now(UTC)
    for permission in clear | grant | deny:
        existing = await repository.get_user_override(
            session,
            target_user_id,
            permission,
        )
        if permission in clear and existing is not None:
            await repository.delete_override(session, existing)
    for effect, permissions in (
        (CRMUserPermissionEffect.GRANT, grant),
        (CRMUserPermissionEffect.DENY, deny),
    ):
        for permission in permissions:
            existing = await repository.get_user_override(
                session,
                target_user_id,
                permission,
            )
            if existing is None:
                await repository.save_override(
                    session,
                    CRMUserPermissionOverride(
                        user_id=target_user_id,
                        permission=permission,
                        effect=effect,
                        changed_by=actor_id,
                    ),
                )
                continue
            existing.effect = effect
            existing.changed_by = actor_id
            existing.updated_at = now
            await repository.save_override(session, existing)
    await session.commit()


async def assign_role(
    session: AsyncSession,
    *,
    actor_id: int,
    target_user_id: int,
    role: UserRole,
) -> CRMUserAccess:
    """Assign a CRM role template with manager guardrails."""

    access_count = await repository.count_user_accesses(session)
    if access_count == 0:
        await require_crm_service_access(session, actor_id)
        if actor_id != target_user_id or role != UserRole.ADMIN:
            raise AuthorizationError("First CRM access must bootstrap the actor as admin")
        access = CRMUserAccess(
            user_id=target_user_id,
            role=UserRole.ADMIN,
            changed_by=actor_id,
        )
        access = await repository.save_user_access(session, access)
        await session.commit()
        await session.refresh(access)
        return access

    actor, _target = await can_manage_user(
        session,
        actor_id=actor_id,
        target_user_id=target_user_id,
        requested_permissions=role_permissions(role),
    )
    actor_access = await require_crm_user_access(session, actor_id)
    if role == UserRole.ADMIN and actor_access.role != UserRole.ADMIN:
        raise AuthorizationError("Only admins can assign the admin role")
    existing_access = await repository.get_user_access(session, target_user_id)
    if existing_access is None:
        access = CRMUserAccess(
            user_id=target_user_id,
            role=role,
            changed_by=actor.id,
        )
    else:
        access = existing_access
        access.role = role
        access.is_active = True
        access.changed_by = actor.id
        access.updated_at = datetime.now(UTC)
    session.add(access)
    await session.commit()
    await session.refresh(access)
    return access


async def grant_and_assign_role(
    session: AsyncSession,
    *,
    actor_id: int,
    target_user_id: int,
    role: UserRole,
) -> CRMUserAccess:
    """Grant IAM CRM service access and assign a CRM role in one transaction."""

    existing = await users_repository.get_service_access(
        session,
        user_id=target_user_id,
        service_key=CRM_SERVICE_KEY,
    )
    if existing is None:
        now = datetime.now(UTC)
        session.add(
            IAMServiceAccess(
                user_id=target_user_id,
                service_key=CRM_SERVICE_KEY,
                is_active=True,
                granted_by=actor_id,
                created_at=now,
                updated_at=now,
            )
        )

    return await assign_role(
        session,
        actor_id=actor_id,
        target_user_id=target_user_id,
        role=role,
    )


async def read_user_permissions(
    session: AsyncSession,
    user_id: int,
) -> tuple[User, CRMUserAccess | None, set[str], set[str], set[str]]:
    """Return user, grants, denials, and effective permissions."""

    user = await get_user(session, user_id)
    access = await get_crm_user_access(session, user_id)
    overrides = await repository.list_user_overrides(session, user_id)
    grants = {
        override.permission
        for override in overrides
        if override.effect == CRMUserPermissionEffect.GRANT
    }
    denials = {
        override.permission
        for override in overrides
        if override.effect == CRMUserPermissionEffect.DENY
    }
    return user, access, grants, denials, await effective_permissions(session, user_id)


async def assign_lead(
    session: AsyncSession,
    *,
    actor_id: int,
    lead_id: int,
    user_id: int,
) -> LeadAssignment:
    """Assign or transfer active sales follow-up for one Lead."""

    await require_permission(session, actor_id, "crm.leads.assign")
    target_access = await require_crm_user_access(session, user_id)
    if target_access.role != UserRole.SALES:
        raise InvalidOperationError("Leads can only be assigned to sales users")
    lead = await leads_repository.get(session, lead_id)
    if lead is None:
        raise NotFoundError("Lead not found", details={"lead_id": lead_id})
    if not await user_can_access_lead(session, user_id=actor_id, lead_id=lead_id):
        raise AuthorizationError("Lead belongs to another owner")
    current = await repository.get_active_lead_assignment(session, lead_id)
    if current is not None and current.user_id == user_id:
        return current
    now = datetime.now(UTC)
    if current is not None:
        current.is_active = False
        current.unassigned_at = now
        session.add(current)
    lead.owner_id = user_id
    session.add(lead)
    assignment = await repository.save_lead_assignment(
        session,
        LeadAssignment(lead_id=lead_id, user_id=user_id, assigned_by=actor_id),
    )
    await session.commit()
    await session.refresh(assignment)
    return assignment


async def assign_proposal(
    session: AsyncSession,
    *,
    actor_id: int,
    proposal_id: int,
    user_id: int,
) -> ProposalAssignment:
    """Assign technical Proposal work to a tech user."""

    await require_permission(session, actor_id, "crm.proposals.assign_tech")
    target_access = await require_crm_user_access(session, user_id)
    if target_access.role != UserRole.TECH:
        raise InvalidOperationError("Proposals can only be assigned to tech users")
    proposal = await proposals_repository.get(session, proposal_id)
    if proposal is None:
        raise NotFoundError(
            "Proposal not found",
            details={"proposal_id": proposal_id},
        )
    if not await user_can_access_proposal(
        session,
        user_id=actor_id,
        proposal_id=proposal_id,
    ):
        raise AuthorizationError("Proposal belongs to another user")
    current = await repository.get_active_proposal_assignment(
        session,
        proposal_id,
        user_id,
    )
    if current is not None:
        return current
    assignment = await repository.save_proposal_assignment(
        session,
        ProposalAssignment(
            proposal_id=proposal_id,
            user_id=user_id,
            assigned_by=actor_id,
        ),
    )
    await session.commit()
    await session.refresh(assignment)
    return assignment


async def get_lead_assignment(
    session: AsyncSession,
    *,
    actor_id: int,
    lead_id: int,
) -> LeadAssignment | None:
    """Return the active assignment for one Lead."""

    await require_permission(session, actor_id, "crm.leads.assign")
    return await repository.get_active_lead_assignment(session, lead_id)


async def unassign_lead(
    session: AsyncSession,
    *,
    actor_id: int,
    lead_id: int,
) -> None:
    """Remove active sales follow-up for one Lead."""

    await require_permission(session, actor_id, "crm.leads.assign")
    current = await repository.get_active_lead_assignment(session, lead_id)
    if current is None:
        raise NotFoundError(
            "Lead has no active assignment",
            details={"lead_id": lead_id},
        )
    await repository.deactivate_assignment(session, current)
    await session.commit()


async def list_proposal_assignments(
    session: AsyncSession,
    *,
    actor_id: int,
    proposal_id: int,
) -> Sequence[ProposalAssignment]:
    """Return active assignments for one Proposal."""

    await require_permission(session, actor_id, "crm.proposals.assign_tech")
    return await repository.list_active_proposal_assignments(session, proposal_id)


async def unassign_proposal(
    session: AsyncSession,
    *,
    actor_id: int,
    proposal_id: int,
    user_id: int,
) -> None:
    """Remove a technical user from one Proposal."""

    await require_permission(session, actor_id, "crm.proposals.assign_tech")
    current = await repository.get_active_proposal_assignment(session, proposal_id, user_id)
    if current is None:
        raise NotFoundError(
            "Proposal has no active assignment for this user",
            details={"proposal_id": proposal_id, "user_id": user_id},
        )
    await repository.deactivate_assignment(session, current)
    await session.commit()


async def user_can_access_proposal(
    session: AsyncSession,
    *,
    user_id: int,
    proposal_id: int,
) -> bool:
    """Return whether a user has resource scope over a Proposal."""

    role = await get_user_crm_role(session, user_id)
    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        return True
    proposal = await proposals_repository.get(session, proposal_id)
    if proposal is None:
        return False
    if role is None and proposal.created_by == user_id:
        return True
    if role == UserRole.SALES:
        lead = await leads_repository.get(session, proposal.lead_id)
        return lead is not None and lead.owner_id == user_id
    if role == UserRole.TECH:
        assigned = await repository.get_active_proposal_assignment(
            session,
            proposal_id,
            user_id,
        )
        return assigned is not None
    return False


async def user_can_access_lead(
    session: AsyncSession,
    *,
    user_id: int,
    lead_id: int,
) -> bool:
    """Return whether a user has resource scope over a Lead."""

    role = await get_user_crm_role(session, user_id)
    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        return True
    lead = await leads_repository.get(session, lead_id)
    if lead is None:
        return False
    if lead.owner_id == user_id:
        return True
    if role == UserRole.SALES:
        return lead.owner_id == user_id
    if role == UserRole.TECH:
        assigned_proposal = await session.exec(
            select(Proposal.id)
            .join(
                ProposalAssignment,
                cast(ColumnElement[Any], ProposalAssignment.proposal_id)
                == cast(ColumnElement[Any], Proposal.id),
            )
            .where(
                Proposal.lead_id == lead_id,
                ProposalAssignment.user_id == user_id,
                cast(ColumnElement[bool], ProposalAssignment.is_active).is_(True),
            )
        )
        if assigned_proposal.first() is not None:
            return True
        assigned_visit = await session.exec(
            select(TechnicalVisit.id)
            .join(
                TechnicalVisitAssignee,
                cast(ColumnElement[Any], TechnicalVisitAssignee.visit_id)
                == cast(ColumnElement[Any], TechnicalVisit.id),
            )
            .where(
                TechnicalVisit.lead_id == lead_id,
                TechnicalVisitAssignee.user_id == user_id,
            )
        )
        return assigned_visit.first() is not None
    return False


async def user_can_access_contact(
    session: AsyncSession,
    *,
    user_id: int,
    contact_id: int,
) -> bool:
    """Return whether a user has resource scope over a Contact."""

    role = await get_user_crm_role(session, user_id)
    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        return True
    contact = await contacts_repository.get(session, contact_id)
    if contact is None:
        return False
    owned_lead = await session.exec(
        select(Lead.id).where(
            Lead.contact_id == contact_id,
            Lead.owner_id == user_id,
        )
    )
    if owned_lead.first() is not None:
        return True
    if role == UserRole.TECH:
        assigned_proposal = await session.exec(
            select(Proposal.id)
            .join(
                Lead,
                cast(ColumnElement[Any], Lead.id) == cast(ColumnElement[Any], Proposal.lead_id),
            )
            .join(
                ProposalAssignment,
                cast(ColumnElement[Any], ProposalAssignment.proposal_id)
                == cast(ColumnElement[Any], Proposal.id),
            )
            .where(
                Lead.contact_id == contact_id,
                ProposalAssignment.user_id == user_id,
                cast(ColumnElement[bool], ProposalAssignment.is_active).is_(True),
            )
        )
        if assigned_proposal.first() is not None:
            return True
        assigned_visit = await session.exec(
            select(TechnicalVisit.id)
            .join(
                Lead,
                cast(ColumnElement[Any], Lead.id)
                == cast(ColumnElement[Any], TechnicalVisit.lead_id),
            )
            .join(
                TechnicalVisitAssignee,
                cast(ColumnElement[Any], TechnicalVisitAssignee.visit_id)
                == cast(ColumnElement[Any], TechnicalVisit.id),
            )
            .where(
                Lead.contact_id == contact_id,
                TechnicalVisitAssignee.user_id == user_id,
            )
        )
        return assigned_visit.first() is not None
    contact_has_lead = await session.exec(
        select(Lead.id).where(Lead.contact_id == contact_id).limit(1)
    )
    return contact.owner_id == user_id and contact_has_lead.first() is None


async def user_can_access_technical_visit(
    session: AsyncSession,
    *,
    user_id: int,
    visit_id: int,
) -> bool:
    """Return whether a user has technical visit assignment scope."""

    role = await get_user_crm_role(session, user_id)
    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        return True
    visit = await session.get(TechnicalVisit, visit_id)
    if visit is None:
        return False
    if visit.created_by == user_id:
        return True
    lead = await leads_repository.get(session, visit.lead_id)
    if role == UserRole.SALES and lead is not None and lead.owner_id == user_id:
        return True
    result = await session.exec(
        select(TechnicalVisitAssignee).where(
            TechnicalVisitAssignee.visit_id == visit_id,
            TechnicalVisitAssignee.user_id == user_id,
        )
    )
    return result.first() is not None
