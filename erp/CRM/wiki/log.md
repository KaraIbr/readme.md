### 2026-05-25 - bootstrap
- **Source:** CRM/AGENTS.md and CRM/docs/tech-spec.md
- **Pages created:** [[overview]], [[users]], [[contacts]], [[leads]], [[proposals]], [[pipeline]], [[agent]], [[core]], [[api-v1]], [[2026-05-25-contact-vs-lead-separation]], [[2026-05-25-sqlmodel-vs-pydantic-strategy]], [[2026-05-25-llmprovider-abstraction]], [[2026-05-25-outcome-lives-in-proposal]], [[2026-05-25-sqlite-to-postgres-portability]], [[2026-05-25-domain-by-business-not-layer]], [[sqlmodel-vs-pydantic]], [[domain-structure]], [[pipeline-invariants]], [[agent-tools]]
- **Pages updated:** [[index]]
- **Notes:** Pre-populated the wiki with the components, decisions, guides, and overview described by the project specification.

### 2026-05-25 - path correction
- **Source:** direct user correction
- **Pages created:** none
- **Pages updated:** [[overview]], [[users]], [[contacts]], [[leads]], [[proposals]], [[pipeline]], [[agent]], [[core]], [[api-v1]]
- **Notes:** Corrected documented service-internal component paths to `src/...` because `CRM/` is already the service root.

### 2026-05-25 - tech spec path cleanup
- **Source:** CRM/docs/tech-spec.md
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Cleaned remaining package-path references in the technical specification so the service layout uses `CRM/src/...` without a nested `crm` package.

### 2026-05-25 - core implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[core]]
- **Notes:** Implemented the initial `CRM/src/core/` package for settings, database sessions, security helpers, structlog configuration, and FastAPI exception handlers with focused unit tests.

### 2026-05-26 - users implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[users]]
- **Notes:** Implemented `CRM/src/domains/users/` with `User` model, DTOs, repository, service, router, JWT login/refresh flow, shared `current_user` dependency, API v1 aggregation, focused unit/integration tests, and minimal mypy configuration for the `CRM/src` layout.

### 2026-05-26 - contacts implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[contacts]], [[api-v1]]
- **Notes:** Implemented `CRM/src/domains/contacts/` with `Contact` model, DTOs, repository, service, authenticated CRUD router, API v1 aggregation, owner scoping, B2B parent-company validation, and focused unit/integration tests.

### 2026-05-26 - leads implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[leads]], [[api-v1]], [[core]]
- **Notes:** Implemented `CRM/src/domains/leads/` with `Lead` model, DTOs, repository, service, authenticated router, API v1 aggregation, owner-scoped contact validation, open-stage movement, terminal close flow, focused unit/integration tests, and a validation-error serialization fix in `CRM/src/core/exceptions.py`.

### 2026-05-26 - proposals implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[proposals]], [[api-v1]]
- **Notes:** Implemented `CRM/src/domains/proposals/` with `Proposal` model, DTOs, repository, service, authenticated router, API v1 aggregation, owner-scoped lead validation, non-terminal stage movement, `mark_won` sibling superseding plus lead close, `mark_lost` loss-reason enforcement plus all-lost lead close, and focused unit/integration tests.

### 2026-05-27 - pipeline implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[pipeline]], [[api-v1]], [[proposals]], [[leads]]
- **Notes:** Implemented `CRM/src/domains/pipeline/` with `StageTransition` audit model, transition repository/service/router, `/api/v1/pipeline/transitions`, `/api/v1/pipeline/summary/{entity_type}/{entity_id}`, owner-scoped summaries, initial transition recording for new Leads/Proposals, audit recording for existing Lead/Proposal stage flows, and focused unit/integration tests.

### 2026-05-27 - agent runtime architecture
- **Source:** direct architecture clarification
- **Pages created:** [[agent-runtime-architecture]]
- **Pages updated:** [[index]], [[agent]], [[agent-tools]]
- **Notes:** Documented the CRM product runtime agent architecture, including LangGraph nodes, runtime SKILL.md bundles, domain-service tools, evidence policy, ambiguity handling, deterministic calculations, owner scoping, and confirmation gates for write operations.

