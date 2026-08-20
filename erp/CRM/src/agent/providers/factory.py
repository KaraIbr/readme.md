"""Provider selection for the CRM runtime assistant."""

from agent.providers.azure_openai import AzureOpenAIProvider
from agent.providers.base import LLMProvider
from core.config import get_settings


def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider."""

    return AzureOpenAIProvider(get_settings())
