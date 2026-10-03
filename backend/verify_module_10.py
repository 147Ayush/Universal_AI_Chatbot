# backend/verify_module_10.py
# Temporary check: confirms retry + fallback works.

import logging

from langchain_core.messages import HumanMessage

from app.core.logging_config import setup_logging
from app.config.settings import get_settings
from app.llm.factory import invoke_with_fallback
from app.llm.base import extract_text

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

print("--- Test 1: normal call, everything healthy ---")
response = invoke_with_fallback(
    messages=[HumanMessage(content="Reply with exactly one word: OK")],
    primary_provider="groq",
    primary_model=settings.groq_default_model,
)
print("Result:", extract_text(response.content))

print("\n--- Test 2: bad model on primary provider -> should fall back ---")
response = invoke_with_fallback(
    messages=[HumanMessage(content="Reply with exactly one word: OK")],
    primary_provider="openai",
    primary_model="this-model-does-not-exist",
)
print("Result:", extract_text(response.content))