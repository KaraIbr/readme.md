# MVP Implementation Plan

## Legend

```
[BACKEND]  → Complete, ready to consume
[FRONTEND] → Status: EMPTY / STUB / PARTIAL / DONE
PERM       → Permission(s) required
SCHEMA     → Key request/response fields
RULE       → Business logic constraints (from backend service layer)
ENDPOINT   → API endpoint(s)
```

---

## P1 — AUTH & FOUNDATION

### 1.1 Fix AuthProvider — real login integration

```
[BACKEND]  POST /api/v1/identity/auth/login → { access_token, refresh_token, token_type }
           POST /api/v1/identity/auth/refresh → { access_token }
           GET  /api/v1/identity/users/me → { id, email, full_name }
[FRONTEND] AuthProvider.tsx currently uses hardcoded MOCK_USER
           Auth service already calls real endpoints but AuthProvider ignores result
PERM       none (authentication is open)
SCHEMA     LoginResponse: { access_token: str, refresh_token: str, token_type: str }
RULE       AuthProvider.login() must:
           1. Call auth.login() → store tokens via setTokens()
           2. Call auth.getCurrentUser() → set real user state
           3. QueryClient must be invalidated after login
```

**Files:** `AuthProvider.tsx`, `auth.service.ts` (exists), `api-client.ts` (exists)

---

### 1.2 Fix permissions role normalization

```
[BACKEND]  UserRole.ADMIN = "admin" (lowercase)
[FRONTEND] showFor arrays use "ADMIN" (uppercase)
STATUS     ✅ DONE (useEffectivePermissions now calls .toUpperCase())
```

---

### 1.3 Fix contacts data shape mismatch

```
[BACKEND]  GET /api/v1/contacts/ → list[ContactRead] (unpaginated)
[FRONTEND] ContactsService expects PaginatedResponse { items, total, limit, offset }
SCHEMA     Backend route returns flat array, NOT { items: [...] }
RULE       Option A: Add pagination wrapper in frontend service
           Option B: Make backend return paginated response
           RECOMMENDED: Option A — wrap response in { items, total, limit, offset }
```

**Files:** `contacts.service.ts`, `ContactListPage.tsx`

---

## P2 — LEADS (Core CRM feature)

### 2.1 Leads — Types

```
[BACKEND]  schemas.LeadCreate, LeadUpdate, LeadRead, LeadClose, LeadStageChange
           schemas.LeadDocumentRead, LeadElectricityBillRead
           schemas.LeadInteractionCreate, LeadInteractionUpdate, LeadInteractionRead
[FRONTEND] src/features/leads/types/ — EMPTY
SCHEMA     LeadCreate: { contact_id: int!, title: str!, interest_type: str!,
                         qualification_score?: int(0-100), notes?: str }
           LeadRead: { id, contact_id, title, interest_type, qualification_score?,
                       current_stage: LeadStage, outcome?, owner_id, notes?,
                       technical_visit_requirement, created_at, closed_at? }
           LeadStage enum: NEW | QUALIFYING | PROPOSAL_PHASE | CLOSED_WON | CLOSED_LOST
           LeadOutcome enum: WON | LOST
           LeadInterestType enum: Photovoltaic | BESS | Hibrid

           LeadDocumentRead: { id, lead_id, title, original_filename,
                               content_type?, size_bytes, uploaded_by, uploaded_at }
           LeadElectricityBillRead: same fields as LeadDocumentRead

           LeadInteractionCreate: { interaction_type: str!, title: str!,
                                    notes: str!, interaction_date: datetime! }
           LeadInteractionType enum: CALL | EMAIL | MEETING | MESSAGE | NEGOTIATION | NOTE
PERM       crm.leads.create | crm.leads.read | crm.leads.update | crm.leads.delete
RULE       Closed leads (WON/LOST) cannot be modified
           Stage endpoint only allows non-terminal transitions
           Close endpoint: LOST allowed directly, WON must come from proposal
```

---

### 2.2 Leads — Service + Queries + Mutations

