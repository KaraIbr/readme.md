# Renewable Energy CRM — Technical Specification

## Overview

Python backend built as a **domain-organized modular monolith**, exposing a versioned REST API (`/api/v1/...`). Covers the commercial lifecycle of renewable energy projects from first contact through to deal close — either a sale or a loss — with no post-sale continuity.

The system includes an intelligent agent powered by **AzureOpenAI with GPT-5.5**, abstracted behind an `LLMProvider` interface so the model or provider can be swapped in the future without touching agent logic.

The frontend is a React.js SPA that consumes the REST API (out of scope for this document).

---

## Architecture

The project follows a standard Python **`src/` layout** organized **by business domain** (not by technical layer). Each domain is a self-contained module with its own model, schemas, repository, service, and router. The `api/v1/` layer aggregates all domain routers under a versioned prefix.

### Folder Structure

```
CRM/
├── pyproject.toml
├── alembic.ini
├── .env.example
├── README.md
│
├── alembic/                          # Database migrations
│   ├── env.py                        # Uses SQLModel.metadata as target
│   └── versions/
│
├── src/
│   ├── __init__.py
│   ├── main.py                       # FastAPI app factory + lifespan
│   │
│   ├── api/                          # HTTP layer: aggregation and dependencies
│   │   ├── __init__.py
│   │   ├── dependencies.py           # Shared Depends (db_session, current_user)
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── router.py             # Mounts all domain routers
│   │
│   ├── core/                         # Cross-cutting infrastructure
│   │   ├── __init__.py
│   │   ├── config.py                 # Typed settings (Pydantic BaseSettings)
│   │   ├── database.py               # Async engine, session_factory
│   │   ├── security.py               # JWT, password hashing
│   │   ├── logging.py                # structlog setup
│   │   └── exceptions.py             # Global exception handlers
│   │
│   ├── domains/                      # CRM business domains
│   │   ├── __init__.py
│   │   ├── users/                    # Read-only IAM user/service-access references
│   │   ├── contacts/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── leads/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── proposals/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── technical_visits/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── permissions/              # CRM permission catalog, overrides, assignment checks
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   └── pipeline/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── repository.py
│   │       ├── service.py
│   │       └── router.py
│   │
│   └── agent/                        # AI agent — consumes domain services
│       ├── __init__.py
│       ├── router.py                 # Endpoint /agent/chat
│       ├── schemas.py                # Agent request/response schemas
│       ├── graph.py                  # LangGraph agent state machine
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py               # LLMProvider (ABC) — swappable interface
│       │   ├── azure_openai.py       # AzureOpenAI + GPT-5.5 implementation
│       │   └── factory.py            # Selects provider based on config
│       └── tools/                    # Tools that invoke domain services
│           ├── __init__.py
│           ├── query_proposals.py
│           ├── query_pipeline.py
│           └── update_lead.py
│
└── tests/
    ├── conftest.py                   # Global fixtures (db, client, auth)
    ├── unit/
    │   └── domains/
    └── integration/
        ├── api/
        └── agent/
```

### Internal Domain Structure

All domains follow the same consistent 5-file pattern:

| File | Responsibility |
|---|---|
| `models.py` | SQLModel (table=True) — entities persisted in the database |
| `schemas.py` | Pydantic BaseModel — request and response DTOs |
| `repository.py` | Data access: async SQLModel/SQLAlchemy queries |
| `service.py` | Domain business logic |
| `router.py` | Domain APIRouter (mounted in `api/v1/router.py`) |

### Layer Dependency Rules

```
router  →  service  →  repository  →  models
   ↓          ↑
schemas    (may call services from the same or other domains)
```

- `router.py` only knows `service.py` and `schemas.py`. It never accesses the repository directly.
- `service.py` orchestrates business logic and calls `repository.py`. It may call services from other domains.
- `repository.py` is the only layer that knows SQLModel/SQLAlchemy queries.
- `models.py` imports nothing from the application — only `sqlmodel` and standard types.

### Router Aggregation in `api/v1/router.py`

