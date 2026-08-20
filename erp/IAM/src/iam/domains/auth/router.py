"""IAM authentication HTTP router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.api.dependencies import CurrentUser, get_db_session
from iam.core.config import get_settings
from iam.domains.auth import schemas, service

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

COOKIE_ACCESS = "verp_access_token"
COOKIE_REFRESH = "verp_refresh_token"


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set httpOnly secure cookies for tokens."""
    settings = get_settings()
    access_max_age = settings.access_token_expire_minutes * 60
    refresh_max_age = settings.refresh_token_expire_minutes * 60

    response.set_cookie(
        key=COOKIE_ACCESS,
        value=access_token,
        max_age=access_max_age,
        httponly=True,
        secure=not settings.is_development,
        samesite="strict",
        path="/api",
    )
    response.set_cookie(
        key=COOKIE_REFRESH,
        value=refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=not settings.is_development,
        samesite="strict",
        path="/api",
    )


def _clear_auth_cookies(response: Response) -> None:
    """Clear auth cookies."""
    response.delete_cookie(key=COOKIE_ACCESS, path="/api")
    response.delete_cookie(key=COOKIE_REFRESH, path="/api")


def _validate_refresh_origin(request: Request) -> None:
    """CSRF protection: reject refresh if Origin is not a trusted source."""

    origin = request.headers.get("origin")
    if origin:
        settings = get_settings()
        allowed_origins = settings.cors_origins
        if allowed_origins and origin not in allowed_origins:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Origin not allowed",
            )


@router.post("/login", response_model=schemas.TokenPair)
@limiter.limit("5/minute")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TokenPair:
    """Authenticate with OAuth2 password form credentials (rate-limited)."""

    result = await service.login(
        session,
        email=form_data.username,
        password=form_data.password,
    )
    _set_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/refresh", response_model=schemas.TokenPair)
async def refresh_token(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    payload: schemas.RefreshTokenRequest | None = None,
) -> schemas.TokenPair:
    """Rotate a refresh token into a fresh token pair.

    Reads the refresh token from the httpOnly cookie first, falling back
    to the request body for backward compatibility.
    Validates the Origin header as CSRF protection.
    """

    _validate_refresh_origin(request)

    refresh_token_value: str | None = None

    if payload and payload.refresh_token:
        refresh_token_value = payload.refresh_token

    if not refresh_token_value:
        refresh_token_value = request.cookies.get(COOKIE_REFRESH)

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    result = await service.refresh_token_pair(session, refresh_token_value)
    _set_auth_cookies(response, result.access_token, result.refresh_token)
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    _: CurrentUser,
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Logout by blacklisting the token and clearing auth cookies."""

    token = request.cookies.get(COOKIE_ACCESS)
    if token:
        await service.revoke_token(session, token)
        await session.commit()

    _clear_auth_cookies(response)
