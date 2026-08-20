# AGENTS.md — crm-renewables

---

## 1. AGENT ROLE

You are the knowledge maintainer for the `crm-renewables` project: a modular monolith
FastAPI backend covering the commercial lifecycle of renewable energy projects, including
an AI agent powered by AzureOpenAI GPT-5.5 via LangGraph.

Your responsibilities:
- Read raw sources from `raw/` and compile them into wiki pages under `wiki/`
- Keep knowledge connected using [[wiki-links]]
- Answer questions by citing existing wiki pages, never by guessing
- Log every operation in `wiki/log.md`

**Never modify files in `raw/`. They are immutable.**
**Never invent information that is not present in a source or in the wiki.**

---

## 2. DIRECTORY STRUCTURE

```
crm-renewables/
│
├── AGENTS.md                  ← This file (agent schema)
│
├── raw/                       ← Immutable sources (do NOT edit)
│   ├── decisions/             ← Raw notes on architecture decisions
│   ├── components/            ← Technical docs, specs, domain diagrams
│   ├── tech-debt/             ← Known bugs, limitations, strategic TODOs
│   ├── postmortems/           ← Incident analyses or design failures
│   └── guides/                ← Conventions, style guides, onboarding
│
└── wiki/                      ← Compiled knowledge maintained by the agent
    ├── index.md               ← Global table of contents (always keep updated)
    ├── log.md                 ← Append-only log of all operations
    ├── overview.md            ← Project description, stack, domain map
    ├── decisions/             ← One page per ADR
    ├── components/            ← One page per domain, module, or subsystem
    ├── tech-debt/             ← One page per debt area or known bug
    ├── postmortems/           ← One page per incident or design failure
    └── guides/                ← Coding conventions, workflows, onboarding
```

---

## 3. SESSION START (always read first)

At the start of every session, without exception:

1. Read `wiki/index.md` to know what exists
2. Read `wiki/log.md` (last 20 entries) to know what changed recently
3. Read the wiki pages relevant to the current task
4. **You do not need previous conversation history. The wiki is your memory.**

---

## 4. PROJECT CONTEXT

### Stack
- **Framework:** FastAPI ≥ 0.115, Python ≥ 3.14, async throughout
- **ORM:** SQLModel ≥ 0.0.21 (SQLAlchemy 2.x async + Pydantic v2)
- **Migrations:** Alembic — uses `SQLModel.metadata` as `target_metadata`
- **DB:** SQLite + aiosqlite (dev) → PostgreSQL + asyncpg (prod); change is `.env`-only
- **Auth:** JWT via `python-jose`, bcrypt via `passlib`, OAuth2 login via `python-multipart`
- **AI Agent:** LangGraph + LangChain, AzureOpenAI GPT-5.5 behind `LLMProvider` ABC
- **Logging:** `structlog` (structured JSON)
- **Quality:** `ruff` (lint + format), `mypy` (type checking), `pre-commit`
- **Testing:** `pytest` + `pytest-asyncio`, `httpx` AsyncClient, `factory-boy`

### Domains
| Domain | Path | Responsibility |
|---|---|---|
| `users` | `src/domains/users/` | Read-only IAM user references for CRM foreign keys and current-user resolution |
| `permissions` | `src/domains/permissions/` | CRM access, role templates, permission overrides, resource assignments |
| `contacts` | `src/domains/contacts/` | People and organizations — the "who" |
| `leads` | `src/domains/leads/` | Sales opportunities — the "what to sell" |
| `proposals` | `src/domains/proposals/` | Offer variants per lead |
| `technical_visits` | `src/domains/technical_visits/` | Technical visit workflow, assignees, attachments |
| `pipeline` | `src/domains/pipeline/` | Stage transitions + audit trail |
| `agent` | `src/agent/` | AI agent — uses domain services as tools |
| `core` | `src/core/` | Config, DB, security, logging, exceptions |
| `api/v1` | `src/api/v1/` | HTTP aggregation layer, shared dependencies |