```python
from fastapi import APIRouter
from domains.contacts.router import router as contacts_router
from domains.leads.router import router as leads_router
from domains.proposals.router import router as proposals_router
from domains.permissions.router import (
    lead_router as permissions_lead_router,
    proposal_router as permissions_proposal_router,
    router as permissions_router,
)
from domains.technical_visits.router import (
    lead_router as technical_visits_lead_router,
    proposal_router as technical_visits_proposal_router,
    router as technical_visits_router,
)
from domains.pipeline.router import router as pipeline_router
from agent.router import router as agent_router

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(contacts_router,  prefix="/contacts",  tags=["contacts"])
api_v1.include_router(leads_router,     prefix="/leads",     tags=["leads"])
api_v1.include_router(proposals_router, prefix="/proposals", tags=["proposals"])
api_v1.include_router(permissions_lead_router,         prefix="/leads",     tags=["permissions"])
api_v1.include_router(permissions_proposal_router,     prefix="/proposals", tags=["permissions"])
api_v1.include_router(technical_visits_lead_router,     prefix="/leads",            tags=["technical-visits"])
api_v1.include_router(technical_visits_proposal_router, prefix="/proposals",        tags=["technical-visits"])
api_v1.include_router(technical_visits_router,          prefix="/technical-visits", tags=["technical-visits"])
api_v1.include_router(pipeline_router,  prefix="/pipeline",  tags=["pipeline"])
api_v1.include_router(permissions_router, prefix="/permissions", tags=["permissions"])
api_v1.include_router(agent_router,     prefix="/agent",     tags=["agent"])
```

### Agent ↔ Domains Relationship

The agent **does not replicate business logic**: its tools invoke domain `service.py` files just like any other internal consumer. This avoids coupling and ensures the agent and the REST API always operate under the same business and authorization rules.

```
agent/tools/query_proposals.py  →  domains/proposals/service.py
agent/tools/update_lead.py      →  domains/leads/service.py
agent/tools/query_pipeline.py   →  domains/pipeline/service.py
```

---

## Migrations

CRM uses root Alembic migrations in `alembic/`. Because CRM references IAM-owned
`iam_user` rows, apply IAM migrations before CRM migrations on a fresh shared
database:

```bash
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
PYTHONPATH=CRM/src uv run python -m alembic upgrade head
```

CRM Alembic autogenerate ignores IAM-owned tables such as `iam_user`,
`iam_service_access`, and `iam_user_permission_override`; CRM owns only CRM tables and
foreign keys that point to IAM user ids.

---

## Domain Model

### `domains/users/` — IAM user reference

CRM does not own central users, password login, refresh tokens, or IAM permissions. Those concerns belong to the sibling IAM service. CRM keeps only a read-only reference to IAM users through the shared `iam_user` table so CRM ownership, assignment, and audit fields can point at `iam_user.id`.

CRM authorization is enforced separately through `CRMUserAccess`, role templates, per-user permission overrides, and assignment-scoped resource checks. Contacts and Leads still keep `owner_id` fields, but Lead ownership now represents active sales follow-up after assignment.

The architecture separates identity from CRM authorization:

- IAM owns users, login/JWT, account status, IAM permissions, and service access grants such as `crm`.
- CRM owns role templates, permission catalog, user permission overrides, and resource assignment checks.
- CRM roles are permission templates, not hard-coded authorization shortcuts.
- Effective CRM permissions are computed as role permissions plus user grants minus user denials.
- Resource scope is checked after permission: `sales` and `tech` users only access assigned CRM records.

CRM roles:

| Role | Meaning |
|---|---|
| `admin` | All CRM permissions and global CRM scope |
| `manager` | All CRM permissions; can manage other non-admin CRM permissions within guardrails |
| `sales` | Commercial follow-up on assigned Leads, with derived Contact access and read-only Proposal/TechnicalVisit access |
| `tech` | Technical work on assigned Proposals and TechnicalVisits, with derived read-only Contact/Lead/document access and no Lead interactions |

Permission management guardrails:

- A manager cannot create IAM users because user creation is not a CRM action.
- A manager cannot modify admin users.
- A manager cannot modify their own role or permissions.
- A manager cannot grant a permission they do not effectively have.

CRM-specific permissions and assignment checks are implemented under the `permissions/` domain. Central user creation, login, IAM permissions, and IAM service-access grants belong to IAM, not CRM.

### `permissions/` — CRM authorization

The permissions domain stores CRM-specific authorization data keyed by the IAM user id.

Implemented entities:

- `CRMUserAccess`: CRM service access and role for one central VERP user.
- `CRMUserPermissionOverride`: user-specific grant or deny for one permission key.
- `LeadAssignment`: active sales follow-up assignment with assignment history.
- `ProposalAssignment`: direct technical assignment for Proposal work.

The permission catalog and role templates are code-defined in `permissions/service.py`; move them to seeded tables only if runtime template administration is needed.

Existing `TechnicalVisitAssignee.user_id` is reused for technical visit assignment scope.

Authorization flow:

1. Resolve the authenticated user from the request token.
2. Load effective CRM permissions.
3. Check the action permission.
4. Check resource scope: global, assigned sales Lead, assigned technical Proposal, assigned TechnicalVisit, or derived related record.
5. Apply field-level rules such as protected Proposal price fields.

### `contacts/` — Directory of people and organizations

Answers the question **"who?"**: the directory of people and organizations with whom the company has or has had a relationship, independent of any specific deal.

**Key distinction — Contact vs Lead:**

| | `Contact` | `Lead` |
|---|---|---|
| Answers | **Who** they are | **What** we want to sell them |
| Lifetime | Permanent | Bounded (opens, then closes) |
| Cardinality | 1 Contact → 0..N Leads | 1 Lead → 1 primary Contact |

If Contact and Lead were merged, closing a lost Lead would destroy the person's information — yet that same person might return months later. Kept separate, the contact persists and the next Lead simply references it.

**`Contact` entity:**

```python
class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    type: ContactType                      # INDIVIDUAL | COMPANY

    name: str                              # Full name or company name
    promoter_id: int = Field(foreign_key="promoter.id")

    address_line: str | None
    city: str | None
    state: str | None
    postal_code: str | None

    owner_id: int = Field(foreign_key="iam_user.id")
    created_at: datetime
    updated_at: datetime
```

Individual and company-specific columns are intentionally separated from `contact`:

```python
class IndividualContactProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    contact_id: int = Field(foreign_key="contact.id", unique=True)
    email: str | None
    phone: str | None


class CompanyContactProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    contact_id: int = Field(foreign_key="contact.id", unique=True)
    industry: str | None
```

Company contacts do not store direct `email`, `phone`, `tax_id`, `country`, or `website` fields. Individual contacts do not store `industry`, `tax_id`, `country`, `first_name`, `last_name`, `parent_contact_id`, or `role`.

**`Promoter` entity:**

```python
class Promoter(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    phone: str
    owner_id: int = Field(foreign_key="iam_user.id")
    created_at: datetime
    updated_at: datetime
```

**`CompanyContactPerson` entity:**

```python
class CompanyContactPerson(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_contact_id: int = Field(foreign_key="contact.id")
    name: str
    phone: str
    email: str | None
    position: str
    created_at: datetime
    updated_at: datetime
```

Every Contact references an owned Promoter. Every company Contact must have one or more CompanyContactPerson rows.

**Fields that do NOT belong in Contact** (they go in Lead or Proposal): `monthly_consumption_kwh`, `roof_orientation`, `budget`, `has_battery`. These describe the opportunity or a specific technical variant, not the identity of the contact.

### `leads/` — The commercial opportunity

Represents a **qualified interest**, before a definitive technical scope has been established. This is the pure commercial phase — the "deal" in CRM terms.

**`Lead` entity:**

```python
class Lead(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    contact_id: int = Field(foreign_key="contact.id")

    title: str                             # "Solar 8kW — John Smith residence"
    interest_type: str                     # Photovoltaic, BESS, Hibrid
    qualification_score: int | None        # 0–100 (BANT or similar)

    current_stage: str                     # NEW, QUALIFYING, PROPOSAL_PHASE, CLOSED_WON, CLOSED_LOST
    outcome: str | None                    # NULL until closed; then WON or LOST

    owner_id: int = Field(foreign_key="iam_user.id")
    notes: str | None
    technical_visit_requirement: str       # UNDETERMINED, NOT_REQUIRED, REQUIRED
    created_at: datetime
    closed_at: datetime | None
```

The same Contact can generate multiple Leads over time (initial installation, subsequent expansion, etc.).
Lead-level project documents are stored separately from electricity bills. General documents capture project context such as plans, requirements, or customer-provided specifications; electricity bills have their own table and API routes because they feed an independent review process. Lead interactions document sales activity and negotiations against the lead history and require an `interaction_date` that may be in the past, present, or future for planned interactions.