```
[FRONTEND] src/features/leads/services/ — EMPTY
           src/features/leads/queries/ — EMPTY
           src/features/leads/mutations/ — EMPTY
ENDPOINT   POST   /api/v1/leads/                                         create
           GET    /api/v1/leads/?contact_id=&stage=&limit=&offset=        list
           GET    /api/v1/leads/{id}                                      detail
           PATCH  /api/v1/leads/{id}                                      update
           DELETE /api/v1/leads/{id}                                      delete
           POST   /api/v1/leads/{id}/stage                                stage change
           POST   /api/v1/leads/{id}/close                                close
           POST   /api/v1/leads/{id}/documents                            upload doc
           GET    /api/v1/leads/{id}/documents                            list docs
           DELETE /api/v1/leads/{id}/documents/{doc_id}                   delete doc
           GET    /api/v1/leads/{id}/documents/{doc_id}/download          download doc
           POST   /api/v1/leads/{id}/electricity-bills                    upload bill
           GET    /api/v1/leads/{id}/electricity-bills                    list bills
           DELETE /api/v1/leads/{id}/electricity-bills/{bill_id}          delete bill
           GET    /api/v1/leads/{id}/electricity-bills/{bill_id}/download download bill
           POST   /api/v1/leads/{id}/interactions                         create interaction
           GET    /api/v1/leads/{id}/interactions                         list interactions
           PATCH  /api/v1/leads/{id}/interactions/{int_id}                update interaction
           DELETE /api/v1/leads/{id}/interactions/{int_id}                delete interaction
PERM       crm.leads.documents.create/read/delete
           crm.leads.electricity_bills.create/read/delete
           crm.leads.interactions.create/read/update/delete
           crm.leads.stage.update | crm.leads.close
```

---

### 2.3 Leads — List Page

```
[FRONTEND] src/features/leads/pages/LeadListPage.tsx — STUB
ENDPOINT   GET /api/v1/leads/?stage=&limit=&offset=
PERM       crm.leads.read
SCHEMA     Returns LeadRead[] — render: title, contact name, stage badge,
           interest type, owner, created_at
RULE       SALES sees own leads, TECH sees assigned, ADMIN/MANAGER sees all
UI         DataTable with columns + "New Lead" button + filter by stage
```

---

### 2.4 Leads — Create Page

```
[FRONTEND] src/features/leads/pages/LeadCreatePage.tsx — STUB
ENDPOINT   POST /api/v1/leads/ (201)
PERM       crm.leads.create
SCHEMA     Form: contact_id (select from contacts), title,
           interest_type (enum select), qualification_score (0-100 slider),
           notes (textarea)
RULE       Contact must exist and be owned/visible
           Initial pipeline transition recorded automatically
```

---

### 2.5 Leads — Detail Page

```
[FRONTEND] src/features/leads/pages/LeadDetailPage.tsx — STUB
ENDPOINT   GET    /api/v1/leads/{id}                          → LeadRead
           PATCH  /api/v1/leads/{id}                          → update
           DELETE /api/v1/leads/{id}                          → 204
           POST   /api/v1/leads/{id}/stage                    → stage change
           POST   /api/v1/leads/{id}/close                    → close
PERM       crm.leads.read/update/delete/stage.update/close
UI         Tabs or sections:
           - Info (title, contact, interest, score, stage badge)
           - Stage history (from pipeline transitions)
           - Documents (upload, list, download, delete)
           - Electricity bills (upload, list, download, delete)
           - Interactions (timeline with create/edit/delete)
           - Stage change buttons / Close lead action
RULE       Stage change: only valid transitions per pipeline rules
           Close: LOST only (WON from proposal workflow)
           Closed leads: all mutations disabled
```

---

## P3 — PROPOSALS (Core CRM feature)

### 3.1 Proposals — Types

```
[BACKEND]  schemas.ProposalCreate, ProposalUpdate, ProposalRead, ProposalStageChange,
           ProposalLost, ProposalPVSystemRead, ProposalBESSSystemRead,
           ProposalCommercialDocumentRead, ProposalDocumentRead
[FRONTEND] src/features/proposals/types/ — EMPTY
SCHEMA     ProposalCreate: { lead_id: int!, name: str!, version?: str,
                             installation_address?: { address_line?, city?, state?,
                             postal_code? }, tariff?, contracted_demand?,
                             system_type?, total_price?, annual_savings?,
                             currency?, estimated_cost?, expected_profit?,
                             submitted_at?, valid_until?, pv_system?, bess_system? }
           ProposalRead: { id, lead_id, name, version, installation_address,
                           tariff, contracted_demand, system_type, total_price,
                           annual_savings, currency, estimated_cost, expected_profit,
                           submitted_at, valid_until, pv_system?, bess_system?,
                           is_complete, missing_required_fields, current_stage,
                           loss_reason?, proposed_at?, created_by, created_at }
           ProposalStage enum: DRAFT | SENT | NEGOTIATION | WON | LOST | SUPERSEDED
           ProposalSystemType enum: PV | BESS | HIBRID
           ProposalDocumentClassification enum: Costs | Technical | Other

           ProposalPVSystemPayload: { panel_count?, panel_model?, panel_power?,
             inverter_model?, inverter_count?, inverter_power?, type_of_surface?,
             total_power_ac?, system_size_kw?, oversizing_kw?, estimated_annual_kwh?,
             estimated_savings_kw?, connection_mode?, cost_watt?, price_watt? }
           ProposalBESSSystemPayload: { battery_model?, battery_count?,
             battery_power_kw?, battery_storage_kwh?, bess_primary_use?,
             technical_notes?, cost_kwh?, price_kwh? }
PERM       crm.proposals.create/read/update/delete
RULE       Price fields require crm.proposals.price.set or price.update
           Only one WON proposal per lead (unique partial index)
           Missing required fields listed in missing_required_fields
```