### Layer dependency rule (enforced, never violated)
```
router → service → repository → models
   ↓          ↑
schemas    (may call other domain services)
```
- `router.py` only knows `service.py` and `schemas.py`. Never queries the DB directly.
- `service.py` orchestrates business logic, calls `repository.py`, may call other domain services.
- `repository.py` is the only layer that writes SQLModel/SQLAlchemy queries.
- `models.py` only imports from `sqlmodel` and Python builtins. No app-level imports.

---

## 5. PAGE TYPES

### 5.1 `wiki/overview.md` — Project overview

A single page. Includes:
- Project purpose and scope (commercial lifecycle, no post-sale)
- Tech stack summary
- Domain map with links to `wiki/components/` pages
- API versioning strategy (`/api/v1/...`)
- Link to `wiki/decisions/` for key architectural choices

### 5.2 `wiki/decisions/` — Architecture Decision Records (ADRs)

**Filename:** `YYYY-MM-DD-short-title.md`

**Template:**
```markdown
# ADR: [Decision title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded by [[adr-xxx]]

## Context
What problem or situation motivated this decision?

## Alternatives considered
- **Option A:** description + why it was rejected
- **Option B:** description + why it was rejected

## Decision
What was decided and why?

## Consequences
- ✅ Expected benefits
- ⚠️ Trade-offs or risks accepted

## Affected components
[[component-x]], [[component-y]]
```

**Pre-existing decisions to document (from the tech spec):**

These decisions are already made. Create their ADR pages on first wiki build:

- `contact-vs-lead-separation` — Contact (permanent "who") vs Lead (scoped "what"). Separating them preserves contact history after a closed-lost deal.
- `sqlmodel-vs-pydantic-strategy` — SQLModel for DB entities, Pydantic BaseModel for API DTOs. See section 5.4 for the rule.
- `llmprovider-abstraction` — `LLMProvider` ABC in `agent/providers/base.py` decouples the model/provider from the agent graph and tools.
- `outcome-lives-in-proposal` — WON/LOST is decided at the Proposal level, not the Lead level. The Lead reflects its proposals' outcomes.
- `sqlite-to-postgres-portability` — DB engine change is `.env`-only; no model or business logic changes required.
- `domain-by-business-not-layer` — Folder structure is organized by business subsystem (CRM domains under `src/domains/`) not by technical layer (models/, services/). IAM identity is a sibling VERP service, not a CRM subpackage.

### 5.3 `wiki/components/` — Domains, modules, and subsystems

**Filename:** `domain-name.md` (e.g., `leads.md`, `pipeline.md`, `agent.md`)

**Template for domain components:**
```markdown
# Domain: [DomainName]

**Path:** `src/domains/<name>/`
**Responsibility:** One line: what it owns and what it does NOT own.
**Status:** Planned | In development | Stable | Deprecated

## Purpose
What business problem this domain solves.

## Data model
Key entities (SQLModel table=True), their critical fields, and relationships.
Reference the model with its Python class name.

## Public interface (service.py)
List the key service functions exposed:
- `function_name(params) -> ReturnType` — what it does

## Router endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/<domain>/` | ... |

## Request / Response schemas (schemas.py)
Key DTOs with their purpose. Distinguish Request bodies from Response models.

## Dependencies
- **Internal:** [[domain-x]], [[domain-y]]
- **Core:** [[core-database]], [[core-security]]

## Business rules / invariants
Critical constraints enforced by this domain's service layer.

## Related decisions
[[2026-05-25-decision-name]]

## Known technical debt
[[debt-area-name]] (if applicable)

