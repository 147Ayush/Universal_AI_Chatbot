# backend/app/llm/base.py

"""
Abstract base class for all LLM providers, plus helpers that normalize
provider output.

Every provider (OpenAI, Groq, Gemini) implements this same interface,
so the rest of the app (graph nodes, services) never needs to know
which provider it's actually talking to.
"""

from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel


class BaseLLMProvider(ABC):
    """Common interface every LLM provider must implement."""

    @abstractmethod
    def get_chat_model(self, model_name: str, **kwargs) -> BaseChatModel:
        """Return a configured LangChain chat model instance.

        Args:
            model_name: provider-specific model identifier
                (e.g. "gpt-4o-mini", "openai/gpt-oss-20b", "gemini-flash-latest")
            **kwargs: optional overrides (temperature, max_tokens, etc.)

        Returns:
            A LangChain BaseChatModel ready to invoke/stream.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_config(self) -> None:
        """Raise ProviderConfigurationError if this provider is missing
        required configuration (e.g. no API key set)."""
        raise NotImplementedError


def extract_text(content) -> str:
    """Normalize a chat model's response content into a plain string.

    Providers differ: some return a string, others (e.g. Gemini) return a
    list of content blocks like [{'type': 'text', 'text': '...'}].
    This returns just the visible text so nothing downstream has to care
    which provider produced it.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)

    return str(content)