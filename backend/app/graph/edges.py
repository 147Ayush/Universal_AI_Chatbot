# backend/app/graph/edges.py

"""
Graph edges — conditional routing logic.

route_after_llm decides what happens after the LLM responds:
- no tool calls -> END (just answer normally)
- tool calls, all low-risk -> "tools" (run immediately)
- tool calls including a risky one -> "human_approval" (pause for review)
"""

from langgraph.graph import END

from app.core.constants import TOOLS_REQUIRING_APPROVAL


def route_after_llm(state):
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []

    if not tool_calls:
        return END

    if any(tc["name"] in TOOLS_REQUIRING_APPROVAL for tc in tool_calls):
        return "human_approval"

    return "tools"