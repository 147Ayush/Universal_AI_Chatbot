# backend/verify_module_10c.py
# Temporary check: confirms feedback capture works.

import logging

from app.core.logging_config import setup_logging
from app.config.settings import get_settings
from app.models.feedback import FeedbackRequest
from app.services.feedback_service import submit_feedback, get_feedback_for_thread

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

thread_id = "test-thread-123"

print("--- Submitting feedback ---")
fb1 = submit_feedback(FeedbackRequest(thread_id=thread_id, rating="up", message_index=1))
print("Recorded:", fb1)

fb2 = submit_feedback(
    FeedbackRequest(thread_id=thread_id, rating="down", message_index=3, comment="Too verbose")
)
print("Recorded:", fb2)

print("\n--- Fetching feedback for thread ---")
all_for_thread = get_feedback_for_thread(thread_id)
print(f"Found {len(all_for_thread)} items:")
for f in all_for_thread:
    print(" -", f.rating, "|", f.comment)

print("\n--- Fetching feedback for a DIFFERENT thread (should be empty) ---")
other = get_feedback_for_thread("some-other-thread")
print("Found:", len(other), "items")