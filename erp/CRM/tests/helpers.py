"""Test helpers for CRM with IAM-owned users."""

from core.security import create_access_token
from domains.permissions.models import CRMUserAccess, UserRole
from domains.users.models import IAMServiceAccess, User
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_iam_user(
    session: AsyncSession,
    *,
    email: str = "owner@example.com",
    is_active: bool = True,
    crm_service_access: bool = True,
) -> User:
    """Insert an IAM user row for CRM tests."""

    user = User(
        email=email.strip().lower(),
        full_name=email.split("@", maxsplit=1)[0].title(),
        hashed_password="not-used-by-crm",
        is_active=is_active,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    if crm_service_access:
        if user.id is None:
            raise RuntimeError("Test user was not properly saved")
        await grant_iam_crm_service_access(session, user_id=user.id)
    return user


async def grant_iam_crm_service_access(
    session: AsyncSession,
    *,
    user_id: int,
    granted_by: int | None = None,
) -> IAMServiceAccess:
    """Grant IAM service access for CRM in tests."""

    access = IAMServiceAccess(
        user_id=user_id,
        service_key="crm",
        granted_by=user_id if granted_by is None else granted_by,
    )
    session.add(access)
    await session.commit()
    await session.refresh(access)
    return access


async def assign_crm_role(
    session: AsyncSession,
    *,
    user_id: int,
    role: UserRole = UserRole.ADMIN,
    changed_by: int | None = None,
) -> CRMUserAccess:
    """Assign CRM access directly for tests that are not testing role assignment."""

    access = CRMUserAccess(
        user_id=user_id,
        role=role,
        changed_by=user_id if changed_by is None else changed_by,
    )
    session.add(access)
    await session.commit()
    await session.refresh(access)
    return access


async def create_crm_user(
    session: AsyncSession,
    *,
    email: str = "owner@example.com",
    role: UserRole = UserRole.ADMIN,
) -> User:
    """Create an IAM user with IAM CRM access and a CRM role."""

    user = await create_iam_user(session, email=email, crm_service_access=False)
    if user.id is None:
        raise RuntimeError("Test user was not properly saved")
    await grant_iam_crm_service_access(session, user_id=user.id)
    await assign_crm_role(session, user_id=user.id, role=role)
    return user


async def create_crm_user_headers(
    session: AsyncSession,
    *,
    email: str = "owner@example.com",
    role: UserRole = UserRole.ADMIN,
) -> tuple[int, dict[str, str]]:
    """Create a CRM-ready user and return bearer headers."""

    user = await create_crm_user(session, email=email, role=role)
    if user.id is None:
        raise RuntimeError("Test user was not properly saved")
    token = create_access_token(user.id)
    return user.id, {"Authorization": f"Bearer {token}"}
