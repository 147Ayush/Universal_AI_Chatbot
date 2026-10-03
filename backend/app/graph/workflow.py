# backend/app/graph/workflow.py

"""
Builds and compiles the LangGraph workflow.

This is the ONLY place that should call StateGraph(...).compile().
Everything else (services, API) should import `get_workflow()` and
use the compiled graph — never rebuild it themselves.
"""

from functools import lru_cache

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode

from app.graph.state import GraphState
from app.graph.nodes import call_llm, human_approval
from app.graph.edges import route_after_llm
from app.memory.short_term import get_checkpointer
from app.mcp.tool_manager import get_all_tools


def build_workflow():
    """Constructs the graph:

        START -> call_llm -> (route_after_llm) -> tools -> call_llm -> ... -> END
                                                 \-> human_approval -> tools (if approved)
                                                 \-> human_approval -> call_llm (if rejected)
                                                 \-> END (if no tool call)

    Short-term memory is enabled via a checkpointer, so conversation
    history persists across calls that share the same thread_id —
    this also powers human-in-the-loop: interrupt() inside human_approval
    pauses the graph, and the checkpointer lets it resume later.

    Tools include both local tools (calculator, weather, search) and
    any MCP tools loaded at app startup — see app/mcp/tool_manager.py.
    """
    builder = StateGraph(GraphState)

    builder.add_node("call_llm", call_llm)
    builder.add_node("tools", ToolNode(get_all_tools()))
    builder.add_node("human_approval", human_approval)

    builder.add_edge(START, "call_llm")
    builder.add_conditional_edges("call_llm", route_after_llm)
    builder.add_edge("tools", "call_llm")  # after a tool runs, let the LLM see the result
    # human_approval routes itself via Command(goto=...) — no add_edge needed

    return builder.compile(checkpointer=get_checkpointer())


@lru_cache
def get_workflow():
    """Returns a cached compiled graph instance (built once per process)."""
    return build_workflow()