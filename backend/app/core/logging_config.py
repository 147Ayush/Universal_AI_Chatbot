"""
Centralized logging configuration.

Call setup_logging() once, early in main.py. After that, every module
just does:

    import logging
    logger = logging.getLogger(__name__)

and logs will be formatted/routed consistently everywhere.
"""

import logging
import sys
from pathlib import Path

from app.core.constants import LOG_FORMAT, LOG_DATE_FORMAT

def setup_logging(log_level : str = "INFO", log_dir: str = "logs") -> None:
    """Configure root logging: console + rotating file output.

    Args:
        log_level: e.g. "DEBUG", "INFO", "WARNING", "ERROR"
        log_dir: folder where log files are written
    """
    Path(log_dir).mkdir(parent=True, exist_ok=True)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt = LOG_DATE_FORMAT)

    # Console handler — what you see while developing
    console_handler = logging.StreamHanlder(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler — persists logs for later debugging
    file_handler = logging.FileHandler(f"{log_dir}/app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Avoid duplicate handlers if setup_logging() is called more than once
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Quiet down noisy third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)









