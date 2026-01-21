"""
Custom exceptions for project-specific error handling.

This module provides a hierarchy of custom exceptions that can be used
throughout the project for consistent error handling. All custom exceptions
inherit from ProjectBaseException, allowing for easy exception catching
at different levels of specificity.

Usage:
    from config.exceptions import ConfigurationError, DataProcessingError

    try:
        if not config_valid:
            raise ConfigurationError("Invalid configuration", {"key": "value"})
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e.message}", extra=e.details)
"""


class ProjectBaseException(Exception):
    """
    Base exception for all project-specific errors.

    This base class provides a consistent structure for all custom exceptions,
    allowing for both error messages and additional context/details.

    Args:
        message: Human-readable error message
        details: Optional dictionary with additional error context

    Example:
        >>> raise ProjectBaseException("Something went wrong", {"user_id": 123})
        ProjectBaseException: Something went wrong
    """

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ConfigurationError(ProjectBaseException):
    """
    Raised when configuration is invalid, missing, or cannot be loaded.

    Use this exception when:
    - Required configuration values are missing
    - Configuration values are invalid (e.g., wrong type, out of range)
    - Configuration files cannot be read or parsed

    Example:
        >>> if not os.path.exists(config_file):
        ...     raise ConfigurationError("Config file not found", {"path": config_file})
    """

    pass


class ValidationError(ProjectBaseException):
    """
    Raised when data validation fails.

    Use this exception when:
    - Input data doesn't meet required format or constraints
    - Data type conversion fails
    - Business rule validation fails

    Example:
        >>> if not email_valid(email):
        ...     raise ValidationError("Invalid email format", {"email": email})
    """

    pass


class DataProcessingError(ProjectBaseException):
    """
    Raised when data processing operations fail.

    Use this exception when:
    - Data transformation fails
    - Data parsing fails
    - Data aggregation or calculation fails

    Example:
        >>> try:
        ...     result = process_data(data)
        ... except Exception as e:
        ...     raise DataProcessingError("Failed to process data", {"error": str(e)})
    """

    pass


class APIError(ProjectBaseException):
    """
    Raised when API operations fail.

    Use this exception when:
    - HTTP requests fail
    - API responses are invalid
    - API rate limits are exceeded
    - API authentication fails

    Example:
        >>> if response.status_code != 200:
        ...     raise APIError("API request failed", {"status": response.status_code})
    """

    pass


class DatabaseError(ProjectBaseException):
    """
    Raised when database operations fail.

    Use this exception when:
    - Database connections fail
    - SQL queries fail
    - Database transactions fail
    - Database constraints are violated

    Example:
        >>> try:
        ...     cursor.execute(query)
        ... except psycopg2.Error as e:
        ...     raise DatabaseError("Database operation failed", {"query": query})
    """

    pass


class FileOperationError(ProjectBaseException):
    """
    Raised when file operations fail.

    Use this exception when:
    - Files cannot be read or written
    - File permissions are insufficient
    - File paths are invalid
    - File operations timeout

    Example:
        >>> if not os.access(file_path, os.R_OK):
        ...     raise FileOperationError("Cannot read file", {"path": file_path})
    """

    pass
