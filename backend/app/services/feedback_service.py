# backend/app/services/feedback_service.py

"""
Feedback service — records and retrieves 👍/👎 feedback on responses.

Persists to Postgres (the 'feedback' table in app/db/models.py) when
DATABASE_URL is configured. Falls back to in-memory storage otherwise,
so the app still works without a database for quick local testing —
same fallback pattern used in app/memory/short_term.py and long_term.py.
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.models.feedback import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)

# In-memory fallback store, used only when no database is configured.
_feedback_store: dict[str, FeedbackResponse] = {}


def _row_to_response(row) -> FeedbackResponse:
    return FeedbackResponse(
        id=row.id,
        thread_id=row.thread_id,
        message_index=row.message_index,
        rating=row.rating,
        comment=row.comment,
        created_at=row.created_at,
    )


async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Records a new piece of feedback."""
    from app.db.session import AsyncSessionLocal
    from app.db.models import Feedback as FeedbackORM

    feedback_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    feedback = FeedbackResponse(
        id=feedback_id,
        thread_id=request.thread_id,
        message_index=request.message_index,
        rating=request.rating,
        comment=request.comment,
        created_at=created_at,
    )

    if AsyncSessionLocal is not None:
        try:
            async with AsyncSessionLocal() as db:
                db.add(FeedbackORM(**feedback.model_dump()))
                await db.commit()
            logger.info(
                "Feedback recorded (Postgres): id=%s thread_id=%s rating=%s",
                feedback_id, request.thread_id, request.rating,
            )
            return feedback
        except Exception as e:
            logger.error("Failed to persist feedback to Postgres, falling back to memory: %s", e)

    _feedback_store[feedback_id] = feedback
    logger.info(
        "Feedback recorded (in-memory): id=%s thread_id=%s rating=%s",
        feedback_id, request.thread_id, request.rating,
    )
    return feedback


async def get_feedback_for_thread(thread_id: str) -> list[FeedbackResponse]:
    """Returns all feedback submitted for a given conversation thread."""
    from app.db.session import AsyncSessionLocal
    from app.db.models import Feedback as FeedbackORM

    if AsyncSessionLocal is not None:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(FeedbackORM).where(FeedbackORM.thread_id == thread_id))
                return [_row_to_response(r) for r in result.scalars().all()]
        except Exception as e:
            logger.error("Failed to read feedback from Postgres, falling back to memory: %s", e)

    return [f for f in _feedback_store.values() if f.thread_id == thread_id]


async def get_all_feedback() -> list[FeedbackResponse]:
    """Returns every piece of feedback ever recorded (admin/debug use)."""
    from app.db.session import AsyncSessionLocal
    from app.db.models import Feedback as FeedbackORM

    if AsyncSessionLocal is not None:
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(FeedbackORM))
                return [_row_to_response(r) for r in result.scalars().all()]
        except Exception as e:
            logger.error("Failed to read feedback from Postgres, falling back to memory: %s", e)

    return list(_feedback_store.values())