### 2026-05-27 - agent runtime implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[agent]], [[agent-tools]], [[agent-runtime-architecture]]
- **Notes:** Implemented `CRM/src/agent/` with authenticated `/api/v1/agent/chat`, LangGraph state machine, AzureOpenAI `LLMProvider`, runtime skill registry and starter `SKILL.md` bundles, owner-scoped LangChain tools for contacts/leads/proposals/pipeline, deterministic proposal metrics, service-level search helpers, and focused unit/integration tests. Write tools remain planned behind confirmation gates.

### 2026-05-27 - agent Azure smoke test
- **Source:** direct smoke-test request
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Smoke-tested `/api/v1/agent/chat` with an in-memory CRM dataset and AzureOpenAI. The endpoint returned 200, selected proposal and metric skills, called contact/lead/proposal/metric tools, and returned evidence. Adjusted response parsing for Responses API text blocks and tightened metric instructions to avoid model-side arithmetic.

### 2026-05-27 - agent continuation notes
- **Source:** direct pause request
- **Pages created:** [[agent-runtime-hardening]]
- **Pages updated:** [[index]], [[agent]], [[agent-runtime-architecture]]
- **Notes:** Documented remaining agent work before pausing implementation: confirmation-gated write tools, stronger entity resolution, skill refinement, eval scenarios, cost data for margins, final-answer validation, conversation-state decision, and Azure environment precedence safeguards.

### 2026-05-27 - api v1 implementation check
- **Source:** direct implementation-readiness request
- **Pages created:** none
- **Pages updated:** [[api-v1]]
- **Notes:** Verified `src/api/v1/router.py` mounts users, contacts, leads, proposals, pipeline, and agent routers under `/api/v1`; ran the full test suite successfully and marked the API v1 aggregation component stable.

### 2026-05-27 - local REST testing setup
- **Source:** direct local testing request
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Added a repository-root local launcher for the CRM FastAPI app, development SQLite table bootstrap on startup, gitignore coverage for local SQLite files, and ready-to-paste REST request examples in `CRM/docs/local-rest.http`.

### 2026-05-27 - service-specific CRM launcher
- **Source:** direct monorepo-readiness request
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Moved the local CRM API launcher responsibility into `CRM/main.py` and returned the repository root `main.py` to a service-neutral workspace helper so future services can add their own launchers without ambiguity.

### 2026-05-27 - REST body catalog
- **Source:** direct local testing request
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Added `CRM/docs/rest-json-bodies.md` with ready-to-copy request bodies for users, contacts, leads, proposals, pipeline, and agent endpoints, including endpoints that require form data or no body.

### 2026-05-28 - contacts promoter redesign
- **Source:** direct design request
- **Pages created:** [[2026-05-28-contact-promoters-and-company-people]]
- **Pages updated:** [[contacts]], [[api-v1]], [[index]], [[overview]]
- **Notes:** Documented the proposed contacts redesign: `source` becomes an owner-scoped `Promoter` entity, contacts link through `promoter_id`, companies drop direct email/phone/tax/country/website fields, company representatives move to `CompanyContactPerson`, and individual client contacts drop tax/country/name-split/parent/role fields. `raw/` was not modified because CRM/AGENTS.md marks raw sources immutable and the current raw tree has no files.

### 2026-05-28 - contacts promoter implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[contacts]], [[api-v1]], [[2026-05-28-contact-promoters-and-company-people]]
- **Notes:** Implemented `Promoter`, `CompanyContactPerson`, and `Contact.promoter_id` in `CRM/src/domains/contacts/`; replaced contact `source`, removed legacy tax/country/name-split/parent/role/website contact fields, added promoter and company-person endpoints under `/api/v1/contacts`, updated agent contact formatting, tests, REST examples, the technical specification, and the contacts wiki note about recreating development SQLite databases because migrations are not present yet.

