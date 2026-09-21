"""
Health check endpoint.

Used by load balancers, Docker/K8s healthchecks, and uptime monitoring
to confirm the service is alive. Keep this fast and dependency-free —
it should not call the database or any LLM provider.
"""

from fastapi import APIRouter

from app.core.constants import APP_NAME, APP_VERSION
from app.config.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Basic liveness check — confirms the API process is up."""
    settings = get_settings()
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
        "environment": settings.app_env,
    }