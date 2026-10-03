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
from langgraph.types import Command

from app.graph.workflow import get_workflow
from app.llm.base import extract_text
from app.llm.factory import get_default_model
from app.models.chat import ChatRequest, ChatResponse, ApprovalRequest

logger = logging.getLogger(__name__)


def _resolve_model_name(provider: str, requested_model: str | None) -> str:
    """Returns the model to use: the caller's choice if given,
    otherwise that provider's configured default."""
    if requested_model:
        return requested_model
    return get_default_model(provider)


def handle_chat_message(request: ChatRequest) -> ChatResponse:
    """Runs a single chat message through the graph and returns the reply.

    If request.thread_id is omitted, a new thread is created and its ID
    is returned to the caller — they should pass it back on the next
    call to continue this same conversation.

    If the graph pauses for human approval (e.g. before a web search),
    this returns early with requires_approval=True — the caller should
    then call handle_approval_decision() with the user's decision.
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

    if "__interrupt__" in result:
        interrupt_payload = result["__interrupt__"][0].value
        return ChatResponse(
            reply="",
            provider=request.provider,
            model_name=model_name,
            thread_id=thread_id,
            requires_approval=True,
            approval_request=interrupt_payload,
        )

    final_message = result["messages"][-1]
    reply_text = extract_text(final_message.content)

    return ChatResponse(
        reply=reply_text,
        provider=request.provider,
        model_name=model_name,
        thread_id=thread_id,
    )


def handle_approval_decision(approval: ApprovalRequest) -> ChatResponse:
    """Resumes a paused conversation after a human approves or rejects
    a pending tool call.

    provider/model_name aren't resent by the caller here — they're read
    back from the graph's own state (persisted via the checkpointer from
    the original call), since this is continuing an existing run, not
    starting a new one.
    """
    workflow = get_workflow()
    config = {"configurable": {"thread_id": approval.thread_id}}

    resume_value = {"approved": approval.approved, "reason": approval.reason}
    result = workflow.invoke(Command(resume=resume_value), config=config)

    if "__interrupt__" in result:
        # Rare: another approval-requiring tool call happened immediately after
        interrupt_payload = result["__interrupt__"][0].value
        return ChatResponse(
            reply="",
            provider=result.get("provider", ""),
            model_name=result.get("model_name", ""),
            thread_id=approval.thread_id,
            requires_approval=True,
            approval_request=interrupt_payload,
        )

    final_message = result["messages"][-1]
    reply_text = extract_text(final_message.content)

    return ChatResponse(
        reply=reply_text,
        provider=result.get("provider", ""),
        model_name=result.get("model_name", ""),
        thread_id=approval.thread_id,
    )


async def stream_chat_message(request: ChatRequest) -> AsyncGenerator[dict, None]:
    """Streams the assistant's reply token-by-token, with thread memory.

    Yields dicts: the first one carries the thread_id (so the client
    learns it even on a brand-new thread), the rest carry text chunks.

    NOTE: human-in-the-loop approval is not yet handled in the streaming
    path — if a risky tool call occurs mid-stream, the stream will simply
    stop without an explicit approval event. Non-streaming (handle_chat_message)
    is the fully-supported path for approval flows for now.
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