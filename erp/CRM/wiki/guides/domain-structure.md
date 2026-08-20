# Guide: Domain Structure

## Rule
Each CRM business domain follows the same 5-file pattern.

| File | Responsibility |
|---|---|
| `models.py` | SQLModel entities persisted in the database |
| `schemas.py` | Pydantic DTOs for requests and responses |
| `repository.py` | Async SQLModel or SQLAlchemy queries only |
| `service.py` | Business logic and orchestration |
| `router.py` | APIRouter mounted by API v1 |

## Layer Dependency Rule
```text
router -> service -> repository -> models
   |          ^
schemas      may call same-domain or other-domain services
```

## Constraints
- `router.py` only knows `service.py` and `schemas.py`.
- `router.py` never queries the database directly.
- `service.py` orchestrates business logic and calls repositories.
- `service.py` may call other domain services.
- `repository.py` is the only layer that writes SQLModel or SQLAlchemy queries.
- `models.py` imports only SQLModel and Python builtins or standard types.

## Related Decisions
[[2026-05-25-domain-by-business-not-layer]]

## Related Components
[[users]], [[contacts]], [[leads]], [[proposals]], [[pipeline]], [[api-v1]]
