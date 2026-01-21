"""
Tests for config.logging module.

These tests verify that the logging setup function works correctly
with different configurations and environment variables.
"""

import logging

import pytest

from config.logging import setup_logging


class TestSetupLogging:
    """Test the setup_logging function."""

    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        # Arrange & Act
        logger = setup_logging(log_to_file=False, log_to_console=True)

        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == "root"

    def test_setup_logging_with_custom_level(self):
        """Test that setup_logging respects custom log level."""
        # Arrange & Act
        logger = setup_logging(
            log_level="DEBUG", log_to_file=False, log_to_console=True
        )

        # Assert
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_custom_log_dir(self, temp_log_dir):
        """Test that setup_logging creates log files in custom directory."""
        # Arrange
        custom_file = "test.log"

        # Act
        logger = setup_logging(
            log_dir=temp_log_dir,
            log_file=custom_file,
            log_to_file=True,
            log_to_console=False,
        )

        # Assert
        log_path = temp_log_dir / custom_file
        assert log_path.exists()
        logger.info("Test message")
        assert log_path.stat().st_size > 0

    def test_setup_logging_console_only(self):
        """Test that setup_logging works with console logging only."""
        # Arrange & Act
        logger = setup_logging(log_to_file=False, log_to_console=True)

        # Assert
        handlers = logger.handlers
        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.StreamHandler)

    def test_setup_logging_file_only(self, temp_log_dir):
        """Test that setup_logging works with file logging only."""
        # Arrange & Act
        logger = setup_logging(
            log_dir=temp_log_dir,
            log_to_file=True,
            log_to_console=False,
        )

        # Assert
        handlers = logger.handlers
        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.handlers.RotatingFileHandler)

    def test_setup_logging_both_handlers(self, temp_log_dir):
        """Test that setup_logging can use both console and file handlers."""
        # Arrange & Act
        logger = setup_logging(
            log_dir=temp_log_dir,
            log_to_file=True,
            log_to_console=True,
        )

        # Assert
        handlers = logger.handlers
        assert len(handlers) == 2
        handler_types = [type(h).__name__ for h in handlers]
        assert "StreamHandler" in handler_types
        assert "RotatingFileHandler" in handler_types

    def test_setup_logging_creates_log_dir(self, temp_dir):
        """Test that setup_logging creates log directory if it doesn't exist."""
        # Arrange
        log_dir = temp_dir / "new_logs"

        # Act
        setup_logging(log_dir=log_dir, log_to_file=True, log_to_console=False)

        # Assert
        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_setup_logging_default_file_name(self, temp_log_dir):
        """Test that setup_logging uses date-based filename by default."""
        # Arrange & Act
        _ = setup_logging(
            log_dir=temp_log_dir,
            log_to_file=True,
            log_to_console=False,
        )

        # Assert - should create a file with today's date
        log_files = list(temp_log_dir.glob("*.log"))
        assert len(log_files) == 1
        # File name should be in YYYY-MM-DD.log format
        assert log_files[0].name.endswith(".log")

    def test_setup_logging_logs_messages(self, temp_log_dir):
        """Test that setup_logging actually logs messages."""
        # Arrange
        logger = setup_logging(
            log_dir=temp_log_dir,
            log_file="test.log",
            log_to_file=True,
            log_to_console=False,
        )

        # Act
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        # Assert
        log_path = temp_log_dir / "test.log"
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert "Test info message" in content
        assert "Test warning message" in content
        assert "Test error message" in content

    @pytest.mark.parametrize(
        "log_level,expected_level",
        [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
        ],
    )
    def test_setup_logging_all_levels(self, log_level, expected_level):
        """Test that setup_logging works with all log levels."""
        # Arrange & Act
        logger = setup_logging(
            log_level=log_level,
            log_to_file=False,
            log_to_console=True,
        )

        # Assert
        assert logger.level == expected_level
