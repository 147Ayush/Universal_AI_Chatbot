# backend/verify_module_7b.py
# Temporary check: confirms long-term (cross-thread, per-user) memory works.

from app.memory.manager import remember_fact, get_user_context

# Save a couple of facts about a user
remember_fact("ayush", "name", "Ayush")
remember_fact("ayush", "favorite_language", "Python")

# Retrieve them back
context = get_user_context("ayush")
print("Context for 'ayush':")
print(context)

# A different user should have no facts
empty_context = get_user_context("someone_else")
print("\nContext for 'someone_else':", repr(empty_context))