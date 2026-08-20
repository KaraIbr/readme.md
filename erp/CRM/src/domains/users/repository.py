"""Read-only repository helpers for IAM users and service access."""

from domains.users.models import IAMServiceAccess, User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get(session: AsyncSession, user_id: int) -> User | None:
    """Load one IAM user by id."""

    return await session.get(User, user_id)


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """Load one IAM user by normalized email."""

    result = await session.exec(select(User).where(User.email == email))
    return result.first()


async def get_service_access(
    session: AsyncSession,
    *,
    user_id: int,
    service_key: str,
) -> IAMServiceAccess | None:
    """Load an IAM service-access row for one user and service."""

    result = await session.exec(
        select(IAMServiceAccess).where(
            IAMServiceAccess.user_id == user_id,
            IAMServiceAccess.service_key == service_key,
        )
    )
    return result.first()
