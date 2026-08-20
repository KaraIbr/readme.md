# CRM Renewables — Frontend Design Reference

> Compiled from the backend wiki. Every concept below is backed by an existing wiki page.
> See: [[overview]], [[api-v1]], [[crm-permissions]], [[pipeline-invariants]]

---

## 1. Architectural Context

| Layer | Technology | Notes |
|---|---|---|
| API | REST under `/api/v1/...` | FastAPI backend, versioned prefix |
| Auth | JWT bearer tokens | Issued by sibling IAM service, shared secret |
| Files | Multipart upload + download endpoints | Documents, bills, attachments, PDFs |
| Agent | `/api/v1/agent/chat` | LangGraph + AzureOpenAI, same auth + permissions |
| DB perms | SQLite dev / PostgreSQL prod | Engine change is `.env`-only, no API difference |

**Key principle:** The frontend never queries the DB directly. Every operation goes through the REST API.

---

## 2. Authentication & Session

### 2.1 Login flow
- POST `/api/v1/identity/auth/login` — form body (`username`, `password`), returns `access_token`, `refresh_token`, `token_type`
- POST `/api/v1/identity/auth/refresh` — form body (`refresh_token`), returns new `access_token`
- Store access token (short-lived) + refresh token (longer-lived) securely
- All subsequent requests use `Authorization: Bearer <access_token>`

### 2.2 Current user
- GET `/api/v1/identity/users/me` — returns `{ id, email, full_name }`
- Used to seed the UI identity and determine CRM access

### 2.3 CRM access check
- CRM access is separate from login. After login, check if user has CRM role.
- Role + effective permissions determine what the UI shows.
- The frontend can fetch permissions via:
  - GET `/api/v1/permissions/users/{user_id}` — returns `role`, `permissions` (role defaults), `grants`, `denials`, `effective_permissions`

---

## 3. Permission-Aware UI Rules

### 3.1 Roles & Scopes

| Role | Scope | Typical UI visibility |
|---|---|---|
| `admin` | `all` — every record in CRM | Full access, global lists |
| `manager` | `all` with guardrails | Full access + user/role management |
| `sales` | `assigned_sales` — only assigned Leads and derived records | Own Leads, Contacts, read-only Proposals/Visits |
| `tech` | `assigned_tech` — only assigned Proposals/Visits | Assigned Proposals, Visits; read-only Contacts/Leads/docs |

### 3.2 Permission-driven UI patterns

The backend permission catalog defines ~50 granular permissions. The frontend should:

1. **Fetch effective permissions once** on login/session init.
2. **Gate actions by permission key** — not by hardcoded role strings.
   - *Example:* `crm.proposals.price.set` gates the ability to fill empty price fields. Don't check `role === 'admin'`.
3. **Hide or disable UI elements** when the user lacks the permission.
4. **Respect resource scope** — even if a user has `crm.proposals.read`, they only see proposals they are assigned to (`assigned_sales` or `assigned_tech`). The backend enforces this; the frontend should filter lists accordingly or let the API scope parameters handle it.

### 3.3 Key permission groups (action-gating)

| Area | Permission pattern | Frontend impact |
|---|---|---|
| Contacts | `crm.contacts.{create,read,update,delete}` | CRUD buttons, forms |
| Leads | `crm.leads.{create,read,update,delete,stage,close,assign}` | Stage transitions, close buttons, assignment UI |
| Lead docs | `crm.leads.documents.{create,read,delete}` | Upload/download/delete buttons |
| Lead interactions | `crm.leads.interactions.{create,read,update,delete}` | Interaction timeline CRUD |
| Proposals | `crm.proposals.{create,read,update,delete,mark_won,mark_lost,stage}` | Stage transitions, won/lost buttons |
| Proposal prices | `crm.proposals.price.{set,update}` | Price field editing — separate from general update |
| Technical Visits | `crm.technical_visits.{create,read,update,complete,cancel,assign}` | Visit lifecycle buttons |
| Pipeline | `crm.pipeline.read` | History/summary view |
| Agent | `crm.agent.chat` | Agent chat panel |
| Admin | `crm.permissions.{read,manage}`, `crm.roles.assign` | User management screens |

