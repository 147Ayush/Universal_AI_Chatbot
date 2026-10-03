# backend/app/services/feedback_service.py

"""
Feedback service — records and retrieves 👍/👎 feedback on responses.

Temporary in-memory storage. Module 12 replaces this with a real
'feedback' table via SQLAlchemy + PostgreSQL — the function signatures
here are designed to stay the same when that happens, so nothing
calling into this service needs to change.
"""

import logging
import uuid
from datetime import datetime, timezone

from app.models.feedback import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)

_feedback_store: dict[str, FeedbackResponse] = {}


def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Records a new piece of feedback."""
    feedback_id = str(uuid.uuid4())
    feedback = FeedbackResponse(
        id=feedback_id,
        thread_id=request.thread_id,
        message_index=request.message_index,
        rating=request.rating,
        comment=request.comment,
        created_at=datetime.now(timezone.utc),
    )
    _feedback_store[feedback_id] = feedback

    logger.info(
        "Feedback recorded: id=%s thread_id=%s rating=%s",
        feedback_id, request.thread_id, request.rating,
    )
    return feedback


def get_feedback_for_thread(thread_id: str) -> list[FeedbackResponse]:
    """Returns all feedback submitted for a given conversation thread."""
    return [f for f in _feedback_store.values() if f.thread_id == thread_id]


def get_all_feedback() -> list[FeedbackResponse]:
    """Returns every piece of feedback ever recorded (admin/debug use)."""
    return list(_feedback_store.values())