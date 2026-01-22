"""
Shared fixtures and test configuration for pytest.

This file is automatically discovered by pytest and provides fixtures
that can be used across all test files.
"""

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_log_dir(temp_dir):
    """Create a temporary log directory for testing."""
    log_dir = temp_dir / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def sample_env_vars(monkeypatch):
    """Set sample environment variables for testing."""
    env_vars = {
        "ENVIRONMENT": "test",
        "DEBUG": "True",
        "LOG_LEVEL": "DEBUG",
        "API_PORT": "8080",
        "WEB_PORT": "3001",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables for testing."""
    # Remove common env vars that might interfere
    env_vars_to_remove = [
        "ENVIRONMENT",
        "DEBUG",
        "LOG_LEVEL",
        "API_PORT",
        "WEB_PORT",
        "DATABASE_PORT",
        "LOG_DIR",
        "DATA_DIR",
        "API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ]
    for var in env_vars_to_remove:
        monkeypatch.delenv(var, raising=False)
    # Mock load_dotenv to prevent .env file from being loaded during module reload
    # Mock both locations where load_dotenv might be called
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr("config.settings.load_dotenv", lambda: None)
    yield
    # Cleanup happens automatically when fixture goes out of scope
