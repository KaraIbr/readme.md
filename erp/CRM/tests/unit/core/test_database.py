import pytest
from core.config import Settings
from core.database import build_async_engine, build_session_factory
from pydantic import SecretStr
from sqlmodel import select


@pytest.mark.asyncio
async def test_session_factory_executes_queries() -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key=SecretStr("super-secret-for-tests"),
    )
    engine = build_async_engine(settings)

    try:
        session_factory = build_session_factory(engine)
        async with session_factory() as session:
            result = await session.exec(select(1))

        assert result.one() == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_sqlite_connections_enforce_foreign_keys() -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key=SecretStr("super-secret-for-tests"),
    )
    engine = build_async_engine(settings)

    try:
        session_factory = build_session_factory(engine)
        async with session_factory() as session:
            connection = await session.connection()
            result = await connection.exec_driver_sql("PRAGMA foreign_keys")

        assert result.scalar_one() == 1
    finally:
        await engine.dispose()
