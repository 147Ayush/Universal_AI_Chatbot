# backend/app/llm/gemini_provider.py

from langchain_google_genai import ChatGoogleGenerativeAI

from app.llm.base import BaseLLMProvider
from app.config.settings import get_settings
from app.core.exceptions import ProviderConfigurationError


class GeminiProvider(BaseLLMProvider):
    def validate_config(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ProviderConfigurationError(
                "Gemini API key is not configured",
                details={"provider": "gemini", "expected_env": "GEMINI_API_KEY"},
            )

    def get_chat_model(self, model_name: str, **kwargs) -> ChatGoogleGenerativeAI:
        self.validate_config()
        settings = get_settings()
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.gemini_api_key,
            **kwargs,
        )