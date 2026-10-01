# backend/app/memory/short_term.py

"""
Short-term (thread-scoped) memory.

Uses LangGraph's checkpointer to persist conversation state per thread_id,
so a client can send just the NEW message each turn, and the graph
automatically has access to everything said earlier in that thread.
"""

from functools import lru_cache

from langgraph.checkpoint.memory import InMemorySaver


@lru_cache
def get_checkpointer():
    """Returns a cached checkpointer instance (one per process).

    IMPORTANT: InMemorySaver stores everything in RAM. All conversation
    history is lost when the server restarts, and it won't work correctly
    across multiple server workers/instances. This is fine for development.
    Module 12 replaces this with a PostgreSQL-backed checkpointer so
    history survives restarts and works in a real multi-worker deployment.
    """
    return InMemorySaver()