### 2026-05-29 - leads documents and interactions implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[leads]], [[contacts]], [[api-v1]], [[core]]
- **Notes:** Removed lead `source`, `estimated_budget`, and `estimated_capacity_kw`; constrained `interest_type` to `Photovoltaic`, `BESS`, and `Hibrid`; added separate lead-scoped tables and API routes for general documents and electricity bills; added lead-level sales interaction/negotiation records; updated agent lead formatting, tests, REST examples, the technical specification, and upload storage configuration. Development SQLite databases created before this redesign must be recreated because migrations are not present yet.

### 2026-05-29 - lead interaction date required
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[leads]]
- **Notes:** Replaced lead interaction `occurred_at` with required `interaction_date` so interactions can be recorded for past, present, or future planned dates; updated service ordering, DTOs, tests, REST examples, and the technical specification.

### 2026-05-29 - proposal PV BESS HIBRID redesign
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[proposals]], [[api-v1]]
- **Notes:** Redesigned proposals around `PV`, `BESS`, and `HIBRID` system types with progressive draft entry requiring only `lead_id` and `name`; added common commercial fields, structured installation address, PV-specific fields, BESS-specific fields, completeness metadata and enforcement before leaving `DRAFT`; added dedicated commercial proposal PDF uploads plus classified proposal documents (`Costs`, `Technical`, `Other`); updated agent proposal formatting/metrics, runtime skill notes, REST examples, technical specification, and focused tests. Development SQLite databases created before this redesign must be recreated because migrations are not present yet.

### 2026-05-29 - database subtype normalization
- **Source:** direct implementation review request
- **Pages created:** none
- **Pages updated:** [[proposals]], [[contacts]]
- **Notes:** Normalized subtype-specific database fields: moved PV proposal fields into one-to-one `proposal_pv_system`, BESS proposal fields into one-to-one `proposal_bess_system`, individual contact email/phone into one-to-one `individual_contact_profile`, and company industry into one-to-one `company_contact_profile`. The API keeps convenient nested proposal detail payloads and flat contact read fields while the database no longer stores subtype columns on the common header tables. Reviewed the remaining current tables: Leads already separates documents, electricity bills, and interactions; Users is a compact auth/owner entity; Pipeline remains a deliberate append-only polymorphic audit table. Updated tests, agent formatting/metrics, REST examples, technical specification, and component wiki pages. Development SQLite databases created before this redesign must be recreated because migrations are not present yet.

### 2026-05-29 - pipeline REST response examples
- **Source:** direct documentation request
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Added example JSON responses for `GET /pipeline/transitions` and `GET /pipeline/summary/{entity_type}/{entity_id}` in `CRM/docs/rest-json-bodies.md`.

### 2026-05-29 - technical visit design consultation
- **Source:** direct design request
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Reviewed CRM agent instructions plus the current Leads, Proposals, Pipeline, outcome-in-proposal, and domain-structure wiki pages to advise on modeling optional technical visits. No ADR or component page was created because the business decision is still under discussion.

### 2026-05-29 - technical visits design accepted
- **Source:** direct implementation request
- **Pages created:** [[2026-05-29-technical-visits-as-lead-subprocess]], [[technical-visits]]
- **Pages updated:** [[index]], [[overview]], [[leads]], [[proposals]], [[api-v1]]
- **Notes:** Documented the accepted design: technical visits are optional Lead-scoped subprocesses with their own lifecycle and attachments; Proposal evidence uses a `ProposalTechnicalVisit` relationship table rather than a direct Proposal field; Lead keeps an explicit visit requirement decision.

### 2026-05-29 - technical visits implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[technical-visits]], [[leads]], [[proposals]], [[api-v1]], [[core]]
- **Notes:** Implemented `CRM/src/domains/technical_visits/` with Lead requirement updates, requested/scheduled/completed/cancelled visit lifecycle, visit assignees, evidence attachments, Proposal-to-visit links constrained to the same Lead, API v1 route aggregation, and unit/integration tests. Added `Lead.technical_visit_requirement`; development SQLite databases created before this change must be recreated because migrations are not present yet.

