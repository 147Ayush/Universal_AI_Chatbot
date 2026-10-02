# backend/app/tools/weather.py

"""
Weather tool — current conditions for a location.

Uses wttr.in, a free weather API that requires no API key.
"""

import httpx
from langchain_core.tools import tool


@tool
def get_weather(location: str) -> str:
    """Gets the current weather for a given city or location.

    Args:
        location: city name, e.g. "London" or "New York"

    Returns:
        A short text description of current conditions.
    """
    try:
        response = httpx.get(
            f"https://wttr.in/{location}",
            params={"format": "3"},  # compact one-line format
            timeout=10,
        )
        response.raise_for_status()
        return response.text.strip()
    except httpx.HTTPError as e:
        return f"Could not retrieve weather for '{location}': {e}"