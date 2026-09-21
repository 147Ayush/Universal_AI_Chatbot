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
from app.api import health

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


@app.on_event("startup")
async def on_startup():
    logger.info("%s v%s starting up | env=%s", APP_NAME, APP_VERSION, settings.app_env)


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("%s shutting down", APP_NAME)