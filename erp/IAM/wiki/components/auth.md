# Component: Auth

**Path:** `src/iam/domains/auth/`
**Responsibility:** Owns authentication, token issuance, token refresh, and current-user resolution. It does not own user profile lifecycle or service-specific authorization.
**Status:** In development

## Purpose

Auth verifies credentials and issues tokens that identify a central IAM user. Authorization decisions must still be made from current IAM and service-specific state rather than long-lived role claims.

## Data Model

No dedicated persisted model is required for the first implementation.

Future persisted models may be added for:
- Refresh-token revocation
- Session audit
- Login attempts

## Public Interface

Implemented service functions:
- `authenticate_user(email, password) -> User | None`
- `issue_token_pair(user) -> TokenPair`
- `refresh_token_pair(refresh_token) -> TokenPair`

## Router Endpoints

Implemented endpoints:

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | OAuth2 password-form login |
| POST | `/api/v1/auth/refresh` | Refresh an access token |
| POST | `/api/v1/auth/logout` | Logout placeholder; persisted revocation is deferred |

`GET /api/v1/users/me` may live in [[users]] while using auth dependencies.

## Request / Response Schemas

Implemented DTOs:
- `TokenPair`
- `RefreshTokenRequest`

Login uses OAuth2 form fields:

```text
username=<email>&password=<password>
```

## Dependencies

- **Internal:** [[users]]
- **Core:** [[core]]

## Business Rules / Invariants

- Access tokens identify the user id.
- Mutable permissions should not be treated as permanent JWT truth.
- Login must not reveal whether email or password failed.
- Inactive users cannot receive tokens.
- Refresh tokens must be type-checked separately from access tokens.

## Related Decisions

[[2026-06-01-iam-as-verp-service]]

## Known Technical Debt

- Logout currently acknowledges the request with `204` but does not revoke JWTs.
- Persisted refresh-token/session revocation is not implemented yet.

## Maintainer Notes

Do not put CRM roles or CRM service permissions into token claims unless they are short-lived cache hints and still revalidated by the owning service.
