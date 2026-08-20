# Guide: Agent Tools

## Rule
Agent tools live in `agent/tools/` and invoke domain service functions. Tools never call repositories directly and never duplicate business logic.

Runtime skills live in `agent/skills/` as `SKILL.md` bundles. Skills decide how to reason, when to clarify, and which tools to use; tools perform typed CRM access through domain services.

## Tool Locations
- `agent/tools/contacts.py`
- `agent/tools/leads.py`
- `agent/tools/proposals.py`
- `agent/tools/pipeline.py`
- `agent/tools/factory.py`

## Constraints
- Domain services are the source of truth for business rules.
- Tools must call `service.py`, not `repository.py`.
- New tools must be registered in `agent/graph.py`.
- The agent graph and tools should remain decoupled from provider-specific model code through `LLMProvider`.
- Tools must be scoped to the authenticated user.
- Tools should return structured data, including record identifiers and missing fields.
- Calculations such as margins, prices per kW, and elapsed time should be deterministic Python code, not model arithmetic.
- Read tools are implemented first. Write tools must remain behind explicit confirmation.

## Implemented Read Tools
- `search_contacts`, `get_contact`
- `search_leads`, `get_lead`, `list_leads_for_contact`
- `search_proposals`, `get_proposal`, `list_proposals_for_lead`
- `calculate_proposal_metrics`, `compare_proposals`
- `get_pipeline_summary`, `list_stage_transitions`

## Related Decisions
[[2026-05-25-llmprovider-abstraction]], [[2026-05-25-domain-by-business-not-layer]]

## Related Components
[[agent]], [[agent-runtime-architecture]], [[contacts]], [[leads]], [[proposals]], [[pipeline]]