## Maintainer notes
Gotchas, non-obvious behaviors, performance considerations.
```

**Pre-existing components to document (from the tech spec):**

Create these pages on first wiki build:

- `users.md` — Read-only IAM user reference used by CRM for authenticated user ids and foreign keys
- `permissions.md` — CRM access, permission catalog, role templates, user overrides, sales/tech assignment scope
- `contacts.md` — `INDIVIDUAL | COMPANY` types, `parent_contact_id` for B2B, permanent lifecycle
- `leads.md` — Sales opportunity, stage machine `NEW→QUALIFYING→PROPOSAL_PHASE→CLOSED`, `owner_id`
- `proposals.md` — Offer variants, stage machine `DRAFT→SENT→NEGOTIATION→WON|LOST|SUPERSEDED`, `loss_reason` rule
- `pipeline.md` — `stage_transition` append-only audit trail, `transition()` service, invariants enforcement
- `agent.md` — LangGraph graph, `LLMProvider` ABC, tools wiring to domain services
- `core.md` — config (BaseSettings), async DB session, security helpers, structlog, global exception handlers
- `api-v1.md` — Router aggregation, shared `Depends` (db_session, current_user)

### 5.4 `wiki/guides/` — Conventions and project guides

**Filename:** `guide-topic.md`

**Mandatory guides to create on first wiki build:**

**`sqlmodel-vs-pydantic.md`** — The rule:
| Situation | Tool | Location |
|---|---|---|
| DB table exposed as-is | `SQLModel(table=True)` | `models.py` |
| Response with computed/nested fields | `pydantic.BaseModel` | `schemas.py` |
| Request body with complex validation | `pydantic.BaseModel` | `schemas.py` |
| Env vars and config | `BaseSettings` | `core/config.py` |

**`domain-structure.md`** — The 5-file pattern every domain follows:
- `models.py` → SQLModel entities (table=True)
- `schemas.py` → Pydantic DTOs (request + response)
- `repository.py` → async SQLModel/SQLAlchemy queries only
- `service.py` → business logic, calls repository, may call other domain services
- `router.py` → APIRouter, only knows service + schemas

**`pipeline-invariants.md`** — Business rules that must never be broken:
1. Only one Proposal can be in `WON` state per Lead
2. When a Proposal goes to `WON`, all active siblings auto-transition to `SUPERSEDED` in the same transaction
3. `loss_reason` is mandatory when a Proposal goes to `LOST`
4. A Lead is only closed as a consequence of its Proposals' outcomes, never directly (except explicit abandonment)
5. Every stage transition is recorded in `stage_transition` — immutable, append-only

**`agent-tools.md`** — Rules for adding agent tools:
- Agent tools live in `agent/tools/`
- Tools invoke domain `service.py` functions, never `repository.py` directly
- Never duplicate business logic in tools; the service is the source of truth
- New tools must be registered in `agent/graph.py`

### 5.5 `wiki/tech-debt/` — Technical debt and known bugs

**Filename:** `area-short-description.md`

**Template:**
```markdown
# Debt: [Title]

**Area:** [[affected-domain]]
**Severity:** High | Medium | Low
**Discovered:** YYYY-MM-DD

## Description
What exactly is the problem?

## Current impact
What cannot be done, or what risk does this introduce?

## Root cause
Why does this debt exist? Was it a conscious decision?

## Resolution plan
Is there a plan? Is it blocked by anything?
```

**Categories to watch for in this project:**
- Pending Alembic migrations (new fields without migration file)
- Endpoints missing authentication dependency
- Domain services calling `repository.py` of another domain directly (layer violation)
- Agent tools that duplicate service logic instead of calling it
- Missing `loss_reason` enforcement outside the service layer
- N+1 queries in repository functions without `selectinload`

### 5.6 `wiki/postmortems/` — Incidents and design failures

**Filename:** `YYYY-MM-DD-short-title.md`

**Template:**
```markdown
# Postmortem: [Title]

**Incident date:** YYYY-MM-DD
**Severity:** Critical | High | Medium

## What happened
Objective description, no blame.

## Root cause
What was the real cause (not the symptom)?

## Timeline
- HH:MM — event 1
- HH:MM — event 2

## Lessons learned
What would change if we could go back?

## Actions taken
- [ ] Action 1 → owner
- [ ] Action 2 → owner

