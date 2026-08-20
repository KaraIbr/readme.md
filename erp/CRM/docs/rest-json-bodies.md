# REST JSON Bodies

Base URL:

```text
http://127.0.0.1:8000/api/v1
```

CRM endpoints require an IAM access token:

```text
Authorization: Bearer <access_token>
```

User creation, login, token refresh, IAM permissions, and service access grants are IAM service endpoints, not CRM endpoints.

## Contacts

### POST `/contacts/promoters`

```json
{
  "name": "Referral Partner",
  "phone": "+52 81 5555 0000"
}
```

### PATCH `/contacts/promoters/{promoter_id}`

Partial body. Send only fields you want to change:

```json
{
  "phone": "+52 81 5555 9999"
}
```

### GET `/contacts/promoters`, GET `/contacts/promoters/{promoter_id}`, DELETE `/contacts/promoters/{promoter_id}`

No body.

### POST `/contacts/` - company

```json
{
  "type": "COMPANY",
  "name": "Acme Manufacturing",
  "promoter_id": 1,
  "address_line": "Av Solar 123",
  "city": "Monterrey",
  "state": "Nuevo Leon",
  "postal_code": "64000",
  "industry": "Manufacturing",
  "company_people": [
    {
      "name": "Jane Manager",
      "phone": "+52 81 5555 0101",
      "email": "jane.manager@acme.example",
      "position": "Facility Manager"
    }
  ]
}
```

Company contacts do not accept direct `email`, `phone`, `tax_id`, `country`, or `website` fields. They must include at least one company person on creation.

### POST `/contacts/` - individual

```json
{
  "type": "INDIVIDUAL",
  "name": "Carlos Rivera",
  "promoter_id": 1,
  "email": "carlos.rivera@example.com",
  "phone": "+52 55 5555 0202",
  "address_line": "Calle Energia 45",
  "city": "Ciudad de Mexico",
  "state": "CDMX",
  "postal_code": "01000"
}
```

Individual contacts do not accept `tax_id`, `country`, `first_name`, `last_name`, `parent_contact_id`, or `role`. `email` is optional.

### POST `/contacts/{company_id}/people`

```json
{
  "name": "John CFO",
  "phone": "+52 81 5555 0202",
  "email": "john.cfo@acme.example",
  "position": "CFO"
}
```

### PATCH `/contacts/{company_id}/people/{person_id}`

Partial body. Send only fields you want to change:

```json
{
  "position": "Finance Director"
}
```

### GET `/contacts/{company_id}/people`, GET `/contacts/{company_id}/people/{person_id}`, DELETE `/contacts/{company_id}/people/{person_id}`

No body. Deleting the last person from a company is rejected.

### PATCH `/contacts/{contact_id}`

Partial body. Send only fields you want to change:

```json
{
  "phone": "+52 81 5555 9999",
  "promoter_id": 2
}
```

### GET `/contacts/`, GET `/contacts/{contact_id}`, DELETE `/contacts/{contact_id}`

No body.

## Leads

### POST `/leads/`

```json
{
  "contact_id": 1,
  "title": "Solar 8.5 kW - Acme Manufacturing",
  "interest_type": "Photovoltaic",
  "qualification_score": 72,
  "notes": "Customer wants a rooftop PV proposal."
}
```

Allowed `interest_type` values are `Photovoltaic`, `BESS`, and `Hibrid`.
New leads start with `technical_visit_requirement` set to `UNDETERMINED`.

### PATCH `/leads/{lead_id}`

Partial body:

```json
{
  "interest_type": "BESS",
  "qualification_score": 80,
  "notes": "Customer now wants storage-only review."
}
```

### POST `/leads/{lead_id}/stage`

Allowed open stages: `NEW`, `QUALIFYING`, `PROPOSAL_PHASE`.

```json
{
  "stage": "PROPOSAL_PHASE"
}
```

### POST `/leads/{lead_id}/close`

Manual close supports `LOST`. A `WON` lead must come from a won proposal.

```json
{
  "outcome": "LOST",
  "notes": "Customer postponed the project."
}
```

