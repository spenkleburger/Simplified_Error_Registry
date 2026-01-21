"""
Centralized configuration management using environment variables.

This module provides type-safe access to all environment variables
with proper type conversion and default values.

Usage:
    from config.settings import API_PORT, DATABASE_URL, DEBUG

    # Use settings throughout your code
    port = API_PORT  # Already an int, no conversion needed
    is_debug = DEBUG  # Already a bool
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# Application Configuration
# ============================================================================

ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "True").lower() == "true"
LOG_TO_CONSOLE: bool = os.getenv("LOG_TO_CONSOLE", "True").lower() == "true"
LOG_DIR: Path = Path(os.getenv("LOG_DIR", "./logs"))
LOG_FILE_MAX_SIZE: str = os.getenv("LOG_FILE_MAX_SIZE", "10MB")
LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", "30"))


# ============================================================================
# Debugging Configuration
# ============================================================================

VERBOSE: bool = os.getenv("VERBOSE", "False").lower() == "true"
SHOW_STACK_TRACE: bool = os.getenv("SHOW_STACK_TRACE", "True").lower() == "true"


# ============================================================================
# API Keys (Sensitive - Never commit to version control)
# ============================================================================

API_KEY: Optional[str] = os.getenv("API_KEY")
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")


# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/dbname"
)


# ============================================================================
# Paths
# ============================================================================

DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))


# ============================================================================
# Port Configuration
# ============================================================================

API_PORT: int = int(os.getenv("API_PORT", "8000"))
WEB_PORT: int = int(os.getenv("WEB_PORT", "3000"))
DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))


# ============================================================================
# Validation (Optional - Add as needed)
# ============================================================================


def validate_settings() -> None:
    """
    Validate that required settings are present and valid.

    Raises:
        ValueError: If required settings are missing or invalid
    """
    # Validate environment
    if ENVIRONMENT not in ["development", "staging", "production", "test"]:
        raise ValueError(
            f"ENVIRONMENT must be one of: development, staging, production, test. Got: {ENVIRONMENT}"
        )

    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if LOG_LEVEL not in valid_log_levels:
        raise ValueError(
            f"LOG_LEVEL must be one of: {valid_log_levels}. Got: {LOG_LEVEL}"
        )

    # Validate ports (must be in valid range)
    if not (1 <= API_PORT <= 65535):
        raise ValueError(f"API_PORT must be between 1 and 65535. Got: {API_PORT}")

    if not (1 <= WEB_PORT <= 65535):
        raise ValueError(f"WEB_PORT must be between 1 and 65535. Got: {WEB_PORT}")

    if not (1 <= DATABASE_PORT <= 65535):
        raise ValueError(
            f"DATABASE_PORT must be between 1 and 65535. Got: {DATABASE_PORT}"
        )

    # Create directories if they don't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    # Validate settings on import (optional)
    # validate_settings()

    # Print current settings (for debugging)
    print("Current Settings:")
    print(f"  Environment: {ENVIRONMENT}")
    print(f"  Debug: {DEBUG}")
    print(f"  API Port: {API_PORT}")
    print(f"  Web Port: {WEB_PORT}")
    print(f"  Database URL: {DATABASE_URL}")
    print(f"  Log Level: {LOG_LEVEL}")
    print(f"  Log Directory: {LOG_DIR}")
    print(f"  Data Directory: {DATA_DIR}")
