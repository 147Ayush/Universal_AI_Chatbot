# backend/app/llm/factory.py

"""
Factory for creating LLM chat model instances.

This is the ONLY place in the app that should know about all three
provider classes. Everywhere else should just call:

    from app.llm.factory import get_llm
    model = get_llm(provider="groq", model_name="llama-3.3-70b-versatile")
"""

from langchain_core.language_models.chat_models import BaseChatModel

from app.llm.base import BaseLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.groq_provider import GroqProvider
from app.llm.gemini_provider import GeminiProvider
from app.core.constants import Provider
from app.core.exceptions import ProviderConfigurationError

_PROVIDER_REGISTRY: dict[str, type[BaseLLMProvider]] = {
    Provider.OPENAI: OpenAIProvider,
    Provider.GROQ: GroqProvider,
    Provider.GEMINI: GeminiProvider,
}


def get_llm(provider: str, model_name: str, **kwargs) -> BaseChatModel:
    """Get a ready-to-use LangChain chat model for the given provider.

    Args:
        provider: one of "openai", "groq", "gemini"
        model_name: provider-specific model id
        **kwargs: passed through to the chat model (temperature, etc.)

    Raises:
        ProviderConfigurationError: unknown provider name, or missing API key
    """
    provider_class = _PROVIDER_REGISTRY.get(provider)
    if provider_class is None:
        raise ProviderConfigurationError(
            f"Unknown provider: '{provider}'",
            details={"supported_providers": list(_PROVIDER_REGISTRY.keys())},
        )

    provider_instance = provider_class()
    return provider_instance.get_chat_model(model_name, **kwargs)