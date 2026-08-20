# Guide: SQLModel vs Pydantic

## Rule
Use SQLModel for what lives in the database. Use Pydantic BaseModel for what lives in the API.

| Situation | Tool | Location |
|---|---|---|
| DB table exposed as-is | `SQLModel(table=True)` | `models.py` |
| Response with computed or nested fields | `pydantic.BaseModel` | `schemas.py` |
| Request body with complex validation | `pydantic.BaseModel` | `schemas.py` |
| Env vars and config | `BaseSettings` | `core/config.py` |

## Examples From The Spec
- `Proposal`, `Contact`, and `Lead` are SQLModel table entities.
- `ProposalWithROI`, `PipelineSummary`, `CreateProposalRequest`, and `CloseLeadRequest` are examples of DTO shapes.
- `Settings` in `core/config.py` uses BaseSettings.

## Related Decisions
[[2026-05-25-sqlmodel-vs-pydantic-strategy]]

## Related Components
[[contacts]], [[leads]], [[proposals]], [[pipeline]], [[core]]
