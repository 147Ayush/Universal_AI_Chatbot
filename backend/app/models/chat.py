# backend/app/models/chat.py

"""
Request/response schemas for the chat API.

These are the ONLY shapes of data that cross the HTTP boundary.
The service layer works with LangChain messages internally, but the
API layer only ever sees/returns these Pydantic models.
"""

from pydantic import BaseModel, Field

from app.core.constants import SUPPORTED_PROVIDERS


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's message")
    provider: str = Field(
        default="groq",
        description=f"LLM provider to use. One of: {SUPPORTED_PROVIDERS}",
    )
    model_name: str | None = Field(
        default=None,
        description="Specific model to use. If omitted, the provider's default is used.",
    )
    thread_id: str | None = Field(
        default=None,
        description="Conversation thread ID (used for memory). Optional for now.",
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="The assistant's response text")
    provider: str
    model_name: str
    thread_id: str | None = None
    requires_approval: bool = Field(
        default=False,
        description="True if the conversation is paused waiting on a human approval decision",
    )
    approval_request: dict | None = Field(
        default=None,
        description="When requires_approval is True, the pending tool call(s) needing review",
    )


class ApprovalRequest(BaseModel):
    thread_id: str = Field(..., description="The paused conversation's thread ID")
    approved: bool = Field(..., description="Whether the human approved the pending tool call(s)")
    reason: str | None = Field(default=None, description="Optional reason, especially for rejections")