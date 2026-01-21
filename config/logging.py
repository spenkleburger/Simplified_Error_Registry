"""
Standardized logging configuration using environment variables.

This module provides a reusable logging setup that can be used across projects.
It reads configuration from .env file and provides sensible defaults.

Features:
- Console and file logging
- Automatic log rotation (prevents log files from growing too large)
- Configurable log levels
- UTF-8 encoding
- Environment variable integration
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default log rotation settings
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5  # Keep 5 backup files


def setup_logging(
    log_level: str = None,
    log_dir: Path = None,
    log_file: str = None,
    log_to_file: bool = None,
    log_to_console: bool = None,
    max_bytes: int = None,
    backup_count: int = None,
) -> logging.Logger:
    """
    Set up standardized logging configuration using environment variables.

    This function configures logging with both console and file handlers.
    File logging uses RotatingFileHandler to automatically rotate log files
    when they reach the specified size limit, preventing log files from
    growing indefinitely.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Defaults to LOG_LEVEL from .env, or "INFO"
        log_dir: Directory to store log files
                Defaults to LOG_DIR from .env, or "./logs"
        log_file: Optional log file name (defaults to YYYY-MM-DD.log)
        log_to_file: Enable/disable file logging
                    Defaults to LOG_TO_FILE from .env, or True
        log_to_console: Enable/disable console logging
                      Defaults to LOG_TO_CONSOLE from .env, or True
        max_bytes: Maximum log file size in bytes before rotation
                  Defaults to LOG_FILE_MAX_SIZE from .env, or 10MB
        backup_count: Number of backup log files to keep
                    Defaults to LOG_BACKUP_COUNT from .env, or 5

    Returns:
        Configured logger instance

    Example:
        >>> from config.logging import setup_logging
        >>> logger = setup_logging()  # Uses .env variables automatically
        >>> logger.info("Application started")
    """
    # Get values from environment or use defaults
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
        # Override if DEBUG is True
        if os.getenv("DEBUG", "False").lower() == "true":
            log_level = "DEBUG"

    if log_dir is None:
        log_dir = Path(os.getenv("LOG_DIR", "./logs"))

    if log_to_file is None:
        log_to_file = os.getenv("LOG_TO_FILE", "True").lower() == "true"

    if log_to_console is None:
        log_to_console = os.getenv("LOG_TO_CONSOLE", "True").lower() == "true"

    # Parse log file max size from environment (supports formats like "10MB", "500KB")
    if max_bytes is None:
        max_size_str = os.getenv("LOG_FILE_MAX_SIZE", "10MB")
        max_bytes = _parse_size(max_size_str)

    # Parse backup count from environment
    if backup_count is None:
        backup_count = int(os.getenv("LOG_BACKUP_COUNT", str(DEFAULT_BACKUP_COUNT)))

    log_dir.mkdir(exist_ok=True)

    if log_file is None:
        log_file = f"{datetime.now().strftime('%Y-%m-%d')}.log"

    log_path = log_dir / log_file

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Clear existing handlers

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_to_file:
        # Use RotatingFileHandler for automatic log rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def _parse_size(size_str: str) -> int:
    """
    Parse size string (e.g., "10MB", "500KB") to bytes.

    Args:
        size_str: Size string with unit (e.g., "10MB", "500KB", "1GB")

    Returns:
        Size in bytes

    Example:
        >>> _parse_size("10MB")
        10485760
        >>> _parse_size("500KB")
        512000
    """
    size_str = size_str.strip().upper()
    multipliers = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}

    for unit, multiplier in multipliers.items():
        if size_str.endswith(unit):
            number = float(size_str[: -len(unit)])
            return int(number * multiplier)

    # If no unit, assume bytes
    return int(size_str)


# Usage example:
# from config.logging import setup_logging
# logger = setup_logging()  # Uses .env variables automatically
# logger.info("Application started")
