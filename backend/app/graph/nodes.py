# backend/app/graph/nodes.py

"""
Graph nodes.

A node is just a function: (state) -> partial state update.
Keep nodes focused on ONE responsibility each — this one calls the
LLM (with tools bound, retry, and fallback) and returns its response
as a new message.
"""

import logging

from app.graph.state import GraphState
from app.llm.factory import invoke_with_fallback
from app.mcp.tool_manager import get_all_tools

logger = logging.getLogger(__name__)


def call_llm(state: GraphState) -> dict:
    """Node: sends the current message history to the configured LLM.

    The LLM may respond with a tool call instead of (or before) a text
    answer — if it does, LangGraph routes to the "tools" node next
    (see graph/edges.py and graph/workflow.py).

    Automatically retries transient failures on the primary provider,
    and falls back to a different provider if it keeps failing — see
    llm/factory.py's invoke_with_fallback for the full logic.

    LangGraph merges this return value into the graph state — since
    `messages` uses the `add_messages` reducer, returning one new
    message here APPENDS it to the history rather than replacing it.
    """
    provider = state["provider"]
    model_name = state["model_name"]

    logger.info("call_llm node: provider=%s model=%s", provider, model_name)

    response = invoke_with_fallback(
        messages=state["messages"],
        primary_provider=provider,
        primary_model=model_name,
        tools=get_all_tools(),
    )

    return {"messages": [response]}