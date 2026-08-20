"""Alembic migration environment."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from core.config import get_settings
from core.model_registry import import_model_modules
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import_model_modules()
target_metadata = SQLModel.metadata

IAM_OWNED_TABLES = {
    "iam_alembic_version",
    "iam_service_access",
    "iam_user",
    "iam_user_permission_override",
}


def _database_url() -> str:
    return get_settings().database_url


def _is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def include_object(
    object_: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Ignore IAM-owned tables in CRM migration autogenerate checks."""

    if type_ == "table":
        return name not in IAM_OWNED_TABLES
    table = getattr(object_, "table", None)
    return not (table is not None and table.name in IAM_OWNED_TABLES)


def run_migrations_offline() -> None:
    """Run migrations without opening a database connection."""

    url = _database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=_is_sqlite_url(url),
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations against an existing connection."""

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=_is_sqlite_url(_database_url()),
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""

    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = _database_url()
    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations with an async database connection."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
