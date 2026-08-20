# ADR: LLMProvider Abstraction

**Date:** 2026-05-25
**Status:** Accepted

## Context
The agent uses AzureOpenAI GPT-5.5, but the model or provider may need to change without rewriting the agent graph or tools.

## Alternatives considered
- **Call AzureOpenAI directly from graph and tools:** Rejected because it would couple agent logic to one provider.
- **Introduce an `LLMProvider` ABC:** Accepted because it isolates provider selection and allows compatible providers to be swapped.

## Decision
Define `LLMProvider` in `agent/providers/base.py`. Implement AzureOpenAI GPT-5.5 in `agent/providers/azure_openai.py`, and select providers through `agent/providers/factory.py`.

## Consequences
- Graph and tools stay decoupled from provider-specific details.
- Provider changes should not require graph or tool changes.
- The abstraction must remain compatible with the LangChain chat model interface used by the agent.

## Affected components
[[agent]], [[core]]