---

## 4. Complete API Surface per Domain

### 4.1 Contacts (`/api/v1/contacts`)

**Entity model:**
```
Contact {
  id, type (INDIVIDUAL|COMPANY), name,
  promoter_id, owner_id,
  address_line, city, state, postal_code,
  created_at, updated_at
}
// Individual detail: phone, email (via individual_contact_profile)
// Company detail: industry (via company_contact_profile)
// Company people: [{ name, phone, email, position }]
```

**Promoter (catalog):**
```
Promoter { id, name, phone, owner_id }
```

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/contacts/` | Create contact (individual or company) |
| GET | `/contacts/` | List contacts (filter: `?contact_type=`, `?q=`) |
| GET | `/contacts/{id}` | Get single contact |
| PATCH | `/contacts/{id}` | Update contact |
| DELETE | `/contacts/{id}` | Delete contact |
| POST | `/contacts/promoters` | Create promoter |
| GET | `/contacts/promoters` | List promoters |
| GET | `/contacts/promoters/{id}` | Get single promoter |
| PATCH | `/contacts/promoters/{id}` | Update promoter |
| DELETE | `/contacts/promoters/{id}` | Delete promoter |
| POST | `/contacts/{company_id}/people` | Add company person |
| GET | `/contacts/{company_id}/people` | List company people |
| GET | `/contacts/{company_id}/people/{id}` | Get company person |
| PATCH | `/contacts/{company_id}/people/{id}` | Update company person |
| DELETE | `/contacts/{company_id}/people/{id}` | Delete company person |

**UI notes:**
- Contact type selector (individual vs company) on create form
- Company creation requires at least one company person
- Promoter is a required dropdown on contact create/edit
- Contact detail should show related Leads (optional: fetch via leads list filtered by `?contact_id=`)

---

### 4.2 Leads (`/api/v1/leads`)

**Entity model:**
```
Lead {
  id, contact_id, title,
  interest_type (Photovoltaic|BESS|Hibrid),
  qualification_score,
  current_stage (NEW|QUALIFYING|PROPOSAL_PHASE|CLOSED_WON|CLOSED_LOST),
  outcome (null|WON|LOST),
  owner_id,
  notes,
  technical_visit_requirement (UNDETERMINED|NOT_REQUIRED|REQUIRED),
  created_at, closed_at
}
```

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leads/` | Create lead |
| GET | `/leads/` | List leads (`?contact_id=`, `?stage=`) |
| GET | `/leads/{id}` | Get single lead |
| PATCH | `/leads/{id}` | Update lead (open only) |
| POST | `/leads/{id}/stage` | Move stage (NEW→QUALIFYING→PROPOSAL_PHASE) |
| POST | `/leads/{id}/close` | Manual close (LOST only) |
| DELETE | `/leads/{id}` | Delete lead (open only) |

**Lead documents:**
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leads/{id}/documents` | Upload document (multipart: `title` + `file`) |
| GET | `/leads/{id}/documents` | List document metadata |
| GET | `/leads/{id}/documents/{doc_id}` | Get document metadata |
| GET | `/leads/{id}/documents/{doc_id}/download` | Download file |
| DELETE | `/leads/{id}/documents/{doc_id}` | Delete document |

**Lead electricity bills:**
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leads/{id}/electricity-bills` | Upload bill (multipart: `title` + `file`) |
| GET | `/leads/{id}/electricity-bills` | List bill metadata |
| GET | `/leads/{id}/electricity-bills/{bill_id}` | Get bill metadata |
| GET | `/leads/{id}/electricity-bills/{bill_id}/download` | Download file |
| DELETE | `/leads/{id}/electricity-bills/{bill_id}` | Delete bill |

**Lead interactions (sales negotiations):**
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leads/{id}/interactions` | Create interaction (`interaction_type`, `title`, `notes`, `interaction_date`) |
| GET | `/leads/{id}/interactions` | List interactions (ordered by `interaction_date`) |
| GET | `/leads/{id}/interactions/{int_id}` | Get single interaction |
| PATCH | `/leads/{id}/interactions/{int_id}` | Update interaction |
| DELETE | `/leads/{id}/interactions/{int_id}` | Delete interaction |

**Lead assignment (permissions):**
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leads/{id}/assignment` | Assign/transfer sales follow-up |

