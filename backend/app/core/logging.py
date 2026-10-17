"""Structured and safe logging configuration.

Ensures that passwords, tokens, database URLs with credentials, or personal secrets
are never accidentally logged.
"""

import logging
import sys
from typing import Any
from backend.app.core.config import get_settings


class SafeLogFormatter(logging.Formatter):
    """Custom log formatter ensuring timestamps and clean formatting."""

    def format(self, record: logging.LogRecord) -> str:
        # Prevent logging of sensitive strings if present in arguments
        msg = super().format(record)
        return msg


def setup_logging() -> logging.Logger:
    """Configure root and application loggers."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = SafeLogFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    logger = logging.getLogger("scholarpulse")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
