# ADR: SQLModel vs Pydantic Strategy

**Date:** 2026-05-25
**Status:** Accepted

## Context
The project needs a clear boundary between database entities and API request or response models.

## Alternatives considered
- **Use SQLModel for everything:** Rejected because computed, nested, and validation-heavy API DTOs should not be forced into database table models.
- **Use Pydantic for everything:** Rejected because persisted entities need SQLModel table definitions for SQLAlchemy and Alembic.
- **Use SQLModel for persistence and Pydantic BaseModel for DTOs:** Accepted because it separates database concerns from API concerns.

## Decision
Use `SQLModel(table=True)` for database entities in `models.py`. Use `pydantic.BaseModel` for request and response DTOs in `schemas.py`. Use BaseSettings for environment configuration in `core/config.py`.

## Consequences
- Database models stay aligned with SQLAlchemy and Alembic.
- API DTOs can express computed, nested, or validation-heavy shapes.
- Developers must choose the model type based on whether the data lives in the database or the API.

## Affected components
[[contacts]], [[leads]], [[proposals]], [[pipeline]], [[core]], [[sqlmodel-vs-pydantic]]
