# backend/app/memory/short_term.py

"""
Short-term (thread-scoped) memory.

Uses a Postgres-backed checkpointer when DATABASE_URL is configured
(persists across restarts, works with multiple workers). Falls back to
in-memory if no database is configured, so the app still runs without
Postgres during quick local testing.

The real Postgres checkpointer instance is created once in main.py's
lifespan (it needs an open async connection for the app's whole
lifetime) and registered here via set_checkpointer().
"""

from langgraph.checkpoint.memory import InMemorySaver

_checkpointer = None


def set_checkpointer(checkpointer) -> None:
    """Called once from main.py's lifespan after the real (Postgres)
    checkpointer is opened."""
    global _checkpointer
    _checkpointer = checkpointer


def get_checkpointer():
    """Returns the active checkpointer. Falls back to an in-memory one
    (lazily created, lost on restart) if none was registered — e.g. when
    DATABASE_URL isn't configured, or in a script run outside the app's
    lifespan (like a verify_*.py test script)."""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = InMemorySaver()
    return _checkpointer
