# Component: IAM User Reference

**Path:** `src/domains/users/`
**Responsibility:** Provides read-only references to IAM users for CRM authentication, foreign keys, ownership, assignments, and audit fields. It does not create users, authenticate passwords, issue tokens, or manage IAM permissions.
**Status:** In development

## Purpose
CRM operates over users created by the sibling IAM service. CRM needs to resolve the authenticated user id in bearer tokens and validate that the referenced IAM user is active, but user lifecycle belongs to IAM.

`src/domains/users/` is therefore a CRM-local reference domain for the shared `iam_user` table. It replaces the incorrect `src/verp/identity/` module that previously lived inside CRM.

## Data Model
The CRM reference model maps to the IAM-owned table:

```text
iam_user
- id
- email
- full_name
- hashed_password
- is_active
- created_at
- updated_at
```

CRM treats this table as externally owned. IAM migrations create and evolve it. CRM models can point foreign keys at `iam_user.id` for integrity, but CRM code must not expose user creation or password-login endpoints.

CRM also reads IAM service access for the `crm` service key from IAM-owned `iam_service_access` when deciding whether a user may enter CRM.

## Public Interface
Implemented service functions:
- `get_user(session, user_id) -> User` - load an IAM user or raise not found.
- `get_active_user(session, user_id) -> User` - load an active IAM user or reject inactive accounts.
- `user_has_crm_service_access(session, user_id) -> bool` - read IAM service access for `crm`.
- `require_crm_service_access(session, user_id) -> None` - reject users without active IAM service access.

## Router Endpoints
None. CRM does not mount identity or IAM permission endpoints.

User creation, login, refresh, IAM permission overrides, and service-access grants are IAM service endpoints.

## Request / Response Schemas
CRM users reference exposes no public request bodies. Public user DTOs belong to IAM.

## Dependencies
- **Core:** [[core]], [[api-v1]]
- **External service:** IAM owns user lifecycle, authentication, IAM permissions, and service access.

## Business Rules / Invariants
- CRM accepts bearer tokens issued by IAM using the shared JWT configuration.
- JWT subject resolves to `iam_user.id`.
- Inactive IAM users cannot act in CRM.
- A user must have active IAM service access for service key `crm` before CRM role/permission access is valid.
- CRM role assignment and CRM permission overrides are handled only by [[permissions]].

## Related Decisions
[[2026-06-01-verp-identity-crm-permissions]]

## Known Technical Debt
- Cross-service token validation is currently shared-secret JWT validation. A later hardening pass may move this to JWKS or an IAM introspection endpoint.

## Maintainer Notes
Do not add user registration, password login, refresh, or IAM permission administration here. Those belong to the sibling `IAM/` service.
