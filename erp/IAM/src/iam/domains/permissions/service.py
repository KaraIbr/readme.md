"""IAM permission business logic."""

from datetime import UTC, datetime
from typing import Final

from sqlmodel.ext.asyncio.session import AsyncSession

from iam.core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from iam.domains.permissions import repository
from iam.domains.permissions.models import (
    IAMUserPermissionEffect,
    IAMUserPermissionOverride,
)
from iam.domains.users import repository as users_repository

PERMISSIONS: Final[dict[str, str]] = {
    "iam.users.create": "Create central VERP users",
    "iam.users.read": "Read central VERP users",
    "iam.users.update": "Update central VERP users",
    "iam.users.deactivate": "Activate or deactivate central VERP users",
    "iam.users.delete": "Permanently delete central VERP users",
    "iam.permissions.read": "Read IAM permission catalog and user permission state",
    "iam.permissions.manage": "Manage IAM permission overrides",
    "iam.services.read": "Read VERP service access",
    "iam.services.manage": "Grant or revoke VERP service access",
}
ALL_PERMISSIONS: Final[frozenset[str]] = frozenset(PERMISSIONS)
BOOTSTRAP_PERMISSIONS: Final[frozenset[str]] = ALL_PERMISSIONS


async def _ensure_active_user(session: AsyncSession, user_id: int) -> None:
    user = await users_repository.get(session, user_id)
    if user is None:
        raise NotFoundError("User not found", details={"user_id": user_id})
    if not user.is_active:
        raise AuthorizationError("User account is inactive")


async def effective_permissions(session: AsyncSession, user_id: int) -> set[str]:
    """Return effective IAM permissions for one active user."""

    await _ensure_active_user(session, user_id)
    overrides = await repository.list_user_overrides(session, user_id)
    grants = {
        override.permission
        for override in overrides
        if override.effect == IAMUserPermissionEffect.GRANT
    }
    denials = {
        override.permission
        for override in overrides
        if override.effect == IAMUserPermissionEffect.DENY
    }
    return (grants & set(ALL_PERMISSIONS)) - denials


async def require_permission(
    session: AsyncSession,
    user_id: int,
    permission: str,
) -> None:
    """Raise when a user lacks an IAM permission."""

    if permission not in ALL_PERMISSIONS:
        raise InvalidOperationError(
            "Unknown IAM permission",
            details={"permission": permission},
        )
    permissions = await effective_permissions(session, user_id)
    if permission not in permissions:
        raise AuthorizationError(
            "Missing IAM permission",
            details={"permission": permission},
        )


async def grant_bootstrap_permissions(session: AsyncSession, user_id: int) -> None:
    """Grant the first IAM user enough authority to administer IAM."""

    now = datetime.now(UTC)
    for permission in sorted(BOOTSTRAP_PERMISSIONS):
        existing = await repository.get_user_override(session, user_id, permission)
        if existing is not None:
            existing.effect = IAMUserPermissionEffect.GRANT
            existing.changed_by = user_id
            existing.updated_at = now
            await repository.save_override(session, existing)
            continue
        await repository.save_override(
            session,
            IAMUserPermissionOverride(
                user_id=user_id,
                permission=permission,
                effect=IAMUserPermissionEffect.GRANT,
                changed_by=user_id,
            ),
        )
    await session.commit()


async def _can_manage_user_permissions(
    session: AsyncSession,
    *,
    actor_id: int,
    target_user_id: int,
    requested_permissions: set[str] | None = None,
) -> None:
    await require_permission(session, actor_id, "iam.permissions.manage")
    await _ensure_active_user(session, target_user_id)
    if actor_id == target_user_id:
        raise AuthorizationError("Users cannot modify their own IAM permissions")
    if requested_permissions:
        actor_permissions = await effective_permissions(session, actor_id)
        missing = sorted(requested_permissions - actor_permissions)
        if missing:
            raise AuthorizationError(
                "Cannot grant IAM permissions the actor does not have",
                details={"permissions": missing},
            )


async def set_user_permission_overrides(
    session: AsyncSession,
    *,
    actor_id: int,
    target_user_id: int,
    grant: set[str],
    deny: set[str],
    clear: set[str],
) -> None:
    """Apply user-specific IAM permission overrides."""

    unknown = sorted((grant | deny | clear) - ALL_PERMISSIONS)
    if unknown:
        raise InvalidOperationError(
            "Unknown IAM permissions",
            details={"permissions": unknown},
        )
    if grant & deny:
        raise InvalidOperationError("Cannot grant and deny the same permission")
    await _can_manage_user_permissions(
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
        (IAMUserPermissionEffect.GRANT, grant),
        (IAMUserPermissionEffect.DENY, deny),
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
                    IAMUserPermissionOverride(
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


async def read_user_permissions(
    session: AsyncSession,
    user_id: int,
) -> tuple[set[str], set[str], set[str]]:
    """Return grants, denials, and effective IAM permissions for one user."""

    await _ensure_active_user(session, user_id)
    overrides = await repository.list_user_overrides(session, user_id)
    grants = {
        override.permission
        for override in overrides
        if override.effect == IAMUserPermissionEffect.GRANT
    }
    denials = {
        override.permission
        for override in overrides
        if override.effect == IAMUserPermissionEffect.DENY
    }
    return grants, denials, await effective_permissions(session, user_id)
