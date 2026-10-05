# backend/app/main.py

"""
FastAPI application entry point.

Responsibilities (and ONLY these):
- create the FastAPI app instance
- configure logging + CORS
- manage startup/shutdown lifecycle (MCP tools, Postgres connections)
- register global exception handlers
- include API routers

No business logic belongs here — that lives in services/, graph/, etc.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.core.constants import APP_NAME, APP_VERSION
from app.core.logging_config import setup_logging
from app.core.exceptions import register_exception_handlers
from app.api import health, chat, feedback, conversations
from app.mcp.tool_manager import load_mcp_tools
from app.graph.workflow import get_workflow
from app.memory.short_term import set_checkpointer
from app.memory.long_term import set_store

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages startup/shutdown. Replaces the older @app.on_event pattern —
    needed here because the Postgres checkpointer/store must stay open as
    a live async context manager for the whole app lifetime."""
    logger.info("%s v%s starting up | env=%s", APP_NAME, APP_VERSION, settings.app_env)

    # Load MCP tools BEFORE the graph is built, so tool-calling has
    # access to them from the very first request. If any MCP server
    # fails to start, load_mcp_tools() logs it and continues with an
    # empty MCP tool set rather than crashing startup.
    await load_mcp_tools()

    if settings.database_url:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from langgraph.store.postgres.aio import AsyncPostgresStore

        async with (
            AsyncPostgresSaver.from_conn_string(settings.database_url) as checkpointer,
            AsyncPostgresStore.from_conn_string(settings.database_url) as store,
        ):
            await checkpointer.setup()
            await store.setup()
            set_checkpointer(checkpointer)
            set_store(store)

            # get_workflow() is cached (lru_cache) — calling it here forces
            # the graph to build NOW, with Postgres + MCP tools already
            # loaded, instead of on the first incoming request.
            get_workflow()
            logger.info("Using PostgreSQL for short-term and long-term memory")
            yield
    else:
        logger.warning(
            "DATABASE_URL not set — using in-memory storage "
            "(conversation history will NOT persist across restarts)"
        )
        get_workflow()
        yield

    logger.info("%s shutting down", APP_NAME)


# --- Create the app ---
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="A production-oriented, multi-provider AI chatbot.",
    lifespan=lifespan,
)

# --- CORS: allow the Vite dev server (and other local dev origins) to call this API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global exception handling ---
register_exception_handlers(app)

# --- Routers ---
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(conversations.router)