**UI notes:**
- Lead detail is the main workspace: shows contact info, stage, proposals, interactions, documents, bills, technical visits
- Stage progression must be sequential: NEW → QUALIFYING → PROPOSAL_PHASE (no skipping)
- Close button only for LOST (WON comes from proposals)
- `tech` users cannot see interactions, only `sales`+ can
- `tech` users can see documents and electricity bills (read-only)

---

### 4.3 Proposals (`/api/v1/proposals`)

**Entity model:**
```
Proposal {
  id, lead_id, name, version,
  system_type (PV|BESS|HIBRID),
  installation_address: { line, city, state, postal_code },
  tariff, contracted_demand,
  total_price, annual_savings, currency,
  estimated_cost, expected_profit,
  submitted_at, valid_until,
  current_stage (DRAFT|SENT|NEGOTIATION|WON|LOST|SUPERSEDED),
  loss_reason,
  proposed_at,
  created_by, created_at
}
// PV detail (pv_system): panel_count, panel_model, panel_power, inverter_model,
//   inverter_count, inverter_power, type_of_surface, total_power_ac,
//   system_size_kw, oversizing_kw, estimated_annual_kwh, estimated_savings_kw,
//   connection_mode, cost_watt, price_watt
// BESS detail (bess_system): battery_model, battery_count, battery_power_kw,
//   battery_storage_kwh, bess_primary_use, technical_notes, cost_kwh, price_kwh
```

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/proposals/` | Create proposal (only `lead_id` + `name` required) |
| GET | `/proposals/` | List proposals (`?lead_id=`, `?stage=`) |
| GET | `/proposals/{id}` | Get single proposal (includes nested `pv_system`, `bess_system`) |
| PATCH | `/proposals/{id}` | Update proposal (non-terminal only) |
| POST | `/proposals/{id}/stage` | Move stage (DRAFT→SENT→NEGOTIATION) |
| POST | `/proposals/{id}/won` | Mark as won (requires `SENT`+ stage) |
| POST | `/proposals/{id}/lost` | Mark as lost (body: `{ loss_reason: string }`) |
| DELETE | `/proposals/{id}` | Delete proposal (non-terminal only) |

**Proposal documents:**
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/proposals/{id}/commercial-pdf` | Upload commercial PDF (multipart: `title` + `file`) |
| GET | `/proposals/{id}/commercial-pdf` | List commercial PDF metadata |
| GET | `/proposals/{id}/commercial-pdf/{doc_id}/download` | Download commercial PDF |
| DELETE | `/proposals/{id}/commercial-pdf/{doc_id}` | Delete commercial PDF |
| POST | `/proposals/{id}/documents` | Upload classified document (`title`, `classification`: Costs\|Technical\|Other, `file`) |
| GET | `/proposals/{id}/documents` | List classified documents (`?classification=`) |
| GET | `/proposals/{id}/documents/{doc_id}/download` | Download classified document |
| DELETE | `/proposals/{id}/documents/{doc_id}` | Delete classified document |

