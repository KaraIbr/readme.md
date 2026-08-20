"""Provider protocol and shared request/response types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from documents.attachments import Attachment


@dataclass(frozen=True)
class GenerationParams:
    max_output_tokens: int = 2048
    system_prompt: str | None = None
    reasoning_effort: str | None = None
    temperature: float | None = None
    top_p: float | None = None


@dataclass(frozen=True)
class GenerationResult:
    text: str
    model: str
    warnings: tuple[str, ...] = field(default_factory=tuple)
    raw: object | None = None


class LLMProvider(Protocol):
    """Minimal interface every model backend must implement."""

    model_id: str

    def generate(
        self,
        prompt: str,
        params: GenerationParams,
        attachments: list[Attachment] | None = None,
    ) -> GenerationResult: ...
