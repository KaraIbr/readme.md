"""CRM permissions HTTP routers."""

from collections.abc import Sequence
from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.permissions import schemas, service
from fastapi import APIRouter, Depends, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()
lead_router = APIRouter()
proposal_router = APIRouter()


def _user_id(current_user: CurrentUser) -> int:
    user_id = current_user.id
    assert user_id is not None
    return user_id


@router.get("/", response_model=list[schemas.PermissionRead])
async def list_permissions(current_user: CurrentUser) -> list[schemas.PermissionRead]:
    """Return the CRM permission catalog."""

    # Reading the catalog is useful for the UI; effective permission details below
    # remain protected by the permission service.
    return [
        schemas.PermissionRead(key=key, description=description)
        for key, description in sorted(service.PERMISSIONS.items())
    ]


@router.get("/users/{user_id}", response_model=schemas.UserPermissionsRead)
async def read_user_permissions(
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserPermissionsRead:
    """Return one user's CRM role, overrides, and effective permissions."""

    actor_id = _user_id(current_user)
    await service.require_permission(session, actor_id, "crm.permissions.read")
    _user, access, grants, denials, effective = await service.read_user_permissions(
        session,
        user_id,
    )
    role = None if access is None else access.role
    return schemas.UserPermissionsRead(
        user_id=user_id,
        role=role,
        role_permissions=[] if role is None else sorted(service.role_permissions(role)),
        grants=sorted(grants),
        denials=sorted(denials),
        effective_permissions=sorted(effective),
    )


@router.patch("/users/{user_id}", response_model=schemas.UserPermissionsRead)
async def update_user_permissions(
    user_id: int,
    payload: schemas.UserPermissionPatch,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserPermissionsRead:
    """Grant, deny, or clear one user's CRM permission overrides."""

    await service.set_user_permission_overrides(
        session,
        actor_id=_user_id(current_user),
        target_user_id=user_id,
        grant=set(payload.grant),
        deny=set(payload.deny),
        clear=set(payload.clear),
    )
    _user, access, grants, denials, effective = await service.read_user_permissions(
        session,
        user_id,
    )
    role = None if access is None else access.role
    return schemas.UserPermissionsRead(
        user_id=user_id,
        role=role,
        role_permissions=[] if role is None else sorted(service.role_permissions(role)),
        grants=sorted(grants),
        denials=sorted(denials),
        effective_permissions=sorted(effective),
    )


@router.post("/users/{user_id}/role", response_model=schemas.UserPermissionsRead)
async def assign_user_role(
    user_id: int,
    payload: schemas.RoleAssignment,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserPermissionsRead:
    """Assign a CRM role template to one user."""

    await service.assign_role(
        session,
        actor_id=_user_id(current_user),
        target_user_id=user_id,
        role=payload.role,
    )
    _, access, grants, denials, effective = await service.read_user_permissions(
        session,
        user_id,
    )
    assert access is not None
    return schemas.UserPermissionsRead(
        user_id=user_id,
        role=access.role,
        role_permissions=sorted(service.role_permissions(access.role)),
        grants=sorted(grants),
        denials=sorted(denials),
        effective_permissions=sorted(effective),
    )


@router.post("/users/{user_id}/grant", response_model=schemas.UserPermissionsRead)
async def grant_and_assign_user_role(
    user_id: int,
    payload: schemas.RoleAssignment,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserPermissionsRead:
    """Grant CRM service access and assign a role in one call."""

    await service.grant_and_assign_role(
        session,
        actor_id=_user_id(current_user),
        target_user_id=user_id,
        role=payload.role,
    )
    _, access, grants, denials, effective = await service.read_user_permissions(
        session,
        user_id,
    )
    assert access is not None
    return schemas.UserPermissionsRead(
        user_id=user_id,
        role=access.role,
        role_permissions=sorted(service.role_permissions(access.role)),
        grants=sorted(grants),
        denials=sorted(denials),
        effective_permissions=sorted(effective),
    )


@lead_router.get(
    "/{lead_id}/assignment",
    response_model=schemas.LeadAssignmentRead | None,
)
async def read_lead_assignment(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadAssignmentRead | None:
    """Return the active sales assignment for one Lead."""

    assignment = await service.get_lead_assignment(
        session,
        actor_id=_user_id(current_user),
        lead_id=lead_id,
    )
    if assignment is None:
        return None
    return schemas.LeadAssignmentRead(
        lead_id=assignment.lead_id,
        user_id=assignment.user_id,
    )


@lead_router.post(
    "/{lead_id}/assignment",
    response_model=schemas.LeadAssignmentRead,
)
async def assign_lead(
    lead_id: int,
    payload: schemas.LeadAssignmentCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadAssignmentRead:
    """Assign or transfer sales follow-up for one Lead."""

    assignment = await service.assign_lead(
        session,
        actor_id=_user_id(current_user),
        lead_id=lead_id,
        user_id=payload.user_id,
    )
    return schemas.LeadAssignmentRead(
        lead_id=assignment.lead_id,
        user_id=assignment.user_id,
    )


@lead_router.delete(
    "/{lead_id}/assignment",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_lead_assignment(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Remove active sales follow-up for one Lead."""

    await service.unassign_lead(
        session,
        actor_id=_user_id(current_user),
        lead_id=lead_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@proposal_router.get(
    "/{proposal_id}/assignments",
    response_model=list[schemas.ProposalAssignmentRead],
)
async def list_proposal_assignments(
    proposal_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[schemas.ProposalAssignmentRead]:
    """Return active technical assignments for one Proposal."""

    assignments: Sequence[service.ProposalAssignment] = await service.list_proposal_assignments(
        session,
        actor_id=_user_id(current_user),
        proposal_id=proposal_id,
    )
    return [
        schemas.ProposalAssignmentRead(
            proposal_id=a.proposal_id,
            user_id=a.user_id,
        )
        for a in assignments
    ]


@proposal_router.post(
    "/{proposal_id}/assignments",
    response_model=schemas.ProposalAssignmentRead,
)
async def assign_proposal(
    proposal_id: int,
    payload: schemas.ProposalAssignmentCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalAssignmentRead:
    """Assign technical Proposal work to a tech user."""

    assignment = await service.assign_proposal(
        session,
        actor_id=_user_id(current_user),
        proposal_id=proposal_id,
        user_id=payload.user_id,
    )
    return schemas.ProposalAssignmentRead(
        proposal_id=assignment.proposal_id,
        user_id=assignment.user_id,
    )


@proposal_router.delete(
    "/{proposal_id}/assignments/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_proposal_assignment(
    proposal_id: int,
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Remove one technical user's assignment from a Proposal."""

    await service.unassign_proposal(
        session,
        actor_id=_user_id(current_user),
        proposal_id=proposal_id,
        user_id=user_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
