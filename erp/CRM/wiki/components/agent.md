# Subsystem: Agent

**Path:** `src/agent/`
**Responsibility:** Owns the runtime CRM assistant graph, skills, and tool wiring; it does not duplicate domain business logic.
**Status:** In development

## Purpose
The agent provides an intelligent interface powered by AzureOpenAI through LangGraph and LangChain. It answers authenticated user questions across contacts, leads, proposals, and pipeline history. Its tools call domain services so the REST API and agent obey the same business rules.

## Data model
The agent subsystem has request and response schemas in `agent/schemas.py`. No persisted agent data model is currently implemented.

## Public interface (service.py)
The agent is organized around:
- `service.py`: runtime entrypoint called by the HTTP router
- `state.py`: typed LangGraph state
- `graph.py`: LangGraph state machine
- `providers/base.py`: `LLMProvider` abstract base class
- `providers/azure_openai.py`: AzureOpenAI implementation using deployment settings
- `providers/factory.py`: provider selection based on config
- `skills/`: runtime `SKILL.md` bundles for entity resolution, proposal Q&A, sales metrics, pipeline analysis, and operations
- `tools/contacts.py`: searches and reads contacts through contact services
- `tools/leads.py`: searches and reads leads through lead services
- `tools/proposals.py`: searches proposals, reads proposal context, and calculates proposal metrics through proposal services
- `tools/pipeline.py`: reads pipeline summaries and transition history through pipeline services
- `tools/factory.py`: binds request-scoped tools to the database session and authenticated user

## Router endpoints
The agent router is mounted under `/api/v1/agent`. The technical specification identifies endpoint `/agent/chat`, which becomes `/api/v1/agent/chat` after router aggregation.

## Request / Response schemas (schemas.py)
- `AgentChatRequest`: current user message plus optional short chat history.
- `AgentChatResponse`: final answer, selected skills, tool calls, evidence references, and confirmation flag.
- `AgentEvidence`: compact references to records returned by tools.

## Dependencies
- **Internal:** [[contacts]], [[leads]], [[proposals]], [[pipeline]]
- **Core:** [[core]], [[api-v1]]

## Business rules / invariants
- Agent tools invoke domain `service.py` functions.
- Agent tools never call repositories directly.
- The agent does not replicate business logic.
- The agent has no independent permissions; it must use the same [[permissions]] checks and resource scopes as REST endpoints.
- `sales` agent context is limited to assigned Leads and derived Contacts, read-only Proposals, TechnicalVisits, and documents.
- `tech` agent context is limited to assigned Proposals and TechnicalVisits with derived read access to Contacts, Leads, and Lead documents; Lead interactions must not be exposed to `tech`.
- The agent must not set or change protected Proposal price fields unless the authenticated user has the required price permission.
- Runtime skills are reasoning procedures and tool-use policies; they do not replace domain services.
- Answers must be grounded in retrieved CRM records or deterministic calculations.
- Ambiguous contacts, leads, or proposals require clarification.
- Mutating operations require explicit user confirmation.
- New tools must be registered through `agent/tools/factory.py` so the graph can bind them.
- Current implementation is read-oriented; write-intent is recognized by skills but write tools are not exposed yet.

## Related decisions
[[2026-05-25-llmprovider-abstraction]], [[2026-05-25-domain-by-business-not-layer]], [[agent-runtime-architecture]], [[agent-tools]], [[2026-06-01-verp-identity-crm-permissions]]

## Known technical debt
[[agent-runtime-hardening]]

## Maintainer notes
Keep model/provider coupling behind `LLMProvider` so the graph and tools do not need to change when the provider changes. AzureOpenAI credentials and deployment are configured through local environment variables, not committed files.
