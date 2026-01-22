# File: tests/test_scripts_test_integration.py
# Description: Unit tests for test_integration.py script
# Version: 1.0


from scripts.test_integration import extract_error_sections


class TestExtractErrorSections:
    """Test extract_error_sections function for integration tests."""

    def test_extract_failures_section(self):
        """Test extraction of FAILURES section."""
        full_output = """Running integration tests...

=== FAILURES ===
FAILED tests/integration/test_api.py::test_endpoint - AssertionError: assert 200 == 404
    def test_endpoint():
        response = client.get("/api/endpoint")
>       assert response.status_code == 200
E       Assert 200 == 404

tests/integration/test_api.py:15: AssertionError

=== short test summary info ===
FAILED tests/integration/test_api.py::test_endpoint
"""

        result = extract_error_sections(full_output)

        assert "=== FAILURES ===" in result
        assert "FAILED tests/integration/test_api.py::test_endpoint" in result
        assert "AssertionError: assert 200 == 404" in result
        assert "=== short test summary info ===" in result
        assert "Command: task test:integration" in result

    def test_extract_errors_section(self):
        """Test extraction of ERRORS section."""
        full_output = """Running integration tests...

=== ERRORS ===
ERROR tests/integration/test_db.py - ConnectionError: Cannot connect to database
tests/integration/test_db.py:5: in <module>
    db = connect_to_database()
E   ConnectionError: Cannot connect to database

=== short test summary info ===
ERROR tests/integration/test_db.py
"""

        result = extract_error_sections(full_output)

        assert "=== ERRORS ===" in result
        assert "ConnectionError: Cannot connect to database" in result
        assert "=== short test summary info ===" in result
        assert "Command: task test:integration" in result

    def test_extract_both_failures_and_errors(self):
        """Test extraction when both failures and errors exist."""
        full_output = """Running integration tests...

=== ERRORS ===
ERROR tests/integration/test_setup.py - ImportError

=== FAILURES ===
FAILED tests/integration/test_api.py::test_request - AssertionError

=== short test summary info ===
ERROR tests/integration/test_setup.py
FAILED tests/integration/test_api.py::test_request
"""

        result = extract_error_sections(full_output)

        assert "=== ERRORS ===" in result
        assert "=== FAILURES ===" in result
        assert "=== short test summary info ===" in result
        assert "ImportError" in result
        assert "AssertionError" in result

    def test_no_error_sections_returns_empty(self):
        """Test that empty string is returned when no error sections found."""
        full_output = """Running integration tests...
tests/integration/test_api.py::test_endpoint PASSED
tests/integration/test_db.py::test_query PASSED

======================== 2 passed in 1.23s ========================
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
tests/integration/test_api.py::test_one PASSED
tests/integration/test_db.py::test_two PASSED
=== 2 passed in 0.50s ===
"""

        result = extract_error_sections(full_output)
        assert result == ""

    def test_extract_summary_without_failures(self):
        """Test that summary alone without failures/errors is not extracted."""
        full_output = """Running tests...
=== short test summary info ===
PASSED tests/integration/test_api.py::test_endpoint
"""

        result = extract_error_sections(full_output)
        # Should return empty since no FAILURES or ERRORS sections
        assert result == ""

    def test_excludes_passing_test_output(self):
        """Test that passing test details are excluded."""
        full_output = """Running integration tests...
tests/integration/test_api.py::test_passing PASSED [ 33%]
tests/integration/test_db.py::test_failing FAILED [ 66%]

=== FAILURES ===
FAILED tests/integration/test_db.py::test_failing - DatabaseError

=== short test summary info ===
FAILED tests/integration/test_db.py::test_failing
"""

        result = extract_error_sections(full_output)

        assert "test_failing" in result
        assert "FAILURES" in result
        # Should not include passing test
        assert "test_passing" not in result
        assert "[ 33%]" not in result

    def test_excludes_collection_info(self):
        """Test that test collection info is excluded."""
        full_output = """=== test session starts ===
platform win32 -- Python 3.11.0
collected 3 items

tests/integration/test_api.py::test_failing FAILED

=== FAILURES ===
FAILED tests/integration/test_api.py::test_failing - AssertionError

=== short test summary info ===
FAILED tests/integration/test_api.py::test_failing
"""

        result = extract_error_sections(full_output)

        assert "test session starts" not in result
        assert "platform" not in result
        assert "collected 3 items" not in result
        assert "FAILURES" in result
        assert "test_failing" in result

    def test_includes_header(self):
        """Test that header with command info is included."""
        full_output = """=== FAILURES ===
FAILED tests/integration/test_api.py::test_endpoint - AssertionError
"""

        result = extract_error_sections(full_output)

        assert "Test Output (Error Sections Only)" in result
        assert "Command: task test:integration" in result
        assert "=" * 70 in result

    def test_multiple_failures_in_summary(self):
        """Test extraction with multiple failures in summary."""
        full_output = """=== FAILURES ===
FAILED tests/integration/test_api.py::test_one - AssertionError
FAILED tests/integration/test_db.py::test_two - DatabaseError

=== short test summary info ===
FAILED tests/integration/test_api.py::test_one
FAILED tests/integration/test_db.py::test_two
"""

        result = extract_error_sections(full_output)

        assert "test_one" in result
        assert "test_two" in result
        assert "AssertionError" in result
        assert "DatabaseError" in result

    def test_traceback_details_included(self):
        """Test that traceback details are included in failures section."""
        full_output = """=== FAILURES ===
FAILED tests/integration/test_api.py::test_request - HTTPError: 500 Internal Server Error

    def test_request():
        response = client.post("/api/data", json={"key": "value"})
>       assert response.status_code == 200
E       HTTPError: 500 Internal Server Error

tests/integration/test_api.py:20: HTTPError

=== short test summary info ===
FAILED tests/integration/test_api.py::test_request
"""

        result = extract_error_sections(full_output)

        assert "def test_request():" in result
        assert "client.post" in result
        assert "HTTPError: 500 Internal Server Error" in result
        assert "tests/integration/test_api.py:20: HTTPError" in result

    def test_service_connection_errors(self):
        """Test extraction of service connection errors common in integration tests."""
        full_output = """=== ERRORS ===
ERROR tests/integration/test_services.py - ConnectionError: Redis connection failed
tests/integration/test_services.py:10: in <module>
    redis_client = connect_redis()
E   ConnectionError: Redis connection failed

=== short test summary info ===
ERROR tests/integration/test_services.py
"""

        result = extract_error_sections(full_output)

        assert "ConnectionError: Redis connection failed" in result
        assert "connect_redis()" in result
