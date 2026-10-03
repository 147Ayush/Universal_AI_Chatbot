# backend/app/models/feedback.py

"""
Request/response schemas for the feedback API.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    thread_id: str = Field(..., description="Conversation thread this feedback relates to")
    message_index: int | None = Field(
        default=None,
        description="Index of the message being rated within the thread, if known",
    )
    rating: Literal["up", "down"] = Field(..., description="Thumbs up or thumbs down")
    comment: str | None = Field(default=None, description="Optional free-text comment")


class FeedbackResponse(BaseModel):
    id: str
    thread_id: str
    message_index: int | None
    rating: Literal["up", "down"]
    comment: str | None
    created_at: datetime