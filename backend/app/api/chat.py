"""
Chat API endpoints.

Keep this file thin: no business logic here, just request handling
and delegation to chat_service.py.
"""

import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest, ChatResponse, ApprovalRequest
from app.services.chat_service import (
    handle_chat_message,
    stream_chat_message,
    handle_approval_decision,
)
from app.core.exceptions import ChatbotException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest) -> ChatResponse:
    """Send a message to the chatbot and get a reply.

    If the response has requires_approval=True, the conversation is
    paused — call POST /chat/approve with the same thread_id to continue.

    Errors (bad provider, missing API key, provider failure) are handled
    globally by the exception handlers registered in main.py — this
    function doesn't need its own try/except for that.
    """
    return await handle_chat_message(request)


@router.post("/approve", response_model=ChatResponse)
async def approve_tool_call(approval: ApprovalRequest) -> ChatResponse:
    """Resumes a paused chat after a human approves or rejects a
    pending tool call (see ChatResponse.requires_approval)."""
    return await handle_approval_decision(approval)


@router.post("/stream")
async def stream_message(request: ChatRequest):
    """Streams the assistant's reply as Server-Sent Events (SSE).

    First event: {"thread_id": "..."}  -- the thread to reuse for follow-ups
    Then:        {"content": "<token>"} for each chunk as it arrives
    Finally:     {"done": true}

    NOTE: human-in-the-loop approval is not yet surfaced in this
    streaming endpoint — use POST /chat (non-streaming) for flows that
    may require approval, for now.
    """

    async def event_generator():
        try:
            async for event in stream_chat_message(request):
                yield f"data: {json.dumps(event)}\n\n"
        except ChatbotException as e:
            # Streaming responses can't use the global exception handlers —
            # headers are already sent by the time an error happens mid-stream,
            # so we send the error as one more SSE event instead.
            logger.error("Stream error: %s", e.message)
            yield f"data: {json.dumps({'error': e.message})}\n\n"
        finally:
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # prevents proxies from buffering the stream
        },
    )
