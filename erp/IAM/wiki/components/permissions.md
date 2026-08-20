# Component: Permissions

**Path:** `src/iam/domains/permissions/`
**Responsibility:** Owns IAM-level permission catalog and user-specific IAM permission overrides. It does not own CRM permissions or CRM roles.
**Status:** In development

## Purpose

IAM permissions authorize central VERP actions such as creating users, managing IAM permissions, and granting access to services.

CRM permissions are intentionally separate and live in the CRM service.

## Data Model

Implemented entity:

```text
IAMUserPermissionOverride
- id
- user_id
- permission
- effect: grant | deny
- changed_by
- created_at
- updated_at
```

Initial permission catalog:

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

## Public Interface

Implemented service functions:
- `effective_permissions(user_id) -> set[str]`
- `require_permission(user_id, permission) -> None`
- `set_user_permission_overrides(...) -> None`
- `read_user_permissions(user_id) -> tuple[set[str], set[str], set[str]]`
- `grant_bootstrap_permissions(user_id) -> None`

## Router Endpoints

Implemented endpoints:

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/permissions/` | List IAM permission catalog |
| GET | `/api/v1/permissions/users/{user_id}` | Read one user's IAM permission state |
| PATCH | `/api/v1/permissions/users/{user_id}` | Grant, deny, or clear IAM permission overrides |

## Request / Response Schemas

Implemented DTOs:
- `PermissionRead`
- `UserPermissionsRead`
- `UserPermissionPatch`

## Dependencies

- **Internal:** [[users]]
- **Core:** [[core]]

## Business Rules / Invariants

- IAM permissions govern IAM actions only.
- A user cannot grant IAM permissions they do not have.
- A user cannot modify their own IAM permissions.
- User-specific denies override user-specific grants for the same key.
- Unknown permission keys are rejected.
- The first IAM user receives all initial IAM permissions as explicit grants.
- CRM cannot satisfy IAM permission checks.

## Related Decisions

[[2026-06-01-iam-as-verp-service]]

## Known Technical Debt

- IAM roles are intentionally deferred. Start with explicit user grants/denials.
- The permission catalog may later move from code-defined constants to seeded database rows.

## Maintainer Notes

Avoid generic `admin` booleans. Central authority must be expressed as explicit permission keys.