### GET `/leads/`, GET `/leads/{lead_id}`, DELETE `/leads/{lead_id}`

No body.

### POST `/leads/{lead_id}/technical-visit-requirement`

```json
{
  "requirement": "REQUIRED"
}
```

Allowed values are `UNDETERMINED`, `NOT_REQUIRED`, and `REQUIRED`. Creating a technical visit for an `UNDETERMINED` lead automatically changes this value to `REQUIRED`; creating one for a `NOT_REQUIRED` lead is rejected.

### POST `/leads/{lead_id}/documents`

This endpoint uses multipart form data, not JSON.

```text
title=Project requirements
file=@requirements.pdf
```

### POST `/leads/{lead_id}/electricity-bills`

Electricity bills use their own multipart endpoint because they are processed separately from general project documents.

```text
title=March CFE receipt
file=@cfe-march.pdf
```

### POST `/leads/{lead_id}/interactions`

```json
{
  "interaction_type": "NEGOTIATION",
  "title": "Initial negotiation",
  "notes": "Customer asked for phased delivery and O&M.",
  "interaction_date": "2026-06-15T16:30:00"
}
```

`interaction_date` is required and can be in the past, present, or future for planned interactions.
Allowed `interaction_type` values are `CALL`, `EMAIL`, `MEETING`, `MESSAGE`, `NEGOTIATION`, and `NOTE`.

### PATCH `/leads/{lead_id}/interactions/{interaction_id}`

Partial body:

```json
{
  "notes": "Customer asked for phased delivery, O&M, and a battery alternate.",
  "interaction_date": "2026-06-18T18:00:00"
}
```

### GET/DELETE lead documents, electricity bills, and interactions

No body. Metadata routes:
- `/leads/{lead_id}/documents`
- `/leads/{lead_id}/documents/{document_id}`
- `/leads/{lead_id}/electricity-bills`
- `/leads/{lead_id}/electricity-bills/{bill_id}`
- `/leads/{lead_id}/interactions`
- `/leads/{lead_id}/interactions/{interaction_id}`

Download routes:
- `/leads/{lead_id}/documents/{document_id}/download`
- `/leads/{lead_id}/electricity-bills/{bill_id}/download`

## Technical Visits

### POST `/leads/{lead_id}/technical-visits`

A visit can be created as a requested visit with no schedule:

```json
{
  "notes": "Customer asked us to coordinate a technical visit."
}
```

Or directly as a scheduled visit:

```json
{
  "scheduled_at": "2026-06-20T16:30:00",
  "receiver_name": "Jane Manager",
  "receiver_phone": "+52 81 5555 0101",
  "notes": "Access through loading dock.",
  "assignees": [
    {
      "name": "Engineer One"
    },
    {
      "name": "Engineer Two",
      "user_id": 2
    }
  ]
}
```

Scheduling requires `scheduled_at`, `receiver_name`, `receiver_phone`, and at least one assignee together.

### PATCH `/technical-visits/{visit_id}`

Partial body. Use it to schedule a requested visit or reschedule an existing scheduled visit:

```json
{
  "scheduled_at": "2026-06-21T10:00:00",
  "receiver_name": "Jane Manager",
  "receiver_phone": "+52 81 5555 0101",
  "notes": "Bring PPE and ask security for roof access.",
  "assignees": [
    {
      "name": "Engineer One"
    }
  ]
}
```

### POST `/technical-visits/{visit_id}/complete`

No body. Completion only marks the visit as performed; at least one attachment must already exist.

### POST `/technical-visits/{visit_id}/cancel`

```json
{
  "reason": "Customer rescheduled the project."
}
```

### POST `/technical-visits/{visit_id}/attachments`

This endpoint uses multipart form data, not JSON.

```text
title=Inspection report
file_kind=DOCUMENT
file=@inspection-report.pdf
```

Allowed `file_kind` values are `DOCUMENT`, `PHOTO`, and `OTHER`.

### GET/DELETE technical visits and attachments

