# backend/verify_module_7.py
# Temporary check: confirms short-term (thread-based) memory works.

import logging

from app.core.logging_config import setup_logging
from app.config.settings import get_settings
from app.models.chat import ChatRequest
from app.services.chat_service import handle_chat_message

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

# --- Turn 1: no thread_id, so a new thread is created ---
response1 = handle_chat_message(
    ChatRequest(message="My name is Ayush. Just say OK.", provider="groq")
)
print("Turn 1 reply:", response1.reply)
print("Thread ID:", response1.thread_id)

# --- Turn 2: same thread_id, should remember the name from turn 1 ---
response2 = handle_chat_message(
    ChatRequest(
        message="What is my name? Answer with just the name.",
        provider="groq",
        thread_id=response1.thread_id,
    )
)
print("Turn 2 reply:", response2.reply)

# --- Turn 3: DIFFERENT (new) thread_id — should NOT know the name ---
response3 = handle_chat_message(
    ChatRequest(message="What is my name? Answer with just the name, or say you don't know.", provider="groq")
)
print("Turn 3 reply (new thread, should not know):", response3.reply)