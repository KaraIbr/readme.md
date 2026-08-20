"""IAM user business logic."""

from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InvalidOperationError,
    NotFoundError,
)
from iam.core.security import hash_password
from iam.domains.permissions import repository as permissions_repository
from iam.domains.permissions import service as permissions_service
from iam.domains.users import repository
from iam.domains.users.models import User
from iam.domains.users.schemas import UserCreate, UserUpdate, normalize_email


async def create_user(
    session: AsyncSession,
    user_create: UserCreate,
) -> User:
    """Create an active central VERP user with a hashed password."""

    email = normalize_email(user_create.email)
    existing = await repository.get_by_email(session, email)
    if existing is not None:
        raise ConflictError("A user with this email already exists")

    user = User(
        email=email,
        full_name=user_create.full_name,
        hashed_password=hash_password(user_create.password),
        is_active=True,
    )
    user = await repository.create(session, user)
    await session.commit()
    return user


async def create_bootstrap_or_permitted_user(
    session: AsyncSession,
    user_create: UserCreate,
    *,
    actor: User | None,
) -> User:
    """Create a central user, allowing only bootstrap or permitted actors."""

    user_count = await repository.count_users(session)
    if user_count == 0:
        user = await create_user(session, user_create)
        if user.id is None:
            raise RuntimeError("Bootstrap user was not properly saved")
        await permissions_service.grant_bootstrap_permissions(session, user.id)
        return user
    if actor is None:
        raise AuthenticationError("Authentication is required to create users")
    if actor.id is None:
        raise RuntimeError("Authenticated actor has no ID")
    await permissions_service.require_permission(session, actor.id, "iam.users.create")
    return await create_user(session, user_create)


async def get_user(session: AsyncSession, user_id: int) -> User:
    """Return a user or raise a domain-level not-found error."""

    user = await repository.get(session, user_id)
    if user is None:
        raise NotFoundError("User not found", details={"user_id": user_id})
    return user


async def get_active_user(session: AsyncSession, user_id: int) -> User:
    """Return an active user or raise an authorization error."""

    user = await get_user(session, user_id)
    if not user.is_active:
        raise AuthorizationError("User account is inactive")
    return user


async def list_users(session: AsyncSession) -> list[User]:
    """Return all central users (for admin listing, no permission check)."""

    return await repository.list_all(session)


async def read_user(
    session: AsyncSession,
    *,
    actor_id: int,
    user_id: int,
) -> User:
    """Read one central user after enforcing IAM user-read permission."""

    await permissions_service.require_permission(session, actor_id, "iam.users.read")
    return await get_user(session, user_id)


async def update_user(
    session: AsyncSession,
    *,
    actor_id: int,
    user_id: int,
    user_update: UserUpdate,
) -> User:
    """Update central user profile fields after enforcing IAM permission."""

    await permissions_service.require_permission(session, actor_id, "iam.users.update")
    user = await get_user(session, user_id)
    updates = user_update.model_dump(exclude_unset=True)
    if "email" in updates and updates["email"] is not None:
        email = normalize_email(updates["email"])
        existing = await repository.get_by_email(session, email)
        if existing is not None and existing.id != user.id:
            raise ConflictError("A user with this email already exists")
        user.email = email
    if "full_name" in updates:
        user.full_name = updates["full_name"]
    if "is_active" in updates:
        await permissions_service.require_permission(session, actor_id, "iam.users.deactivate")
        if actor_id == user_id and not updates["is_active"]:
            raise AuthorizationError("Users cannot deactivate their own account")
        user.is_active = updates["is_active"]
    user.updated_at = datetime.now(UTC)
    user = await repository.save(session, user)
    await session.commit()
    return user


async def delete_user_permanently(
    session: AsyncSession,
    *,
    actor_id: int,
    user_id: int,
) -> User:
    """Permanently delete a user after cleaning up related records."""

    await permissions_service.require_permission(session, actor_id, "iam.users.delete")

    if actor_id == user_id:
        raise AuthorizationError("Users cannot delete their own account")

    user = await get_user(session, user_id)

    # Clean IAM permission overrides
    overrides = await permissions_repository.list_user_overrides(session, user_id)
    for override in overrides:
        await session.delete(override)
    await session.execute(
        text("DELETE FROM iam_user_permission_override WHERE changed_by = :uid"),
        {"uid": user_id},
    )

    # Clean CRM user access + permission overrides (pragmatic: same DB)
    await session.execute(
        text("DELETE FROM crm_user_access WHERE user_id = :uid OR changed_by = :uid"),
        {"uid": user_id},
    )
    await session.execute(
        text("DELETE FROM crm_user_permission_override WHERE user_id = :uid OR changed_by = :uid"),
        {"uid": user_id},
    )

    # Hard delete the user
    await repository.hard_delete(session, user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise InvalidOperationError(
            "User cannot be permanently deleted because they have "
            "active business records (lead/proposal assignments). "
            "Deactivate the user instead."
        )

    return user


async def set_user_active(
    session: AsyncSession,
    *,
    actor_id: int,
    user_id: int,
    is_active: bool,
) -> User:
    """Activate or deactivate a user after enforcing IAM permission."""

    await permissions_service.require_permission(
        session,
        actor_id,
        "iam.users.deactivate",
    )
    if actor_id == user_id and not is_active:
        raise AuthorizationError("Users cannot deactivate their own account")
    user = await get_user(session, user_id)
    user.is_active = is_active
    user.updated_at = datetime.now(UTC)
    user = await repository.save(session, user)
    await session.commit()
    return user
