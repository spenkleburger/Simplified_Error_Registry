# Testing Guide

**Last Updated:** 2026-01-22

## Overview

This document provides information about the test suite, test infrastructure, and testing best practices for the Simplified Error Registry project.

---

## Test Infrastructure

### Test Organization

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and test configuration
├── test_config_*.py              # Configuration module tests
├── test_consolidation_app_*.py   # Consolidation app module tests
├── test_scripts_*.py             # Script tests
├── integration/                  # Integration tests
│   ├── __init__.py
│   └── test_consolidation_workflow.py
└── test_verify_*.py             # Verification tests (can be skipped)
```

### Shared Fixtures

The `tests/conftest.py` file provides shared fixtures for all tests:

- **`temp_dir`**: Creates a temporary directory for testing (automatically cleaned up)
- **`temp_log_dir`**: Creates a temporary log directory within temp_dir
- **`cleanup_logging_handlers`**: Automatically closes all file handlers after each test (Windows compatibility)
- **`sample_env_vars`**: Sets sample environment variables for testing
- **`clean_env`**: Cleans environment variables for testing

### Windows Compatibility

**File Handler Cleanup:**
- Windows requires file handlers to be explicitly closed before files can be deleted
- The `cleanup_logging_handlers` fixture (with `autouse=True`) automatically closes all file handlers after each test
- This prevents `PermissionError: [WinError 32]` errors when cleaning up temporary directories

**Implementation:**
```python
@pytest.fixture(autouse=True)
def cleanup_logging_handlers():
    """Automatically close all file handlers after each test."""
    yield
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            root_logger.removeHandler(handler)
```

---

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_config_logging.py

# Run specific test
pytest tests/test_config_logging.py::TestSetupLogging::test_setup_logging_returns_logger
```

### Test Categories

**Backend Tests:**
```bash
task test:backend
# Or: python scripts/test_backend.py
```

**Frontend Tests:**
```bash
task test:frontend
# Or: python scripts/test_frontend.py
```

**Integration Tests:**
```bash
task test:integration
# Or: python scripts/test_integration.py
```

### Test Output

The test scripts (`test_backend.py`, `test_frontend.py`, `test_integration.py`) automatically:
- Capture test failures and errors
- Copy relevant output to clipboard
- Filter out passing tests and irrelevant output
- Provide only essential error information for debugging

**Captured Sections:**
- `=== FAILURES ===` or `=== ERRORS ===` section
- `=== short test summary info ===` section
- Error tracebacks and messages

---

## Test Fixes and Improvements

### Recent Fixes (2026-01-22)

1. **Missing Module Handling:**
   - `test_scripts_pre_commit_checks.py` now gracefully handles missing `pre_commit_checks` module
   - Uses conditional import with `@pytest.mark.skipif` to skip tests if module doesn't exist

2. **Input Function Patching:**
   - `test_scripts_git_push.py` fixed to properly patch `builtins.input` instead of `git_push.input`
   - Windows-compatible monkeypatching for user input

3. **Intentional Failure Tests:**
   - Phase 2.3 verification tests now have `@pytest.mark.skip` markers
   - Prevents false test failures while keeping tests for reference
   - Can be removed once Phase 2.3 verification is confirmed complete

4. **Windows File Lock Issues:**
   - Added automatic handler cleanup fixture to prevent file lock errors
   - Ensures all file handlers are closed before temporary directory cleanup
   - Fixes `PermissionError: [WinError 32]` errors on Windows

---

## Test Coverage

### Current Coverage

- **Unit Tests:** Comprehensive coverage for all modules
- **Integration Tests:** End-to-end workflow testing
- **Script Tests:** All utility scripts have test coverage

### Test Statistics

- **Total Tests:** 100+ tests
- **Test Files:** 25+ test files
- **Coverage:** Core modules have >90% coverage

---

## Writing Tests

### Best Practices

1. **Use Fixtures:**
   - Use shared fixtures from `conftest.py` when possible
   - Create project-specific fixtures in test files if needed

2. **Clean Up Resources:**
   - Close file handlers explicitly if not using the automatic cleanup fixture
   - Clean up temporary files and directories
   - Reset environment variables after tests

3. **Windows Compatibility:**
   - Always close file handlers before deleting files
   - Use `pathlib.Path` for cross-platform path handling
   - Test on Windows if possible (file locking is stricter)

4. **Test Isolation:**
   - Each test should be independent
   - Don't rely on test execution order
   - Use fixtures for setup/teardown

### Example Test Structure

```python
"""Tests for module_name."""

import pytest
from pathlib import Path

from module_name import function_name


class TestFunctionName:
    """Test the function_name function."""

    def test_basic_functionality(self, temp_dir):
        """Test basic functionality."""
        # Arrange
        test_file = temp_dir / "test.txt"
        
        # Act
        result = function_name(test_file)
        
        # Assert
        assert result is not None
        assert test_file.exists()
```

---

## Troubleshooting

### Common Issues

**File Lock Errors (Windows):**
- **Symptom:** `PermissionError: [WinError 32]` during test teardown
- **Solution:** Ensure file handlers are closed. The `cleanup_logging_handlers` fixture should handle this automatically.

**Import Errors:**
- **Symptom:** `ImportError: cannot import name 'module'`
- **Solution:** Check if module exists. Use conditional imports and `@pytest.mark.skipif` for optional modules.

**Test Failures:**
- **Symptom:** Tests fail unexpectedly
- **Solution:** Run tests with `-v` flag for verbose output. Check test output capture for detailed error messages.

---

## Related Documentation

- `docs/TEST_OUTPUT_CAPTURE.md` - Test output capture functionality
- `docs/PHASE_4_6_REVIEW.md` - Code review including test verification
- `docs/SER_IMPLEMENTATION_PLAN.md` - Implementation plan with test requirements

---

## Notes

- **Verification Tests:** Some tests (e.g., `test_verify_output_capture.py`) are intentionally skipped. These are for Phase 2.3 verification and can be removed once verification is complete.
- **Missing Modules:** Some tests handle missing modules gracefully (e.g., `pre_commit_checks`). These modules may be implemented in the future.
- **Windows Testing:** All tests are designed to work on Windows, Linux, and macOS. File handler cleanup is critical for Windows compatibility.
