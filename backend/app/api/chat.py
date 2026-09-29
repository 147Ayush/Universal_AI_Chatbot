# backend/app/api/chat.py

"""
Chat API endpoints.

Keep this file thin: no business logic here, just request handling
and delegation to chat_service.py.
"""

from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def send_message(request: ChatRequest) -> ChatResponse:
    """Send a message to the chatbot and get a reply.

    Errors (bad provider, missing API key, provider failure) are handled
    globally by the exception handlers registered in main.py — this
    function doesn't need its own try/except for that.
    """
    return handle_chat_message(request)