# backend/app/api/feedback.py

"""
Feedback API endpoints.
"""

from fastapi import APIRouter

from app.models.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import submit_feedback, get_feedback_for_thread

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
async def send_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Records thumbs up/down feedback on an assistant response."""
    return await submit_feedback(request)


@router.get("/{thread_id}", response_model=list[FeedbackResponse])
async def list_feedback(thread_id: str) -> list[FeedbackResponse]:
    """Lists all feedback submitted for a given conversation thread."""
    return await get_feedback_for_thread(thread_id)
