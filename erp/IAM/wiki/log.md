# IAM Wiki Log

Append one entry for every documentation or source-code operation.

## Entries

### 2026-08-11 - Expanded IAM test suite to 88% coverage
- **Source:** opencode session (test expansion phase T2.1, quality-gate work)
- **Tests created:** `tests/unit/test_core_security.py`, `tests/unit/test_core_config.py`, `tests/unit/test_core_exceptions.py`, `tests/unit/test_middleware.py`, `tests/integration/test_auth_flows.py`, `tests/integration/test_users_admin.py`, `tests/integration/test_permissions_extra.py`, `tests/integration/test_services_extra.py`
- **Code updated:** `src/iam/api/dependencies.py` (current-user now rejects blacklisted tokens via `auth_service.check_token_valid`, fixing logout not actually revoking access), `src/iam/domains/auth/service.py` (normalize naive `locked_until` to UTC-aware before comparison, fixing `TypeError` on account-lock checks against SQLite/naive timestamps), `tests/conftest.py` (create minimal `crm_user_access` / `crm_user_permission_override` compat tables so the isolated in-memory test DB honors the shared-database contract IAM reads).
- **Validation:** `uv run pytest IAM/tests --cov=IAM/src` → 63 passed, 88% line coverage (gate 70%); `uv run ruff check IAM/src IAM/tests` clean; `uv run ruff format --check` clean; `uv run mypy IAM/src` clean.
- **Notes:** New tests surfaced two genuine bugs (blacklist never consulted on authenticated requests; naive/aware datetime comparison in lockout). Both fixed in source. `SecurityHeadersMiddleware` went from 0% to 100%; `core/security.py`, `core/exceptions.py` at 100%.

### 2026-06-01 - Corrected IAM database ownership
- **Source:** direct user correction
- **Pages created:** [[2026-06-01-iam-shares-verp-database]]
- **Pages updated:** [[overview]], [[core]], [[service-boundaries]], [[index]]
- **Docs updated:** `AGENTS.md`, `docs/tech-spec.md`, `docs/local-rest-quickstart.md`
- **Code updated:** `src/iam/core/config.py`, `alembic.ini`, `alembic/env.py`
- **Database updated:** Applied IAM migration `20260601_0001` to the shared workspace database `ventura.db`. Created backup `ventura.db.before_iam_20260601.bak` before applying the migration.
- **Validation:** `uv run ruff check IAM`, `MYPYPATH=src uv run mypy --cache-dir /private/tmp/iam_mypy_cache --explicit-package-bases src`, `PYTHONPATH=IAM/src uv run pytest IAM/tests`, IAM Alembic `upgrade head`, and IAM Alembic `check`.
- **Notes:** Corrected the earlier wrong assumption that service independence meant a separate IAM database. IAM now uses the shared VERP database by default (`sqlite+aiosqlite:///./ventura.db`). IAM keeps service-local migrations but uses `iam_alembic_version` so it does not conflict with CRM's `alembic_version`. IAM Alembic autogenerate now filters to IAM-owned tables only, ignoring CRM tables in the shared database.

### 2026-06-01 - IAM service initial implementation
- **Source:** direct user request
- **Pages updated:** [[overview]], [[users]], [[auth]], [[permissions]], [[services]], [[api-v1]], [[core]], [[permission-model]], [[bootstrap-flow]]
- **Docs updated:** `docs/tech-spec.md`, `docs/local-rest-quickstart.md`, `docs/local-rest.http`, `docs/rest-json-bodies.md`
- **Code created:** IAM FastAPI app, async DB core, auth/users/permissions/services domains, service-local Alembic environment, initial IAM schema migration, and integration tests.
- **Validation:** `uv run ruff check IAM`, `MYPYPATH=src uv run mypy --explicit-package-bases src`, `PYTHONPATH=IAM/src uv run pytest IAM/tests`, Alembic `upgrade head`, and Alembic `check`.
- **Notes:** Implemented IAM as its own VERP service without touching CRM. The first IAM user bootstraps with explicit IAM grants; later IAM actions require current IAM permissions. Service access supports the initial `crm` service key only and does not assign CRM roles or CRM permissions.

### 2026-06-01 - IAM service documentation bootstrap
- **Source:** direct user request
- **Pages created:** [[overview]], [[users]], [[auth]], [[permissions]], [[services]], [[api-v1]], [[core]], [[2026-06-01-iam-as-verp-service]], [[service-boundaries]], [[permission-model]], [[bootstrap-flow]]
- **Pages updated:** none
- **Notes:** Created the initial IAM service structure as a sibling service of CRM under `VERP/IAM`, with service-specific `AGENTS.md`, wiki index, overview, component pages, decision record, and guides. Documented that IAM owns central VERP users, authentication, IAM permissions, and service access, while CRM owns CRM roles, CRM permissions, and CRM resource scope.