### 2026-05-29 - shared Ventura SQLite database
- **Source:** direct database recreation request
- **Pages created:** none
- **Pages updated:** [[core]]
- **Notes:** Changed the CRM default development SQLite URL to `sqlite+aiosqlite:///./ventura.db` so the database lives at the VERP workspace root and can be shared by future services. Recreated the local SQLite schema from current SQLModel metadata.

### 2026-05-29 - proposal unit economics fields
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[proposals]]
- **Notes:** Added PV unit economics fields `cost_watt` and `price_watt` to `ProposalPVSystem`, BESS unit economics fields `cost_kwh` and `price_kwh` to `ProposalBESSSystem`, and documented that `HIBRID` proposals carry all four fields through both detail rows. Updated API DTOs, agent proposal records/metrics, REST examples, technical specification, focused tests, and the local `ventura.db` schema.

### 2026-06-01 - database integrity baseline
- **Source:** direct database design review follow-up
- **Pages created:** none
- **Pages updated:** [[core]], [[contacts]], [[leads]], [[proposals]], [[technical-visits]]
- **Notes:** Initialized root Alembic configuration with an initial CRM schema migration, added SQLModel metadata model registry, enabled SQLite foreign-key enforcement for application connections, added database-level check/unique constraints and query-aligned composite indexes, and recreated the empty local `ventura.db` from Alembic with a backup kept as `ventura.db.before_alembic_20260601.bak`.

### 2026-06-01 - permissions design kickoff
- **Source:** direct design request
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Read `CRM/AGENTS.md`, current wiki index/log, users and API v1 component pages, then inspected current routers and auth dependencies to start mapping user actions to required permissions. Current implementation authenticates most CRM endpoints with `CurrentUser`, scopes CRM records to the authenticated user's ownership fields, and stores roles `admin`, `manager`, and `sales`, but does not yet enforce role-based permissions.

### 2026-06-01 - role templates and user overrides discussion
- **Source:** direct design clarification
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Discussed a hybrid authorization model: roles as permission templates, per-user permission grants/denials as overrides, resource assignment rules for sales users, technical-user access to proposals and technical visits, and field-level protection for established proposal price fields. Current model fields inspected include `Contact.owner_id`, `Lead.owner_id`, `Proposal.created_by`, `TechnicalVisit.created_by`, `TechnicalVisitAssignee.user_id`, and proposal price fields `total_price`, `price_watt`, and `price_kwh`.

### 2026-06-01 - permissions architecture documentation
- **Source:** direct documentation request
- **Pages created:** [[2026-06-01-verp-identity-crm-permissions]], [[permissions]], [[crm-permissions]]
- **Pages updated:** [[index]], [[overview]], [[users]], [[contacts]], [[leads]], [[proposals]], [[technical-visits]], [[pipeline]], [[agent]], [[api-v1]], [[agent-runtime-architecture]]
- **Notes:** Documented the accepted authorization design: VERP central identity owns users and service access; CRM owns permission catalog, role templates, user overrides, assignment-scoped resource access, manager guardrails, sales and tech scope rules, agent permission inheritance, and protected Proposal price permissions. Updated `CRM/docs/tech-spec.md` with the same implementation-ready design and noted that `price_watt` and `price_kwh` should later be calculated and rounded to four decimal places.

### 2026-06-01 - permissions implementation
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[permissions]], [[crm-permissions]], [[users]], [[contacts]], [[leads]], [[proposals]], [[technical-visits]], [[pipeline]], [[api-v1]]
- **Notes:** Implemented `src/domains/permissions/` with code-defined permission catalog and role templates, `tech` role support, user permission overrides, Lead and Proposal assignment tables, manager/admin guardrails, route-level permission checks, assignment-scoped resource checks for sales and tech users, agent/pipeline scope reuse, and protected Proposal price permissions. Added Alembic migration `f4b8f4d6c2b1_crm_permissions.py`, upgraded local `ventura.db`, updated technical/REST docs, and added integration coverage for sales lead transfer, tech proposal access, blocked Lead interactions, and blocked price edits. Verified with `ruff`, `mypy`, full `pytest`, Alembic upgrade on a temporary SQLite database, and Alembic check.