Leads also store the explicit technical visit requirement decision: `UNDETERMINED`, `NOT_REQUIRED`, or `REQUIRED`. This separates "not decided yet" from "a visit is not needed." Visit scheduling, completion, and evidence are owned by the `technical_visits/` domain.

Authorization treats active Lead assignment as the source of `sales` access:

- A sales user may have one or more assigned Leads.
- A Lead should have one active sales follow-up owner at a time.
- Assigning a Lead to another sales user removes the previous sales user's scope over that Lead and derived records.
- Contact access for sales is derived from assigned Leads; Contacts without active Leads can use their current assigned owner until a Lead assignment exists.
- `tech` users can read Leads and Lead documents only when derived from assigned Proposals or TechnicalVisits.
- `tech` users must not read Lead interactions.

### `proposals/` — The technical proposals

Represents each **concrete technical proposal** offered to a customer to close a Lead. Previously called "projects" — renamed because until a proposal is won, there is no project in a strict sense.

A Lead can have **multiple Proposals** (variants: "basic option" vs "with batteries" vs "with roof extension"). When one is won, that proposal *becomes* the project to be executed.

Proposals are classified by `system_type`: `PV`, `BESS`, or `HIBRID`. `lead_id` and `name` are the only fields required at creation time. All commercial and technical fields may be filled progressively while the proposal remains `DRAFT`; before the proposal can advance to `SENT`, `NEGOTIATION`, `WON`, or `LOST`, the required common fields and the required fields for its system type must be complete.

**`Proposal` entity: common commercial header**

```python
class Proposal(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id")

    name: str                              # "Option with batteries"
    version: str | None                    # "1.0"
    installation_address_line: str | None
    installation_city: str | None
    installation_state: str | None
    installation_postal_code: str | None
    tariff: str | None
    contracted_demand: float | None
    system_type: str | None                # PV, BESS, HIBRID

    total_price: Decimal | None
    annual_savings: Decimal | None
    currency: str | None
    estimated_cost: Decimal | None
    expected_profit: Decimal | None
    submitted_at: datetime | None
    valid_until: date | None
    current_stage: str                     # DRAFT, SENT, NEGOTIATION, WON, LOST, SUPERSEDED
    loss_reason: str | None                # required when current_stage = LOST

    proposed_at: datetime | None
    created_by: int = Field(foreign_key="iam_user.id")
    created_at: datetime
```

**PV detail table (`ProposalPVSystem`)** — present for `PV` and `HIBRID` proposals:

```python
class ProposalPVSystem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id", unique=True)
    panel_count: int | None
    panel_model: str | None
    panel_power: float | None
    inverter_model: str | None
    inverter_count: int | None
    inverter_power: float | None
    type_of_surface: str | None
    total_power_ac: float | None
    system_size_kw: float | None
    oversizing_kw: float | None
    estimated_annual_kwh: float | None
    estimated_savings_kw: float | None
    connection_mode: str | None            # interconnected, isolated, self-sufficiency, etc.
    cost_watt: Decimal | None              # PV cost per W
    price_watt: Decimal | None             # PV sale price per W
```

**BESS detail table (`ProposalBESSSystem`)** — present for `BESS` and `HIBRID` proposals:

```python
class ProposalBESSSystem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id", unique=True)
    battery_model: str | None
    battery_count: int | None
    battery_power_kw: float | None
    battery_storage_kwh: float | None
    bess_primary_use: str | None           # peak-shaving, backup, etc.
    technical_notes: str | None
    cost_kwh: Decimal | None               # BESS cost per kWh
    price_kwh: Decimal | None              # BESS sale price per kWh
```

`HIBRID` proposals use both detail rows, so they carry all four unit economics fields: `cost_watt`, `price_watt`, `cost_kwh`, and `price_kwh`.

Proposal documents are split into a special customer-facing commercial PDF collection (`ProposalCommercialDocument`) and classified internal documents (`ProposalDocument`) with `title` plus `classification` (`Costs`, `Technical`, or `Other`). Both store upload metadata and files under the configured document storage path.

