"""
Logging configuration for Tiresias
"""
import logging
import sys

from src.core.settings import get_settings


def setup_logging() -> None:
    """Configure application logging"""
    settings = get_settings()

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if settings.LOG_FORMAT == "json":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "name": "%(name)s", '
            '"level": "%(levelname)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
