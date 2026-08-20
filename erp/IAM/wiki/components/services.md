# Component: Services

**Path:** `src/iam/domains/services/`
**Responsibility:** Owns access grants from central users to VERP services such as CRM. It does not own service-specific roles or permissions.
**Status:** In development

## Purpose

Service access answers whether a central VERP user may enter a service. It does not answer what the user can do inside that service.

Example:

```text
IAM says: user 12 has access to crm.
CRM says: user 12 has role sales and can read only assigned Leads.
```

## Data Model

Implemented entity:

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

Initial service keys:

```text
crm
```

## Public Interface

Implemented service functions:
- `grant_service_access(user_id, service_key, actor_id) -> ServiceAccess`
- `revoke_service_access(user_id, service_key, actor_id) -> None`
- `user_has_service_access(user_id, service_key) -> bool`
- `list_user_service_access(user_id) -> list[ServiceAccess]`
- `list_services() -> dict[str, str]`

## Router Endpoints

Implemented endpoints:

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/services/` | List known VERP service keys |
| GET | `/api/v1/services/users/{user_id}` | List service access for one user |
| POST | `/api/v1/services/users/{user_id}/access` | Grant access to one service |
| DELETE | `/api/v1/services/users/{user_id}/access/{service_key}` | Revoke access to one service |

## Request / Response Schemas

Implemented DTOs:
- `ServiceRead`
- `ServiceAccessCreate`
- `ServiceAccessRead`

## Dependencies

- **Internal:** [[users]], [[permissions]]
- **Core:** [[core]]

## Business Rules / Invariants

- Granting service access requires `iam.services.manage`.
- Reading service access requires `iam.services.read`.
- Only known service keys can be granted.
- Service keys are normalized to lowercase.
- Service access is not a role.
- Service access is not a permission inside the target service.
- Revocation should not delete business history in target services.

## Related Decisions

[[2026-06-01-iam-as-verp-service]]

## Known Technical Debt

- Cross-service enforcement mechanism is not implemented yet. CRM will need to verify IAM service access before accepting a user as active in CRM.

## Maintainer Notes

Keep service keys stable and lowercase. Prefer `crm`, not display names such as `CRM Renewables`.
