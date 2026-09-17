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