# backend/app/main.py

"""
FastAPI application entry point.

Responsibilities (and ONLY these):
- create the FastAPI app instance
- configure logging at startup
- register global exception handlers
- include API routers

No business logic belongs here — that lives in services/, graph/, etc.
"""

import logging

from fastapi import FastAPI

from app.config.settings import get_settings
from app.core.constants import APP_NAME, APP_VERSION
from app.core.logging_config import setup_logging
from app.core.exceptions import register_exception_handlers
from app.api import health, chat, feedback
from app.mcp.tool_manager import load_mcp_tools
from app.graph.workflow import get_workflow

# --- Startup: load settings, configure logging BEFORE anything else runs ---
settings = get_settings()
setup_logging(log_level=settings.log_level)

logger = logging.getLogger(__name__)

# --- Create the app ---
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="A production-oriented, multi-provider AI chatbot.",
)

# --- Global exception handling ---
register_exception_handlers(app)

# --- Routers ---
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(feedback.router)


@app.on_event("startup")
async def on_startup():
    logger.info("%s v%s starting up | env=%s", APP_NAME, APP_VERSION, settings.app_env)

    # Load MCP tools BEFORE the graph is built, so tool-calling has
    # access to them from the very first request. If any MCP server
    # fails to start, load_mcp_tools() logs it and continues with an
    # empty MCP tool set rather than crashing startup.
    await load_mcp_tools()

    # get_workflow() is cached (lru_cache) — calling it here forces the
    # graph to build NOW, with MCP tools already loaded, instead of on
    # the first incoming request (which could race with tool loading).
    get_workflow()


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("%s shutting down", APP_NAME)