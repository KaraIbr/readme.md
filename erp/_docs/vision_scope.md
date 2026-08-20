# VERP Vision and Scope

## Purpose

VERP is the logical workspace for a suite of backend services used by companies that sell and install renewable-energy systems, primarily photovoltaic systems and energy storage systems. The product direction is an integrated operating platform that supports the full business lifecycle around renewable-energy projects while keeping each major capability in an independently runnable service.

VERP itself is not a single monolithic API. It is the container for service APIs that share conventions, identity, documentation standards, tests, and a common database. Each service owns its startup, endpoints, domain model, migrations, local documentation, and operational boundary.

## Architecture Direction

The current architecture is service-oriented inside one repository:

```text
VERP/
|-- IAM/
|-- CRM/
|-- _docs/
|-- alembic/
|-- ventura.db
`-- main.py
```

Each service is expected to remain independently understandable and independently startable. Services may interact through shared identity, shared persisted references, and future service-to-service contracts. The repository-level documentation in `_docs/` is intentionally broad: it gives engineers a fast mental model of the platform. Service-specific details remain in each service's own `docs/` and `wiki/` directories.

## Shared Database

All current services share the same physical database. In local development this is the SQLite file:

```text
./ventura.db
```

The shared database does not erase service ownership. IAM owns IAM tables and IAM migration history. CRM owns CRM tables and CRM migration history. Foreign keys are used where services need stable references, especially from CRM business tables to central IAM users.

In production, the intended equivalent is a shared VERP PostgreSQL database unless a later architecture decision explicitly changes that.

## Current Services

### IAM

IAM is the central identity and access-management service for VERP. It owns:

- Central human user accounts.
- Password authentication and token issuance.
- Account active/inactive state.
- IAM-level permissions for central administration.
- Access grants to VERP services, currently including `crm`.

IAM does not own CRM business roles or CRM resource authorization. For example, IAM can say that user `12` exists and has active access to the `crm` service. CRM then decides whether that user is an admin, manager, sales user, or technical user and which records that user can access.

IAM runs as its own FastAPI service and mounts endpoints under `/api/v1`.

### CRM

CRM is the first functional VERP business service. It covers the commercial lifecycle for renewable-energy opportunities from first contact through deal close. It currently owns:

- Contacts, promoters, company representatives, and contact profiles.
- Leads as bounded sales opportunities.
- Lead project documents, electricity bills, and sales interactions.
- Proposals as concrete technical and commercial offer variants.
- PV and BESS proposal detail records.
- Technical visits, visit assignees, visit attachments, and proposal-to-visit evidence links.
- Pipeline stage transitions and immutable transition history.
- CRM-specific roles, permissions, user overrides, and assignment-scoped resource authorization.
- A read-oriented CRM AI agent that uses the same domain services and authorization rules as REST endpoints.

CRM relies on IAM for user identity, bearer tokens, account status, and service access. CRM owns its own authorization model after IAM service access has been granted.

## Service Boundary Principles

1. Each service owns its business language.
2. Each service exposes its own API surface under its own application startup.
3. Each service owns its own domain modules, tests, docs, wiki, and migrations.
4. Cross-service user references should point to central IAM users by stable `iam_user.id` values.
5. Mutable permissions should be checked from current database state, not treated as permanent JWT truth.
6. Service-specific permissions should stay in the service that owns the business action.
7. Shared database tables should not become shared ownership tables. A table has one owning service even if another service references it.

## Documentation Map

Use these repository-level documents for orientation:

| Document | Purpose |
|---|---|
| `_docs/vision_scope.md` | Platform vision, service boundaries, and current service map |
| `_docs/iam.md` | General IAM service explanation |
| `_docs/crm.md` | General CRM service explanation |
| `_docs/venturadb.md` | Technical data dictionary for the shared database |

Use the service-local documentation for deeper implementation details:

| Service | Documentation |
|---|---|
| IAM | `IAM/docs/` and `IAM/wiki/` |
| CRM | `CRM/docs/` and `CRM/wiki/` |

## Current Scope

The current VERP scope is limited to IAM and CRM. Future services should be added to this document when they become real service boundaries with their own startup, API, data ownership, and documentation.

Potential future services may cover installation execution, procurement, inventory, engineering design, finance, customer portals, monitoring, or post-sale support. Those areas are not part of the current implemented scope unless a future service introduces them.

## Out of Scope Today

- VERP as a single combined backend API.
- Post-sale project execution outside CRM's commercial close.
- A separate physical database per service.
- Runtime administration of permission catalogs and role templates through seeded database tables.
- Formal cross-service token introspection or JWKS validation. Current development uses shared JWT validation configuration.

## Operational Notes

On a fresh local database, apply IAM migrations before CRM migrations because CRM tables reference IAM users:

```bash
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
PYTHONPATH=CRM/src uv run python -m alembic upgrade head
```

IAM and CRM can then be started independently from the repository root:

```bash
uv run python IAM/main.py
uv run python CRM/main.py
```
