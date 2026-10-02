# backend/app/mcp/client.py

"""
MCP client configuration.

Defines how to reach each MCP server. All three run as local
subprocesses over stdio — launched automatically by the client when
tools are requested, no manual server startup needed.
"""

import os
from functools import lru_cache

from langchain_mcp_adapters.client import MultiServerMCPClient

# backend/app/mcp/client.py -> up 3 levels -> project root -> mcp_servers/
_MCP_SERVERS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "mcp_servers")
)


@lru_cache
def get_mcp_client() -> MultiServerMCPClient:
    """Returns a cached MCP client configured for all known servers."""
    return MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": [os.path.join(_MCP_SERVERS_DIR, "math_server.py")],
            },
            "weather": {
                "transport": "stdio",
                "command": "python",
                "args": [os.path.join(_MCP_SERVERS_DIR, "weather_server.py")],
            },
            "search": {
                "transport": "stdio",
                "command": "python",
                "args": [os.path.join(_MCP_SERVERS_DIR, "search_server.py")],
            },
        }
    )