---
name: "crm-entity-resolution"
description: "Resolve user phrases to CRM contacts, leads, proposals, and related records before answering."
---

# CRM Entity Resolution

Use this skill whenever a user mentions a customer, company, person, project, lead, proposal, location, informal name, or partial identifier.

1. Search broadly across contacts, leads, and proposals.
2. Prefer exact normalized matches, then strong partial matches, then weaker matches.
3. If one clear match exists, continue with that record and its related records.
4. If multiple plausible matches exist, ask a concise clarification question.
5. If no match exists, say that no CRM record was found and include close matches only if tools returned them.
6. Never infer that two records are the same unless the returned data supports it.
