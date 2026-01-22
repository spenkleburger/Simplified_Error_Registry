# File: tests/test_scripts_test_frontend.py
# Description: Unit tests for test_frontend.py script
# Version: 1.0


from scripts.test_frontend import extract_error_sections


class TestExtractErrorSections:
    """Test extract_error_sections function for frontend tests."""

    def test_extract_pytest_style_failures(self):
        """Test extraction of pytest-style FAILURES section."""
        full_output = """Running tests...

=== FAILURES ===
FAILED tests/test_example.test.ts - AssertionError
    Expected: true
    Received: false

=== short test summary info ===
FAILED tests/test_example.test.ts
"""

        result = extract_error_sections(full_output)

        assert "=== FAILURES ===" in result
        assert "AssertionError" in result
        assert "Command: task test:frontend" in result

    def test_extract_vitest_fail_marker(self):
        """Test extraction of Vitest-style FAIL markers."""
        full_output = """Running tests...

FAIL tests/example.test.ts > test function
AssertionError: Expected true but got false

  Expected: true
  Received: false

Test Files  1 failed (1)
"""

        result = extract_error_sections(full_output)

        assert "FAIL" in result
        assert "test function" in result
        assert "AssertionError" in result
        assert "Command: task test:frontend" in result

    def test_extract_vitest_errors(self):
        """Test extraction of Vitest error output."""
        full_output = """Running tests...

FAIL tests/example.test.ts > test with error
Error: Cannot read property 'value' of undefined

Test Files  1 failed (1)
"""

        result = extract_error_sections(full_output)

        assert "FAIL" in result
        assert "Error:" in result
        assert "Cannot read property" in result

    def test_no_error_sections_returns_empty(self):
        """Test that empty string is returned when no errors found."""
        full_output = """Running tests...

PASS tests/example.test.ts > test function

Test Files  1 passed (1)
"""

        result = extract_error_sections(full_output)
        assert result == ""

    def test_empty_input_returns_empty(self):
        """Test that empty input returns empty string."""
        result = extract_error_sections("")
        assert result == ""

    def test_excludes_passing_tests(self):
        """Test that passing test output is excluded."""
        full_output = """Running tests...

PASS tests/example.test.ts > passing test
FAIL tests/example.test.ts > failing test
AssertionError: Expected true

Test Files  1 failed (1)
"""

        result = extract_error_sections(full_output)

        assert "failing test" in result
        assert "FAIL" in result
        # Should not include passing test
        assert "passing test" not in result
        assert "PASS" not in result or "PASS" not in result.split("\n")[0]

    def test_includes_header(self):
        """Test that header with command info is included."""
        full_output = """FAIL tests/example.test.ts > test
AssertionError
"""

        result = extract_error_sections(full_output)

        assert "Test Output (Error Sections Only)" in result
        assert "Command: task test:frontend" in result
        assert "=" * 70 in result

    def test_pytest_and_vitest_combined(self):
        """Test handling of both pytest and Vitest output formats."""
        full_output = """=== FAILURES ===
FAILED tests/test_example.test.ts - AssertionError

FAIL tests/example.test.ts > vitest test
Error: Test failed

=== short test summary info ===
FAILED tests/test_example.test.ts
"""

        result = extract_error_sections(full_output)

        assert "=== FAILURES ===" in result
        assert "FAIL" in result
        assert "vitest test" in result

    def test_multiple_failures(self):
        """Test extraction with multiple failures."""
        full_output = """FAIL tests/example.test.ts > test one
AssertionError: First error

FAIL tests/example.test.ts > test two
TypeError: Second error

Test Files  1 failed (1)
"""

        result = extract_error_sections(full_output)

        assert "test one" in result
        assert "test two" in result
        assert "First error" in result
        assert "Second error" in result

    def test_only_summary_without_failures(self):
        """Test that summary alone without failures is not extracted."""
        full_output = """Test Files  1 passed (1)
Tests: 5 passed
"""

        result = extract_error_sections(full_output)
        # Should return empty since no FAIL markers or error sections
        assert result == ""
