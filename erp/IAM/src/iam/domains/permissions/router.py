"""IAM permissions HTTP router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.api.dependencies import CurrentUser, get_db_session
from iam.domains.permissions import schemas, service

router = APIRouter()


def _user_id(current_user: CurrentUser) -> int:
    user_id = current_user.id
    assert user_id is not None
    return user_id


@router.get("/", response_model=list[schemas.PermissionRead])
async def list_permissions(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[schemas.PermissionRead]:
    """Return the IAM permission catalog."""

    await service.require_permission(
        session,
        _user_id(current_user),
        "iam.permissions.read",
    )
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
    """Return one user's IAM permission overrides and effective permissions."""

    await service.require_permission(
        session,
        _user_id(current_user),
        "iam.permissions.read",
    )
    grants, denials, effective = await service.read_user_permissions(session, user_id)
    return schemas.UserPermissionsRead(
        user_id=user_id,
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
    """Grant, deny, or clear one user's IAM permission overrides."""

    await service.set_user_permission_overrides(
        session,
        actor_id=_user_id(current_user),
        target_user_id=user_id,
        grant=set(payload.grant),
        deny=set(payload.deny),
        clear=set(payload.clear),
    )
    grants, denials, effective = await service.read_user_permissions(session, user_id)
    return schemas.UserPermissionsRead(
        user_id=user_id,
        grants=sorted(grants),
        denials=sorted(denials),
        effective_permissions=sorted(effective),
    )
