# Domain: Contacts

**Path:** `src/domains/contacts/`
**Responsibility:** Owns people and organizations, the permanent "who"; it does not own opportunity or technical proposal fields.
**Status:** In development; promoter/company-person/profile redesign implemented

## Purpose
Contacts form the durable directory of people and organizations with whom the company has or has had a relationship. A contact can generate multiple leads over time.

## Data model
`Contact` remains the durable row linked by leads. The implemented `Contact` SQLModel table is named `contact`.
- Common fields: `id`, `type`, `name`, `promoter_id`, `owner_id`, `created_at`, `updated_at`
- Address fields: `address_line`, `city`, `state`, `postal_code`
- Individual-only fields moved to `IndividualContactProfile` (`individual_contact_profile`): `phone`, optional `email`
- Company-only fields moved to `CompanyContactProfile` (`company_contact_profile`): optional `industry`
- Company contacts also have one or more related `CompanyContactPerson` rows
- Removed from contact shape: `tax_id`, `country`, `first_name`, `last_name`, `parent_contact_id`, `role`, `source`, `website`

`Promoter` is a contacts-domain SQLModel catalog table named `promoter`.
- Business fields: `name`, `phone`
- Technical fields: `id`, `owner_id`, `created_at`, `updated_at`
- Relationship: one promoter can be linked to many contacts; every contact must reference an owned promoter

`CompanyContactPerson` is a contacts-domain SQLModel table named `company_contact_person` for individual people inside a company.
- Business fields: `name`, `phone`, optional `email`, `position`
- Technical fields: `id`, `company_contact_id`, `created_at`, `updated_at`
- Relationship: `company_contact_id` must reference an owned `Contact` with `type=COMPANY`

Fields that do not belong in Contact include `monthly_consumption_kwh`, `roof_orientation`, `budget`, and `has_battery`; those describe opportunities or technical variants.

## Public interface (service.py)
- `create_contact(session, contact_create, owner_id) -> Contact` — creates an owned person or company contact
- `get_contact(session, contact_id, owner_id) -> Contact` — loads an owned contact or raises `NotFoundError` / `AuthorizationError`
- `list_contacts(session, owner_id, contact_type=None, limit=100, offset=0) -> list[Contact]` — lists contacts scoped to one owner
- `update_contact(session, contact_id, contact_update, owner_id) -> Contact` — partially updates an owned contact and refreshes `updated_at`
- `delete_contact(session, contact_id, owner_id) -> None` — deletes an owned contact
- `create_promoter(session, promoter_create, owner_id) -> Promoter` — creates an owned promoter catalog entry
- `list_promoters(session, owner_id, limit=100, offset=0) -> list[Promoter]` — lists owned promoters
- `get_promoter(session, promoter_id, owner_id) -> Promoter` — loads an owned promoter
- `update_promoter(session, promoter_id, promoter_update, owner_id) -> Promoter` — updates promoter name or phone
- `delete_promoter(session, promoter_id, owner_id) -> None` — deletes an unused promoter or rejects deletion when linked
- `add_company_person(session, company_contact_id, person_create, owner_id) -> CompanyContactPerson` — adds a person to an owned company contact
- `list_company_people(session, company_contact_id, owner_id) -> list[CompanyContactPerson]` — lists company people for an owned company contact
- `update_company_person(session, company_contact_id, person_id, person_update, owner_id) -> CompanyContactPerson` — updates one company person
- `delete_company_person(session, company_contact_id, person_id, owner_id) -> None` — deletes one company person without violating the one-person minimum