No body. Metadata routes:
- `/leads/{lead_id}/technical-visits`
- `/technical-visits`
- `/technical-visits/{visit_id}`
- `/technical-visits/{visit_id}/attachments`
- `/technical-visits/{visit_id}/attachments/{attachment_id}`

Download route:
- `/technical-visits/{visit_id}/attachments/{attachment_id}/download`

## Proposals

### POST `/proposals/`

Only `lead_id` and `name` are required at creation time. A draft can start as:

```json
{
  "lead_id": 1,
  "name": "Acme rooftop PV option"
}
```

Complete PV example:

```json
{
  "lead_id": 1,
  "name": "Acme rooftop PV option",
  "version": "1.0",
  "installation_address": {
    "address_line": "Av Solar 123",
    "city": "Monterrey",
    "state": "Nuevo Leon",
    "postal_code": "64000"
  },
  "tariff": "GDMTH",
  "contracted_demand": 120,
  "system_type": "PV",
  "total_price": "250000.00",
  "annual_savings": "78000.00",
  "currency": "MXN",
  "estimated_cost": "180000.00",
  "expected_profit": "70000.00",
  "submitted_at": "2026-06-01T12:00:00",
  "valid_until": "2026-06-30",
  "pv_system": {
    "panel_count": 16,
    "panel_model": "Jinko 550",
    "panel_power": 550,
    "inverter_model": "INV-8K",
    "inverter_count": 1,
    "inverter_power": 8,
    "type_of_surface": "roof",
    "total_power_ac": 8,
    "system_size_kw": 8.5,
    "oversizing_kw": 0.5,
    "estimated_annual_kwh": 12800,
    "estimated_savings_kw": 7.2,
    "connection_mode": "interconnected",
    "cost_watt": "21.1765",
    "price_watt": "29.4118"
  }
}
```

Complete BESS example:

```json
{
  "lead_id": 1,
  "name": "Acme backup BESS option",
  "version": "1.0",
  "installation_address": {
    "address_line": "Av Solar 123",
    "city": "Monterrey",
    "state": "Nuevo Leon",
    "postal_code": "64000"
  },
  "tariff": "GDMTH",
  "contracted_demand": 120,
  "system_type": "BESS",
  "total_price": "330000.00",
  "annual_savings": "64000.00",
  "currency": "MXN",
  "estimated_cost": "250000.00",
  "expected_profit": "80000.00",
  "submitted_at": "2026-06-01T12:00:00",
  "valid_until": "2026-06-30",
  "bess_system": {
    "battery_model": "PowerWall Commercial",
    "battery_count": 2,
    "battery_power_kw": 10,
    "battery_storage_kwh": 27,
    "bess_primary_use": "backup",
    "technical_notes": "Backup for critical loads.",
    "cost_kwh": "9259.2593",
    "price_kwh": "12222.2222"
  }
}
```

For `HIBRID`, include both `pv_system` and `bess_system`, including all four unit economics fields: `cost_watt`, `price_watt`, `cost_kwh`, and `price_kwh`. A proposal cannot move beyond `DRAFT` until `is_complete` is `true`; the API response includes `missing_required_fields` to show what remains.

### PATCH `/proposals/{proposal_id}`

Partial body:

```json
{
  "total_price": "245000.00",
  "valid_until": "2026-07-15",
  "installation_address": {
    "city": "San Pedro Garza Garcia"
  },
  "pv_system": {
    "inverter_model": "INV-8K-V2",
    "price_watt": "28.8235"
  }
}
```

### POST `/proposals/{proposal_id}/stage`

Allowed non-terminal stages: `DRAFT`, `SENT`, `NEGOTIATION`.

```json
{
  "stage": "SENT"
}
```

### POST `/proposals/{proposal_id}/won`

No body.

### POST `/proposals/{proposal_id}/lost`

```json
{
  "loss_reason": "Customer selected another provider."
}
```

### GET `/proposals/`, GET `/proposals/{proposal_id}`, DELETE `/proposals/{proposal_id}`

No body.

### Proposal document uploads

Commercial customer PDF:

