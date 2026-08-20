# Local REST API Quickstart

This guide is for local manual testing from the repository root, without setting
`PYTHONPATH`. The CRM service has its own launcher so the repository root can
remain neutral when more services are added.

## Start the API

On a fresh shared database, apply IAM migrations before CRM migrations:

```bash
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
PYTHONPATH=CRM/src uv run python -m alembic upgrade head
```

```bash
uv run python CRM/main.py
```

Alternative:

```bash
uv run uvicorn CRM.main:app --reload
```

The development app creates the local SQLite tables on startup. The default
database file is `ventura.db` in the repository root so other VERP services can share the same local SQLite database.

Open the interactive docs at:

```text
http://127.0.0.1:8000/docs
```

## Minimal flow

1. Start IAM and create/login the user through IAM (`http://127.0.0.1:8100/api/v1/auth/login`).
2. In IAM, grant the user service access for `crm`.
3. Copy the IAM `access_token`.
4. In CRM, bootstrap CRM access once with `POST /api/v1/permissions/users/{your_user_id}/role` and body `{"role": "admin"}`.
5. Send CRM requests with `Authorization: Bearer <access_token>`.
6. Create records in this order: contact, lead, proposal.

CRM no longer exposes `/api/v1/identity/...` endpoints. User creation, login, IAM permissions, and service access belong to the sibling `IAM/` service.

Ready-to-paste requests are in `CRM/docs/local-rest.http`.
All request body examples are cataloged in `CRM/docs/rest-json-bodies.md`.
