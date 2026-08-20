# Guide: CRM Feature-Permission Matrix

**Scope:** Complete map of every CRM feature, its required permission, and which roles can execute it with their data access scope.

## Legend

| Icon | Meaning |
|------|---------|
| ✅ | Full access (create/read/update/delete within scope) |
| 👁️ | Read-only |
| — | No access |
| 🔒 | Requires separate `price.set` / `price.update` permission |

**Scope levels:**
- `ALL` — admin/manager: every record in the system
- `OWN` — sales: only assigned Leads and derived Contacts, Proposals, Visits
- `TECH` — tech: only assigned Proposals/Visits and derived read-only access to Leads/Contacts

---

## 1. CONTACTS

| # | Feature | Permission | ADMIN | MANAGER | SALES | TECH |
|---|---------|-----------|-------|---------|-------|------|
| 1.1 | Create promoter | `crm.contacts.create` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.2 | List promoters | `crm.contacts.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 1.3 | Read promoter | `crm.contacts.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 1.4 | Update promoter | `crm.contacts.update` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.5 | Delete promoter | `crm.contacts.delete` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.6 | Create contact (individual/company) | `crm.contacts.create` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.7 | List contacts | `crm.contacts.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 1.8 | Read contact | `crm.contacts.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 1.9 | Update contact | `crm.contacts.update` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.10 | Delete contact | `crm.contacts.delete` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.11 | Add company person | `crm.contacts.create` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.12 | List company people | `crm.contacts.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 1.13 | Read company person | `crm.contacts.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 1.14 | Update company person | `crm.contacts.update` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 1.15 | Delete company person | `crm.contacts.delete` | ✅ ALL | ✅ ALL | ✅ OWN | — |

---

## 2. LEADS

| # | Feature | Permission | ADMIN | MANAGER | SALES | TECH |
|---|---------|-----------|-------|---------|-------|------|
| 2.1 | Create lead | `crm.leads.create` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.2 | List leads | `crm.leads.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.3 | Read lead | `crm.leads.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.4 | Update lead (open only) | `crm.leads.update` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.5 | Move stage (non-terminal) | `crm.leads.stage.update` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.6 | Close lead (LOST only) | `crm.leads.close` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.7 | Delete lead (open only) | `crm.leads.delete` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.8 | Read assignment | `crm.leads.assign` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.9 | Assign/transfer lead | `crm.leads.assign` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.10 | Unassign lead | `crm.leads.assign` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.11 | Upload document | `crm.leads.documents.create` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.12 | List documents | `crm.leads.documents.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.13 | Read document metadata | `crm.leads.documents.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.14 | Download document | `crm.leads.documents.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.15 | Delete document | `crm.leads.documents.delete` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.16 | Upload electricity bill | `crm.leads.electricity_bills.create` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.17 | List electricity bills | `crm.leads.electricity_bills.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.18 | Read bill metadata | `crm.leads.electricity_bills.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.19 | Download bill | `crm.leads.electricity_bills.read` | ✅ ALL | ✅ ALL | ✅ OWN | 👁️ TECH |
| 2.20 | Delete electricity bill | `crm.leads.electricity_bills.delete` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.21 | Create interaction | `crm.leads.interactions.create` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.22 | List interactions | `crm.leads.interactions.read` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.23 | Read interaction | `crm.leads.interactions.read` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.24 | Update interaction | `crm.leads.interactions.update` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.25 | Delete interaction | `crm.leads.interactions.delete` | ✅ ALL | ✅ ALL | ✅ OWN | — |
| 2.26 | Set visit requirement | `crm.leads.update` | ✅ ALL | ✅ ALL | ✅ OWN | — |

---

## 3. PROPOSALS

| # | Feature | Permission | ADMIN | MANAGER | SALES | TECH |
|---|---------|-----------|-------|---------|-------|------|
| 3.1 | Create proposal | `crm.proposals.create` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.2 | List proposals | `crm.proposals.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.3 | Read proposal | `crm.proposals.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.4 | Update proposal (non-terminal) | `crm.proposals.update` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.5 | Move stage (DRAFT→SENT→NEGOTIATION) | `crm.proposals.stage.update` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.6 | Mark as won | `crm.proposals.mark_won` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.7 | Mark as lost | `crm.proposals.mark_lost` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.8 | Delete proposal (non-terminal) | `crm.proposals.delete` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.9 | Set empty price fields | `crm.proposals.price.set` 🔒 | ✅ ALL | ✅ ALL | — | — |
| 3.10 | Update established price fields | `crm.proposals.price.update` 🔒 | ✅ ALL | ✅ ALL | — | — |
| 3.11 | Assign tech user to proposal | `crm.proposals.assign_tech` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.12 | List proposal assignments | `crm.proposals.assign_tech` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.13 | Remove tech assignment | `crm.proposals.assign_tech` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.14 | Upload commercial PDF | `crm.proposals.commercial_documents.create` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.15 | List commercial PDFs | `crm.proposals.commercial_documents.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.16 | Read commercial PDF metadata | `crm.proposals.commercial_documents.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.17 | Download commercial PDF | `crm.proposals.commercial_documents.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.18 | Delete commercial PDF | `crm.proposals.commercial_documents.delete` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.19 | Upload classified document | `crm.proposals.documents.create` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.20 | List classified documents | `crm.proposals.documents.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.21 | Read classified document metadata | `crm.proposals.documents.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.22 | Download classified document | `crm.proposals.documents.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.23 | Delete classified document | `crm.proposals.documents.delete` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.24 | Link proposal to technical visit | `crm.proposals.technical_visits.link` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 3.25 | List proposal-visit links | `crm.proposals.technical_visits.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 3.26 | Unlink proposal-visit | `crm.proposals.technical_visits.unlink` | ✅ ALL | ✅ ALL | — | ✅ TECH |

