import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ChatbotException(Exception):
    def __init__(self, message: str, *, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ProviderConfigurationError(ChatbotException):
    pass


class LLMProviderError(ChatbotException):
    pass


class MCPToolError(ChatbotException):
    pass


class MemoryError(ChatbotException):
    pass


class DatabaseError(ChatbotException):
    pass


class RateLimitError(ChatbotException):
    pass


def register_exception_handlers(app):
    """Registers handlers that convert our custom exceptions into
    safe JSON responses. Call this once from main.py after creating
    the FastAPI app.
    """

    @app.exception_handler(ChatbotException)
    async def chatbot_exception_handler(request: Request, exc: ChatbotException):
        # Log full detail internally...
        logger.error(
            "ChatbotException: %s | path=%s | details=%s",
            exc.message, request.url.path, exc.details,
        )
        # ...but only return a safe, generic-enough message to the client
        return JSONResponse(
            status_code=400,
            content={"error": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Catch-all: anything we didn't anticipate. Log full traceback
        # internally, but never expose it to the caller.
        logger.exception("Unhandled exception on path=%s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "type": "InternalError"},
        )
