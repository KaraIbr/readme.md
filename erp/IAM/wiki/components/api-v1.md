# Component: API v1

**Path:** `src/iam/api/v1/`
**Responsibility:** Owns IAM REST router aggregation under `/api/v1`. It does not implement domain business logic.
**Status:** In development

## Purpose

API v1 provides stable versioned HTTP routing for the IAM service.

## Data Model

API v1 owns no persisted data.

## Public Interface

The implemented public interface is the `api_v1` router.

## Router Endpoints

Implemented router groups:

| Router | Prefix | Responsibility |
|---|---|---|
| users | `/api/v1/users` | Central user lifecycle and current user |
| auth | `/api/v1/auth` | Login and refresh |
| permissions | `/api/v1/permissions` | IAM permission catalog and user overrides |
| services | `/api/v1/services` | Access grants to VERP services |

## Request / Response Schemas

API v1 does not define DTOs directly. DTOs belong to each domain.

## Dependencies

- **Internal:** [[users]], [[auth]], [[permissions]], [[services]]
- **Core:** [[core]]

## Business Rules / Invariants

- Routers call domain services; they do not query repositories directly.
- Authentication dependency resolves the central IAM user.
- Permission checks must be performed by the domain service that owns the action.

## Related Decisions

[[2026-06-01-iam-as-verp-service]]

## Known Technical Debt

None yet.

## Maintainer Notes

Keep route naming independent from CRM. IAM endpoints should not be mounted under CRM.
