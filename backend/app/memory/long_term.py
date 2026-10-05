# backend/app/memory/long_term.py

"""
Long-term memory: facts that persist ACROSS different conversation
threads, using LangGraph's Store.

Unlike the checkpointer (one conversation's history), a Store holds
data under a (namespace, key) addressing scheme — e.g. namespace
("user_facts", user_id), key "name" — so it's addressable by WHO the
fact is about, not which conversation it came from.

Uses a Postgres-backed store when DATABASE_URL is configured; falls
back to in-memory otherwise. The real instance is created once in
main.py's lifespan and registered via set_store().
"""

from langgraph.store.memory import InMemoryStore

_store = None


def set_store(store) -> None:
    """Called once from main.py's lifespan after the real (Postgres)
    store is opened."""
    global _store
    _store = store


def get_store():
    """Returns the active store. Falls back to an in-memory one
    (lazily created, lost on restart) if none was registered."""
    global _store
    if _store is None:
        _store = InMemoryStore()
    return _store


def save_fact(user_id: str, key: str, value: str) -> None:
    """Saves one fact about a user, e.g. save_fact('ayush', 'name', 'Ayush')."""
    store = get_store()
    store.put(("user_facts", user_id), key, {"value": value})


def get_fact(user_id: str, key: str) -> str | None:
    """Retrieves one fact about a user, or None if not set."""
    store = get_store()
    item = store.get(("user_facts", user_id), key)
    return item.value["value"] if item else None


def get_all_facts(user_id: str) -> dict[str, str]:
    """Retrieves every known fact about a user as a flat dict."""
    store = get_store()
    items = store.search(("user_facts", user_id))
    return {item.key: item.value["value"] for item in items}
