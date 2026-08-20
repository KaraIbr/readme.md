"""Integration-test helpers for CRM API auth."""

from domains.permissions.models import UserRole
from fastapi import FastAPI
from helpers import create_crm_user_headers


async def auth_headers(
    app: FastAPI,
    *,
    email: str = "owner@example.com",
    role: UserRole = UserRole.ADMIN,
) -> tuple[int, dict[str, str]]:
    """Create a CRM-ready IAM user and return bearer headers."""

    session_factory = app.state.session_factory
    async with session_factory() as session:
        return await create_crm_user_headers(session, email=email, role=role)
