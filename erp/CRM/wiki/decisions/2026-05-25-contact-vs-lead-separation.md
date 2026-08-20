# ADR: Contact vs Lead Separation

**Date:** 2026-05-25
**Status:** Accepted

## Context
The CRM needs to preserve people and organizations independently from individual sales opportunities. A contact may return months later with another opportunity after a previous lead was lost.

## Alternatives considered
- **Merge Contact and Lead:** Rejected because closing a lost deal would risk destroying or obscuring permanent identity and relationship history.
- **Separate Contact and Lead:** Accepted because it preserves the permanent "who" while allowing many bounded "what to sell" records over time.

## Decision
Contacts and Leads are separate domains. Contact represents the durable person or organization. Lead represents a bounded commercial opportunity linked to a primary Contact.

## Consequences
- Contact history survives closed-lost deals.
- One Contact can generate multiple Leads over time.
- Opportunity-specific fields must stay out of Contact.

## Affected components
[[contacts]], [[leads]], [[proposals]]