## Router endpoints
The contacts router is mounted under `/api/v1/contacts`.

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/contacts/` | Create a contact owned by the authenticated user |
| GET | `/api/v1/contacts/` | List contacts owned by the authenticated user |
| GET | `/api/v1/contacts/{contact_id}` | Return one owned contact |
| PATCH | `/api/v1/contacts/{contact_id}` | Partially update one owned contact |
| DELETE | `/api/v1/contacts/{contact_id}` | Delete one owned contact |
| POST | `/api/v1/contacts/promoters` | Create a promoter catalog entry |
| GET | `/api/v1/contacts/promoters` | List promoter catalog entries |
| GET | `/api/v1/contacts/promoters/{promoter_id}` | Return one promoter |
| PATCH | `/api/v1/contacts/promoters/{promoter_id}` | Update one promoter |
| DELETE | `/api/v1/contacts/promoters/{promoter_id}` | Delete one unused promoter |
| POST | `/api/v1/contacts/{company_id}/people` | Add a person inside a company |
| GET | `/api/v1/contacts/{company_id}/people` | List people inside a company |
| GET | `/api/v1/contacts/{company_id}/people/{person_id}` | Return one company person |
| PATCH | `/api/v1/contacts/{company_id}/people/{person_id}` | Update one company person |
| DELETE | `/api/v1/contacts/{company_id}/people/{person_id}` | Delete one company person |

## Request / Response schemas (schemas.py)
- `PromoterCreate`, `PromoterUpdate`, `PromoterRead` — promoter catalog DTOs with `name` and `phone`
- `CompanyContactPersonCreate`, `CompanyContactPersonUpdate`, `CompanyContactPersonRead` — company-person DTOs with `name`, `phone`, optional `email`, and `position`
- `ContactCreate` — request body for creating a person or company contact; requires `promoter_id`; company creation includes at least one `company_people` item; `owner_id` is assigned from the authenticated user
- `ContactUpdate` — partial update body; omitted fields are left unchanged and explicit `null` clears nullable fields; allows changing `promoter_id`
- `ContactRead` — public contact response including `promoter_id`, ownership, and timestamps

## Dependencies
- **Internal:** [[users]]
- **Core:** [[core]], [[api-v1]]

## Business rules / invariants
- Contact answers "who they are."
- Contact lifetime is permanent relative to bounded lead lifecycles.
- One Contact can have zero or many Leads.
- Company people are represented by `CompanyContactPerson`, not by `Contact.parent_contact_id`.
- `owner_id` is never accepted from the request body; it currently comes from `current_user`.
- Contact reads, updates, deletes, and lists are currently scoped to the authenticated owner.
- Authorization: `sales` contact access is derived from active Lead assignment when the Contact has Leads. If a Contact has no Leads, the Contact creator can still access it.
- Authorization: `tech` contact access is read-only and derived from assigned Proposals or TechnicalVisits.
- A `promoter_id` must reference an owned promoter.
- A promoter can be linked to many contacts.
- A company contact must have at least one company person.
- Company person deletion must not leave a company with zero people.
- Company fields are invalid for individual contacts.
- Company contacts cannot carry direct email, phone, tax ID, country, or website data.
- Individual client contacts cannot carry tax ID, country, first name, last name, parent contact, or role data.
- `contact` stores only common identity/address/ownership fields; subtype-specific fields live in one-to-one profile tables.

## Related decisions
[[2026-05-25-contact-vs-lead-separation]], [[2026-05-25-domain-by-business-not-layer]], [[2026-05-25-sqlmodel-vs-pydantic-strategy]], [[2026-05-28-contact-promoters-and-company-people]], [[2026-06-01-verp-identity-crm-permissions]]

## Known technical debt
None documented.

## Maintainer notes
Keep identity and relationship information here. Put deal-specific information in [[leads]] or [[proposals]].
The implementation lives under `CRM/src/domains/contacts/`, is mounted in `CRM/src/api/v1/router.py`, and is covered by unit tests in `CRM/tests/unit/domains/contacts/` plus integration tests in `CRM/tests/integration/api/`.
The promoter/company-person redesign from [[2026-05-28-contact-promoters-and-company-people]] is implemented in code; the later profile normalization keeps the API response flat while storing individual and company-only fields in separate one-to-one tables.
Promoter routes are declared before parameterized paths such as `/{contact_id}` so FastAPI does not route the literal segment `promoters` through the contact ID handler.
The project now includes an initial Alembic schema migration. Development SQLite databases created before that baseline should be recreated from Alembic or explicitly stamped only after confirming their schema matches the baseline.
