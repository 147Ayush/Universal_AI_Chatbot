# backend/verify_module_8.py
# Temporary check: confirms tool-calling works end-to-end.

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

test_cases = [
    ("What is 84732 * 9123? Just give me the number, use your tool to be precise.", "calculator (forced)"),
    ("What's the weather in London right now?", "weather"),
    ("What is 2 + 2? Reply with just the digit, no tool needed.", "no tool (trivial math)"),
]

for message, label in test_cases:
    print(f"\n--- Testing: {label} ---")
    result = workflow.invoke(
        {
            "messages": [HumanMessage(content=message)],
            "provider": "groq",
            "model_name": settings.groq_default_model,
        },
        config={"configurable": {"thread_id": f"test-{label}"}},
    )
    for msg in result["messages"]:
        print(f"  [{type(msg).__name__}]", extract_text(msg.content)[:150])