**Proposal assignments (tech):**
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/proposals/{id}/assignments` | Assign technical user |

**UI notes:**
- Proposal creation starts minimally (lead_id + name), then fills details
- System type selector (PV / BESS / HIBRID) determines which detail form sections to show
- **Completeness check:** before leaving DRAFT, all required fields for the system type must be filled. The API returns `is_complete` and `missing_required_fields` on the proposal read.
- **Price fields are special:** `total_price`, `price_watt`, `price_kwh` require separate price permissions. Tech users cannot edit prices.
- **Won/Lost are terminal** — after WON/LOST/SUPERSEDED, no further edits.
- **Atomic win flow:** marking one proposal WON auto-supersedes siblings and closes the Lead.
- **Loss reason is mandatory** for LOST.
- **Proposal-to-visit evidence linking** happens under technical-visits endpoints:
  - POST `/proposals/{id}/technical-visits` — link visit
  - GET `/proposals/{id}/technical-visits` — list links
  - DELETE `/proposals/{id}/technical-visits/{visit_id}` — unlink

---

### 4.4 Technical Visits (`/api/v1/technical-visits`)

**Entity model:**
```
TechnicalVisit {
  id, lead_id,
  status (REQUESTED|SCHEDULED|COMPLETED|CANCELLED),
  scheduled_at, completed_at,
  receiver_name, receiver_phone, receiver_email,
  notes, created_by, created_at
}
// Assignees: [{ user_id?, name, phone, email }]
// Attachments: [{ title, file_kind, filename, content_type, size, uploaded_by, uploaded_at }]
```

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leads/{lead_id}/technical-visit-requirement` | Set requirement decision |
| POST | `/leads/{lead_id}/technical-visits` | Create visit for a lead |
| GET | `/leads/{lead_id}/technical-visits` | List visits for a lead |
| GET | `/technical-visits` | List owned visits across all leads |
| GET | `/technical-visits/{id}` | Get single visit |
| PATCH | `/technical-visits/{id}` | Update visit (before completion) |
| POST | `/technical-visits/{id}/complete` | Mark completed |
| POST | `/technical-visits/{id}/cancel` | Cancel visit |
| POST | `/technical-visits/{id}/attachments` | Upload attachment (multipart: `title`, `file_kind`, `file`) |
| GET | `/technical-visits/{id}/attachments` | List attachment metadata |
| GET | `/technical-visits/{id}/attachments/{att_id}/download` | Download attachment |
| DELETE | `/technical-visits/{id}/attachments/{att_id}` | Delete attachment |

**UI notes:**
- Visit lifecycle: REQUESTED → SCHEDULED → COMPLETED (or CANCELLED at any time before completion)
- Scheduling requires `scheduled_at`, receiver info, and at least one assignee
- Completion requires a complete schedule + at least one attachment uploaded
- Completed/cancelled visits are read-only
- `sales` can read visits for assigned Leads; `tech` can manage assigned visits
- Proposal evidence linking is a separate action on the proposal detail page

---

### 4.5 Pipeline (`/api/v1/pipeline`)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/pipeline/transitions` | List transitions (`?entity_type=lead\|proposal`, `?entity_id=`) |
| GET | `/pipeline/summary/{entity_type}/{entity_id}` | Compact current-stage + history summary |

**Purpose:** Audit trail for all stage changes. Read-only from the frontend perspective.

---

### 4.6 Agent (`/api/v1/agent/chat`)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/agent/chat` | Send message, receive AI response |

**Body:** `{ message: string, history?: [{ role, content }] }`
**Response:** `{ answer: string, skills: string[], evidence: [...], confirmation_required: boolean }`

**UI notes:**
- Chat panel embedded in the CRM UI
- Permissions apply — agent only sees what the user can see
- Agent cannot mutate without explicit user confirmation
- Not exposed to users who lack `crm.agent.chat` permission

---

### 4.7 Permissions Admin (`/api/v1/permissions`)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/permissions` | List full permission catalog |
| GET | `/permissions/users/{user_id}` | Read user's role, overrides, effective permissions |
| PATCH | `/permissions/users/{user_id}` | Grant/deny/clear individual permissions |
| POST | `/permissions/users/{user_id}/role` | Assign CRM role template |

**UI notes:**
- Admin/manager screens only
- Manager cannot modify admin users, cannot modify own permissions/role

---

## 5. State Machines & Workflows

### 5.1 Lead Lifecycle
```
NEW ──→ QUALIFYING ──→ PROPOSAL_PHASE ──→ CLOSED_WON  (via proposal won)
                                      └──→ CLOSED_LOST  (via all proposals lost, or manual close)
```
- Stages move forward only, no backward transitions
- Manual close is LOST-only (WON is reserved for proposal outcome)
- Closed leads are immutable (no update, no delete, no stage change)
- Stage changes are all recorded in pipeline audit trail automatically

