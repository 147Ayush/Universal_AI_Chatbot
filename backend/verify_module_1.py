# backend/verify_module_1.py (temporary — delete after checking it works)

import logging

from app.config.settings import get_settings
from app.core.logging_config import setup_logging
from app.core.security import mask_secret
from app.core.exceptions import ProviderConfigurationError

settings = get_settings()
setup_logging(log_level=settings.log_level)

logger = logging.getLogger(__name__)

logger.info("App environment: %s", settings.app_env)
logger.info("OpenAI key (masked): %s", mask_secret(settings.openai_api_key))

# Confirm our custom exception works as expected
try:
    raise ProviderConfigurationError("Example: no provider configured", details={"provider": "openai"})
except ProviderConfigurationError as e:
    logger.error("Caught expected exception: %s | details=%s", e.message, e.details)

print("Module 1 check complete — see console output and logs/app.log")