Proposal technical visit evidence is linked through `ProposalTechnicalVisit`, not through a direct field on `Proposal`. This allows one visit to inform multiple proposal versions, and one proposal to cite multiple visits when needed.

Authorization separates Proposal update permission from protected price permissions:

- Protected price fields are `Proposal.total_price`, `ProposalPVSystem.price_watt`, and `ProposalBESSSystem.price_kwh`.
- Setting an empty protected price field requires `crm.proposals.price.set`.
- Changing an already established protected price field requires `crm.proposals.price.update`.
- Default `admin` and `manager` role templates include price permissions.
- Default `tech` role templates can update assigned Proposals except protected price fields.
- Default `sales` role templates can read Proposals associated with assigned Leads, but cannot mutate Proposals.

Do not add a separate pricing table for the first permission implementation. Add a pricing revision table later only if CRM needs formal approval workflow, pricing history, or commercial audit beyond normal Proposal updates.

Later proposal work: `price_watt` and `price_kwh` must be calculated from proposal values and rounded to 4 decimal places instead of being freely edited unit fields.

### `technical_visits/` — On-site technical visits

Represents an optional Lead-scoped subprocess for qualified engineering inspections at the customer's installation site. A technical visit can happen before any Proposal exists, or after a first Proposal has already been sent.

The visit does not determine the commercial outcome. It stores schedule data, assigned visitors, the customer receiver, completion state, and uploaded documents/photos.

**Lead requirement decision:**

```python
class TechnicalVisitRequirement(StrEnum):
    UNDETERMINED = "UNDETERMINED"
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
```

**`TechnicalVisit` entity:**

```python
class TechnicalVisit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id")
    status: str                            # REQUESTED, SCHEDULED, COMPLETED, CANCELLED
    scheduled_at: datetime | None
    receiver_name: str | None
    receiver_phone: str | None
    notes: str | None
    created_by: int = Field(foreign_key="iam_user.id")
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
```

**`TechnicalVisitAssignee` entity:**

```python
class TechnicalVisitAssignee(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    visit_id: int = Field(foreign_key="technical_visit.id")
    name: str
    user_id: int | None = Field(foreign_key="iam_user.id")
    created_at: datetime
```

`TechnicalVisitAssignee.user_id` is also the source of `tech` scope over assigned TechnicalVisits. Proposal work can be assigned directly through `ProposalAssignment` when a `tech` user needs Proposal access independent of a visit.

**`TechnicalVisitAttachment` entity:**

```python
class TechnicalVisitAttachment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    visit_id: int = Field(foreign_key="technical_visit.id")
    title: str
    file_kind: str                         # DOCUMENT, PHOTO, OTHER
    original_filename: str
    content_type: str | None
    stored_path: str
    size_bytes: int
    uploaded_by: int = Field(foreign_key="iam_user.id")
    uploaded_at: datetime
```

**`ProposalTechnicalVisit` entity:**

```python
class ProposalTechnicalVisit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id")
    technical_visit_id: int = Field(foreign_key="technical_visit.id")
    relationship_type: str                 # BASED_ON, VALIDATED_BY
    notes: str | None
    linked_by: int = Field(foreign_key="iam_user.id")
    linked_at: datetime
```

Technical visit rules:

1. A Lead can be `UNDETERMINED`, `NOT_REQUIRED`, or `REQUIRED`.
2. Creating a visit for an `UNDETERMINED` Lead marks it `REQUIRED`; creating one for a `NOT_REQUIRED` Lead is rejected.
3. A visit can start as `REQUESTED`, or as `SCHEDULED` when `scheduled_at`, receiver name, receiver phone, and at least one assignee are provided together.
4. Completing a visit only sets completion state; at least one inspection attachment must already exist.
5. Attachments can be uploaded before or after completion, but not after cancellation.
6. Proposal-to-visit links must stay within the same Lead.
7. If a visit changes assumptions after a Proposal has moved beyond `DRAFT`, create a new Proposal version and link that version to the visit evidence instead of silently editing the existing sent Proposal.

### `pipeline/` — The funnel state machine

Cross-cutting infrastructure that tracks **which stage each Lead and each Proposal is in**, and maintains an immutable history of transitions. It is not a business entity in itself.

**Entities:**

