"""CRM read-side access to IAM users."""

from core.exceptions import AuthorizationError, NotFoundError
from domains.users import repository
from domains.users.models import User
from sqlmodel.ext.asyncio.session import AsyncSession

CRM_SERVICE_KEY = "crm"


async def get_user(session: AsyncSession, user_id: int) -> User:
    """Return an IAM user or raise not found."""

    user = await repository.get(session, user_id)
    if user is None:
        raise NotFoundError("User not found", details={"user_id": user_id})
    return user


async def get_active_user(session: AsyncSession, user_id: int) -> User:
    """Return an active IAM user or reject the request."""

    user = await get_user(session, user_id)
    if not user.is_active:
        raise AuthorizationError("User account is inactive")
    return user


async def user_has_crm_service_access(
    session: AsyncSession,
    user_id: int,
) -> bool:
    """Return whether IAM grants this user access to CRM."""

    await get_active_user(session, user_id)
    access = await repository.get_service_access(
        session,
        user_id=user_id,
        service_key=CRM_SERVICE_KEY,
    )
    return access is not None and access.is_active


async def require_crm_service_access(session: AsyncSession, user_id: int) -> None:
    """Reject users who do not have IAM service access for CRM."""

    if not await user_has_crm_service_access(session, user_id):
        raise AuthorizationError("User does not have IAM access to CRM")
