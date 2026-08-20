# VERP IAM Overview

**Scope:** Central identity, authentication, IAM permissions, and service access for VERP services.

## Purpose

IAM is a standalone VERP service. It owns central users and access concerns shared by CRM and future services. It exposes its own API, has its own service documentation, and starts independently from CRM.

VERP is the workspace that contains services. VERP itself does not run as one backend API. A workspace-level script may later start IAM, CRM, and any other services together.

## Database Boundary

IAM is an independent service, but it does not own a separate physical database. In
local development IAM uses the shared VERP SQLite database at `./ventura.db`, the same
database file used by CRM. In production IAM should point to the shared VERP
PostgreSQL database unless a later architecture decision explicitly changes that.

IAM separation is expressed through service-owned tables, code, API, docs, wiki, and
migrations, not through `IAM/iam.db`.

## Service Boundary

IAM owns:
- Central VERP users
- Authentication and token issuance
- Account active/inactive state
- IAM permission grants and denials
- Access grants to VERP services such as CRM

IAM does not own:
- CRM roles such as `admin`, `manager`, `sales`, or `tech`
- CRM permissions such as `crm.leads.read`
- CRM resource scopes such as assigned Leads, Proposals, or TechnicalVisits
- Proposal price rules or commercial workflow rules

CRM depends on IAM users, but CRM owns its own roles and permissions over those users.

## Domain Map

| Component | Path | Responsibility |
|---|---|---|
| [[users]] | `src/iam/domains/users/` | Central VERP user accounts and lifecycle |
| [[auth]] | `src/iam/domains/auth/` | Login, token refresh, token issuance, current user |
| [[permissions]] | `src/iam/domains/permissions/` | IAM permission catalog and per-user permission overrides |
| [[services]] | `src/iam/domains/services/` | Access grants to VERP services such as CRM |
| [[api-v1]] | `src/iam/api/v1/` | Versioned router aggregation |
| [[core]] | `src/iam/core/` | Config, DB, security, exceptions, logging |

## API Versioning

IAM endpoints are mounted under `/api/v1` inside the IAM service.

Implemented endpoint groups:
- `/api/v1/users`
- `/api/v1/auth`
- `/api/v1/permissions`
- `/api/v1/services`

## Bootstrap Summary

When no IAM users exist, `POST /api/v1/users/` may create the first user without authentication. That first user receives explicit IAM permission grants. After bootstrap, central user creation requires `iam.users.create`.

There is no `is_platform_admin` flag.

## Current Implementation

IAM now includes:
- Async SQLModel database wiring and a service-local Alembic environment.
- Central user lifecycle endpoints.
- OAuth2 password login, refresh tokens, and bearer-token current-user resolution.
- Code-defined IAM permission catalog with per-user grant/deny overrides.
- Service-access grants for the initial service key `crm`.
- Integration tests for bootstrap, auth, permissions, and service access.

CRM integration is not part of this IAM-only implementation step.

## Key Decisions

- [[2026-06-01-iam-as-verp-service]]
- [[2026-06-01-iam-shares-verp-database]]

## Guides

- [[service-boundaries]]
- [[permission-model]]
- [[bootstrap-flow]]
