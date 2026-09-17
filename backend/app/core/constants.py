APP_NAME = "Universal AI Chatbot"
APP_VERSION = "0.1.0"


class Provider:
    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"


SUPPORTED_PROVIDERS = [Provider.OPENAI, Provider.GROQ, Provider.GEMINI]

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Environment:
    DEV = "development"
    STAGING = "staging"
    PROD = "production"