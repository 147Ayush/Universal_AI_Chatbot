# backend/app/graph/workflow.py

"""
Builds and compiles the LangGraph workflow.

This is the ONLY place that should call StateGraph(...).compile().
Everything else (services, API) should import `get_workflow()` and
use the compiled graph — never rebuild it themselves.
"""

from functools import lru_cache

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.graph.state import GraphState
from app.graph.nodes import call_llm
from app.graph.edges import route_after_llm
from app.memory.short_term import get_checkpointer
from app.tools import ALL_TOOLS


def build_workflow():
    """Constructs the graph:

        START -> call_llm -> (route_after_llm) -> tools -> call_llm -> ... -> END
                                                 \-> END (if no tool call)

    Short-term memory is enabled via a checkpointer, so conversation
    history persists across calls that share the same thread_id.
    """
    builder = StateGraph(GraphState)

    builder.add_node("call_llm", call_llm)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    builder.add_edge(START, "call_llm")
    builder.add_conditional_edges("call_llm", route_after_llm)
    builder.add_edge("tools", "call_llm")  # after a tool runs, let the LLM see the result

    return builder.compile(checkpointer=get_checkpointer())


@lru_cache
def get_workflow():
    """Returns a cached compiled graph instance (built once per process)."""
    return build_workflow()