---

### 3.2 Proposals — Service + Queries + Mutations

```
[FRONTEND] src/features/proposals/services/ — EMPTY
           src/features/proposals/queries/ — EMPTY
           src/features/proposals/mutations/ — EMPTY
ENDPOINT   POST   /api/v1/proposals/                                          create (201)
           GET    /api/v1/proposals/?lead_id=&stage=&limit=&offset=            list
           GET    /api/v1/proposals/{id}                                       detail
           PATCH  /api/v1/proposals/{id}                                       update
           DELETE /api/v1/proposals/{id}                                       204
           POST   /api/v1/proposals/{id}/stage                                 stage change
           POST   /api/v1/proposals/{id}/won                                   mark won
           POST   /api/v1/proposals/{id}/lost                                  mark lost
           POST   /api/v1/proposals/{id}/commercial-pdf                        upload PDF
           GET    /api/v1/proposals/{id}/commercial-pdf                        list PDFs
           DELETE /api/v1/proposals/{id}/commercial-pdf/{doc_id}               delete PDF
           GET    /api/v1/proposals/{id}/commercial-pdf/{doc_id}/download      download PDF
           POST   /api/v1/proposals/{id}/documents                             upload doc
           GET    /api/v1/proposals/{id}/documents/?classification=            list docs
           DELETE /api/v1/proposals/{id}/documents/{doc_id}                    delete doc
           GET    /api/v1/proposals/{id}/documents/{doc_id}/download           download doc
PERM       crm.proposals.stage.update | crm.proposals.mark_won | crm.proposals.mark_lost
           crm.proposals.commercial_documents.* | crm.proposals.documents.*
           crm.proposals.price.set | crm.proposals.price.update
```

---

### 3.3 Proposals — List Page

```
[FRONTEND] src/features/proposals/pages/ProposalListPage.tsx — STUB
ENDPOINT   GET /api/v1/proposals/?stage=&lead_id=&limit=&offset=
PERM       crm.proposals.read
UI         DataTable: name, lead, stage badge, system type, total price, created_at
           Filter by stage + lead
```

---

### 3.4 Proposals — Create Page

```
[FRONTEND] src/features/proposals/pages/ProposalCreatePage.tsx — STUB
ENDPOINT   POST /api/v1/proposals/ (201)
PERM       crm.proposals.create
SCHEMA     Large form with sections:
           - Basic: name, lead selector, version, system type
           - Installation address (address_line, city, state, postal_code)
           - Technical specs: tariff, contracted_demand
           - PV System fields (if system_type=PV or HIBRID)
           - BESS System fields (if system_type=BESS or HIBRID)
           - Financial: total_price, annual_savings, currency, estimated_cost, expected_profit
           - Dates: submitted_at, valid_until
RULE       Lead must be owned and open
           Price fields require price permission
           Initial pipeline transition to DRAFT
```

---

### 3.5 Proposals — Detail Page

```
[FRONTEND] src/features/proposals/pages/ProposalDetailPage.tsx — STUB
ENDPOINT   GET    /api/v1/proposals/{id}                   → ProposalRead
           PATCH  /api/v1/proposals/{id}                   → update
           DELETE /api/v1/proposals/{id}                   → 204
           POST   /api/v1/proposals/{id}/stage             → stage change
           POST   /api/v1/proposals/{id}/won               → mark won
           POST   /api/v1/proposals/{id}/lost              → mark lost
PERM       crm.proposals.read/update/delete/stage.update/mark_won/mark_lost
UI         Sections:
           - Proposal info with completeness indicator
           - PV System details (if applicable)
           - BESS System details (if applicable)
           - Financial summary
           - Stage timeline + stage change buttons
           - Won/Lost actions
           - Commercial PDFs (upload/list/download/delete)
           - Classified documents (upload/list/download/delete)
           - Linked technical visits (from /api/v1/proposals/{id}/technical-visits)
RULE       Stage: only non-terminal transitions via stage endpoint
           Mark won: must be SENT/NEGOTIATION, lead must be open,
                     supersedes siblings, closes lead with WON
           Mark lost: must be SENT/NEGOTIATION, requires loss_reason,
                      closes lead with LOST if no active proposals remain
           Delete: only non-terminal stages
           Update: must be complete if leaving DRAFT
```