### 2026-06-01 - VERP identity user service
- **Source:** direct implementation request
- **Pages created:** none
- **Pages updated:** [[users]], [[permissions]], [[crm-permissions]], [[api-v1]], [[overview]]
- **Notes:** Moved the concrete user/auth implementation to shared `src/verp/identity/`, mounted central user endpoints at `/api/v1/identity/users`, removed `/api/v1/users` from API v1 aggregation, and left `src/domains/users/` as a compatibility facade for existing imports. Added `User.is_platform_admin` with migration `a91c8d0f5b2e_verp_identity_platform_admin.py`; the first user bootstraps platform admin access, while later user creation requires a platform-admin token. Updated REST docs and tests, upgraded local `ventura.db`, confirmed mounted user routes, and verified with `ruff`, `mypy`, full `pytest`, and Alembic check.

### 2026-06-01 - AGENTS identity map alignment
- **Source:** documentation verification follow-up
- **Pages created:** none
- **Pages updated:** none
- **Notes:** Updated `CRM/AGENTS.md` project context so the canonical component map points users/auth to shared `src/verp/identity/`, marks `src/domains/users/` as a compatibility facade only, includes the CRM permissions module, and lists the permissions component in bootstrap guidance.

### 2026-06-01 - VERP identity and CRM access separation
- **Source:** corrective implementation request
- **Pages created:** none
- **Pages updated:** [[users]], [[permissions]], [[crm-permissions]], [[api-v1]], [[overview]]
- **Notes:** Removed CRM role and `is_platform_admin` from the central `User` model. Added VERP-level permission overrides under `src/verp/permissions/` for central actions such as `verp.users.create`, added `CRMUserAccess` under `src/domains/permissions/` for CRM roles, and changed central user creation to require explicit VERP permission after first-user bootstrap. Added Alembic migration `b6c2d8f90a31_separate_verp_identity_crm_access.py`, updated REST/wiki/docs, upgraded local `ventura.db`, verified a fresh Alembic upgrade from scratch, and re-ran `ruff`, `mypy`, and full `pytest`.

### 2026-06-01 - IAM sibling service correction for CRM permissions
- **Source:** corrective implementation request
- **Pages created:** none
- **Pages updated:** [[users]], [[permissions]], [[crm-permissions]], [[api-v1]], [[overview]], [[leads]], [[proposals]]
- **Notes:** Removed the incorrect `CRM/src/verp` package. CRM now treats `src/domains/users/` as a read-only reference to IAM-owned `iam_user` and `iam_service_access` tables; user creation, password authentication, IAM permissions, and service-access grants belong to the sibling `IAM/` service. CRM-specific role templates, overrides, assignments, and resource checks remain in `src/domains/permissions/`, require active IAM service access for `crm`, and keep CRM foreign keys pointed at `iam_user.id`. Added Alembic migration `d9f0c3a2b4e1_crm_references_iam_users.py`, migrated the local `ventura.db` after backing it up as `ventura.db.before_crm_iam_reference_20260601.bak`, updated CRM docs and tests, and verified with `ruff`, `mypy`, full `pytest`, CRM Alembic check, and fresh IAM-then-CRM migration/check runs on a shared SQLite database.

### 2026-07-06 - B2B funnel product alignment
- **Source:** Finish CRM B2B wiki-aligned plan
- **Pages created:** [[2026-07-06-lead-centric-funnel-opportunities-deferred]], [[activities]], [[companies]], [[opportunities]], [[activities-vs-lead-interactions]]
- **Pages updated:** [[index]], [[overview]]
- **Notes:** Documented v1 Lead-centric funnel; Opportunities deferred from product UX; Activities vs Lead interactions guide; companies API facade page.
