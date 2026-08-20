"""Application settings and per-model defaults."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiKind(StrEnum):
    """Which Azure HTTP API a model uses."""

    RESPONSES = "responses"  # Azure OpenAI /openai/responses
    CHAT_COMPLETIONS = "chat_completions"  # Azure AI /models/chat/completions


class ReasoningOption(BaseModel):
    """One selectable reasoning level for a model."""

    value: str
    label: str


class ModelDefaults(BaseModel):
    """Default generation parameters for a model deployment."""

    max_output_tokens: int = 2048
    supports_vision: bool = True
    supports_pdf: bool = True
    # Sampling (usually off for reasoning models).
    supports_temperature: bool = False
    supports_top_p: bool = False
    temperature: float = 0.7
    top_p: float = 1.0
    # Reasoning effort — options differ per model family.
    supports_reasoning_effort: bool = False
    reasoning_effort_options: list[ReasoningOption] = Field(default_factory=list)
    default_reasoning_effort: str | None = None


class ModelSpec(BaseModel):
    """Registered model that can be selected in the UI."""

    id: str
    display_name: str
    deployment: str
    api_kind: ApiKind
    backend: str  # "azure_openai" | "azure_ai"
    defaults: ModelDefaults = Field(default_factory=ModelDefaults)


_GPT_REASONING = [
    ReasoningOption(value="low", label="Bajo"),
    ReasoningOption(value="medium", label="Medio"),
    ReasoningOption(value="high", label="Alto"),
]

_DEEPSEEK_REASONING = [
    ReasoningOption(value="disabled", label="Sin razonamiento"),
    ReasoningOption(value="high", label="Alto"),
    ReasoningOption(value="max", label="Máximo"),
]

_GROK_REASONING = [
    ReasoningOption(value="none", label="Ninguno"),
    ReasoningOption(value="low", label="Bajo"),
    ReasoningOption(value="medium", label="Medio"),
    ReasoningOption(value="high", label="Alto"),
]


_BASE_CATALOG: dict[str, ModelSpec] = {
    "gpt-5.6-sol": ModelSpec(
        id="gpt-5.6-sol",
        display_name="GPT-5.6 Sol",
        deployment="gpt-5.6-sol",
        api_kind=ApiKind.RESPONSES,
        backend="azure_openai",
        defaults=ModelDefaults(
            max_output_tokens=4096,
            supports_vision=True,
            supports_pdf=True,
            supports_reasoning_effort=True,
            reasoning_effort_options=_GPT_REASONING,
            default_reasoning_effort="medium",
        ),
    ),
    "gpt-5.6-terra": ModelSpec(
        id="gpt-5.6-terra",
        display_name="GPT-5.6 Terra",
        deployment="gpt-5.6-terra",
        api_kind=ApiKind.RESPONSES,
        backend="azure_openai",
        defaults=ModelDefaults(
            max_output_tokens=4096,
            supports_vision=True,
            supports_pdf=True,
            supports_reasoning_effort=True,
            reasoning_effort_options=_GPT_REASONING,
            default_reasoning_effort="medium",
        ),
    ),
    "DeepSeek-V4-Pro": ModelSpec(
        id="DeepSeek-V4-Pro",
        display_name="DeepSeek V4 Pro",
        deployment="DeepSeek-V4-Pro",
        api_kind=ApiKind.CHAT_COMPLETIONS,
        backend="azure_ai",
        defaults=ModelDefaults(
            max_output_tokens=4096,
            supports_vision=False,
            supports_pdf=False,
            supports_reasoning_effort=True,
            reasoning_effort_options=_DEEPSEEK_REASONING,
            default_reasoning_effort="high",
        ),
    ),
    "grok-4.3": ModelSpec(
        id="grok-4.3",
        display_name="Grok 4.3",
        deployment="grok-4.3",
        api_kind=ApiKind.CHAT_COMPLETIONS,
        backend="azure_ai",
        defaults=ModelDefaults(
            max_output_tokens=4096,
            supports_vision=True,
            supports_pdf=False,
            supports_reasoning_effort=True,
            reasoning_effort_options=_GROK_REASONING,
            default_reasoning_effort="low",
        ),
    ),
}


def _strip_endpoint(value: str) -> str:
    endpoint = value.strip().rstrip("/")
    for marker in (
        "/openai/responses",
        "/openai/v1",
        "/openai/deployments",
        "/models/chat/completions",
        "/models",
        "/chat/completions",
    ):
        if marker in endpoint:
            endpoint = endpoint.split(marker, maxsplit=1)[0].rstrip("/")
    if "?" in endpoint:
        endpoint = endpoint.split("?", maxsplit=1)[0].rstrip("/")
    return endpoint


class Settings(BaseSettings):
    """Azure connection settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Resource A: Azure OpenAI (GPT models → Responses API)
    azure_openai_endpoint: str = "https://chatiq.openai.azure.com"
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2025-04-01-preview"

    # Resource B: Azure AI Services (DeepSeek / Grok → Chat Completions)
    azure_ai_endpoint: str = "https://ai-asigcha5956ai083120569258.services.ai.azure.com"
    azure_ai_api_key: str = ""
    azure_ai_api_version: str = "2024-05-01-preview"

    # Optional deployment name overrides (Name/Model are the same in your portal)
    deployment_gpt_5_6_sol: str = "gpt-5.6-sol"
    deployment_gpt_5_6_terra: str = "gpt-5.6-terra"
    deployment_deepseek_v4_pro: str = "DeepSeek-V4-Pro"
    deployment_grok_4_3: str = "grok-4.3"

    @field_validator("azure_openai_endpoint", "azure_ai_endpoint", mode="before")
    @classmethod
    def normalize_endpoint(cls, value: object) -> object:
        if not isinstance(value, str) or not value.strip():
            return value
        return _strip_endpoint(value)

    @field_validator("azure_openai_api_key", "azure_ai_api_key", mode="before")
    @classmethod
    def empty_key_as_blank(cls, value: object) -> object:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return value

    def deployment_overrides(self) -> dict[str, str]:
        return {
            "gpt-5.6-sol": self.deployment_gpt_5_6_sol,
            "gpt-5.6-terra": self.deployment_gpt_5_6_terra,
            "DeepSeek-V4-Pro": self.deployment_deepseek_v4_pro,
            "grok-4.3": self.deployment_grok_4_3,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Prefer values from .env over stale shell exports during local development.
    load_dotenv(override=True)
    return Settings()


def _catalog_with_overrides() -> dict[str, ModelSpec]:
    overrides = get_settings().deployment_overrides()
    catalog: dict[str, ModelSpec] = {}
    for model_id, spec in _BASE_CATALOG.items():
        catalog[model_id] = spec.model_copy(
            update={"deployment": overrides.get(model_id, spec.deployment)}
        )
    return catalog


def list_models() -> list[ModelSpec]:
    return list(_catalog_with_overrides().values())


def get_model(model_id: str) -> ModelSpec:
    catalog = _catalog_with_overrides()
    try:
        return catalog[model_id]
    except KeyError as exc:
        known = ", ".join(catalog)
        raise KeyError(f"Unknown model '{model_id}'. Known: {known}") from exc


MODEL_CATALOG = _BASE_CATALOG