```http
POST /proposals/{proposal_id}/commercial-pdf
Content-Type: multipart/form-data

title=Commercial proposal v1.0
file=@proposal.pdf
```

Cost, technical, or other internal documents:

```http
POST /proposals/{proposal_id}/documents
Content-Type: multipart/form-data

title=Cost breakdown
classification=Costs
file=@costs.xlsx
```

Metadata and download routes have no JSON body:
- `/proposals/{proposal_id}/commercial-pdf`
- `/proposals/{proposal_id}/commercial-pdf/{document_id}`
- `/proposals/{proposal_id}/commercial-pdf/{document_id}/download`
- `/proposals/{proposal_id}/documents`
- `/proposals/{proposal_id}/documents/{document_id}`
- `/proposals/{proposal_id}/documents/{document_id}/download`

### POST `/proposals/{proposal_id}/technical-visits`

Links a proposal version to technical visit evidence from the same lead:

```json
{
  "technical_visit_id": 1,
  "relationship_type": "BASED_ON",
  "notes": "Proposal version uses field measurements from the visit."
}
```

Allowed `relationship_type` values are `BASED_ON` and `VALIDATED_BY`.

### GET `/proposals/{proposal_id}/technical-visits`, DELETE `/proposals/{proposal_id}/technical-visits/{technical_visit_id}`

No body.

## Permissions

### GET `/permissions`

No body.

### GET `/permissions/users/{user_id}`

No body.

### PATCH `/permissions/users/{user_id}`

All arrays are optional. `grant` adds explicit grants, `deny` adds explicit denials, and `clear` removes existing overrides for those permission keys.

```json
{
  "grant": ["crm.proposals.documents.create"],
  "deny": ["crm.proposals.price.update"],
  "clear": ["crm.leads.delete"]
}
```

### POST `/permissions/users/{user_id}/role`

```json
{
  "role": "tech"
}
```

`role` can be `admin`, `manager`, `sales`, or `tech`.
When no CRM access rows exist yet, the authenticated first user can bootstrap CRM access by assigning `admin` to itself.

### POST `/leads/{lead_id}/assignment`

Assign or transfer sales follow-up for one Lead.

```json
{
  "user_id": 2
}
```

### POST `/proposals/{proposal_id}/assignments`

Assign technical Proposal work to a `tech` user.

```json
{
  "user_id": 4
}
```

## Pipeline

### GET `/pipeline/transitions`

No body.

Optional query params:

```text
entity_type=lead
entity_id=1
limit=100
offset=0
```

`entity_type` can be `lead` or `proposal`.

Example response:

```json
[
  {
    "id": 2,
    "entity_type": "lead",
    "entity_id": 1,
    "from_stage": "NEW",
    "to_stage": "QUALIFYING",
    "transitioned_by": 1,
    "transitioned_at": "2026-05-29T16:42:15.123456Z",
    "reason": null,
    "notes": null
  },
  {
    "id": 1,
    "entity_type": "lead",
    "entity_id": 1,
    "from_stage": null,
    "to_stage": "NEW",
    "transitioned_by": 1,
    "transitioned_at": "2026-05-29T16:40:02.654321Z",
    "reason": "created",
    "notes": null
  }
]
```

### GET `/pipeline/summary/{entity_type}/{entity_id}`

No body.

Example:

```text
/pipeline/summary/lead/1
```

Example response:

```json
{
  "entity_type": "lead",
  "entity_id": 1,
  "current_stage": "QUALIFYING",
  "transition_count": 2,
  "last_transition_at": "2026-05-29T16:42:15.123456Z"
}
```

## Agent

### POST `/agent/chat`

Requires Azure OpenAI settings in `.env` or `CRM/.env`.

```json
{
  "message": "Que propuestas tengo abiertas para Acme?",
  "history": []
}
```

With history:

```json
{
  "message": "Y cual tiene mejor precio por kW?",
  "history": [
    {
      "role": "user",
      "content": "Que propuestas tengo abiertas para Acme?"
    },
    {
      "role": "assistant",
      "content": "Encontre una propuesta abierta para Acme."
    }
  ]
}
```
