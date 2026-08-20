# AGENTS.md - VERP IAM

---

## 1. AGENT ROLE

You are the knowledge maintainer for the `VERP/IAM` service: the VERP identity,
authentication, user administration, central permission, and service-access backend.

Your responsibilities:
- Read raw sources from `raw/` and compile them into wiki pages under `wiki/`
- Keep knowledge connected using [[wiki-links]]
- Answer questions by citing existing wiki pages, never by guessing
- Log every operation in `wiki/log.md`
- Keep IAM boundaries separate from service-specific business rules such as CRM Leads,
  Proposals, TechnicalVisits, price rules, or CRM role scopes

**Never modify files in `raw/`. They are immutable.**
**Never invent information that is not present in a source or in the wiki.**

---

## 2. DIRECTORY STRUCTURE

```text
IAM/
|
|-- AGENTS.md                  <- This file
|-- main.py                    <- Local service launcher
|
|-- raw/                       <- Immutable sources (do NOT edit)
|   |-- decisions/
|   |-- components/
|   |-- tech-debt/
|   |-- postmortems/
|   `-- guides/
|
|-- docs/                      <- Human-facing service docs and REST examples
|   |-- tech-spec.md
|   |-- local-rest-quickstart.md
|   |-- local-rest.http
|   `-- rest-json-bodies.md
|
|-- src/
|   `-- iam/
|       |-- api/
|       |   |-- dependencies.py
|       |   `-- v1/
|       |       |-- __init__.py
|       |       `-- router.py
|       |-- core/
|       |   |-- config.py
|       |   |-- database.py
|       |   |-- exceptions.py
|       |   |-- logging.py
|       |   |-- model_registry.py
|       |   `-- security.py
|       `-- domains/
|           |-- users/
|           |-- auth/
|           |-- permissions/
|           `-- services/
|
|-- tests/
|   |-- integration/
|   `-- unit/
|
`-- wiki/                      <- Compiled knowledge maintained by the agent
    |-- index.md
    |-- log.md
    |-- overview.md
    |-- components/
    |-- decisions/
    |-- guides/
    |-- tech-debt/
    `-- postmortems/
```

---

## 3. SESSION START (always read first)

At the start of every IAM session, without exception:

1. Read `wiki/index.md` to know what exists
2. Read `wiki/log.md` (last 20 entries) to know what changed recently
3. Read the wiki pages relevant to the current task
4. Treat the wiki as project memory

If work touches another VERP service, read that service's `AGENTS.md` and relevant wiki
pages too. For CRM work, read `../CRM/AGENTS.md`.

---

## 4. SERVICE CONTEXT

### Workspace Position

`VERP` is the workspace containing services. It does not run as one monolithic API by
itself. Each service has its own launcher, endpoints, documentation, wiki, and tests.

IAM is a sibling service of CRM:

```text
VERP/
|-- IAM/
`-- CRM/
```

IAM owns central identity and access concerns. CRM owns renewable-energy commercial
workflow and CRM-specific authorization.

### Stack

Use the same backend stack conventions as the rest of VERP unless a later decision
changes them:

- **Framework:** FastAPI, async throughout
- **ORM:** SQLModel with SQLAlchemy 2.x async
- **Migrations:** Alembic per service
- **DB:** Shared VERP database. SQLite + aiosqlite at `./ventura.db` for dev,
  PostgreSQL + asyncpg for prod. IAM must not create a separate physical database.
- **Auth:** JWT via `python-jose`, password hashing via `passlib`
- **Quality:** `ruff`, `mypy`, `pytest`, `pytest-asyncio`

IAM owns IAM tables and migrations, but not a separate database file. When using a
service-local Alembic environment against the shared database, IAM must use its own
Alembic version table, `iam_alembic_version`, so it does not conflict with CRM's
workspace Alembic history.

### Domains

| Domain | Path | Responsibility |
|---|---|---|
| `users` | `src/iam/domains/users/` | Central VERP user accounts and lifecycle |
| `auth` | `src/iam/domains/auth/` | Login, refresh, token issuance, current user |
| `permissions` | `src/iam/domains/permissions/` | IAM permission catalog and user permission overrides |
| `services` | `src/iam/domains/services/` | Access grants to VERP services such as CRM |
| `core` | `src/iam/core/` | Config, DB, security helpers, logging, exceptions |
| `api/v1` | `src/iam/api/v1/` | HTTP aggregation layer and versioned routes |

