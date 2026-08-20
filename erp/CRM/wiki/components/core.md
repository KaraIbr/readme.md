# Subsystem: Core

**Path:** `src/core/`
**Responsibility:** Owns cross-cutting infrastructure: config, database, security, logging, and exception handling.
**Status:** In development

## Purpose
Core provides shared application infrastructure used by the API, domains, and agent.

## Data model
Core does not own CRM business entities. Database metadata comes from SQLModel models in the domain modules and is used by Alembic.

## Public interface (service.py)
Core is organized by infrastructure module:
- `config.py`: typed `Settings` using Pydantic BaseSettings and `get_settings()`, including `document_storage_path` for uploaded CRM files
- `database.py`: async engine/session factory builders, process-wide database dependencies, SQLite foreign-key enforcement, and table bootstrap helpers
- `model_registry.py`: imports every persisted model module before SQLModel metadata operations such as Alembic autogenerate and local test bootstrap
- `security.py`: JWT access/refresh token helpers and password hashing/verification helpers
- `logging.py`: `configure_logging()` and `get_logger()` for structlog setup
- `exceptions.py`: application exception classes and `register_exception_handlers()` for FastAPI

No `service.py` interface is specified for core.

## Router endpoints
Core does not expose a domain router in the technical specification.

## Request / Response schemas (schemas.py)
Core does not own API DTOs in the technical specification.

## Dependencies
- **Internal:** none specified
- **Core:** not applicable

## Business rules / invariants
- Environment variables and application settings use BaseSettings.
- Uploaded lead, proposal, and technical visit files use the configured `document_storage_path`; local upload directories are ignored by git.
- The development database uses SQLite with aiosqlite at the workspace root as `ventura.db` by default, so multiple VERP services can share one local database.
- Production can use PostgreSQL with asyncpg by changing `DATABASE_URL` and running migrations.
- SQLite application connections enable `PRAGMA foreign_keys=ON`, so declared foreign keys are enforced during local development and tests.
- Alembic is initialized at the repository root with an initial CRM schema migration; new schema changes should be delivered as versioned migrations.
- Structured logging uses structlog.
- Validation exception details are sanitized before JSON response serialization so Pydantic validator context errors remain readable and serializable.

## Related decisions
[[2026-05-25-sqlite-to-postgres-portability]], [[2026-05-25-sqlmodel-vs-pydantic-strategy]]

## Known technical debt
None documented.

## Maintainer notes
Keep cross-cutting infrastructure here. Domain business rules belong in domain services.
The initial core implementation lives under `CRM/src/core/` and is covered by focused unit tests in `CRM/tests/unit/core/`.