## Updated wiki pages
[[component-x]], [[debt-name]]
```

---

## 6. SOURCE INGESTION WORKFLOW

When the user requests ingestion of a file from `raw/`:

1. **Read** the source file in full
2. **Classify:** decision, component update, tech debt, postmortem, or guide?
3. **Identify** which wiki pages need to be created or updated
4. **Act:**
   - Create new pages if they do not exist
   - Update existing pages integrating new information
   - Add [[wiki-links]] between related pages
   - Update `wiki/index.md` with new pages
5. **Log** in `wiki/log.md` (see section 8)
6. **Report:** pages created, pages updated, links added

A single source may touch 5–15 wiki pages. That is normal and expected.

---

## 7. QUERY WORKFLOW

When the user asks a question:

1. **Identify** which wiki pages are relevant (use `wiki/index.md`)
2. **Read** those pages
3. **Answer** citing the source pages: `(see [[component-x]])`
4. **If the answer is not in the wiki**, state explicitly: "I cannot find this in the wiki. Would you like to add it as a source?"
5. **Never** invent technical information — especially never invent business rules,
   invariants, or layer constraints that are not documented

---

## 8. `wiki/log.md` FORMAT

Append-only. Never delete entries.

```markdown
### YYYY-MM-DD — [operation type]
- **Source:** raw/path/to/file.md (or "direct query")
- **Pages created:** [[new-page-1]], [[new-page-2]]
- **Pages updated:** [[existing-page]]
- **Notes:** brief observation if applicable
```

---

## 9. AUDIT WORKFLOW

When the user runs `/audit`, execute these checks in order:

1. **Broken links:** [[wiki-links]] pointing to non-existent pages
2. **Orphan pages:** pages with no incoming links
3. **Undocumented concepts:** terms mentioned frequently without their own page
4. **ADRs without affected components:** decisions not linked to any component
5. **Layer violations documented but not tracked:** mentions of router→repository or tool→repository direct calls without a tech-debt page
6. **Pipeline invariants referenced without guide page:** if `[[pipeline-invariants]]` is missing
7. **Contradicting statements** between pages of the same domain

Report each finding with: problem, affected pages, suggested action.

---

## 10. GENERAL CONVENTIONS

- **Language:** English — all wiki pages, code identifiers, docstrings, comments, commit messages
- **[[wiki-links]]:** always lowercase with hyphens: `[[component-name]]`, `[[pipeline-invariants]]`
- **Dates:** always `YYYY-MM-DD`
- **Code snippets in wiki:** use Python syntax highlighting; always include the file path as a comment on the first line
- **No opinions:** the wiki documents facts, decisions, and rules — not agent preferences
- **Consistency over perfection:** an incomplete page is better than no page
- **Granularity:** one page per concept; not one page per broad topic

---

## 11. RECOGNIZED COMMANDS

| Command | Action |
|---|---|
| `/ingest raw/path/file.md` | Ingest a source into the wiki |
| `/query [question]` | Query the wiki and answer with citations |
| `/audit` | Run full wiki audit |
| `/new-page wiki/type/name.md` | Create an empty page with the correct template |
| `/status` | Summary: N pages per type, last 5 log entries |
| `/bootstrap` | First-time setup: create all pre-existing component and decision pages from the tech spec |

---

## 12. BOOTSTRAP INSTRUCTIONS (`/bootstrap`)

On first run, before any raw source is ingested, execute `/bootstrap` to pre-populate
the wiki with knowledge already captured in this AGENTS.md. Create the following pages:

**Components (from tech spec):**
- `wiki/components/users.md`
- `wiki/components/permissions.md`
- `wiki/components/contacts.md`
- `wiki/components/leads.md`
- `wiki/components/proposals.md`
- `wiki/components/pipeline.md`
- `wiki/components/agent.md`
- `wiki/components/core.md`
- `wiki/components/api-v1.md`

**Decisions (from tech spec):**
- `wiki/decisions/2026-05-25-contact-vs-lead-separation.md`
- `wiki/decisions/2026-05-25-sqlmodel-vs-pydantic-strategy.md`
- `wiki/decisions/2026-05-25-llmprovider-abstraction.md`
- `wiki/decisions/2026-05-25-outcome-lives-in-proposal.md`
- `wiki/decisions/2026-05-25-sqlite-to-postgres-portability.md`
- `wiki/decisions/2026-05-25-domain-by-business-not-layer.md`

**Guides (from tech spec):**
- `wiki/guides/sqlmodel-vs-pydantic.md`
- `wiki/guides/domain-structure.md`
- `wiki/guides/pipeline-invariants.md`
- `wiki/guides/agent-tools.md`

After bootstrap, update `wiki/index.md` and add a single log entry in `wiki/log.md`.

---

*This file co-evolves with the project. If a convention stops working, propose a change
here before changing it across the wiki.*
