# Renewable Energy CRM Overview

**Scope:** Commercial lifecycle for renewable energy projects from first contact through deal close. Post-sale continuity is out of scope.

## Purpose
The system is a domain-organized modular monolith backend for a renewable energy CRM. It exposes a versioned REST API under `/api/v1/...` and supports an AI agent that consumes the same domain services as the REST API.

## Stack
- **Backend framework:** FastAPI >= 0.115 with Python >= 3.12
- **ORM:** SQLModel >= 0.0.21 with SQLAlchemy 2.x async
- **Migrations:** Alembic using SQLModel metadata
- **Database:** SQLite with aiosqlite for development; PostgreSQL with asyncpg for production
- **Auth:** JWT with `python-jose`, bcrypt with `passlib`, OAuth2 form support with `python-multipart`
- **Agent:** LangGraph and LangChain with AzureOpenAI GPT-5.5 behind `LLMProvider`
- **Logging:** structlog
- **Quality:** ruff, mypy, pre-commit
- **Testing:** pytest, pytest-asyncio, httpx AsyncClient, factory-boy

## Domain Map
| Domain | Path | Responsibility |
|---|---|---|
| [[users]] | `src/domains/users/` | Read-only IAM user and service-access references |
| [[contacts]] | `src/domains/contacts/` | People and organizations: the permanent "who" |
| [[companies]] | `src/domains/companies/` | B2B company contact API facade over contacts |
| [[leads]] | `src/domains/leads/` | Sales opportunities: the bounded "what to sell" |
| [[proposals]] | `src/domains/proposals/` | Technical offer variants per lead |
| [[technical-visits]] | `src/domains/technical_visits/` | Optional on-site visit subprocesses and proposal evidence links |
| [[activities]] | `src/domains/activities/` | Calendar tasks (distinct from lead interactions) |
| [[opportunities]] | `src/domains/opportunities/` | Deferred from v1 UX; use leads for funnel |
| [[pipeline]] | `src/domains/pipeline/` | Stage transitions and immutable audit history |
| [[agent]] | `src/agent/` | LangGraph agent using domain services as tools |
| [[permissions]] | `src/domains/permissions/` | CRM access, permission catalog, role templates, user overrides, and assignment-scoped authorization |
| [[core]] | `src/core/` | Settings, database, security, logging, and exceptions |
| [[api-v1]] | `src/api/v1/` | Versioned router aggregation and shared dependencies |

## API Versioning
All CRM routers are mounted under `/api/v1` by `src/api/v1/router.py`. IAM identity and IAM permission endpoints are exposed by the sibling IAM service, not by CRM.

## Key Decisions
- [[2026-05-25-contact-vs-lead-separation]]
- [[2026-05-25-sqlmodel-vs-pydantic-strategy]]
- [[2026-05-25-llmprovider-abstraction]]
- [[2026-05-25-outcome-lives-in-proposal]]
- [[2026-05-25-sqlite-to-postgres-portability]]
- [[2026-05-25-domain-by-business-not-layer]]
- [[2026-05-28-contact-promoters-and-company-people]]
- [[2026-05-29-technical-visits-as-lead-subprocess]]
- [[2026-06-01-verp-identity-crm-permissions]]
- [[2026-07-06-lead-centric-funnel-opportunities-deferred]]