---

## 4. TECHNICAL VISITS

| # | Feature | Permission | ADMIN | MANAGER | SALES | TECH |
|---|---------|-----------|-------|---------|-------|------|
| 4.1 | Create visit for lead | `crm.technical_visits.create` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 4.2 | List visits (by lead or global) | `crm.technical_visits.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 4.3 | Read visit | `crm.technical_visits.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 4.4 | Update visit (schedule/assignees) | `crm.technical_visits.update` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 4.5 | Assign visit users | `crm.technical_visits.assign` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 4.6 | Complete visit | `crm.technical_visits.complete` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 4.7 | Cancel visit | `crm.technical_visits.cancel` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 4.8 | Upload attachment | `crm.technical_visits.attachments.create` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 4.9 | List attachments | `crm.technical_visits.attachments.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 4.10 | Read attachment metadata | `crm.technical_visits.attachments.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 4.11 | Download attachment | `crm.technical_visits.attachments.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 4.12 | Delete attachment | `crm.technical_visits.attachments.delete` | ✅ ALL | ✅ ALL | — | ✅ TECH |

---

## 5. PIPELINE

| # | Feature | Permission | ADMIN | MANAGER | SALES | TECH |
|---|---------|-----------|-------|---------|-------|------|
| 5.1 | List transition history | `crm.pipeline.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |
| 5.2 | Read pipeline summary | `crm.pipeline.read` | ✅ ALL | ✅ ALL | 👁️ OWN | 👁️ TECH |

---

## 6. PERMISSIONS & ADMINISTRATION

| # | Feature | Permission | ADMIN | MANAGER | SALES | TECH |
|---|---------|-----------|-------|---------|-------|------|
| 6.1 | Read permission catalog | `crm.permissions.read` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 6.2 | Read user permissions | `crm.permissions.read` | ✅ ALL | ✅ ALL | — | ✅ TECH |
| 6.3 | Grant/deny/clear overrides | `crm.permissions.manage` | ✅ ALL | ✅ (limited) | — | — |
| 6.4 | Assign role template | `crm.roles.assign` | ✅ ALL | ✅ (limited) | — | — |

