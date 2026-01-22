# File: tests/test_scripts_test_backend.py
# Description: Unit tests for test_backend.py script
# Version: 1.0


from scripts.test_backend import extract_error_sections


class TestExtractErrorSections:
    """Test extract_error_sections function."""

    def test_extract_failures_section(self):
        """Test extraction of FAILURES section."""
        full_output = """Running tests...
tests/test_example.py::test_function PASSED
tests/test_example.py::test_failing FAILED

=== FAILURES ===
FAILED tests/test_example.py::test_failing - AssertionError: assert 1 == 2
    def test_failing():
        assert 1 == 2
                    ^
AssertionError: assert 1 == 2

=== short test summary info ===
FAILED tests/test_example.py::test_failing
"""

        result = extract_error_sections(full_output)

        assert "=== FAILURES ===" in result
        assert "FAILED tests/test_example.py::test_failing" in result
        assert "AssertionError: assert 1 == 2" in result
        assert "=== short test summary info ===" in result
        assert "Command: task test:backend" in result
        # Should not include passing test
        assert "test_function PASSED" not in result

    def test_extract_errors_section(self):
        """Test extraction of ERRORS section."""
        full_output = """Running tests...

=== ERRORS ===
ERROR tests/test_example.py - ImportError: cannot import name 'module'
tests/test_example.py:1: in <module>
    from module import function
E   ImportError: cannot import name 'module'

=== short test summary info ===
ERROR tests/test_example.py
"""

        result = extract_error_sections(full_output)

        assert "=== ERRORS ===" in result
        assert "ImportError: cannot import name 'module'" in result
        assert "=== short test summary info ===" in result
        assert "Command: task test:backend" in result

    def test_extract_both_failures_and_errors(self):
        """Test extraction when both failures and errors exist."""
        full_output = """Running tests...

=== ERRORS ===
ERROR tests/test_import.py - ImportError

=== FAILURES ===
FAILED tests/test_example.py::test_function - AssertionError

=== short test summary info ===
ERROR tests/test_import.py
FAILED tests/test_example.py::test_function
"""

        result = extract_error_sections(full_output)

        assert "=== ERRORS ===" in result
        assert "=== FAILURES ===" in result
        assert "=== short test summary info ===" in result
        assert "ImportError" in result
        assert "AssertionError" in result

    def test_no_error_sections_returns_empty(self):
        """Test that empty string is returned when no error sections found."""
        full_output = """Running tests...
tests/test_example.py::test_function PASSED
tests/test_example.py::test_other PASSED

======================== 2 passed in 0.01s ========================
"""

        result = extract_error_sections(full_output)

        assert result == ""

    def test_empty_input_returns_empty(self):
        """Test that empty input returns empty string."""
        result = extract_error_sections("")
        assert result == ""

    def test_only_passing_tests_returns_empty(self):
        """Test that only passing tests returns empty string."""
        full_output = """=== test session starts ===
tests/test_example.py::test_one PASSED
tests/test_example.py::test_two PASSED
=== 2 passed in 0.01s ===
"""

        result = extract_error_sections(full_output)
        assert result == ""

    def test_extract_summary_without_failures(self):
        """Test that summary alone without failures/errors is not extracted."""
        full_output = """Running tests...
=== short test summary info ===
PASSED tests/test_example.py::test_function
"""

        result = extract_error_sections(full_output)
        # Should return empty since no FAILURES or ERRORS sections
        assert result == ""

    def test_excludes_passing_test_output(self):
        """Test that passing test details are excluded."""
        full_output = """Running tests...
tests/test_example.py::test_passing PASSED [ 50%]
tests/test_example.py::test_failing FAILED [100%]

=== FAILURES ===
FAILED tests/test_example.py::test_failing - AssertionError

=== short test summary info ===
FAILED tests/test_example.py::test_failing
"""

        result = extract_error_sections(full_output)

        assert "test_failing" in result
        assert "FAILURES" in result
        # Should not include passing test
        assert "test_passing" not in result
        assert "[ 50%]" not in result

    def test_excludes_collection_info(self):
        """Test that test collection info is excluded."""
        full_output = """=== test session starts ===
platform win32 -- Python 3.11.0
collected 5 items

tests/test_example.py::test_failing FAILED

=== FAILURES ===
FAILED tests/test_example.py::test_failing - AssertionError

=== short test summary info ===
FAILED tests/test_example.py::test_failing
"""

        result = extract_error_sections(full_output)

        assert "test session starts" not in result
        assert "platform" not in result
        assert "collected 5 items" not in result
        assert "FAILURES" in result
        assert "test_failing" in result

    def test_includes_header(self):
        """Test that header with command info is included."""
        full_output = """=== FAILURES ===
FAILED tests/test_example.py::test_function - AssertionError
"""

        result = extract_error_sections(full_output)

        assert "Test Output (Error Sections Only)" in result
        assert "Command: task test:backend" in result
        assert "=" * 70 in result

    def test_multiple_failures_in_summary(self):
        """Test extraction with multiple failures in summary."""
        full_output = """=== FAILURES ===
FAILED tests/test_example.py::test_one - AssertionError
FAILED tests/test_example.py::test_two - ValueError

=== short test summary info ===
FAILED tests/test_example.py::test_one
FAILED tests/test_example.py::test_two
"""

        result = extract_error_sections(full_output)

        assert "test_one" in result
        assert "test_two" in result
        assert "AssertionError" in result
        assert "ValueError" in result

    def test_traceback_details_included(self):
        """Test that traceback details are included in failures section."""
        full_output = """=== FAILURES ===
FAILED tests/test_example.py::test_function - AssertionError: assert 1 == 2

    def test_function():
>       assert 1 == 2
E       AssertionError: assert 1 == 2

tests/test_example.py:5: AssertionError

=== short test summary info ===
FAILED tests/test_example.py::test_function
"""

        result = extract_error_sections(full_output)

        assert "def test_function():" in result
        assert "assert 1 == 2" in result
        assert "tests/test_example.py:5: AssertionError" in result
