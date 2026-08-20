"""IAM authentication request and response DTOs."""

from typing import Literal

from pydantic import BaseModel, Field


class TokenPair(BaseModel):
    """JWT access and refresh tokens returned after authentication."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request body for rotating an access token from a refresh token."""

    refresh_token: str | None = Field(default=None, min_length=1)
