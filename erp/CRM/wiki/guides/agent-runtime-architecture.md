# Guide: Agent Runtime Architecture

## Scope
This guide describes the product runtime agent under `src/agent/`. It is separate from `CRM/AGENTS.md`, which guides the coding assistant and wiki maintenance workflow.

The runtime agent answers and performs CRM work for authenticated users across contacts, leads, proposals, and pipeline history. User questions may involve prices, costs, margins, elapsed time, kilowatts, equipment, project type, proposal stage, lead status, or related commercial context.

## Architectural Principles
- The agent is an orchestration layer over CRM domain services.
- Domain `service.py` modules remain the source of truth for business rules.
- Tools are typed adapters around domain services; tools never call repositories directly.
- Skills are reusable reasoning procedures stored as `SKILL.md` bundles and selected on demand by the agent graph.
- Skills coordinate tool use, ambiguity handling, calculations, and answer shape; they do not replace tools or domain services.
- AzureOpenAI stays behind `LLMProvider` so graph and tools do not depend on provider-specific code.
- Answers must be grounded in retrieved CRM records. If the requested fact is missing, the agent states that it cannot find the value.
- Ambiguous entity matches require clarification before answering or mutating data.
- Write operations require explicit user confirmation and must preserve owner scoping.

## Runtime Layout
```text
src/agent/
  router.py
  schemas.py
  service.py
  state.py
  graph.py
  providers/
    base.py
    azure_openai.py
    factory.py
  tools/
    contacts.py
    leads.py
    proposals.py
    pipeline.py
    metrics.py
  skills/
    crm-entity-resolution/
      SKILL.md
    crm-proposal-qa/
      SKILL.md
    crm-sales-metrics/
      SKILL.md
    crm-pipeline-analysis/
      SKILL.md
    crm-operations/
      SKILL.md
```

## Request Flow
```text
/api/v1/agent/chat
  -> agent/router.py
  -> agent/service.py
  -> agent/graph.py
  -> selected SKILL.md instructions
  -> agent/tools/*
  -> domains/*/service.py
  -> domains/*/repository.py
  -> database
```

`router.py` injects the authenticated user and database session. `service.py` prepares graph input and owns the runtime boundary. `graph.py` coordinates classification, skill selection, tool calls, evidence validation, and final response composition.

## LangGraph Nodes
- `classify_intent`: categorize the request by CRM topic, requested operation, and risk level.
- `select_skills`: choose candidate skills from `name` and `description`, then load full `SKILL.md` instructions only for selected skills.
- `resolve_entities`: identify contacts, leads, proposals, dates, stages, equipment, monetary fields, and units mentioned by the user.
- `retrieve_records`: call typed tools to fetch permission-scoped CRM records.
- `derive_answer`: compute deterministic values such as margins, totals, price per kW, elapsed time, and comparisons.
- `validate_evidence`: ensure every factual answer is backed by retrieved records or explicit calculation inputs.
- `compose_answer`: return a concise answer with relevant record identifiers, missing data, and assumptions.
- `confirm_write`: gate mutating operations behind explicit user confirmation.
- `execute_write`: run confirmed mutating tools through domain services.

## Skills
Runtime skills live in `src/agent/skills/<skill-name>/SKILL.md`. Each skill must include YAML front matter with `name` and `description`, followed by concise operational instructions. The description should be specific enough for on-demand selection without loading every skill.

Recommended initial skills:
- `crm-entity-resolution`: resolve user phrases to contacts, leads, proposals, or pipeline entities.
- `crm-proposal-qa`: answer questions about proposal technical and commercial data.
- `crm-sales-metrics`: compute prices, costs, margins, power totals, unit economics, and date intervals.
- `crm-pipeline-analysis`: answer stage, transition history, elapsed time, and status questions.
- `crm-operations`: create or update CRM records after confirmation.

Each skill should define:
- When to use it.
- Allowed tools.
- Required evidence.
- Ambiguity policy.
- Missing-data policy.
- Output shape.
- Examples that cover broad patterns, not customer-specific fixtures.

## Tools
Tools should be small, typed, and permission-scoped. They adapt user intent to domain services and return structured data for the graph.

Initial tool groups:
- Contacts: `search_contacts`, `get_contact`.
- Leads: `search_leads`, `get_lead`, `list_leads_for_contact`.
- Proposals: `search_proposals`, `get_proposal`, `list_proposals_for_lead`.
- Pipeline: `get_pipeline_summary`, `list_stage_transitions`.
- Metrics: `calculate_proposal_metrics`, `compare_proposals`.
- Operations: `update_lead`, `update_proposal`, `transition_pipeline_stage`.

Tool outputs should include record IDs, display names, relevant fields, match confidence when applicable, and explicit missing fields. The graph should never rely on the model to infer facts that were not returned by a tool.

Current implementation includes the read and metric tools. Mutating operation tools remain planned and must be added with confirmation checkpoints.

## Entity Resolution
Entity resolution should search contacts, leads, and proposals because users may refer to a company, person, project name, proposal name, or informal phrase. Matching should prefer exact and normalized matches, then partial matches, and finally semantic or alias matches if implemented.

If multiple records plausibly match the user request, the agent asks a clarification question. If no record matches, it says so and may suggest the closest available matches.

## Calculations
Commercial and technical calculations must be deterministic Python code, not model arithmetic. This includes:
- Gross margin and margin percentage.
- Total cost, total price, and price per kW.
- Installed or proposed kW.
- Battery capacity summaries.
- Elapsed time between stage transitions.
- Proposal comparisons.

The final answer should name calculation inputs when useful and identify missing values that prevent a calculation.

## Security And Permissions
All tool calls must be scoped through [[permissions]]. The agent must not expose records outside the authenticated user's effective CRM permissions and resource assignments. Mutating tools must use existing domain services, must pass the same permission checks as REST, and should only execute after the user confirms the intended change. `tech` users must not receive Lead interactions through agent tools, and protected Proposal price fields must not be set or changed without the corresponding price permission.

## Testing Strategy
- Unit-test skill registry parsing and selection.
- Unit-test each tool against mocked or fixture-backed domain services.
- Unit-test calculation helpers with edge cases.
- Integration-test graph flows with a fake `LLMProvider`.
- Integration-test `/api/v1/agent/chat` authentication, permission/resource scoping, clarification, missing-data, and successful answer paths.

## Continuation Notes
The current implementation is intentionally read-first. Continue with [[agent-runtime-hardening]] before exposing mutating tools or production CRM operations.

## Related Pages
[[agent]], [[agent-tools]], [[agent-runtime-hardening]], [[crm-permissions]], [[contacts]], [[leads]], [[proposals]], [[pipeline]], [[2026-05-25-llmprovider-abstraction]]
