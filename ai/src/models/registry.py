"""Factory for model providers."""

from __future__ import annotations

from config.settings import get_model, list_models
from models.azure_provider import AzureModelProvider
from models.client import clear_client_cache, get_azure_ai_client, get_azure_openai_client
from models.provider import LLMProvider


def get_provider(model_id: str) -> LLMProvider:
    """Return a provider for the given catalog model id."""
    spec = get_model(model_id)
    return AzureModelProvider(
        openai_client=get_azure_openai_client(),
        ai_client=get_azure_ai_client(),
        spec=spec,
    )


def list_provider_ids() -> list[str]:
    return [spec.id for spec in list_models()]


__all__ = ["clear_client_cache", "get_provider", "list_provider_ids"]
