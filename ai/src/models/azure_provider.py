"""Azure providers for Responses and Chat Completions APIs."""

from __future__ import annotations

from openai import AzureOpenAI, OpenAI

from config.settings import ApiKind, ModelSpec
from documents.attachments import Attachment, AttachmentKind
from models.provider import GenerationParams, GenerationResult


class AzureModelProvider:
    """Routes to Responses or Chat Completions based on the model spec."""

    def __init__(
        self,
        *,
        openai_client: AzureOpenAI,
        ai_client: OpenAI,
        spec: ModelSpec,
    ) -> None:
        self._openai_client = openai_client
        self._ai_client = ai_client
        self._spec = spec
        self.model_id = spec.id

    def generate(
        self,
        prompt: str,
        params: GenerationParams,
        attachments: list[Attachment] | None = None,
    ) -> GenerationResult:
        attachments = attachments or []
        if self._spec.api_kind is ApiKind.RESPONSES:
            return self._generate_responses(prompt, params, attachments)
        return self._generate_chat(prompt, params, attachments)

    def _generate_responses(
        self,
        prompt: str,
        params: GenerationParams,
        attachments: list[Attachment],
    ) -> GenerationResult:
        content, warnings = self._build_responses_content(prompt, attachments)
        input_messages: list[dict] = []
        if params.system_prompt:
            input_messages.append(
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": params.system_prompt}],
                }
            )
        input_messages.append({"role": "user", "content": content})

        create_kwargs: dict = {
            "model": self._spec.deployment,
            "input": input_messages,
            "max_output_tokens": params.max_output_tokens,
        }
        if params.reasoning_effort and self._spec.defaults.supports_reasoning_effort:
            create_kwargs["reasoning"] = {"effort": params.reasoning_effort}
        if self._spec.defaults.supports_temperature and params.temperature is not None:
            create_kwargs["temperature"] = params.temperature
        if self._spec.defaults.supports_top_p and params.top_p is not None:
            create_kwargs["top_p"] = params.top_p

        response = self._openai_client.responses.create(**create_kwargs)
        text = getattr(response, "output_text", None) or _extract_responses_text(response)
        return GenerationResult(
            text=text or "",
            model=getattr(response, "model", self._spec.deployment),
            warnings=tuple(warnings),
            raw=response,
        )

    def _generate_chat(
        self,
        prompt: str,
        params: GenerationParams,
        attachments: list[Attachment],
    ) -> GenerationResult:
        user_content, warnings = self._build_chat_content(prompt, attachments)
        messages: list[dict] = []
        if params.system_prompt:
            messages.append({"role": "system", "content": params.system_prompt})
        messages.append({"role": "user", "content": user_content})

        create_kwargs: dict = {
            "model": self._spec.deployment,
            "messages": messages,
            "max_tokens": params.max_output_tokens,
        }
        if self._spec.defaults.supports_temperature and params.temperature is not None:
            create_kwargs["temperature"] = params.temperature
        if self._spec.defaults.supports_top_p and params.top_p is not None:
            create_kwargs["top_p"] = params.top_p

        extra_body: dict = {}
        if params.reasoning_effort and self._spec.defaults.supports_reasoning_effort:
            if self.model_id == "DeepSeek-V4-Pro":
                if params.reasoning_effort == "disabled":
                    extra_body["thinking"] = {"type": "disabled"}
                else:
                    create_kwargs["reasoning_effort"] = params.reasoning_effort
                    extra_body["thinking"] = {"type": "enabled"}
            else:
                # Grok and other chat models that accept reasoning_effort.
                create_kwargs["reasoning_effort"] = params.reasoning_effort

        if extra_body:
            create_kwargs["extra_body"] = extra_body

        response = self._ai_client.chat.completions.create(**create_kwargs)
        choice = response.choices[0].message if response.choices else None
        text = (choice.content if choice else None) or ""
        return GenerationResult(
            text=text,
            model=getattr(response, "model", self._spec.deployment) or self._spec.deployment,
            warnings=tuple(warnings),
            raw=response,
        )

    def _build_responses_content(
        self,
        prompt: str,
        attachments: list[Attachment],
    ) -> tuple[list[dict], list[str]]:
        content: list[dict] = [{"type": "input_text", "text": prompt}]
        warnings: list[str] = []
        defaults = self._spec.defaults

        for attachment in attachments:
            if attachment.kind is AttachmentKind.IMAGE:
                if not defaults.supports_vision:
                    warnings.append(
                        f"Model '{self.model_id}' does not support images; "
                        f"skipped '{attachment.filename}'."
                    )
                    continue
                content.append({"type": "input_image", "image_url": attachment.data_url})
                continue

            if attachment.kind is AttachmentKind.PDF:
                if defaults.supports_pdf:
                    content.append(
                        {
                            "type": "input_file",
                            "filename": attachment.filename,
                            "file_data": attachment.data_url,
                        }
                    )
                else:
                    warning = self._append_pdf_as_text(content, attachment, as_responses=True)
                    if warning:
                        warnings.append(warning)

        return content, warnings

    def _build_chat_content(
        self,
        prompt: str,
        attachments: list[Attachment],
    ) -> tuple[str | list[dict], list[str]]:
        warnings: list[str] = []
        defaults = self._spec.defaults
        parts: list[dict] = [{"type": "text", "text": prompt}]
        has_image = False

        for attachment in attachments:
            if attachment.kind is AttachmentKind.IMAGE:
                if not defaults.supports_vision:
                    warnings.append(
                        f"Model '{self.model_id}' does not support images; "
                        f"skipped '{attachment.filename}'."
                    )
                    continue
                has_image = True
                parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": attachment.data_url},
                    }
                )
                continue

            if attachment.kind is AttachmentKind.PDF:
                # Chat Completions path does not take native PDF files.
                warning = self._append_pdf_as_text(parts, attachment, as_responses=False)
                if warning:
                    warnings.append(warning)

        if not has_image and len(parts) == 1:
            return parts[0]["text"], warnings
        return parts, warnings

    def _append_pdf_as_text(
        self,
        content: list[dict],
        attachment: Attachment,
        *,
        as_responses: bool,
    ) -> str | None:
        extracted = attachment.extract_text()
        if not extracted:
            return f"Could not extract text from '{attachment.filename}'."

        text = f"\n\n--- Document: {attachment.filename} ---\n{extracted}\n--- End document ---"
        if as_responses:
            content.append({"type": "input_text", "text": text})
        else:
            # Merge into the first text part when possible.
            if content and content[0].get("type") == "text":
                content[0]["text"] = content[0]["text"] + text
            else:
                content.append({"type": "text", "text": text})
        return (
            f"Model '{self.model_id}' has no native PDF support; "
            f"sent '{attachment.filename}' as extracted text."
        )


def _extract_responses_text(response: object) -> str:
    chunks: list[str] = []
    for item in getattr(response, "output", None) or []:
        for part in getattr(item, "content", None) or []:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)
    return "\n".join(chunks)


# Backwards-compatible alias
AzureFoundryProvider = AzureModelProvider
