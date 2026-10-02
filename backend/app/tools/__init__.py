"""
Central registry of all tools available to the agent.
Import ALL_TOOLS wherever the graph needs to bind/execute tools.

"""
"""
Central registry of LOCAL tools available to the agent.
MCP tools are registered separately in app/mcp/tool_manager.py —
see get_all_tools() there for the combined local + MCP tool list.
"""

from app.tools.calculator import calculator
from app.tools.weather import get_weather
from app.tools.search import web_search

LOCAL_TOOLS = [calculator, get_weather, web_search]

from app.tools.calculator import calculator
from app.tools.weather import get_weather
from app.tools.search import web_search

ALL_TOOLS = [calculator, get_weather, web_search]