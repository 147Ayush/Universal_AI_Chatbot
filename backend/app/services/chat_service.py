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
import uuid
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage

from app.config.settings import get_settings
from app.graph.workflow import get_workflow
from app.llm.base import extract_text
from app.models.chat import ChatRequest, ChatResponse
from app.core.exceptions import ProviderConfigurationError

logger = logging.getLogger(__name__)


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
    """Runs a single chat message through the graph and returns the reply.

    If request.thread_id is omitted, a new thread is created and its ID
    is returned to the caller — they should pass it back on the next
    call to continue this same conversation.
    """
    model_name = _resolve_model_name(request.provider, request.model_name)
    thread_id = request.thread_id or str(uuid.uuid4())

    logger.info(
        "handle_chat_message: provider=%s model=%s thread_id=%s",
        request.provider, model_name, thread_id,
    )

    workflow = get_workflow()
    config = {"configurable": {"thread_id": thread_id}}

    # Only the NEW message is sent — the checkpointer already holds
    # everything said earlier in this thread.
    input_state = {
        "messages": [HumanMessage(content=request.message)],
        "provider": request.provider,
        "model_name": model_name,
    }

    result = workflow.invoke(input_state, config=config)
    final_message = result["messages"][-1]
    reply_text = extract_text(final_message.content)

    return ChatResponse(
        reply=reply_text,
        provider=request.provider,
        model_name=model_name,
        thread_id=thread_id,
    )


async def stream_chat_message(request: ChatRequest) -> AsyncGenerator[dict, None]:
    """Streams the assistant's reply token-by-token, with thread memory.

    Yields dicts: the first one carries the thread_id (so the client
    learns it even on a brand-new thread), the rest carry text chunks.
    """
    model_name = _resolve_model_name(request.provider, request.model_name)
    thread_id = request.thread_id or str(uuid.uuid4())

    logger.info(
        "stream_chat_message: provider=%s model=%s thread_id=%s",
        request.provider, model_name, thread_id,
    )

    workflow = get_workflow()
    config = {"configurable": {"thread_id": thread_id}}

    input_state = {
        "messages": [HumanMessage(content=request.message)],
        "provider": request.provider,
        "model_name": model_name,
    }

    yield {"thread_id": thread_id}

    async for message_chunk, _metadata in workflow.astream(
        input_state, config=config, stream_mode="messages"
    ):
        text = extract_text(message_chunk.content)
        if text:
            yield {"content": text}