### Boundary Rules

- IAM creates and manages central VERP users.
- IAM authenticates users and issues tokens.
- IAM grants central permissions such as `iam.users.create`.
- IAM grants access to services such as `crm`.
- IAM does not define CRM roles (`admin`, `manager`, `sales`, `tech`).
- IAM does not define CRM permissions such as `crm.leads.read`.
- IAM does not know CRM resource rules such as assigned Leads, assigned Proposals,
  TechnicalVisits, or Proposal price fields.
- CRM may assign CRM roles and CRM permission overrides only for users that exist in IAM.

### Layer Dependency Rule

```text
router -> service -> repository -> models
   |          ^
schemas      may call other domain services
```

- `router.py` only knows `service.py` and `schemas.py`. It does not query directly.
- `service.py` owns business logic and calls repositories.
- `repository.py` is the only layer that writes SQLModel/SQLAlchemy queries.
- `models.py` imports only SQLModel/SQLAlchemy primitives and Python builtins.
- `schemas.py` uses Pydantic DTOs for request and response shapes.

---

## 5. PAGE TYPES

### 5.1 `wiki/overview.md`

The service overview. It must include:
- Purpose and scope
- Boundary with CRM and future services
- Domain map
- API versioning strategy
- Links to key decisions and guides

### 5.2 `wiki/components/`

One page per domain, module, or subsystem.

Template:

```markdown
# Component: [Name]

**Path:** `src/iam/...`
**Responsibility:** What it owns and what it does not own.
**Status:** Planned | In development | Stable | Deprecated

## Purpose

## Data model

## Public interface

## Router endpoints

## Request / Response schemas

## Dependencies

## Business rules / invariants

## Related decisions

## Known technical debt

## Maintainer notes
```

Initial component pages:
- `users.md`
- `auth.md`
- `permissions.md`
- `services.md`
- `api-v1.md`
- `core.md`

### 5.3 `wiki/decisions/`

Architecture Decision Records.

Template:

```markdown
# ADR: [Decision title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded by [[adr-name]]

## Context

## Alternatives considered

## Decision

## Consequences

## Affected components
```

Initial decision:
- `2026-06-01-iam-as-verp-service.md`

### 5.4 `wiki/guides/`

Operational and engineering guides.

Initial guides:
- `service-boundaries.md`
- `permission-model.md`
- `bootstrap-flow.md`

### 5.5 `wiki/tech-debt/`

Known debt, limitations, and deliberate deferrals.

### 5.6 `wiki/postmortems/`

Incident or design failure records.

---

## 6. INITIAL IAM DESIGN

### User Model

The central user must be identity-only:

```text
User
- id
- email
- full_name
- hashed_password
- is_active
- created_at
- updated_at
```

Never store CRM roles or CRM permissions on the central `User`.

### IAM Permission Model

Initial IAM permissions:

```text
iam.users.create
iam.users.read
iam.users.update
iam.users.deactivate
iam.permissions.read
iam.permissions.manage
iam.services.read
iam.services.manage
```

Permissions are user-level grants/denials. Roles may be added later only if there is a
clear IAM-level use case.

### Service Access Model

IAM should track whether a user can access a VERP service.

```text
ServiceAccess
- id
- user_id
- service_key
- is_active
- granted_by
- created_at
- updated_at
```

Initial service key:

```text
crm
```

Service access means "the user may enter CRM." It does not mean "the user is a CRM
admin" or "the user can read all Leads." CRM handles those rules.

### Bootstrap Rule

If no users exist, IAM allows unauthenticated creation of the first user. That user
receives initial IAM permission grants:

```text
iam.users.create
iam.users.read
iam.users.update
iam.users.deactivate
iam.permissions.read
iam.permissions.manage
iam.services.read
iam.services.manage
```

After the first user, user creation requires `iam.users.create`.

There is no `is_platform_admin` shortcut.

---

## 7. RECOGNIZED COMMANDS

| Command | Action |
|---|---|
| `/status` | Summary of wiki pages and recent log entries |
| `/audit` | Audit wiki consistency and missing links |
| `/new-page wiki/type/name.md` | Create an empty page using the right template |

---

## 8. LOGGING RULE

Every operation that creates, updates, or deletes IAM documentation or source code must
append an entry to `wiki/log.md`.
