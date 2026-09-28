# backend/app/llm/openai_provider.py

from langchain_openai import ChatOpenAI

from app.llm.base import BaseLLMProvider
from app.config.settings import get_settings
from app.core.exceptions import ProviderConfigurationError


class OpenAIProvider(BaseLLMProvider):
    def validate_config(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ProviderConfigurationError(
                "OpenAI API key is not configured",
                details={"provider": "openai", "expected_env": "OPENAI_API_KEY"},
            )

    def get_chat_model(self, model_name: str, **kwargs) -> ChatOpenAI:
        self.validate_config()
        settings = get_settings()
        return ChatOpenAI(
            model=model_name,
            api_key=settings.openai_api_key,
            **kwargs,
        )