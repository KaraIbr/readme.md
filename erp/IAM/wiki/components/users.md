# Component: Users

**Path:** `src/iam/domains/users/`
**Responsibility:** Owns central VERP user accounts and account lifecycle. It does not own service-specific roles or permissions.
**Status:** In development

## Purpose

Users are the shared human accounts for VERP services. CRM and future services reference IAM users by id, but they do not create their own separate user accounts.

## Data Model

Implemented entity:

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

The central `User` must not contain CRM role fields, CRM permission fields, or service-specific shortcuts.

## Public Interface

Implemented service functions:
- `create_user(...) -> User` - creates a central user with a hashed password
- `create_bootstrap_or_permitted_user(...) -> User` - allows first-user bootstrap or permission-checked user creation
- `get_user(user_id) -> User` - loads one user or raises not found
- `get_active_user(user_id) -> User` - loads one active user or rejects inactive accounts
- `update_user(...) -> User` - updates allowed profile/account fields
- `set_user_active(...) -> User` - activates or deactivates a user without deleting history

## Router Endpoints

Implemented endpoints:

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/users/` | Create a central VERP user |
| GET | `/api/v1/users/me` | Return the authenticated user |
| GET | `/api/v1/users/{user_id}` | Read one central user |
| PATCH | `/api/v1/users/{user_id}` | Update central user profile/account fields |
| POST | `/api/v1/users/{user_id}/activate` | Activate a user |
| POST | `/api/v1/users/{user_id}/deactivate` | Deactivate a user |

## Request / Response Schemas

Implemented DTOs:
- `UserCreate`
- `UserRead`
- `UserUpdate`

## Dependencies

- **Internal:** [[permissions]]
- **Core:** [[core]], [[api-v1]]

## Business Rules / Invariants

- Email is normalized before persistence and login lookup.
- Passwords are stored only as hashes.
- Inactive users cannot authenticate or act as `current_user`.
- The first user bootstrap rule is documented in [[bootstrap-flow]].
- Creating users after bootstrap requires `iam.users.create`.
- Updating or deactivating users requires IAM permissions, not CRM permissions.

## Related Decisions

[[2026-06-01-iam-as-verp-service]]

## Known Technical Debt

- Password reset/change and user list pagination are not implemented yet.

## Maintainer Notes

Keep this component identity-only. Service access belongs to [[services]]. IAM permissions belong to [[permissions]]. CRM roles and CRM permissions belong to CRM.
