# ADR: Contact Promoters and Company People

**Date:** 2026-05-28
**Status:** Accepted

## Context
The current contacts implementation stores acquisition origin as a free-text `source` field and uses `parent_contact_id` plus `role` to represent a person inside a company. The next contacts redesign needs stricter CRM semantics:

- `source` becomes an owned `Promoter` catalog entry that can be linked to contacts.
- A company contact should not carry direct email, phone, tax ID, country, or website fields.
- Every company needs one or more individual people inside that company, each with only name, phone, optional email, and position.
- An individual contact represents the client directly, so it no longer needs tax ID, country, first name, last name, parent company, or role fields.

## Alternatives considered
- **Keep `source` as text:** Rejected because promoters need their own name and phone and should be reused across contacts.
- **Keep company people as `Contact(type=INDIVIDUAL)` rows linked by `parent_contact_id`:** Rejected because those people are company representatives, not direct client contacts, and their field shape is different from direct individual clients.
- **Add `Promoter` and `CompanyContactPerson` entities inside the contacts domain:** Proposed because it keeps the contacts domain as the owner of relationship identity while separating direct clients, company records, company representatives, and promoter catalog data.

## Decision
The contacts domain should keep `ContactType` with `INDIVIDUAL` and `COMPANY`, but split supporting concepts into dedicated entities:

- `Promoter` is an owner-scoped catalog entity with business fields `name` and `phone`.
- `Contact.source` is replaced by `Contact.promoter_id`, which must reference an owned `Promoter`.
- `CompanyContactPerson` stores the required people inside a company with `company_contact_id`, `name`, `phone`, optional `email`, and `position`.
- Company contacts no longer accept `email`, `phone`, `tax_id`, `country`, or `website`.
- Individual contacts no longer accept `tax_id`, `country`, `first_name`, `last_name`, `parent_contact_id`, or `role`; `email` remains optional.
- A company must have at least one `CompanyContactPerson`. Creating a company should be transactional with its first one or more people, and deleting company people must not leave the company with zero people.

`Contact` remains the durable entity linked by leads. `CompanyContactPerson` rows are representatives for a company and are not lead-owning contacts unless promoted later by an explicit future workflow.

## Consequences
- API payloads that send `source` must migrate to `promoter_id`.
- Existing B2B payloads using `parent_contact_id` and `role` must migrate to company people endpoints or nested company creation payloads.
- Existing company payloads with direct email, phone, tax ID, country, or website should be rejected after implementation.
- Existing individual payloads with tax ID, country, first name, last name, parent contact, or role should be rejected after implementation.
- Migration from old `source` values is not lossless because `Promoter.phone` is now required; seed or cleanup data must provide phone values.
- Agent contact tools and REST body examples must be updated after the implementation so they expose promoter and company-person data consistently.

## Affected components
[[contacts]], [[leads]], [[agent]], [[api-v1]]
