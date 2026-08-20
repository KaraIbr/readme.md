# Guide: IAM Permission Model

## Purpose

IAM permissions authorize central VERP actions. They do not authorize CRM actions.

## Initial Permissions

| Permission | Meaning |
|---|---|
| `iam.users.create` | Create central VERP users |
| `iam.users.read` | Read central VERP users |
| `iam.users.update` | Update central VERP users |
| `iam.users.deactivate` | Activate or deactivate users |
| `iam.permissions.read` | Read IAM permission catalog and user permission state |
| `iam.permissions.manage` | Grant, deny, or clear IAM permission overrides |
| `iam.services.read` | Read service access |
| `iam.services.manage` | Grant or revoke service access |

## Effective Permissions

The current implementation uses explicit user grants and denials stored in
`iam_user_permission_override`:

```text
effective_permissions = user_grants - user_denies
```

IAM roles are intentionally deferred. Add them only if central IAM administration needs templates later.

## Guardrails

- Unknown permission keys are rejected.
- A user cannot grant permissions they do not have.
- A user cannot modify their own IAM permissions.
- CRM permissions cannot satisfy IAM permission checks.
- IAM permissions cannot satisfy CRM permission checks.

## Management Endpoint

Use `PATCH /api/v1/permissions/users/{user_id}`:

```json
{
  "grant": ["iam.users.create"],
  "deny": [],
  "clear": []
}
```

The actor must have `iam.permissions.manage`. Any permission listed in `grant` must
already be present in the actor's effective IAM permissions.

## Bootstrap

The first user receives all initial IAM permissions as explicit grants. See [[bootstrap-flow]].
