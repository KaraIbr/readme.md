# IAM Technical Specification

## Status

Initial IAM service implementation is complete for local development and automated
tests. CRM integration is intentionally not included in this step.

## Purpose

IAM is the VERP service for central users, authentication, IAM permissions, and service access. It is a sibling service of CRM, not a module inside CRM.

## Structure

```text
IAM/
|-- main.py
|-- alembic.ini
|-- alembic/
|-- src/iam/
|   |-- api/
|   |-- core/
|   `-- domains/
|       |-- users/
|       |-- auth/
|       |-- permissions/
|       `-- services/
|-- tests/
|-- docs/
`-- wiki/
```

## Data Model

IAM stores its tables in the shared VERP database. For local development that database
is the workspace-root SQLite file `ventura.db`. IAM must not create or depend on
`IAM/iam.db`.

| Table | Purpose |
|---|---|
| `iam_user` | Central VERP user account, password hash, and active state |
| `iam_user_permission_override` | Explicit per-user IAM permission grant or denial |
| `iam_service_access` | Per-user access grant to a VERP service key such as `crm` |

IAM users do not include CRM roles, CRM permissions, or service-specific admin flags.

## Endpoint Groups

| Prefix | Responsibility |
|---|---|
| `/api/v1/users` | Central user lifecycle |
| `/api/v1/auth` | Login, refresh, and logout placeholder |
| `/api/v1/permissions` | IAM permission catalog and overrides |
| `/api/v1/services` | Access to VERP services such as CRM |

## Auth

`POST /api/v1/auth/login` accepts OAuth2 password-form fields:

```text
username=<email>&password=<password>
```

Successful login returns bearer access and refresh tokens. JWTs identify the IAM user
id. Mutable permissions are not embedded as authority in the token; endpoints check
current database state.

## Bootstrap

When no users exist, `POST /api/v1/users/` can create the first user without auth.
That user receives explicit grants for all current IAM permissions. After bootstrap,
creating users requires `iam.users.create`.

## IAM Permission Catalog

| Permission | Meaning |
|---|---|
| `iam.users.create` | Create central VERP users |
| `iam.users.read` | Read central VERP users |
| `iam.users.update` | Update central VERP users |
| `iam.users.deactivate` | Activate or deactivate central users |
| `iam.permissions.read` | Read IAM permission catalog and user IAM state |
| `iam.permissions.manage` | Grant, deny, or clear IAM permission overrides |
| `iam.services.read` | Read service access |
| `iam.services.manage` | Grant or revoke service access |

Guardrails:
- Users cannot modify their own IAM permissions.
- Users cannot grant permissions they do not have.
- Unknown permission keys are rejected.

## Service Access

Initial service catalog:

| Key | Meaning |
|---|---|
| `crm` | Renewable-energy CRM service |

Service access answers whether a central IAM user may enter a service. The target
service still owns its own roles, permissions, and resource scopes.

## Migrations

IAM has its own Alembic environment under `IAM/alembic`, but it runs against the
shared VERP database:

```text
sqlite+aiosqlite:///./ventura.db
```

Because CRM and IAM share the same physical database while keeping service-local
migration histories, IAM uses `iam_alembic_version` as its Alembic version table.
CRM keeps the default workspace `alembic_version` table.

IAM Alembic autogenerate checks are filtered to IAM-owned tables only. CRM tables are
intentionally ignored by the IAM migration environment even though they live in the
same database.

Run from the VERP root:

```bash
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
```

## Tests

Run IAM tests from the VERP root:

```bash
PYTHONPATH=IAM/src uv run pytest IAM/tests
```

## Boundary

IAM owns central users and access to services. CRM owns CRM roles, CRM permissions, and CRM resource scopes over those central users.
