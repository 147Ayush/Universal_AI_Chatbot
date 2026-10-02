# backend/app/tools/__init__.py

"""
Central registry of all tools available to the agent.
Import ALL_TOOLS wherever the graph needs to bind/execute tools.
"""

from app.tools.calculator import calculator
from app.tools.weather import get_weather
from app.tools.search import web_search

ALL_TOOLS = [calculator, get_weather, web_search]