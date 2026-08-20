"""Provider abstraction for chat models used by the runtime agent."""

from abc import ABC, abstractmethod

from langchain_core.language_models.chat_models import BaseChatModel


class LLMProvider(ABC):
    """Factory for LangChain-compatible chat models."""

    @abstractmethod
    def chat_model(self) -> BaseChatModel:
        """Return a chat model ready for LangGraph execution."""
