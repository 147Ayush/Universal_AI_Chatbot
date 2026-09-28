from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import Environment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_env: str = Field(default=Environment.DEV, alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # --- LLM provider keys ---
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")

    # --- Default models per provider ---
    openai_default_model: str = Field(default="gpt-4o-mini", alias="OPENAI_DEFAULT_MODEL")
    groq_default_model: str = Field(default="openai/gpt-oss-20b", alias="GROQ_DEFAULT_MODEL")
    gemini_default_model: str = Field(default="gemini-flash-lite-latest", alias="GEMINI_DEFAULT_MODEL")

    # --- Database (used from Module 12) ---
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    @property
    def is_production(self) -> bool:
        return self.app_env == Environment.PROD


@lru_cache
def get_settings() -> Settings:
    return Settings()