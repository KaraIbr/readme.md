# Debt: Agent Runtime Hardening

**Area:** [[agent]]
**Severity:** Medium
**Discovered:** 2026-05-27

## Description
The runtime CRM agent is implemented and smoke-tested for authenticated read-oriented question answering, but it is not yet complete for production-grade CRM operations.

Implemented today:
- Authenticated `/api/v1/agent/chat`.
- LangGraph state machine with AzureOpenAI behind `LLMProvider`.
- Runtime `SKILL.md` loading and keyword-based skill selection.
- Read tools for contacts, leads, proposals, pipeline summaries, transition history, and proposal metrics.
- Owner-scoped tool execution through domain `service.py` functions.
- Deterministic proposal metrics for price per kW and price per estimated annual kWh.
- Unit/integration tests with a fake provider.
- Azure smoke test with an in-memory CRM dataset.

Remaining work:
- Add write tools for controlled operations such as `update_lead`, `update_proposal`, `transition_pipeline_stage`, `mark_proposal_won`, and `mark_proposal_lost`.
- Add a real confirmation checkpoint before any mutating tool can execute.
- Strengthen entity resolution beyond simple text search: normalization, scoring, contact-to-lead-to-proposal traversal, and ambiguity ranking.
- Refine runtime skills with richer instructions, examples, output contracts, missing-data policy, and tool choice rules.
- Add eval scenarios for common user questions across contacts, leads, proposals, prices, margins, kilowatts, elapsed time, and pipeline status.
- Add cost fields or a cost source before supporting true margin calculations. Current proposal data has `total_price` but no stored total cost.
- Improve output validation so final answers always cite evidence and do not add unsolicited follow-up offers.
- Decide whether the agent should persist conversation state or remain stateless per request.
- Add operational safeguards for Azure configuration precedence. A previously inherited `AZURE_OPENAI_API_KEY` environment variable overrode `CRM/.env` during smoke testing and caused an Azure 401 until the process environment was cleared.

## Current impact
The agent can answer read-only CRM questions and calculate available proposal metrics. It should not yet be used for production write operations, autonomous CRM changes, or margin answers that require unavailable cost data.

Some user questions may still require clarification more often than ideal because entity resolution is keyword-based. Multiple plausible contacts, leads, or proposals may not be ranked with enough nuance until scoring is added.

## Root cause
The current implementation intentionally prioritized a safe read-first agent: graph, provider, skill registry, read tools, metric tools, tests, and Azure smoke validation. Write operations and stronger resolution were deferred to avoid exposing mutating tools before explicit confirmation gates exist.

The margin limitation is a data-model limitation: proposals currently store `total_price` but do not store total cost or line-item cost data.

## Resolution plan
1. Add an eval suite for agent behavior before expanding capabilities.
2. Implement entity resolution scoring and clarification tests.
3. Refine each `SKILL.md` with concrete examples and output contracts.
4. Add cost data or a cost service before margin tools.
5. Implement confirmation-aware write tools only after read/eval behavior is stable.
6. Add integration tests for write-intent flows that stop at confirmation and confirmed flows that mutate through domain services.
7. Document production environment precedence for Azure variables and avoid inherited secret collisions in local smoke scripts.

## Related pages
[[agent]], [[agent-tools]], [[agent-runtime-architecture]], [[proposals]], [[pipeline]]
