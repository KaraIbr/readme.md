# Component: Core

**Path:** `src/iam/core/`
**Responsibility:** Owns IAM cross-cutting infrastructure: config, database, security helpers, exceptions, logging, and model registry.
**Status:** In development

## Purpose

Core provides infrastructure shared by IAM domains without containing business rules.

## Data Model

Core owns no business tables.

## Public Interface

Implemented modules:
- `config.py` - service settings
- `database.py` - async engine and session factory
- `security.py` - password hashing and JWT helpers
- `exceptions.py` - service exception types and FastAPI handlers
- `logging.py` - structured logging setup
- `model_registry.py` - imports persisted models for migrations and `create_all`

IAM also has its own Alembic configuration under `IAM/alembic`.

The default IAM database URL is the shared VERP development database:

```text
sqlite+aiosqlite:///./ventura.db
```

IAM must not create a separate `IAM/iam.db` database. Its Alembic environment uses
the `iam_alembic_version` version table so IAM migration history can coexist with
CRM migration history in `ventura.db`.

IAM Alembic autogenerate checks include only IAM-owned tables from IAM metadata.
Existing CRM tables in the shared database are ignored by IAM migrations.

## Router Endpoints

None.

## Request / Response Schemas

None.

## Dependencies

Core should not import IAM domain services.

## Business Rules / Invariants

- Core helpers must stay domain-agnostic.
- Security helpers must not know CRM or service-specific roles.
- Database helpers must import models through a registry, not through domain side effects.
- IAM shares the VERP physical database with CRM while owning only IAM tables.

## Related Decisions

[[2026-06-01-iam-as-verp-service]]

## Known Technical Debt

- Development startup currently calls `create_all`; migrations are still the contract for durable schema changes.

## Maintainer Notes

If a helper needs to know a permission key or service key, it probably belongs outside core.
