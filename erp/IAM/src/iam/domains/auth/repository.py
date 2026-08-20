"""Token blacklist data access functions."""

from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.domains.auth.models import TokenBlacklist


async def add_to_blacklist(
    session: AsyncSession,
    jti: str,
    expires_at: datetime,
) -> TokenBlacklist:
    """Persist a revoked token JWT ID."""

    entry = TokenBlacklist(jti=jti, expires_at=expires_at)
    session.add(entry)
    await session.flush()
    return entry


async def is_blacklisted(session: AsyncSession, jti: str) -> bool:
    """Return whether a JWT ID has been revoked."""

    result = await session.exec(select(TokenBlacklist).where(TokenBlacklist.jti == jti))
    return result.first() is not None


async def clean_expired(session: AsyncSession) -> int:
    """Remove blacklist entries whose expires_at has passed. Returns count removed."""

    now = datetime.now()
    result = await session.exec(select(TokenBlacklist).where(TokenBlacklist.expires_at <= now))
    entries = result.all()
    for entry in entries:
        await session.delete(entry)
    await session.flush()
    return len(entries)
