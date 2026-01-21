"""
Tests for config.settings module.

These tests verify that settings are loaded correctly from environment
variables with proper type conversion and default values.
"""

from pathlib import Path

import pytest

from config import settings


class TestSettingsDefaults:
    """Test that settings have correct default values."""

    def test_environment_default(self, clean_env):
        """Test that ENVIRONMENT defaults to 'development'."""
        # Reload settings module to get defaults
        import importlib

        importlib.reload(settings)
        assert settings.ENVIRONMENT == "development"

    def test_debug_default(self, clean_env):
        """Test that DEBUG defaults to False."""
        import importlib

        importlib.reload(settings)
        assert settings.DEBUG is False

    def test_api_port_default(self, clean_env):
        """Test that API_PORT defaults to 8000."""
        import importlib

        importlib.reload(settings)
        assert settings.API_PORT == 8000
        assert isinstance(settings.API_PORT, int)

    def test_web_port_default(self, clean_env):
        """Test that WEB_PORT defaults to 3000."""
        import importlib

        importlib.reload(settings)
        assert settings.WEB_PORT == 3000
        assert isinstance(settings.WEB_PORT, int)

    def test_database_port_default(self, clean_env):
        """Test that DATABASE_PORT defaults to 5432."""
        import importlib

        importlib.reload(settings)
        assert settings.DATABASE_PORT == 5432
        assert isinstance(settings.DATABASE_PORT, int)

    def test_log_level_default(self, clean_env):
        """Test that LOG_LEVEL defaults to 'INFO'."""
        import importlib

        importlib.reload(settings)
        assert settings.LOG_LEVEL == "INFO"

    def test_log_dir_default(self, clean_env):
        """Test that LOG_DIR defaults to './logs'."""
        import importlib

        importlib.reload(settings)
        assert settings.LOG_DIR == Path("./logs")
        assert isinstance(settings.LOG_DIR, Path)

    def test_data_dir_default(self, clean_env):
        """Test that DATA_DIR defaults to './data'."""
        import importlib

        importlib.reload(settings)
        assert settings.DATA_DIR == Path("./data")
        assert isinstance(settings.DATA_DIR, Path)


class TestSettingsTypeConversion:
    """Test that settings convert types correctly."""

    def test_debug_bool_conversion(self, monkeypatch):
        """Test that DEBUG converts string to bool correctly."""
        # Arrange
        monkeypatch.setenv("DEBUG", "true")

        # Act
        import importlib

        importlib.reload(settings)

        # Assert
        assert settings.DEBUG is True
        assert isinstance(settings.DEBUG, bool)

    def test_debug_false_conversion(self, monkeypatch):
        """Test that DEBUG converts 'False' string to False."""
        # Arrange
        monkeypatch.setenv("DEBUG", "False")

        # Act
        import importlib

        importlib.reload(settings)

        # Assert
        assert settings.DEBUG is False

    def test_api_port_int_conversion(self, monkeypatch):
        """Test that API_PORT converts string to int."""
        # Arrange
        monkeypatch.setenv("API_PORT", "9000")

        # Act
        import importlib

        importlib.reload(settings)

        # Assert
        assert settings.API_PORT == 9000
        assert isinstance(settings.API_PORT, int)

    def test_log_dir_path_conversion(self, monkeypatch):
        """Test that LOG_DIR converts string to Path."""
        # Arrange
        monkeypatch.setenv("LOG_DIR", "/custom/logs")

        # Act
        import importlib

        importlib.reload(settings)

        # Assert
        assert settings.LOG_DIR == Path("/custom/logs")
        assert isinstance(settings.LOG_DIR, Path)


class TestSettingsValidation:
    """Test the validate_settings function."""

    def test_validate_settings_success(self, sample_env_vars):
        """Test that validate_settings passes with valid settings."""
        # Arrange
        import importlib

        importlib.reload(settings)

        # Act & Assert - should not raise
        settings.validate_settings()

    def test_validate_settings_invalid_environment(self, monkeypatch):
        """Test that validate_settings raises error for invalid environment."""
        # Arrange
        monkeypatch.setenv("ENVIRONMENT", "invalid")
        import importlib

        importlib.reload(settings)

        # Act & Assert
        with pytest.raises(ValueError, match="ENVIRONMENT must be one of"):
            settings.validate_settings()

    def test_validate_settings_invalid_log_level(self, monkeypatch):
        """Test that validate_settings raises error for invalid log level."""
        # Arrange
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        import importlib

        importlib.reload(settings)

        # Act & Assert
        with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
            settings.validate_settings()

    def test_validate_settings_invalid_port_too_low(self, monkeypatch):
        """Test that validate_settings raises error for port < 1."""
        # Arrange
        monkeypatch.setenv("API_PORT", "0")
        import importlib

        importlib.reload(settings)

        # Act & Assert
        with pytest.raises(ValueError, match="API_PORT must be between"):
            settings.validate_settings()

    def test_validate_settings_invalid_port_too_high(self, monkeypatch):
        """Test that validate_settings raises error for port > 65535."""
        # Arrange
        monkeypatch.setenv("API_PORT", "70000")
        import importlib

        importlib.reload(settings)

        # Act & Assert
        with pytest.raises(ValueError, match="API_PORT must be between"):
            settings.validate_settings()

    def test_validate_settings_creates_directories(self, temp_dir, monkeypatch):
        """Test that validate_settings creates required directories."""
        # Arrange
        log_dir = temp_dir / "logs"
        data_dir = temp_dir / "data"
        monkeypatch.setenv("LOG_DIR", str(log_dir))
        monkeypatch.setenv("DATA_DIR", str(data_dir))
        import importlib

        importlib.reload(settings)

        # Act
        settings.validate_settings()

        # Assert
        assert log_dir.exists()
        assert data_dir.exists()


class TestSettingsOptionalValues:
    """Test optional settings that can be None."""

    def test_api_key_optional(self, clean_env):
        """Test that API_KEY can be None if not set."""
        import importlib

        importlib.reload(settings)
        assert settings.API_KEY is None

    def test_api_key_set(self, monkeypatch):
        """Test that API_KEY is set when environment variable exists."""
        # Arrange
        monkeypatch.setenv("API_KEY", "test-key-123")

        # Act
        import importlib

        importlib.reload(settings)

        # Assert
        assert settings.API_KEY == "test-key-123"