`Stage` — configurable stage catalog
```
entity_type=lead:     NEW → QUALIFYING → PROPOSAL_PHASE → CLOSED_WON | CLOSED_LOST
entity_type=proposal: DRAFT → SENT → NEGOTIATION → WON | LOST | SUPERSEDED
```

`StageTransition` — immutable history
```python
class StageTransition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    entity_type: str                       # "lead" | "proposal"
    entity_id: int
    from_stage: str | None
    to_stage: str
    transitioned_by: int = Field(foreign_key="iam_user.id")
    transitioned_at: datetime
    reason: str | None
    notes: str | None
```

The `pipeline.service.transition()` service validates that the transition is allowed and records the event.

---

## Lifecycle and Transitions

### General flow

```
Contact ──┐
          │  (1:N — one contact can generate multiple leads over time)
          ▼
        Lead  ────► pipeline tracks its stage ────► [NEW → QUALIFYING → PROPOSAL_PHASE → CLOSED]
          │
          ├──► TechnicalVisit ──► [REQUESTED → SCHEDULED → COMPLETED | CANCELLED]
          │
          │  (1:N — one lead can have multiple proposal variants)
          ▼
       Proposal ──► pipeline tracks its stage ────► [DRAFT → SENT → NEGOTIATION → WON | LOST | SUPERSEDED]
          ▲
          │  (N:M — ProposalTechnicalVisit links proposal versions to visit evidence)
          └────────────────────────────────────────────────────────────────────
```

### Core rule: the outcome lives in the Proposal

The terminal state (WON/LOST) **is decided at the Proposal level**, not the Lead level. This preserves the critical information about *which* variant won:

> Did we win with batteries or without? With or without the roof extension? What was the price difference between the winning proposal and the ones that didn't make it?

The Lead **reflects** the outcome of its proposals but does not determine it:

| Situation | Proposals | Lead |
|---|---|---|
| Customer accepts Proposal A | A → `WON`; B and C → `SUPERSEDED` (automatic) | `CLOSED_WON` |
| Customer rejects all | A, B, C → `LOST` (each with its own `loss_reason`) | `CLOSED_LOST` |
| Customer abandons / no response | A, B, C → `LOST` with `loss_reason="no_response"` | `CLOSED_LOST` |
| Customer requests a new variant | A, B remain in `SENT`; D is created in `DRAFT` | stays in `PROPOSAL_PHASE` |

### Model invariants

1. **Only one Proposal per Lead can be in `WON`** (enforced by the service layer).
2. **When a Proposal moves to `WON`, active siblings automatically move to `SUPERSEDED`** within the same transaction.
3. **`loss_reason` is mandatory** when a Proposal moves to `LOST`.
4. **A Lead only closes as a consequence** of its proposals' outcomes — never directly, except for an explicit manual abandonment.
5. **Every stage transition is recorded** in `stage_transition` — immutable, append-only history.

### Atomic operation: winning a proposal

```python
# proposals/service.py
async def mark_won(proposal_id: int, user_id: int, session: AsyncSession) -> Proposal:
    async with session.begin():
        proposal = await proposal_repo.get(session, proposal_id)

        # 1. This proposal wins
        await pipeline_service.transition(
            session, "proposal", proposal.id, to_stage="WON", by=user_id
        )

        # 2. Active siblings move to SUPERSEDED
        siblings = await proposal_repo.list_active_siblings(
            session, lead_id=proposal.lead_id, exclude_id=proposal.id
        )
        for sib in siblings:
            await pipeline_service.transition(
                session, "proposal", sib.id,
                to_stage="SUPERSEDED", by=user_id,
                reason=f"Lead won with proposal #{proposal.id}",
            )

        # 3. The Lead closes reflecting the outcome
        await leads_service.close(
            session, proposal.lead_id, outcome="WON", by=user_id
        )

        return proposal
```

---

## Model Strategy: SQLModel vs Pydantic

| Situation | Tool | Location | Example |
|---|---|---|---|
| DB table exposed as-is | `SQLModel(table=True)` | `domains/<x>/models.py` | `Proposal`, `Contact`, `Lead` |
| Response with computed or nested fields | `pydantic.BaseModel` | `domains/<x>/schemas.py` | `ProposalWithROI`, `PipelineSummary` |
| Request body with complex validation | `pydantic.BaseModel` | `domains/<x>/schemas.py` | `CreateProposalRequest`, `CloseLeadRequest` |
| Environment variables and config | `pydantic_settings.BaseSettings` | `core/config.py` | `Settings` |