---

## P4 — TECHNICAL VISITS

### 4.1 Technical Visits — Types

```
[BACKEND]  schemas.TechnicalVisitCreate, TechnicalVisitUpdate, TechnicalVisitRead,
           TechnicalVisitCancel, TechnicalVisitAssigneeRead, TechnicalVisitAttachmentRead,
           ProposalTechnicalVisitCreate, ProposalTechnicalVisitRead
[FRONTEND] src/features/technical-visits/types/ — EMPTY
SCHEMA     TechnicalVisitRead: { id, lead_id, status, scheduled_at?, receiver_name?,
             receiver_phone?, notes?, created_by, created_at, updated_at,
             completed_at?, cancelled_at?, cancellation_reason?, assignees }
           TechnicalVisitStatus enum: REQUESTED | SCHEDULED | COMPLETED | CANCELLED
           TechnicalVisitAttachmentKind enum: DOCUMENT | PHOTO | OTHER
           TechnicalVisitAssigneeRead: { id, visit_id, name, user_id?, created_at }
PERM       crm.technical_visits.create/read/update/complete/cancel/assign
           crm.technical_visits.attachments.create/read/delete
```

---

### 4.2 Technical Visits — Service + Queries + Mutations

```
[FRONTEND] src/features/technical-visits/services/ — EMPTY
           src/features/technical-visits/queries/ — EMPTY
           src/features/technical-visits/mutations/ — EMPTY
ENDPOINT   GET    /api/v1/technical-visits/?lead_id=&status=&limit=&offset=  list
           GET    /api/v1/technical-visits/{id}                               detail
           PATCH  /api/v1/technical-visits/{id}                               update
           POST   /api/v1/technical-visits/{id}/complete                      complete
           POST   /api/v1/technical-visits/{id}/cancel                        cancel
           POST   /api/v1/technical-visits/{id}/attachments                   upload attach
           GET    /api/v1/technical-visits/{id}/attachments                   list attach
           DELETE /api/v1/technical-visits/{id}/attachments/{att_id}          delete attach
           GET    /api/v1/technical-visits/{id}/attachments/{att_id}/download download
           POST   /api/v1/leads/{lead_id}/technical-visit-requirement         set requirement
           POST   /api/v1/leads/{lead_id}/technical-visits                    create for lead
           GET    /api/v1/leads/{lead_id}/technical-visits                    list for lead
           POST   /api/v1/proposals/{proposal_id}/technical-visits            link to proposal
           DELETE /api/v1/proposals/{proposal_id}/technical-visits/{tv_id}    unlink
PERM       crm.leads.update (for setting requirement)
           crm.proposals.technical_visits.link/read/unlink
```

---

### 4.3 Technical Visits — List Page

```
[FRONTEND] src/features/technical-visits/pages/VisitListPage.tsx — STUB
ENDPOINT   GET /api/v1/technical-visits/?lead_id=&status=
PERM       crm.technical_visits.read
UI         DataTable: lead, status badge, scheduled date, assignees
```

---

### 4.4 Technical Visits — Detail Page

```
[FRONTEND] src/features/technical-visits/pages/VisitDetailPage.tsx — STUB
ENDPOINT   GET    /api/v1/technical-visits/{id}           → TechVisitRead
           PATCH  /api/v1/technical-visits/{id}           → update
           POST   /api/v1/technical-visits/{id}/complete  → complete
           POST   /api/v1/technical-visits/{id}/cancel    → cancel
PERM       crm.technical_visits.update/complete/cancel
UI         Status, schedule info, notes, assignees, attachments
           Complete/Cancel buttons (conditional on status)
RULE       Complete: only SCHEDULED, needs schedule + ≥1 attachment
           Cancel: only if not already COMPLETED/CANCELLED
           Update: only REQUESTED/SCHEDULED
```

---

## P5 — DASHBOARD (Connect to real data)

### 5.1 Dashboard — API integration

