# backend/app/tools/search.py

"""
Web search tool — uses DuckDuckGo (no API key required).
"""

from langchain_core.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """Searches the web for current information on a topic.

    Args:
        query: what to search for

    Returns:
        A short summary of the top results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No results found."

        formatted = []
        for r in results:
            formatted.append(f"- {r['title']}: {r['body']}")
        return "\n".join(formatted)
    except Exception as e:
        return f"Search failed: {e}"