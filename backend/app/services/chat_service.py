# backend/app/services/chat_service.py

"""
Chat service — the business logic layer between the API and the graph.

Responsibilities:
- resolve defaults (e.g. which model to use if the caller didn't specify one)
- build the initial graph state from a validated request
- invoke the compiled LangGraph workflow
- convert the graph's output back into a clean response shape

The API layer (api/chat.py) should never touch the graph directly —
it only ever calls functions in this file.
"""

import logging

from langchain_core.messages import HumanMessage

from app.config.settings import get_settings
from app.graph.workflow import get_workflow
from app.llm.base import extract_text
from app.models.chat import ChatRequest, ChatResponse
from app.core.exceptions import ProviderConfigurationError

logger = logging.getLogger(__name__)

_DEFAULT_MODELS = {}  # populated lazily below to avoid calling get_settings() at import time


def _resolve_model_name(provider: str, requested_model: str | None) -> str:
    """Returns the model to use: the caller's choice if given,
    otherwise that provider's configured default."""
    if requested_model:
        return requested_model

    settings = get_settings()
    defaults = {
        "openai": settings.openai_default_model,
        "groq": settings.groq_default_model,
        "gemini": settings.gemini_default_model,
    }
    if provider not in defaults:
        raise ProviderConfigurationError(
            f"Unknown provider: '{provider}'",
            details={"supported_providers": list(defaults.keys())},
        )
    return defaults[provider]


def handle_chat_message(request: ChatRequest) -> ChatResponse:
    """Runs a single chat message through the graph and returns the reply."""
    model_name = _resolve_model_name(request.provider, request.model_name)

    logger.info(
        "handle_chat_message: provider=%s model=%s thread_id=%s",
        request.provider, model_name, request.thread_id,
    )

    workflow = get_workflow()

    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "provider": request.provider,
        "model_name": model_name,
    }

    result = workflow.invoke(initial_state)
    final_message = result["messages"][-1]
    reply_text = extract_text(final_message.content)

    return ChatResponse(
        reply=reply_text,
        provider=request.provider,
        model_name=model_name,
        thread_id=request.thread_id,
    )