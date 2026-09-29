# backend/app/graph/workflow.py

"""
Builds and compiles the LangGraph workflow.

This is the ONLY place that should call StateGraph(...).compile().
Everything else (services, API) should import `get_workflow()` and
use the compiled graph — never rebuild it themselves.
"""

from functools import lru_cache

from langgraph.graph import StateGraph, START, END

from app.graph.state import GraphState
from app.graph.nodes import call_llm


def build_workflow():
    """Constructs the graph: START -> call_llm -> END."""
    builder = StateGraph(GraphState)

    builder.add_node("call_llm", call_llm)

    builder.add_edge(START, "call_llm")
    builder.add_edge("call_llm", END)

    return builder.compile()


@lru_cache
def get_workflow():
    """Returns a cached compiled graph instance (built once per process)."""
    return build_workflow()