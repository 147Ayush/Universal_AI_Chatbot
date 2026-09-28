# backend/verify_module_3.py
# Temporary check script for Module 3 (LLM provider layer).
#
# Usage (from backend/, venv active):
#   python verify_module_3.py groq
#   python verify_module_3.py gemini
#   python verify_module_3.py openai
#   python verify_module_3.py unknown_provider   # tests the error path

import logging
import sys

from app.core.logging_config import setup_logging
from app.core.exceptions import ChatbotException
from app.config.settings import get_settings
from app.llm.factory import get_llm
from app.llm.base import extract_text

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

# Provider comes from the command line; defaults to groq.
provider_to_test = sys.argv[1] if len(sys.argv) > 1 else "groq"

default_models = {
    "openai": settings.openai_default_model,
    "groq": settings.groq_default_model,
    "gemini": settings.gemini_default_model,
}
# Unknown providers have no model; the factory should reject them anyway.
model_name = default_models.get(provider_to_test, "unused")

logger.info("Testing provider=%s model=%s", provider_to_test, model_name)

try:
    llm = get_llm(provider=provider_to_test, model_name=model_name)
    response = llm.invoke("Reply with exactly one word: OK")
except ChatbotException as e:
    # Our own exceptions: clean, expected failures (bad provider, missing key)
    logger.error("Caught %s: %s | details=%s", type(e).__name__, e.message, e.details)
    sys.exit(1)

text = extract_text(response.content)
logger.info("Response: %s", text)
print(f"Module 3 check complete [{provider_to_test}]. Response was: {text}")