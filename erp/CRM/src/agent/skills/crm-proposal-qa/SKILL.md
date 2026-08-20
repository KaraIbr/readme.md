---
name: "crm-proposal-qa"
description: "Answer questions about proposal technical and commercial fields such as inverter, panels, capacity, batteries, system type, and price."
---

# CRM Proposal Q&A

Use this skill for questions about proposal content, technical equipment, commercial offer values, proposal status, or proposal comparisons.

1. Retrieve the relevant proposal and, when needed, its lead and contact context.
2. Use common proposal fields and nested technical details: `system_type`, `total_price`, `estimated_cost`, `expected_profit`, `valid_until`, `current_stage`, `pv_system.*`, and `bess_system.*`.
3. If a requested technical field is missing, state that the proposal does not currently contain that value; use `missing_fields` when present.
4. If multiple proposals belong to the same lead, prefer the one that best matches the user's wording. If still ambiguous, ask which proposal to use.
5. Include record IDs or names when they help the user verify the answer.
