# backend/app/graph/nodes.py

"""
Graph nodes.

A node is just a function: (state) -> partial state update.
Keep nodes focused on ONE responsibility each — this one only calls
the LLM and returns its response as a new message.
"""

import logging

from app.graph.state import GraphState
from app.llm.factory import get_llm

logger = logging.getLogger(__name__)


def call_llm(state: GraphState) -> dict:
    """Node: sends the current message history to the configured LLM
    and returns its reply.

    LangGraph merges this return value into the graph state — since
    `messages` uses the `add_messages` reducer, returning one new
    message here APPENDS it to the history rather than replacing it.
    """
    provider = state["provider"]
    model_name = state["model_name"]

    logger.info("call_llm node: provider=%s model=%s", provider, model_name)

    llm = get_llm(provider=provider, model_name=model_name)
    response = llm.invoke(state["messages"])

    return {"messages": [response]}