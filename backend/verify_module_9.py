# backend/verify_module_9.py
# Temporary check: confirms MCP tools load and get used by the agent.

import asyncio
import logging

from langchain_core.messages import HumanMessage

from app.core.logging_config import setup_logging
from app.config.settings import get_settings
from app.mcp.tool_manager import load_mcp_tools
from app.graph.workflow import get_workflow
from app.llm.base import extract_text

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)


async def main():
    tools = await load_mcp_tools()
    print(f"Loaded {len(tools)} MCP tools:", [t.name for t in tools])

    workflow = get_workflow()

    result = workflow.invoke(
        {
            "messages": [HumanMessage(content="Add 482.5 and 913.25 using your math tool.")],
            "provider": "groq",
            "model_name": settings.groq_default_model,
        },
        config={"configurable": {"thread_id": "test-mcp-math"}},
    )
    for msg in result["messages"]:
        print(f"  [{type(msg).__name__}]", extract_text(msg.content)[:150])


asyncio.run(main())