### 5.2 Proposal Lifecycle
```
DRAFT ──→ SENT ──→ NEGOTIATION ──→ WON
                               └──→ LOST
                               └──→ SUPERSEDED (auto when sibling wins)
```
- DRAFT requires minimal fields; all fields needed before leaving DRAFT
- First time a proposal is SENT, `proposed_at` is set
- WON/LOST/SUPERSEDED are terminal (no more edits)
- Only one WON per Lead (others auto-superseded)
- SUPERSEDED is automatic, never user-initiated

### 5.3 Technical Visit Lifecycle
```
REQUESTED ──→ SCHEDULED ──→ COMPLETED
     │                        ↑
     └──→ CANCELLED (any time before completion)
```
- REQUESTED = no schedule yet
- SCHEDULED = has date, receiver, assignees
- COMPLETED = has schedule + attachments
- CANCELLED = no longer needed

### 5.4 Technical Visit Requirement (Lead-level)
```
UNDETERMINED ──→ NOT_REQUIRED
            └──→ REQUIRED (auto-set when first visit created)
```
- Creating a visit for NOT_REQUIRED is rejected
- UNDETERMINED auto-upgrades to REQUIRED when a visit is created

---

## 6. Business Rules the Frontend Must Enforce (or Let the API Reject)

1. **Only one WON proposal per Lead** — UI should disable "Mark won" on other proposals when one is already WON.
2. **Loss reason required for LOST** — the LOST form must have a required `loss_reason` field.
3. **Proposal completeness before leaving DRAFT** — the UI should validate all required fields for the selected system type before allowing DRAFT→SENT.
4. **Lead contact must be owned by user** — the contact picker on lead creation should only show contacts the user owns (or has scope over).
5. **Cannot create proposal for closed lead** — disabled or hidden.
6. **Company contacts must have ≥1 company person** — the company creation flow must include at least one person entry.
7. **Visit completion requires attachments** — the "complete" action should be gated on having uploaded at least one attachment.
8. **Proposal→visit links must share the same Lead** — the visit picker should filter to visits belonging to the same Lead.
9. **Price field separation** — price fields should have a different edit guard than regular fields. Show lock icon when user lacks price permission.
10. **Interaction date is required** — date picker for past, present, or future dates.
11. **Interest type is constrained** — dropdown: Photovoltaic, BESS, Hibrid (only these three).
12. **Stage transitions are sequential** — only show the next valid stage as actionable.

---

## 7. Suggested UI Navigation Structure

### Main navigation (sidebar)
```
┌─────────────────────────┐
│ 🔍  Dashboard / Overview │ — summary cards, pipeline funnel
│ 👥  Contacts              │ — contact + promoter management
│ 📋  Leads                 │ — lead list + kanban or table
│ 📄  Proposals             │ — proposal list per lead context
│ 🔧  Technical Visits      │ — visit list + calendar view
│ 📊  Pipeline              │ — audit trail viewer
│ 🤖  Agent                 │ — AI chat assistant
│ ⚙️  Admin                 │ — (role=admin|manager only)
│     ├─ Users & Permissions│ — role assignment, permission overrides
│     └─ Permission Catalog │ — view defined permissions
└─────────────────────────┘
```

### Detail page layout pattern
For most entities (Lead, Proposal, Contact, Visit):
```
┌────────────────────────────────────────────┐
│  Header: Name/Title + Stage Badge + Actions│
├──────────┬─────────────────────────────────┤
│          │                                 │
│  Sidebar │  Main Content Area              │
│  / Tabs  │  (context-sensitive sections)   │
│          │                                 │
│  Info    │  Example Lead tabs:             │
│  Stage   │  - Details (form)               │
│  Owner   │  - Interactions (timeline)      │
│  Dates   │  - Documents (file list)        │
│          │  - Electricity Bills            │
│          │  - Proposals (sub-list)         │
│          │  - Technical Visits (sub-list)  │
│          │  - Pipeline History (audit)     │
└──────────┴─────────────────────────────────┘
```

### Permission-gated actions summary

