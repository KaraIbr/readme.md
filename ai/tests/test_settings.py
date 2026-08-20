"""Tests for endpoint normalization and catalog wiring."""

from __future__ import annotations

from config.settings import ApiKind, Settings, _strip_endpoint, get_model


def test_strip_openai_responses_target_uri() -> None:
    uri = "https://chatiq.openai.azure.com/openai/responses?api-version=2025-04-01-preview"
    assert _strip_endpoint(uri) == "https://chatiq.openai.azure.com"


def test_strip_ai_chat_completions_target_uri() -> None:
    uri = (
        "https://ai-asigcha5956ai083120569258.services.ai.azure.com"
        "/models/chat/completions?api-version=2024-05-01-preview"
    )
    assert _strip_endpoint(uri) == ("https://ai-asigcha5956ai083120569258.services.ai.azure.com")


def test_model_api_kinds() -> None:
    assert get_model("gpt-5.6-sol").api_kind is ApiKind.RESPONSES
    assert get_model("gpt-5.6-terra").backend == "azure_openai"
    assert get_model("DeepSeek-V4-Pro").api_kind is ApiKind.CHAT_COMPLETIONS
    assert get_model("grok-4.3").backend == "azure_ai"


def test_reasoning_options_differ_by_model() -> None:
    gpt = get_model("gpt-5.6-sol")
    deepseek = get_model("DeepSeek-V4-Pro")
    grok = get_model("grok-4.3")

    assert [o.value for o in gpt.defaults.reasoning_effort_options] == [
        "low",
        "medium",
        "high",
    ]
    assert gpt.defaults.default_reasoning_effort == "medium"

    assert [o.value for o in deepseek.defaults.reasoning_effort_options] == [
        "disabled",
        "high",
        "max",
    ]
    assert [o.value for o in grok.defaults.reasoning_effort_options] == [
        "none",
        "low",
        "medium",
        "high",
    ]


def test_settings_defaults_match_user_uris() -> None:
    settings = Settings()
    assert settings.azure_openai_endpoint == "https://chatiq.openai.azure.com"
    assert settings.azure_openai_api_version == "2025-04-01-preview"
    assert (
        settings.azure_ai_endpoint == "https://ai-asigcha5956ai083120569258.services.ai.azure.com"
    )
    assert settings.azure_ai_api_version == "2024-05-01-preview"
