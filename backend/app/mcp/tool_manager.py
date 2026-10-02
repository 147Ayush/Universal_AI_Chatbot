# backend/app/mcp/tool_manager.py

"""
MCP tool discovery and registration.

MCP tool loading is async (it has to start each server subprocess and
query its capabilities), but the graph is built once and reused — so
we load MCP tools ONCE at app startup and cache them here, rather than
reconnecting to MCP servers on every request.
"""

import logging

from app.mcp.client import get_mcp_client
from app.tools import LOCAL_TOOLS

logger = logging.getLogger(__name__)

_mcp_tools_cache: list = []


async def load_mcp_tools() -> list:
    """Connects to all configured MCP servers and loads their tools.

    Call this once, during app startup. If any server fails to start
    or respond, we log the error and continue with an empty MCP tool
    set — a down MCP server shouldn't prevent the whole app from
    starting (local tools still work fine on their own).
    """
    global _mcp_tools_cache
    client = get_mcp_client()
    try:
        _mcp_tools_cache = await client.get_tools()
        logger.info(
            "Loaded %d MCP tools: %s",
            len(_mcp_tools_cache),
            [t.name for t in _mcp_tools_cache],
        )
    except Exception as e:
        logger.error("Failed to load MCP tools: %s", e)
        _mcp_tools_cache = []
    return _mcp_tools_cache


def get_mcp_tools() -> list:
    """Returns the cached MCP tools. load_mcp_tools() must have been
    called first (e.g. during app startup) for this to return anything."""
    return _mcp_tools_cache


def get_all_tools() -> list:
    """Returns every tool available to the agent: local + MCP."""
    return LOCAL_TOOLS + get_mcp_tools()