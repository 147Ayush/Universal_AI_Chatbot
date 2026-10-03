# backend/app/graph/nodes.py

"""
Graph nodes.

A node is just a function: (state) -> partial state update.
Keep nodes focused on ONE responsibility each.
"""

import logging

from langchain_core.messages import ToolMessage
from langgraph.types import interrupt, Command

from app.graph.state import GraphState
from app.llm.factory import invoke_with_fallback
from app.mcp.tool_manager import get_all_tools

logger = logging.getLogger(__name__)


def call_llm(state: GraphState) -> dict:
    """Node: sends the current message history to the configured LLM.

    The LLM may respond with a tool call instead of (or before) a text
    answer — if it does, LangGraph routes to the "tools" node (directly,
    or via "human_approval" first for risky tools) next (see
    graph/edges.py and graph/workflow.py).

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


def human_approval(state: GraphState):
    """Node: pauses execution and asks a human to approve or reject
    pending tool calls flagged as requiring approval (e.g. web search).

    interrupt() pauses the graph HERE and persists state via the
    checkpointer. Execution resumes only when something external calls
    workflow.invoke(Command(resume=decision), config=same_thread_id).
    """
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []

    decision = interrupt(
        {
            "type": "tool_approval",
            "tool_calls": [
                {"name": tc["name"], "args": tc["args"]} for tc in tool_calls
            ],
        }
    )

    if decision.get("approved"):
        logger.info("Tool call(s) approved by human")
        return Command(goto="tools")

    logger.info("Tool call(s) rejected by human: %s", decision.get("reason"))
    reason = decision.get("reason")
    rejection_messages = [
        ToolMessage(
            content=(
                f"Tool call '{tc['name']}' was rejected by the user."
                + (f" Reason: {reason}" if reason else "")
            ),
            tool_call_id=tc["id"],
        )
        for tc in tool_calls
    ]
    return Command(goto="call_llm", update={"messages": rejection_messages})