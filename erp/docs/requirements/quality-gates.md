# Quality Gates

Measured coverage baseline and the fixed thresholds that CI enforces on every pull request.
Thresholds only change by explicit decision, documented below.

## Baseline (measured)

| Suite | Command | Tests | Coverage | Date |
|---|---|---|---|---|
| CRM backend | `uv run pytest --cov=CRM/src` | 82 | 78% | 2026-08-11 |
| IAM backend | `uv run pytest IAM/tests --cov=IAM/src` | 5 | 71% | 2026-08-11 |
| Frontend | `npm run test:coverage` | 345 | 20.2% (lines) | 2026-08-11 |

Notes:
- CRM and IAM run in separate pytest invocations because both services define the
  same table names (`iam_user`, `iam_service_access`) in the same global
  `SQLModel.metadata`. They cannot coexist in one process; this mirrors production,
  where each service runs in its own process.
- Frontend coverage is measured across `src/features`, `src/shared`, `src/lib` and
  `src/services` (see `frontend/vite.config.ts`).

## Fixed gates (enforced in CI on PR)

| Suite | Threshold | Enforcement |
|---|---|---|
| CRM backend | `--cov-fail-under=75` | `scripts/test-backend.ps1`, `ci.yml` |
| IAM backend | `--cov-fail-under=70` | `scripts/test-backend.ps1`, `ci.yml` |
| Frontend | thresholds `lines = 20, statements = 15, functions = 35, branches = 6` | `frontend/vite.config.ts`, `ci.yml` |

- Backend gates are meaningful immediately (set just below the measured baseline to
  avoid blocking on incidental new code).
- The frontend gate now reflects the T2.1 logic test suite (permissions, schemas,
  services, query and mutation hooks, constants and shared utilities): 345 tests,
  20.2% lines. It was raised from the placeholder floor (0.1%) by explicit decision
  and is reviewed each quarter.

## Running the gates locally

```powershell
# Full backend suite with coverage gates (CRM + IAM)
scripts\test-backend.ps1

# Frontend suite with coverage gate
scripts\test-frontend.ps1
```

## Raising or lowering a threshold

1. Open a change to this document and the corresponding config (`pyproject.toml`
   does not hold thresholds; they live in `scripts/test-backend.ps1` and
   `frontend/vite.config.ts`).
2. State the measured coverage before and after.
3. Merge only through a PR with the CI gate green.

## Not quality gates

- Playwright E2E: runs in CI but is non-blocking until it proves stable (Semana 2).
- Locust load smoke: manual, on-demand, not part of CI (`scripts/load/`).
