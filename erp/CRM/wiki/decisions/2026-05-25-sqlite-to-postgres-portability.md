# ADR: SQLite to PostgreSQL Portability

**Date:** 2026-05-25
**Status:** Accepted

## Context
The project uses SQLite for local development and PostgreSQL for production.

## Alternatives considered
- **Maintain separate model or business logic paths per database:** Rejected because it increases complexity and divergence.
- **Use SQLModel, SQLAlchemy async, and Alembic with database URL configuration:** Accepted because switching engines can be handled through environment configuration and migrations.

## Decision
Use SQLite with aiosqlite in development and PostgreSQL with asyncpg in production. Switching database engines requires updating `DATABASE_URL` and running `alembic upgrade head`; it should not require model, schema, or business logic changes.

## Consequences
- Database portability is an explicit design constraint.
- Migrations must remain compatible with the supported engines.
- Database-specific behavior should not leak into business logic.

## Affected components
[[core]], [[sqlmodel-vs-pydantic]]
