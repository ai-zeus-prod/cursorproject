"""
Logging utility for Investment Agent System
Uses loguru for better logging experience
"""

import sys
from loguru import logger
from pathlib import Path
from config.settings import settings


def setup_logger():
    """Configure loguru logger"""

    # Remove default handler
    logger.remove()

    # Console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # File handler
    log_path = Path(settings.LOG_FILE_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_path,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL
    )

    logger.info(f"Logger initialized - Level: {settings.LOG_LEVEL}")

    return logger


# Initialize logger on import
setup_logger()
