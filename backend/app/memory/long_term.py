# backend/app/memory/long_term.py

"""
Long-term memory: facts that persist ACROSS different conversation
threads, using LangGraph's Store.

Unlike the checkpointer (one conversation's history), a Store holds
data under a (namespace, key) addressing scheme — e.g. namespace
("user_facts", user_id), key "name" — so it's addressable by WHO the
fact is about, not which conversation it came from.

Like short_term.py, this is in-memory for now (lost on restart).
Module 12 swaps InMemoryStore for a Postgres-backed store.
"""

from functools import lru_cache

from langgraph.store.memory import InMemoryStore


@lru_cache
def get_store():
    """Returns a cached Store instance (one per process)."""
    return InMemoryStore()


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