# backend/app/graph/state.py

"""
Graph state definition.

State is the shared object passed between every node in the graph.
We extend LangGraph's built-in MessagesState, which already gives us
a `messages` list with the correct merge behavior (new messages are
appended, not overwritten) via the `add_messages` reducer.

We add a couple of extra fields we'll need once routing (Module 8+)
and multi-provider selection come into play.
"""

from langgraph.graph import MessagesState


class GraphState(MessagesState):
    """Shared state for the chatbot graph.

    Inherited from MessagesState:
        messages: list[AnyMessage]  -- the conversation so far

    Added here:
        provider: which LLM provider to use for this run
        model_name: which model to use for this run
    """
    provider: str
    model_name: str