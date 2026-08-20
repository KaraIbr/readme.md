"""Shared IAM test fixtures."""

import sys
from collections.abc import AsyncIterator
from pathlib import Path

# ruff: noqa: E402 - IAM/src must be on sys.path before iam imports below.

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from iam.api.dependencies import get_db_session
from iam.api.v1 import api_v1
from iam.core.config import Settings, get_settings
from iam.core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from iam.core.exceptions import register_exception_handlers
from iam.domains.auth.router import limiter as auth_limiter

auth_limiter.enabled = False


async def _ensure_crm_compat_tables(engine: object) -> None:
    """Create the minimal CRM tables IAM reads from the shared VERP database.

    Production runs against one shared database that already contains CRM tables.
    The isolated in-memory test database only knows IAM models, so create the two
    tables IAM touches (via raw SQL) to keep the shared-database contract honest.
    """

    from sqlalchemy import text

    async with engine.begin() as connection:  # type: ignore[attr-defined]
        await connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS crm_user_access ("
                "id INTEGER PRIMARY KEY,"
                "user_id INTEGER NOT NULL,"
                "role VARCHAR(50),"
                "changed_by INTEGER,"
                "created_at DATETIME,"
                "updated_at DATETIME)"
            )
        )
        await connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS crm_user_permission_override ("
                "id INTEGER PRIMARY KEY,"
                "user_id INTEGER NOT NULL,"
                "changed_by INTEGER,"
                "created_at DATETIME,"
                "updated_at DATETIME)"
            )
        )


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Return an isolated IAM API client backed by an in-memory database."""

    settings = Settings(
        environment="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key="test-secret-key-for-iam",
        dev_bootstrap_enabled=False,
    )
    engine = build_async_engine(settings)
    session_factory = build_session_factory(engine)
    await create_all(engine)
    await _ensure_crm_compat_tables(engine)

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(api_v1)

    async def override_get_db_session() -> AsyncIterator[object]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async def override_get_settings() -> Settings:
        return settings

    app.dependency_overrides[get_settings] = override_get_settings
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client

    await drop_all(engine)
    await engine.dispose()
