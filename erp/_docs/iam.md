# IAM Service Overview

## Purpose

IAM is the VERP service responsible for central identity, authentication, IAM-level authorization, and access grants to VERP services. It is a sibling service to CRM, not a CRM module and not a repository-root API.

The service exists so CRM and future VERP services can share one stable human identity model without duplicating user accounts or coupling future services to CRM internals.

## Service Boundary

IAM owns:

- Central VERP user accounts.
- Password verification and JWT token issuance.
- Account active/inactive state.
- IAM permission grants and denials.
- Access grants to service keys such as `crm`.
- IAM-owned tables and IAM migration history inside the shared VERP database.

IAM does not own:

- CRM roles such as `ADMIN`, `MANAGER`, `SALES`, or `TECH`.
- CRM permission keys such as `crm.leads.read`.
- CRM resource scopes such as assigned Leads, Proposals, or TechnicalVisits.
- CRM business lifecycle rules or proposal pricing rules.

The intended cross-service contract is simple: IAM can determine whether a user exists, is active, can authenticate, and has access to a service. The target service determines what the user can do inside that service.

## Code Structure

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

IAM follows the same broad pattern as the rest of VERP: domain code is separated from core infrastructure and versioned API aggregation.

## Runtime

IAM is a FastAPI application. The API router is mounted under:

```text
/api/v1
```

Local startup from the VERP root:

```bash
uv run python IAM/main.py
```

The local IAM quickstart documents the service at:

```text
http://127.0.0.1:8100
```

## Domain Components

### Users

The users domain owns central VERP user accounts. The persisted table is `iam_user`, with fields for email, full name, password hash, active state, and timestamps.

Important rules:

- Email is normalized before persistence and login lookup.
- Passwords are stored only as hashes.
- Inactive users cannot authenticate or act as the current user.
- The first user can be created without authentication only while the system has no users.
- After bootstrap, creating users requires the `iam.users.create` permission.
- User records must not contain CRM roles, CRM permissions, or service-specific shortcuts.

Main endpoints:

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/users/` | Create a central VERP user |
| GET | `/api/v1/users/me` | Read the authenticated IAM user |
| GET | `/api/v1/users/{user_id}` | Read a central user |
| PATCH | `/api/v1/users/{user_id}` | Update central user profile/account fields |
| POST | `/api/v1/users/{user_id}/activate` | Activate a user |
| POST | `/api/v1/users/{user_id}/deactivate` | Deactivate a user |

### Auth

The auth domain verifies credentials and issues token pairs. Login uses OAuth2 password form fields rather than JSON:

```text
username=<email>&password=<password>
```

JWTs identify the IAM user id. Mutable authorization state is intentionally checked from the database by the owning service rather than treated as permanent token authority.

Main endpoints:

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/auth/login` | Login and receive bearer access and refresh tokens |
| POST | `/api/v1/auth/refresh` | Refresh an access token |
| POST | `/api/v1/auth/logout` | Logout placeholder; persisted token revocation is deferred |

### Permissions

The permissions domain owns IAM-level permission keys and explicit per-user overrides stored in `iam_user_permission_override`.

Current IAM permission catalog:

| Permission | Meaning |
|---|---|
| `iam.users.create` | Create central VERP users |
| `iam.users.read` | Read central VERP users |
| `iam.users.update` | Update central VERP users |
| `iam.users.deactivate` | Activate or deactivate central VERP users |
| `iam.permissions.read` | Read IAM permission catalog and user permission state |
| `iam.permissions.manage` | Grant, deny, or clear IAM permission overrides |
| `iam.services.read` | Read VERP service access |
| `iam.services.manage` | Grant or revoke VERP service access |

Effective IAM permissions are computed from explicit grants and denials:

```text
effective_permissions = user_grants - user_denies
```

Important rules:

- Unknown IAM permission keys are rejected.
- A user cannot modify their own IAM permissions.
- A user cannot grant IAM permissions they do not already have.
- IAM permissions cannot satisfy CRM permission checks.
- CRM permissions cannot satisfy IAM permission checks.

Main endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/permissions/` | List IAM permission catalog |
| GET | `/api/v1/permissions/users/{user_id}` | Read a user's IAM permission state |
| PATCH | `/api/v1/permissions/users/{user_id}` | Grant, deny, or clear IAM permission overrides |

### Services

The services domain owns access grants from central users to VERP services. Service access is stored in `iam_service_access`.

Current service catalog:

| Service key | Meaning |
|---|---|
| `crm` | Renewable-energy CRM service |

Service access is not a role and not a permission inside the target service. It answers only whether the user may enter the service.

Main endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/services/` | List known VERP service keys |
| GET | `/api/v1/services/users/{user_id}` | List service access rows for a user |
| POST | `/api/v1/services/users/{user_id}/access` | Grant access to a service |
| DELETE | `/api/v1/services/users/{user_id}/access/{service_key}` | Revoke access to a service |

## Bootstrap Flow

When no IAM users exist, `POST /api/v1/users/` may create the first user without a bearer token. That first user receives explicit grants for all current IAM permissions.

After the first user exists:

1. User creation requires `iam.users.create`.
2. IAM permission changes require `iam.permissions.manage`.
3. Service access changes require `iam.services.manage`.

There is no `is_platform_admin` boolean. Central authority is represented by explicit permission keys so it can be granted and removed per user.

The typical CRM onboarding sequence is:

1. Create the first IAM user.
2. Login through IAM and obtain a bearer token.
3. Grant that IAM user access to service key `crm`.
4. Assign the user's CRM role inside CRM.

## Database Ownership

IAM stores its data in the shared VERP database. In local development this is:

```text
sqlite+aiosqlite:///./ventura.db
```

IAM owns these tables:

| Table | Purpose |
|---|---|
| `iam_user` | Central VERP user account and password hash |
| `iam_user_permission_override` | Explicit IAM permission grant or denial per user |
| `iam_service_access` | Active/inactive access grant to a VERP service key |
| `iam_alembic_version` | IAM migration version table |

IAM uses its own Alembic environment under `IAM/alembic` and tracks migration history in `iam_alembic_version` so it can coexist with CRM's migration history in the same database.

Run IAM migrations from the VERP root:

```bash
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
```

## Integration With CRM

CRM consumes IAM users as externally owned identities. CRM references `iam_user.id` in owner, creator, assignment, and audit fields. CRM also checks active IAM service access for `crm` before treating CRM role and permission records as valid.

Current development uses shared JWT validation configuration between IAM and CRM. A future hardening pass may move this to JWKS or an IAM introspection endpoint.

## Known Technical Debt

- Logout returns success but does not persist refresh-token or session revocation yet.
- IAM roles are intentionally deferred. Current central authorization uses explicit per-user grants and denials.
- The IAM permission catalog and service catalog are code-defined rather than stored in seeded database tables.
- Development startup can call `create_all`; migrations remain the durable schema contract.

## Where To Go Deeper

Read the IAM service-local documentation:

| Path | Use |
|---|---|
| `IAM/docs/tech-spec.md` | Technical specification |
| `IAM/docs/local-rest-quickstart.md` | Local REST workflow |
| `IAM/docs/rest-json-bodies.md` | Request body examples |
| `IAM/wiki/` | Component pages, guides, and ADRs |
