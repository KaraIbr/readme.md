"""Alembic migration environment for IAM."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from iam.core.config import get_settings
from iam.core.model_registry import import_model_modules
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
target_table_names = set(target_metadata.tables)


def _database_url() -> str:
    return get_settings().database_url


def _is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def _version_table() -> str:
    return config.get_main_option("version_table") or "iam_alembic_version"


def include_object(
    object_: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Limit IAM autogenerate checks to IAM-owned tables."""

    if type_ == "table":
        return name in target_table_names
    table = getattr(object_, "table", None)
    if table is not None:
        return table.name in target_table_names
    return True


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
        version_table=_version_table(),
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
        version_table=_version_table(),
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