```
[BACKEND]  No dedicated dashboard endpoint — use composite queries:
           GET /api/v1/leads/?limit=5              → recent leads
           GET /api/v1/pipeline/transitions?limit=5 → recent activity
           GET /api/v1/contacts/?limit=5            → recent contacts
[FRONTEND] src/features/dashboard/pages/DashboardPage.tsx — hardcoded data
PERM       crm.leads.read | crm.contacts.read | crm.pipeline.read
RULE       Create a DashboardService that aggregates multiple API calls
           Show stats: total leads by stage, recent transitions, recent contacts
```

---

## P6 — ADMIN PANEL

### 6.1 Admin Users Page

```
[FRONTEND] src/features/admin/pages/AdminUsersPage.tsx — STUB
ENDPOINT   GET  /api/v1/permissions/users/{user_id}    → UserPermissionsRead
           POST /api/v1/permissions/users/{user_id}/role → assign role
           PATCH /api/v1/permissions/users/{user_id}     → override permissions
           (User listing via IAM — not in CRM)
PERM       crm.permissions.read | crm.roles.assign | crm.permissions.manage
SCHEMA     UserPermissionsRead: { user_id, role, role_permissions,
                                   grants, denials, effective_permissions }
RULE       Admin cannot modify own permissions
           Managers cannot modify admin users
```

---

### 6.2 Admin Permissions Page

```
[FRONTEND] src/features/admin/pages/AdminPermissionsPage.tsx — STUB
ENDPOINT   GET  /api/v1/permissions/                    → list[PermissionRead]
           PATCH /api/v1/permissions/users/{user_id}     → grant/deny/clear
           POST  /api/v1/permissions/users/{user_id}/role → RoleAssignment
PERM       crm.permissions.read | crm.permissions.manage
SCHEMA     PermissionRead: { key: str, description: str }
           UserPermissionPatch: { grant?: [str], deny?: [str], clear?: [str] }
UI         Permission catalog table + user role manager + override editor
```

---

## P7 — AGENT CHAT

### 7.1 Agent Page

```
[FRONTEND] src/features/agent/pages/AgentPage.tsx — STUB
ENDPOINT   POST /api/v1/agent/chat  { message: str, conversation_id?: str }
           → { response: str, conversation_id: str }
PERM       crm.agent.chat
UI         Chat interface: message input + conversation thread
```

---

## P8 — PAGINATION & DATA SHAPE FIXES

### 8.1 Standardize list responses

```
[BACKEND]  Currently all list endpoints return flat arrays
[FRONTEND] Some features expect PaginatedResponse { items, total, limit, offset }
RULE       Create a frontend wrapper function that converts flat arrays:
           function wrapPaginated<T>(items: T[]): PaginatedResponse<T> {
             return { items, total: items.length, limit: items.length, offset: 0 }
           }
```

---

## P9 — DESIGN SYSTEM UNUSED COMPONENTS

### 9.1 Integrate FilterBar + SearchInput

```
[FRONTEND] FilterBar.tsx — exists, used only in system showcase
           SearchInput.tsx — exists, used only in system showcase
           StatusBadge.tsx — exists, used only in showcase
           Checkbox.tsx — exists, used only in showcase
RULE       Integrate these into Leads/Proposals list pages for filtering
```

---

## Summary — Effort Estimate

| Priority | Feature | Backend | Frontend | Est. effort |
|----------|---------|---------|----------|-------------|
| **P1** | Auth + permissions fix | ✅ done | 🔧 needs fix | 0.5 day |
| **P1** | Contacts pagination fix | ✅ done | 🔧 needs fix | 0.25 day |
| **P2** | Leads CRUD | ✅ done | ❌ empty | 3 days |
| **P3** | Proposals CRUD | ✅ done | ❌ empty | 4 days |
| **P4** | Technical Visits CRUD | ✅ done | ❌ empty | 2 days |
| **P5** | Dashboard real data | ⚠️ composite | 🔧 partial | 1 day |
| **P6** | Admin users/permissions | ✅ done | ❌ stub | 1 day |
| **P7** | Agent chat | ✅ done | ❌ stub | 1 day |
| **P8** | Pagination standardize | ✅ done | 🔧 needs fix | 0.25 day |
| **P9** | Design system integration | n/a | 🔧 low effort | 0.5 day |

**Total MVP: ~13 days**

---

## Implementation Order

1. **P1** (Auth + permissions + pagination) — foundation for everything
2. **P2** (Leads) — core pipeline entity, most complex flow
3. **P3** (Proposals) — leads flow into proposals
4. **P4** (Technical Visits) — supports proposals validation
5. **P5** (Dashboard) — aggregate data from all features
6. **P6** (Admin) — user management
7. **P7** (Agent) — standalone chat
