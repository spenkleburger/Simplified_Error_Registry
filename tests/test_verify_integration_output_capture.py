# File: tests/test_verify_integration_output_capture.py
# Description: Temporary test file to verify integration test output capture functionality
# Version: 1.0
# NOTE: This file is for Phase 2.3 verification - can be deleted after testing

"""Temporary test file to verify integration test output capture works correctly."""

import pytest


@pytest.mark.integration
def test_intentional_integration_failure_for_verification():
    """
    This test intentionally fails to verify that integration test output capture
    correctly extracts FAILURES section and summary.

    After running 'task test:integration', check clipboard contents:
    - Should contain '=== FAILURES ===' section
    - Should contain '=== short test summary info ===' section
    - Should NOT contain passing test output
    - Should NOT contain test collection info
    """
    # Intentional failure for Phase 2.3 verification
    assert 1 == 2, "Intentional integration test failure to test output capture"


@pytest.mark.integration
def test_another_integration_failure_for_verification():
    """
    Second intentional failure to test multiple failures in summary.
    """
    # Another intentional failure
    assert "expected" == "actual", "Second intentional integration test failure"


@pytest.mark.integration
def test_passing_integration_test_should_be_excluded():
    """
    This test passes and should NOT appear in clipboard output.
    If this appears in clipboard, the filtering is not working correctly.
    """
    assert 1 == 1  # This should pass and be excluded from clipboard
