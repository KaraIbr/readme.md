"""Shared FastAPI dependencies."""

from collections.abc import AsyncIterator
from typing import Annotated

from core.database import get_session
from core.exceptions import AuthenticationError
from core.security import InvalidTokenError, decode_token
from domains.users.models import User
from domains.users.service import get_active_user
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

COOKIE_ACCESS = "verp_access_token"


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session."""

    async for session in get_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def resolve_access_token(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> str | None:
    """Resolve access token from Authorization header or httpOnly cookie."""
    if token:
        return token
    return request.cookies.get(COOKIE_ACCESS)


AccessToken = Annotated[str | None, Depends(resolve_access_token)]


async def get_current_user(
    token: AccessToken,
    session: DbSession,
) -> User:
    """Resolve the authenticated CRM user from a bearer access token."""

    if token is None:
        raise AuthenticationError("Authentication required")

    try:
        payload = decode_token(token, expected_type="access")
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Invalid authentication credentials") from exc

    return await get_active_user(session, user_id)


CurrentUser = Annotated[User, Depends(get_current_user)]
