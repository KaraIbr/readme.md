"""Async SQLModel database wiring for IAM."""

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.core.config import Settings, get_settings
from iam.core.model_registry import import_model_modules

_engine: AsyncEngine | None = None
_engine_url: str | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite+aiosqlite")


def _enable_sqlite_foreign_keys(engine: AsyncEngine) -> None:
    """Ensure every SQLite connection enforces declared foreign keys."""

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(
        dbapi_connection: Any,
        _connection_record: Any,
    ) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()


def build_async_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create a new async engine for the provided settings."""

    settings = settings or get_settings()
    kwargs: dict[str, object] = {
        "echo": settings.database_echo,
        "future": True,
    }

    is_sqlite = _is_sqlite_url(settings.database_url)
    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
        if ":memory:" in settings.database_url:
            kwargs["poolclass"] = StaticPool
    else:
        kwargs["pool_pre_ping"] = True

    engine = create_async_engine(settings.database_url, **kwargs)
    if is_sqlite:
        _enable_sqlite_foreign_keys(engine)
    return engine


def build_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to an engine."""

    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


def get_engine(settings: Settings | None = None) -> AsyncEngine:
    """Return the process-wide async engine."""

    global _engine, _engine_url, _session_factory

    settings = settings or get_settings()
    if _engine is None or _engine_url != settings.database_url:
        _engine = build_async_engine(settings)
        _engine_url = settings.database_url
        _session_factory = None
    return _engine


def get_session_factory(
    settings: Settings | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Return the process-wide async session factory."""

    global _session_factory

    if _session_factory is None:
        _session_factory = build_session_factory(get_engine(settings))
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields an async database session."""

    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def create_all(engine: AsyncEngine | None = None) -> None:
    """Create all registered SQLModel tables for local dev and tests."""

    import_model_modules()
    engine = engine or get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def drop_all(engine: AsyncEngine | None = None) -> None:
    """Drop all registered SQLModel tables for isolated tests."""

    import_model_modules()
    engine = engine or get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)


async def dispose_engine() -> None:
    """Dispose the process-wide engine and reset cached database state."""

    global _engine, _engine_url, _session_factory

    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _engine_url = None
    _session_factory = None
