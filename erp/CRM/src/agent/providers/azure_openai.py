"""AzureOpenAI provider for the CRM runtime assistant."""

from agent.providers.base import LLMProvider
from core.config import Settings
from core.exceptions import InvalidOperationError
from langchain_openai import AzureChatOpenAI


class AzureOpenAIProvider(LLMProvider):
    """Build LangChain chat models backed by AzureOpenAI."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def chat_model(self) -> AzureChatOpenAI:
        """Return the configured AzureOpenAI chat model."""

        missing = [
            name
            for name, value in {
                "azure_openai_endpoint": self._settings.azure_openai_endpoint,
                "azure_openai_api_key": self._settings.azure_openai_api_key,
                "azure_openai_deployment": self._settings.azure_openai_deployment,
            }.items()
            if value is None
        ]
        if missing:
            raise InvalidOperationError(
                "AzureOpenAI settings are incomplete",
                details={"missing": missing},
            )

        assert self._settings.azure_openai_endpoint is not None
        assert self._settings.azure_openai_api_key is not None
        assert self._settings.azure_openai_deployment is not None

        return AzureChatOpenAI(
            azure_endpoint=self._settings.azure_openai_endpoint.rstrip("/"),
            azure_deployment=self._settings.azure_openai_deployment,
            api_key=self._settings.azure_openai_api_key,
            api_version=self._settings.azure_openai_api_version,
            model=self._settings.azure_openai_deployment,
            timeout=30,
            max_retries=2,
            use_responses_api=self._settings.azure_openai_use_responses_api,
        )
