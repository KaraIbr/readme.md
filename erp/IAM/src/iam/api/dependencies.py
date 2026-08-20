"""Shared FastAPI dependencies for IAM."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.core.database import get_session
from iam.core.exceptions import AuthenticationError
from iam.core.security import InvalidTokenError
from iam.domains.auth import service as auth_service
from iam.domains.users.models import User
from iam.domains.users.service import get_active_user

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
    """Resolve the authenticated IAM user from a bearer access token."""

    if token is None:
        raise AuthenticationError("Authentication required")

    try:
        payload = await auth_service.check_token_valid(session, token)
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Invalid authentication credentials") from exc

    return await get_active_user(session, user_id)


CurrentUser = Annotated[User, Depends(get_current_user)]