| UI Element | Required Permission | Visible to |
|---|---|---|
| Contact create/edit/delete buttons | `crm.contacts.{create,update,delete}` | sales, manager, admin |
| Lead create/edit/delete buttons | `crm.leads.{create,update,delete}` | sales, manager, admin |
| Lead stage move buttons | `crm.leads.stage.update` | sales, manager, admin |
| Lead close button | `crm.leads.close` | sales, manager, admin |
| Lead assignment UI | `crm.leads.assign` | manager, admin |
| Interaction CRUD | `crm.leads.interactions.*` | sales, manager, admin (NOT tech) |
| Proposal create/edit/delete | `crm.proposals.{create,update,delete}` | manager, admin (tech: assigned only, no delete) |
| Proposal mark won/lost | `crm.proposals.mark_won`, `crm.proposals.mark_lost` | manager, admin |
| Proposal price fields | `crm.proposals.price.set`, `crm.proposals.price.update` | manager, admin (NOT tech, NOT sales) |
| Proposal stage move | `crm.proposals.stage.update` | manager, admin |
| Tech assignment | `crm.proposals.assign_tech` | manager, admin |
| Visit create/update/complete/cancel | `crm.technical_visits.*` | tech, manager, admin |
| Visit attachment upload/delete | `crm.technical_visits.attachments.*` | tech, manager, admin |
| Pipeline view | `crm.pipeline.read` | all roles |
| Agent chat | `crm.agent.chat` | all roles (scoped) |
| Admin: user permissions | `crm.permissions.{read,manage}`, `crm.roles.assign` | manager, admin |

---

## 8. Upload Handling Reference

All file uploads use multipart form data. Key patterns:

| Domain | Upload endpoint | Fields | Download |
|---|---|---|---|
| Lead document | POST `/leads/{id}/documents` | `title` (str), `file` (binary) | GET `.../documents/{id}/download` |
| Lead electricity bill | POST `/leads/{id}/electricity-bills` | `title` (str), `file` (binary) | GET `.../electricity-bills/{id}/download` |
| Proposal commercial PDF | POST `/proposals/{id}/commercial-pdf` | `title` (str), `file` (binary, PDF) | GET `.../commercial-pdf/{id}/download` |
| Proposal classified doc | POST `/proposals/{id}/documents` | `title` (str), `classification` (Costs\|Technical\|Other), `file` (binary) | GET `.../documents/{id}/download` |
| Visit attachment | POST `/visits/{id}/attachments` | `title` (str), `file_kind` (str), `file` (binary) | GET `.../attachments/{id}/download` |

All list endpoints return metadata only (no file content). Download is a separate endpoint.

---

## 9. Error Handling

The API returns standard HTTP codes:
- `200` — success
- `201` — created
- `401` — unauthorized (missing/invalid token)
- `403` — forbidden (lacks permission or scope)
- `404` — not found (or not in user's scope)
- `409` — conflict (business rule violation, e.g., already closed)
- `422` — validation error (Pydantic validation details in response)

Frontend should:
- Handle 401 by attempting token refresh, then redirect to login
- Handle 403 by hiding the action and optionally showing a message
- Handle 409 by showing the specific business rule message
- Handle 422 by displaying field-level validation errors from the response

---

## 10. Suggested Tech Stack for Frontend

Based on the backend patterns (FastAPI, async, structured DTOs):

| Concern | Suggestion | Rationale |
|---|---|---|
| Framework | React + TypeScript | Wide ecosystem, type safety |
| State / Data fetching | TanStack Query (React Query) | Matches REST patterns, caching, mutations |
| HTTP client | Axios or fetch + interceptors | Token refresh interceptor |
| Forms | React Hook Form + Zod | Validation mirrors Pydantic patterns |
| UI components | shadcn/ui + Tailwind CSS | Accessible, customizable, permission-gating friendly |
| Auth flow | JWT storage + interceptor | Refresh-token rotation |
| File upload | Multipart form, upload progress | Direct match to backend expectations |

---

*This document is derived from the CRM wiki. Every endpoint, permission, business rule, and entity definition references backend wiki pages. When the backend changes, update this document to match.*