**Manager guardrails:**
- Cannot create IAM users
- Cannot modify ADMIN accounts
- Cannot modify own permissions or role
- Cannot grant a permission they don't effectively have

---

## 7. AI AGENT

| # | Feature | Permission | ADMIN | MANAGER | SALES | TECH |
|---|---------|-----------|-------|---------|-------|------|
| 7.1 | Chat with agent | `crm.agent.chat` | ✅ ALL | ✅ ALL | ✅ OWN | ✅ TECH |

Agent scoping:
- Sales: answers within assigned Leads (no price changes)
- Tech: answers within assigned Proposals/Visits (no interactions, no prices)
- Admin/Manager: answers with global scope
- Agent is read-only: no mutations exposed

---

## 8. SUMMARY BY ROLE

### ADMIN
- **All permissions, all records** (global scope)
- Can bootstrap CRM (first user must be ADMIN)
- Can assign any role including ADMIN
- No guardrails apply

### MANAGER
- **All permissions, all records** (global scope)
- Cannot create IAM users (IAM-only ability)
- Cannot modify ADMIN users
- Cannot modify own permissions/role
- Cannot grant permissions they don't have
- Can manage SALES/TECH user permissions

### SALES
- **Full CRUD** on Contacts and Leads (own scope)
- **Read-only** on Proposals, Commercial PDFs, Technical Visits (from assigned Leads)
- **No price permissions** (cannot set/change `total_price`, `price_watt`, `price_kwh`)
- **No proposal mutation** (cannot create/update/delete proposals)
- **No technical visit mutation** (cannot create/update/complete/cancel visits)
- **Can read** pipeline history for own entities
- **Can use** the AI agent (read-only, own scope)
- **Scope:** Active Lead assignments only. Transfer removes access.

### TECH
- **Full CRUD** on Proposals (assigned scope) EXCEPT price fields
- **Full CRUD** on Technical Visits (assigned scope)
- **Read-only** on Contacts, Leads (derived from assignments)
- **Read-only** on Lead documents and electricity bills (derived)
- **Cannot see** Lead interactions at all
- **Cannot create/update/delete** Contacts or Leads
- **Cannot update** lead stages, close, or delete leads
- **Cannot upload/delete** Lead documents or bills
- **No price permissions** (cannot set/change `total_price`, `price_watt`, `price_kwh`)
- **Can manage** Proposal assignments (self and others)
- **Can use** the AI agent (read-only, tech scope)
- **Scope:** Assigned Proposals and TechnicalVisits only

---

## 9. FEATURE COUNT BY ROLE

| Domain | Features | ADMIN | MANAGER | SALES | TECH |
|--------|----------|-------|---------|-------|------|
| Contacts | 15 | 15 ✅ | 15 ✅ | 15 ✅ | 6 👁️ |
| Leads | 26 | 26 ✅ | 26 ✅ | 26 ✅ | 6 👁️ |
| Proposals | 26 | 26 ✅ | 26 ✅ | 8 👁️ | 26 ✅ (no 🔒) |
| Tech Visits | 12 | 12 ✅ | 12 ✅ | 3 👁️ | 12 ✅ |
| Pipeline | 2 | 2 ✅ | 2 ✅ | 2 👁️ | 2 👁️ |
| Permissions | 4 | 4 ✅ | 4 ✅ | 0 | 1 👁️ |
| AI Agent | 1 | 1 ✅ | 1 ✅ | 1 ✅ | 1 ✅ |
| **Total** | **86** | **86 ✅** | **86 ✅** (limited) | **55 ✅ + 14 👁️** | **40 ✅ + 15 👁️** |

**Breakdown:**
- ADMIN: 86 features (full access, all scopes)
- MANAGER: 86 features (full access, all scopes, with guardrails)
- SALES: 55 writable features + 14 read-only features = 69 accessible features
- TECH: 40 writable features (no price) + 15 read-only features = 55 accessible features (no interactions)

---

## Related pages
[[permissions]], [[crm-permissions]], [[leads]], [[contacts]], [[proposals]], [[technical-visits]], [[pipeline]], [[agent]]
