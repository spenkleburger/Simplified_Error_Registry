"""
Example tests demonstrating testing patterns and best practices.

These tests serve as examples for writing tests in your project.
They demonstrate common patterns like fixtures, parametrization, and mocking.
"""

import os

import pytest

# ============================================================================
# Basic Test Structure (AAA Pattern)
# ============================================================================


def test_basic_assertion():
    """Simple test demonstrating basic assertion."""
    # Arrange: Set up test data
    expected = 2

    # Act: Execute the code being tested
    result = 1 + 1

    # Assert: Verify the result
    assert result == expected


def test_string_operations():
    """Test demonstrating string operations."""
    # Arrange
    text = "Hello, World!"

    # Act
    upper_text = text.upper()
    lower_text = text.lower()

    # Assert
    assert upper_text == "HELLO, WORLD!"
    assert lower_text == "hello, world!"


# ============================================================================
# Parametrized Tests (Testing Multiple Cases)
# ============================================================================


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (2, 4),
        (3, 9),
        (4, 16),
        (5, 25),
        (0, 0),
        (-2, 4),  # Negative numbers
    ],
)
def test_square_function(input_value, expected):
    """Test square function with multiple inputs."""
    # Arrange & Act
    result = input_value * input_value

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (10, -5, 5),
    ],
)
def test_addition(a, b, expected):
    """Test addition with multiple test cases."""
    # Arrange & Act
    result = a + b

    # Assert
    assert result == expected


# ============================================================================
# Using Fixtures
# ============================================================================


def test_using_temp_dir_fixture(temp_dir):
    """Test demonstrating use of temp_dir fixture."""
    # Arrange
    test_file = temp_dir / "test.txt"

    # Act
    test_file.write_text("Hello, World!")

    # Assert
    assert test_file.exists()
    assert test_file.read_text() == "Hello, World!"


def test_using_sample_env_vars(sample_env_vars):
    """Test demonstrating use of sample_env_vars fixture."""
    # Arrange & Act
    # Fixture sets environment variables

    # Assert
    assert os.getenv("ENVIRONMENT") == "test"
    assert os.getenv("DEBUG") == "True"
    assert os.getenv("API_PORT") == "8080"


# ============================================================================
# Test Markers (Categorizing Tests)
# ============================================================================


@pytest.mark.unit
def test_unit_example():
    """Example unit test (fast, isolated)."""
    # Unit tests test individual functions/classes
    result = 2 + 2
    assert result == 4


@pytest.mark.slow
def test_slow_example():
    """Example slow test (can be skipped with -m 'not slow')."""
    # Slow tests might do expensive operations
    # In real tests, this might be a database query, API call, etc.
    import time

    time.sleep(0.1)  # Simulate slow operation
    assert True


@pytest.mark.integration
def test_integration_example():
    """Example integration test (tests components working together)."""
    # Integration tests test how multiple components work together
    # This is a simple example - real integration tests would test
    # actual integration between components
    data = {"key": "value"}
    processed = str(data)  # Simulate processing
    assert "key" in processed


# ============================================================================
# Testing Exceptions
# ============================================================================


def test_division_by_zero():
    """Test that division by zero raises ZeroDivisionError."""
    # Arrange
    numerator = 10
    denominator = 0

    # Act & Assert
    with pytest.raises(ZeroDivisionError):
        _ = numerator / denominator


def test_index_error():
    """Test that accessing invalid index raises IndexError."""
    # Arrange
    my_list = [1, 2, 3]

    # Act & Assert
    with pytest.raises(IndexError):
        _ = my_list[10]


# ============================================================================
# Testing with Mocking (Example Structure)
# ============================================================================


def test_mocking_example(monkeypatch):
    """Example of using monkeypatch to mock functions."""

    # Arrange
    def mock_getenv(key, default=None):
        """Mock os.getenv."""
        return "mocked_value"

    # Act
    monkeypatch.setattr("os.getenv", mock_getenv)

    # Assert
    import os

    assert os.getenv("ANY_KEY") == "mocked_value"


# ============================================================================
# Testing Lists and Collections
# ============================================================================


def test_list_operations():
    """Test list operations."""
    # Arrange
    my_list = [1, 2, 3]

    # Act
    my_list.append(4)
    my_list.remove(2)

    # Assert
    assert my_list == [1, 3, 4]
    assert len(my_list) == 3


def test_dictionary_operations():
    """Test dictionary operations."""
    # Arrange
    my_dict = {"a": 1, "b": 2}

    # Act
    my_dict["c"] = 3
    value = my_dict.get("a")

    # Assert
    assert "c" in my_dict
    assert my_dict["c"] == 3
    assert value == 1


# ============================================================================
# Testing with Context Managers
# ============================================================================


def test_file_operations(temp_dir):
    """Test file operations using context manager pattern."""
    # Arrange
    test_file = temp_dir / "test.txt"

    # Act
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Test content")

    # Assert
    assert test_file.exists()
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "Test content"


# ============================================================================
# Test Organization Example
# ============================================================================


class TestCalculator:
    """Example of organizing tests in a class."""

    def test_add(self):
        """Test addition."""
        assert 2 + 2 == 4

    def test_subtract(self):
        """Test subtraction."""
        assert 5 - 3 == 2

    def test_multiply(self):
        """Test multiplication."""
        assert 3 * 4 == 12

    def test_divide(self):
        """Test division."""
        assert 10 / 2 == 5
