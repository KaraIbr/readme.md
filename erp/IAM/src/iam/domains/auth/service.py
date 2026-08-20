"""IAM authentication business logic."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession

from iam.core.exceptions import AuthenticationError, AuthorizationError
from iam.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from iam.domains.auth import repository as blacklist_repo
from iam.domains.auth.schemas import TokenPair
from iam.domains.users import repository as users_repository
from iam.domains.users.models import User
from iam.domains.users.schemas import normalize_email
from iam.domains.users.service import get_active_user

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _token_claims(user: User) -> dict[str, Any]:
    return {"email": user.email}


async def _record_failed_attempt(session: AsyncSession, user: User) -> None:
    """Increment failed login attempts and lock account if threshold reached."""

    user.failed_login_attempts += 1
    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = datetime.now(UTC) + timedelta(minutes=LOCKOUT_MINUTES)
    user.updated_at = datetime.now(UTC)
    await users_repository.save(session, user)


async def _check_account_locked(user: User) -> None:
    """Raise if the account is temporarily locked due to too many failed attempts."""

    locked_until = user.locked_until
    if locked_until is None:
        return
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=UTC)
    if datetime.now(UTC) < locked_until:
        remaining = int((locked_until - datetime.now(UTC)).total_seconds())
        raise AuthenticationError(
            f"Account is temporarily locked. Try again in {remaining} seconds.",
        )
    user.locked_until = None
    user.failed_login_attempts = 0


async def _check_token_blacklisted(session: AsyncSession, payload: dict[str, Any]) -> None:
    """Raise if the token's JWT ID is blacklisted."""

    jti = payload.get("jti")
    if jti and await blacklist_repo.is_blacklisted(session, jti):
        raise AuthenticationError("Token has been revoked")


async def authenticate_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
) -> User | None:
    """Validate credentials and return the matching active user."""

    user = await users_repository.get_by_email(session, normalize_email(email))
    if user is None:
        return None

    await _check_account_locked(user)

    if not verify_password(password, user.hashed_password):
        await _record_failed_attempt(session, user)
        await session.commit()
        return None

    if not user.is_active:
        raise AuthorizationError("User account is inactive")

    user.failed_login_attempts = 0
    user.locked_until = None
    user.updated_at = datetime.now(UTC)
    await users_repository.save(session, user)
    await session.commit()

    return user


def issue_token_pair(user: User) -> TokenPair:
    """Issue access and refresh tokens for an authenticated user."""

    if user.id is None:
        raise AuthenticationError("Cannot issue tokens for an unsaved user")
    claims = _token_claims(user)
    return TokenPair(
        access_token=create_access_token(user.id, additional_claims=claims),
        refresh_token=create_refresh_token(user.id, additional_claims=claims),
    )


async def login(
    session: AsyncSession,
    *,
    email: str,
    password: str,
) -> TokenPair:
    """Authenticate credentials and issue a token pair."""

    user = await authenticate_user(session, email=email, password=password)
    if user is None:
        raise AuthenticationError("Invalid email or password")
    return issue_token_pair(user)


async def refresh_token_pair(
    session: AsyncSession,
    refresh_token: str,
) -> TokenPair:
    """Validate a refresh token and return a fresh token pair."""

    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except InvalidTokenError as exc:
        raise AuthenticationError("Invalid refresh token") from exc

    await _check_token_blacklisted(session, payload)

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Invalid refresh token") from exc

    user = await get_active_user(session, user_id)
    return issue_token_pair(user)


async def revoke_token(
    session: AsyncSession,
    token: str,
) -> None:
    """Revoke a token by adding its JWT ID to the blacklist."""

    try:
        payload = decode_token(token, expected_type="access")
    except InvalidTokenError:
        return

    jti = payload.get("jti")
    if not jti:
        return

    exp = payload.get("exp")
    if exp:
        expires_at = datetime.fromtimestamp(exp, tz=UTC)
        await blacklist_repo.add_to_blacklist(session, jti, expires_at)


async def check_token_valid(session: AsyncSession, token: str) -> dict[str, Any]:
    """Decode a token and verify it is not blacklisted. Return the payload."""

    payload = decode_token(token, expected_type="access")
    await _check_token_blacklisted(session, payload)
    return payload