**Practical rule:** SQLModel for what lives in the database, Pydantic for what lives in the API.

### SQLite → PostgreSQL Portability

With SQLModel/SQLAlchemy 2.x and Alembic, switching the database engine requires only:

1. Updating `DATABASE_URL` in `.env` (from `sqlite+aiosqlite:///...` to `postgresql+asyncpg://...`).
2. Running `alembic upgrade head` against the new database.

No business logic, models, or schemas need to be modified.

---

## Library Stack

### Core Framework

| Library | Version | Purpose |
|---|---|---|
| `fastapi` | ≥ 0.115 | Main ASGI framework |
| `uvicorn[standard]` | latest | ASGI server with `uvloop` and `httptools` |
| `pydantic` | v2 ≥ 2.7 | Schema validation and DTOs |
| `pydantic-settings` | ≥ 2.3 | Typed environment variable management |

### Database and ORM

| Library | Purpose |
|---|---|
| `sqlmodel` ≥ 0.0.21 | Primary ORM — combines SQLAlchemy 2.x async with Pydantic v2 |
| `alembic` | Versioned migrations; uses `SQLModel.metadata` as `target_metadata` |
| `aiosqlite` | Async driver for SQLite (local development) |
| `asyncpg` | Async driver for PostgreSQL (production) |

### Authentication and Security

| Library | Purpose |
|---|---|
| `python-jose[cryptography]` | JWT generation and validation (access + refresh tokens) |
| `passlib[bcrypt]` | Secure password hashing |
| `python-multipart` | Form data support for the OAuth2 login flow |

Authorization design:

- IAM owns user creation, login, account lifecycle, IAM permissions, and service access grants.
- CRM should resolve CRM-specific effective permissions at request time or through short-lived cache.
- JWTs should identify the user and should not be treated as the only source of mutable CRM permissions.
- CRM REST endpoints and agent tools must call the same authorization layer before reading or mutating CRM records.
- Effective permission checks must be paired with resource scope checks for assigned `sales` and `tech` users.

### Intelligent Agent

| Library | Purpose |
|---|---|
| `openai` ≥ 1.30 | Official SDK — supports both `AzureOpenAI` and `OpenAI` with the same interface |
| `langchain-openai` | Model integration with the LangChain ecosystem |
| `langchain-core` | `BaseChatModel` — base class for a swappable provider interface |
| `langgraph` | Agent orchestration as a state graph (ReAct loop, memory, tools) |

> The `LLMProvider` interface (ABC) in `agent/providers/base.py` allows replacing AzureOpenAI/GPT-5.5 with any LangChain-compatible model without modifying the graph or the tools.

### HTTP Client

| Library | Purpose |
|---|---|
| `httpx` | Async HTTP client for external API integrations |

### Utilities

| Library | Purpose |
|---|---|
| `pendulum` | Robust date, time, and timezone handling |
| `structlog` | Structured JSON logging, production-ready |
| `python-slugify` | Human-readable slug generation for identifiers |

### Testing

| Library | Purpose |
|---|---|
| `pytest` + `pytest-asyncio` | Test runner with native async support |
| `httpx` | `AsyncClient` for endpoint testing without spinning up a server |
| `factory-boy` | Per-domain test data factories |
| `pytest-cov` | Code coverage reporting |

### Quality and Tooling

| Library | Purpose |
|---|---|
| `ruff` | Linter + formatter (replaces flake8, black, and isort) |
| `mypy` | Static type checking |
| `pre-commit` | Automated pre-commit hooks |

---

## `pyproject.toml`

```toml
[project]
name = "crm-renewables"
requires-python = ">=3.14"

dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]",
    "sqlmodel>=0.0.21",
    "alembic",
    "aiosqlite",
    "asyncpg",
    "pydantic>=2.7",
    "pydantic-settings>=2.3",
    "python-jose[cryptography]",
    "passlib[bcrypt]",
    "python-multipart",
    "openai>=1.30",
    "langchain-openai",
    "langchain-core",
    "langgraph",
    "httpx",
    "pendulum",
    "structlog",
    "python-slugify",
]

[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "factory-boy",
    "ruff",
    "mypy",
    "pre-commit",
]

```
