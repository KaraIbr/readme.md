# IAM REST JSON Bodies

## Users

### POST `/users/`

```json
{
  "email": "owner@example.com",
  "password": "correct-password",
  "full_name": "Owner User"
}
```

### PATCH `/users/{user_id}`

```json
{
  "email": "new.email@example.com",
  "full_name": "New Display Name"
}
```

Both fields are optional.

## Auth

### POST `/auth/login`

Login uses `application/x-www-form-urlencoded`, not JSON:

```text
username=owner@example.com&password=correct-password
```

### POST `/auth/refresh`

```json
{
  "refresh_token": "paste-refresh-token-here"
}
```

## Permissions

### PATCH `/permissions/users/{user_id}`

```json
{
  "grant": ["iam.users.create"],
  "deny": [],
  "clear": []
}
```

`grant`, `deny`, and `clear` accept IAM permission keys only. Unknown keys are rejected.

## Services

### POST `/services/users/{user_id}/access`

```json
{
  "service_key": "crm"
}
```
