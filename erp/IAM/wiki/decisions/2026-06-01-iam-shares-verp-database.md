# ADR: IAM Shares The VERP Database

**Date:** 2026-06-01
**Status:** Accepted

## Context

VERP is a workspace containing independently started services such as CRM and IAM.
CRM already uses the workspace-root development database `ventura.db`, and CRM
documentation states that this database can be shared by future services.

IAM is a separate service, but that separation is about API, code ownership,
documentation, tests, and domain boundaries. It is not a requirement for a separate
physical database.

## Alternatives Considered

- Give IAM a separate database file such as `IAM/iam.db`.
- Store IAM tables in the shared VERP database while keeping IAM as its own service.

## Decision

IAM uses the shared VERP database. In local development the default URL is:

```text
sqlite+aiosqlite:///./ventura.db
```

IAM owns IAM tables and IAM migrations, but not a separate database file. Since IAM
and CRM share the same physical database while using separate Alembic environments,
IAM uses `iam_alembic_version` as its Alembic version table.

## Consequences

- IAM and CRM can reference the same central user identities in one database.
- Local development continues to use one workspace database file.
- IAM migrations can be run independently without overwriting CRM's Alembic version
  row.
- A future multi-database architecture would require a new explicit ADR.

## Affected Components

- [[core]]
- [[users]]
- [[permissions]]
- [[services]]
- [[service-boundaries]]
