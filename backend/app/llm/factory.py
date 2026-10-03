# backend/app/llm/factory.py

"""
Factory for creating LLM chat model instances, plus retry/fallback
orchestration across providers.

This is the ONLY place in the app that should know about all three
provider classes. Everywhere else should just call:

    from app.llm.factory import get_llm
    model = get_llm(provider="groq", model_name="openai/gpt-oss-20b")
"""

import logging

from langchain_core.language_models.chat_models import BaseChatModel

from app.llm.base import BaseLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.groq_provider import GroqProvider
from app.llm.gemini_provider import GeminiProvider
from app.core.constants import Provider
from app.core.exceptions import ProviderConfigurationError, LLMProviderError
from app.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)

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


def get_default_model(provider: str) -> str:
    """Returns the configured default model for a provider.

    Shared by chat_service.py (resolving the caller's chosen provider)
    and invoke_with_fallback (resolving fallback providers' models).
    """
    from app.config.settings import get_settings  # local import avoids import-order issues

    settings = get_settings()
    defaults = {
        Provider.OPENAI: settings.openai_default_model,
        Provider.GROQ: settings.groq_default_model,
        Provider.GEMINI: settings.gemini_default_model,
    }
    if provider not in defaults:
        raise ProviderConfigurationError(
            f"Unknown provider: '{provider}'",
            details={"supported_providers": list(defaults.keys())},
        )
    return defaults[provider]


# Order to try fallback providers in, if the primary one keeps failing
_DEFAULT_FALLBACK_ORDER = [Provider.GROQ, Provider.OPENAI, Provider.GEMINI]


def invoke_with_fallback(
    messages,
    primary_provider: str,
    primary_model: str,
    tools: list | None = None,
    max_retries: int = 2,
):
    """Invokes an LLM with automatic retry (same provider) and fallback
    (different provider) if the primary provider keeps failing.

    Tries: primary_provider -> remaining providers in _DEFAULT_FALLBACK_ORDER.
    Each provider gets `max_retries` attempts before moving to the next.

    Raises:
        LLMProviderError: if every provider (primary + all fallbacks) fails
    """
    providers_to_try = [(primary_provider, primary_model)] + [
        (p, get_default_model(p)) for p in _DEFAULT_FALLBACK_ORDER if p != primary_provider
    ]

    last_error: Exception | None = None

    for provider_name, model_name in providers_to_try:
        try:
            llm = get_llm(provider=provider_name, model_name=model_name)
            if tools:
                llm = llm.bind_tools(tools)

            logger.info("Trying provider=%s model=%s", provider_name, model_name)
            response = retry_with_backoff(llm.invoke, messages, max_retries=max_retries)

            if provider_name != primary_provider:
                logger.warning(
                    "Primary provider '%s' failed — succeeded via fallback provider '%s'",
                    primary_provider, provider_name,
                )
            return response

        except Exception as e:
            last_error = e
            logger.error("Provider '%s' failed after retries: %s", provider_name, e)
            continue

    raise LLMProviderError(
        "All providers failed to respond",
        details={
            "attempted_providers": [p for p, _ in providers_to_try],
            "last_error": str(last_error),
        },
    )