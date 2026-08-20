# IAM Local REST Quickstart

Run these commands from the VERP root.

## 1. Apply Migrations

IAM migrations run against the shared VERP development database at `./ventura.db`.
They do not create a separate `IAM/iam.db` file.

```bash
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
```

## 2. Start IAM

```bash
uv run python IAM/main.py
```

The local service listens on `http://127.0.0.1:8100`.

## 3. Bootstrap First User

Create the first user with `POST /api/v1/users/`. If no users exist, this request does
not need a bearer token. The created user receives all current IAM permissions as
explicit grants.

## 4. Login

Use `POST /api/v1/auth/login` with OAuth2 form data:

```text
username=owner@example.com&password=correct-password
```

Copy the returned `access_token` into the `Authorization: Bearer <token>` header for
protected requests.

## 5. Create Users And Grant Access

After bootstrap:
- Creating more users requires `iam.users.create`.
- Changing IAM permission overrides requires `iam.permissions.manage`.
- Granting or revoking service access requires `iam.services.manage`.

Use `POST /api/v1/services/users/{user_id}/access` with `{"service_key": "crm"}` to
let a central user enter the CRM service. CRM still decides that user's CRM role and
CRM permissions later.

The first-user bootstrap is documented in `wiki/guides/bootstrap-flow.md`.
