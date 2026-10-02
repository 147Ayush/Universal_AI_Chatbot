# backend/app/memory/manager.py

"""
Memory manager — coordinates short-term (thread) and long-term
(cross-thread, per-user) memory so the rest of the app has one
place to go for "what do we remember?"
"""

from app.memory.long_term import get_all_facts, save_fact, get_fact


def get_user_context(user_id: str) -> str:
    """Builds a short text summary of known long-term facts about a user,
    suitable for injecting into a system/context message.

    Returns an empty string if nothing is known yet.
    """
    facts = get_all_facts(user_id)
    if not facts:
        return ""

    lines = [f"{key}: {value}" for key, value in facts.items()]
    return "Known facts about this user:\n" + "\n".join(lines)


def remember_fact(user_id: str, key: str, value: str) -> None:
    """Stores a new long-term fact about a user."""
    save_fact(user_id, key, value)