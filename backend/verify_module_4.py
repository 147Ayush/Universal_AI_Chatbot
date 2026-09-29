# backend/verify_module_4.py
# Temporary check script for Module 4 (LangGraph core).

import logging

from langchain_core.messages import HumanMessage

from app.core.logging_config import setup_logging
from app.config.settings import get_settings
from app.graph.workflow import get_workflow
from app.llm.base import extract_text

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

workflow = get_workflow()

initial_state = {
    "messages": [HumanMessage(content="Reply with exactly one word: OK")],
    "provider": "groq",
    "model_name": settings.groq_default_model,
}

result = workflow.invoke(initial_state)

final_message = result["messages"][-1]
logger.info("Final message type: %s", type(final_message).__name__)
print("Module 4 check complete. Response:", extract_text(final_message.content))