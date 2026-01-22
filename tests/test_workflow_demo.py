"""Tests for workflow_demo module."""

import pytest

from src.workflow_demo import add_numbers, divide_numbers


def test_add_numbers():
    """Test add_numbers function."""
    assert add_numbers(2, 3) == 5
    assert add_numbers(0, 0) == 0
    assert add_numbers(-1, 1) == 0


def test_divide_numbers():
    """Test divide_numbers function."""
    assert divide_numbers(10, 2) == 5.0
    assert divide_numbers(9, 3) == 3.0


def test_divide_numbers_by_zero():
    """Test divide_numbers raises ZeroDivisionError when dividing by zero."""
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        divide_numbers(10, 0)


def test_intentional_failure_for_workflow_testing():
    """Intentional test failure for Phase 2.5 workflow testing.
    
    This test is designed to fail so we can test the error resolution workflow.
    """
    # Fixed: corrected expected value from 6 to 5
    result = add_numbers(2, 3)
    assert result == 5, f"Expected 5, but got {result}"  # Fixed: corrected expected value
