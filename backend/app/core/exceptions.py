"""
Custom exception hierarchy for the chatbot.

Rule of thumb:
- Raise the most specific exception that applies.
- Never let raw exceptions (KeyError, ValueError, etc.) escape a service
  layer function — catch them and re-raise as one of these instead.
"""

class ChatbotException(Exception):
    """Base exception for all custom errors in this application.

    Every other custom exception should inherit from this, so a single
    `except ChatbotException` in the API layer can catch anything we
    raised on purpose.
    """

    def __init__(self, message: str, *, details: dict | None = None):
        self.message = message 
        self.details = details or {}
        super().__init__(self.message)

class ProviderConfigurationError(ChatbotException):
    """Raised when a provider (OpenAI/Groq/Gemini) is misconfigured,
    e.g. missing API key or invalid model name."""
    pass


class LLMProviderError(ChatbotException):
    """Raised when a call to an LLM provider fails at runtime
    (timeout, bad response, provider-side error)."""
    pass


class MCPToolError(ChatbotException):
    """Raised when an MCP tool call fails or an MCP server is unreachable."""
    pass


class MemoryError(ChatbotException):
    """Raised when reading/writing short-term or long-term memory fails."""
    pass


class DatabaseError(ChatbotException):
    """Raised when a database operation fails."""
    pass


class RateLimitError(ChatbotException):
    """Raised when a provider or our own API rate limit is hit."""
    pass