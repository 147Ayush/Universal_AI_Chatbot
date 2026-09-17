"""
Application-wide constants.
Keep this file free of logic — just names and values other modules import.
"""
# --- App metadata ---
APP_NAME = "Universal AI Chatbot"
APP_version = "0.1.0"

# --- Supported LLM providers (used later by llm/factory.py) ---
class Provider:
    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"

SUPPORTED_PROVIDERS =  [Provider.OPENAI, Provider.GROQ, Provider.GEMINI]

# --- Logging ---
LOG_FORMAT = "%(astime)s | %(Levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Environments ---
class Environment:
    DEV = "development"
    STAGING = "staging"
    PROD = "production"