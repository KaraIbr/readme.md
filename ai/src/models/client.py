"""OpenAI-compatible clients for the two Azure backends."""

from __future__ import annotations

from functools import lru_cache

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI, OpenAI

from config.settings import Settings, get_settings


def _entra_token_provider():
    return get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default",
    )


@lru_cache(maxsize=1)
def get_azure_openai_client() -> AzureOpenAI:
    """Client for Azure OpenAI classic Responses API (api-key + api-version)."""
    settings = get_settings()
    if not settings.azure_openai_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not set in .env")

    # Portal Target URI style:
    # https://chatiq.openai.azure.com/openai/responses?api-version=2025-04-01-preview
    # AzureOpenAI sends the key as `api-key` (not Bearer).
    kwargs: dict = {
        "azure_endpoint": settings.azure_openai_endpoint.rstrip("/") + "/",
        "api_version": settings.azure_openai_api_version,
    }
    if settings.azure_openai_api_key:
        kwargs["api_key"] = settings.azure_openai_api_key
    else:
        kwargs["azure_ad_token_provider"] = _entra_token_provider()

    return AzureOpenAI(**kwargs)


@lru_cache(maxsize=1)
def get_azure_ai_client() -> OpenAI:
    """Client for Azure AI model inference (Chat Completions)."""
    settings = get_settings()
    if not settings.azure_ai_endpoint:
        raise ValueError("AZURE_AI_ENDPOINT is not set in .env")

    base_url = settings.azure_ai_endpoint.rstrip("/") + "/models"
    if settings.azure_ai_api_key:
        api_key: str | object = settings.azure_ai_api_key
    else:
        api_key = _entra_token_provider()

    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_query={"api-version": settings.azure_ai_api_version},
    )


def clear_client_cache() -> None:
    get_azure_openai_client.cache_clear()
    get_azure_ai_client.cache_clear()


def build_openai_client(settings: Settings) -> AzureOpenAI:
    del settings
    clear_client_cache()
    return get_azure_openai_client()
