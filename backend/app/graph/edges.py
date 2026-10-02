# backend/app/graph/edges.py

"""
Graph edges — conditional routing logic.

tools_condition (from langgraph.prebuilt) inspects the last message:
if it contains tool_calls, route to the "tools" node; otherwise, end.
We re-export it here so the rest of the project imports routing
logic from this file, not scattered prebuilt imports.
"""

from langgraph.prebuilt import tools_condition

route_after_llm = tools_condition