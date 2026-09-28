# backend/app/llm/groq_provider.py

from langchain_groq import ChatGroq

from app.llm.base import BaseLLMProvider
from app.config.settings import get_settings
from app.core.exceptions import ProviderConfigurationError


class GroqProvider(BaseLLMProvider):
    def validate_config(self) -> None:
        settings = get_settings()
        if not settings.groq_api_key:
            raise ProviderConfigurationError(
                "Groq API key is not configured",
                details={"provider": "groq", "expected_env": "GROQ_API_KEY"},
            )

    def get_chat_model(self, model_name: str, **kwargs) -> ChatGroq:
        self.validate_config()
        settings = get_settings()
        return ChatGroq(
            model=model_name,
            api_key=settings.groq_api_key,
            **kwargs,
        )