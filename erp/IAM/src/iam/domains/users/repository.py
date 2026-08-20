"""IAM user data access functions."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.domains.users.models import User


async def create(session: AsyncSession, user: User) -> User:
    """Persist a new user and refresh database-populated fields."""

    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def get(session: AsyncSession, user_id: int) -> User | None:
    """Return a user by primary key."""

    return await session.get(User, user_id)


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """Return a user by normalized email."""

    result = await session.exec(select(User).where(User.email == email))
    return result.first()


async def count_users(session: AsyncSession) -> int:
    """Return the number of persisted users."""

    result = await session.exec(select(User.id))
    return len(result.all())


async def list_all(session: AsyncSession) -> list[User]:
    """Return all persisted users ordered by creation time."""

    result = await session.exec(select(User).order_by(User.created_at.desc()))  # type: ignore[attr-defined]
    return list(result.all())


async def hard_delete(session: AsyncSession, user: User) -> None:
    """Permanently remove a user from the database."""

    await session.delete(user)


async def save(session: AsyncSession, user: User) -> User:
    """Persist changes to an existing user."""

    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user
