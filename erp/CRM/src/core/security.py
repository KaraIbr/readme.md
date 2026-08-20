"""Password hashing and JWT helpers."""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from core.config import Settings, get_settings
from jose import JWTError, jwt
from passlib.context import CryptContext

TokenType = Literal["access", "refresh"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _jwt_secret(settings: Settings) -> str:
    """Return the configured JWT secret, raising a clear error if it is not set."""

    if settings.jwt_secret_key is None:
        raise RuntimeError("JWT_SECRET_KEY is not configured")
    return settings.jwt_secret_key.get_secret_value()


class InvalidTokenError(ValueError):
    """Raised when a JWT cannot be decoded or does not match expectations."""


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return whether a plaintext password matches a stored hash."""

    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    subject: str | int,
    *,
    token_type: TokenType,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create a signed JWT for a subject."""

    settings = settings or get_settings()
    issued_at = datetime.now(UTC)
    if expires_delta is None:
        minutes = (
            settings.access_token_expire_minutes
            if token_type == "access"
            else settings.refresh_token_expire_minutes
        )
        expires_delta = timedelta(minutes=minutes)

    payload: dict[str, Any] = {
        **(additional_claims or {}),
        "sub": str(subject),
        "type": token_type,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": issued_at + expires_delta,
    }
    return jwt.encode(
        payload,
        _jwt_secret(settings),
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(
    subject: str | int,
    *,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create an access token."""

    return create_token(
        subject,
        token_type="access",
        settings=settings,
        expires_delta=expires_delta,
        additional_claims=additional_claims,
    )


def create_refresh_token(
    subject: str | int,
    *,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create a refresh token."""

    return create_token(
        subject,
        token_type="refresh",
        settings=settings,
        expires_delta=expires_delta,
        additional_claims=additional_claims,
    )


def decode_token(
    token: str,
    *,
    expected_type: TokenType | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Decode and validate a JWT payload."""

    settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            _jwt_secret(settings),
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise InvalidTokenError("Invalid or expired token") from exc

    token_type = payload.get("type")
    if expected_type is not None and token_type != expected_type:
        raise InvalidTokenError(f"Expected {expected_type} token")

    if not payload.get("sub"):
        raise InvalidTokenError("Token subject is missing")

    return payload
