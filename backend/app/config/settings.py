"""
Application settings, loaded from environment variables (.env file).

Usage elsewhere in the app:

    from app.config.settings import get_settings
    settings = get_settings()
    print(settings.openai_api_key)
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import Environment

class Settings(BaseSettings):
    # Tell pydantic-settings to read from a .env file, UTF-8 encoded,
    # and ignore any extra vars in .env we haven't declared here.

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_env: str = Field(default = Environment.DEV, alias="APP_ENV")
    log_level : str = Field(default = "INFO", alias = "LOG_LEVEL")

    # --- LLM provider keys (all optional here — factory.py validates
    # that the one actually being used is present) ---
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")

    # --- Database (used starting Module 12, defined now so it's ready) ---
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    @property
    def is_production(self) -> bool:
        return self.app_env == Environment.PROD

@lru_cache
def get_setting() -> Settings:
    """Returns a cached Settings instance.

    lru_cache means the .env file is only read/parsed once per process,
    not on every call — settings are effectively a singleton.
    """
    return Settings()

