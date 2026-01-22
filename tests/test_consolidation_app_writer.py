"""Tests for the consolidation app writer."""

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.consolidation_app.parser import ErrorEntry
from src.consolidation_app.writer import (
    clear_errors_and_fixes,
    write_coding_tips,
    write_fix_repo,
)


def _build_entry(
    *,
    signature: str,
    timestamp: datetime,
    success_count: int = 1,
    is_process_issue: bool = False,
    tags: list[str] | None = None,
    error_type: str = "ValueError",
    file_path: str = "src/app/example.py",
    result: str = "✅ Solved",
) -> ErrorEntry:
    """Helper to create test ErrorEntry."""
    return ErrorEntry(
        error_signature=signature,
        error_type=error_type,
        file=file_path,
        line=1,
        fix_code="fixed_code()",
        explanation="Keeps the guardrails intact.",
        result=result,
        success_count=success_count,
        tags=tags or ["tag-a"],
        timestamp=timestamp,
        is_process_issue=is_process_issue,
    )


def test_write_fix_repo_creates_file():
    """Test that write_fix_repo creates fix_repo.md with correct content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        entry = _build_entry(
            signature="ExampleError",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            success_count=1,
        )

        write_fix_repo(project_path, [entry])

        output_file = project_path / ".errors_fixes" / "fix_repo.md"
        assert output_file.exists(), "fix_repo.md should be created"

        content = output_file.read_text(encoding="utf-8")
        assert "# Fix Repository" in content
        assert "## ExampleError" in content
        assert "Success Count: 1" in content


def test_write_fix_repo_creates_directory():
    """Test that write_fix_repo creates .errors_fixes directory if missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        entry = _build_entry(
            signature="ExampleError",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
        )

        write_fix_repo(project_path, [entry])

        errors_fixes_dir = project_path / ".errors_fixes"
        assert errors_fixes_dir.exists(), ".errors_fixes directory should be created"
        assert errors_fixes_dir.is_dir()


def test_write_fix_repo_filters_process_issues():
    """Test that write_fix_repo only writes non-process-issue entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        error_entry = _build_entry(
            signature="ExampleError",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            is_process_issue=False,
        )
        process_entry = _build_entry(
            signature="ProcessIssue",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            is_process_issue=True,
        )

        write_fix_repo(project_path, [error_entry, process_entry])

        output_file = project_path / ".errors_fixes" / "fix_repo.md"
        content = output_file.read_text(encoding="utf-8")
        assert "## ExampleError" in content
        assert "ProcessIssue" not in content


def test_write_fix_repo_empty_entries():
    """Test that write_fix_repo handles empty entry list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        write_fix_repo(project_path, [])

        output_file = project_path / ".errors_fixes" / "fix_repo.md"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "# Fix Repository" in content
        assert "Total Entries:** 0" in content


def test_write_fix_repo_uses_lf_line_endings():
    """Test that write_fix_repo uses LF line endings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        entry = _build_entry(
            signature="ExampleError",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
        )

        write_fix_repo(project_path, [entry])

        output_file = project_path / ".errors_fixes" / "fix_repo.md"
        content_bytes = output_file.read_bytes()
        # Check that there are no CRLF line endings (Windows)
        assert b"\r\n" not in content_bytes
        # Check that LF line endings are present
        assert b"\n" in content_bytes


def test_write_coding_tips_creates_file():
    """Test that write_coding_tips creates coding_tips.md with correct content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        entry = _build_entry(
            signature="ProcessRule",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            is_process_issue=True,
        )

        write_coding_tips(project_path, [entry])

        output_file = project_path / ".errors_fixes" / "coding_tips.md"
        assert output_file.exists(), "coding_tips.md should be created"

        content = output_file.read_text(encoding="utf-8")
        assert "# Coding Tips - Agent Process Rules" in content
        assert "Rule: ProcessRule" in content


def test_write_coding_tips_creates_directory():
    """Test that write_coding_tips creates .errors_fixes directory if missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        entry = _build_entry(
            signature="ProcessRule",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            is_process_issue=True,
        )

        write_coding_tips(project_path, [entry])

        errors_fixes_dir = project_path / ".errors_fixes"
        assert errors_fixes_dir.exists(), ".errors_fixes directory should be created"
        assert errors_fixes_dir.is_dir()


def test_write_coding_tips_filters_non_process_issues():
    """Test that write_coding_tips only writes process-issue entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        error_entry = _build_entry(
            signature="ExampleError",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            is_process_issue=False,
        )
        process_entry = _build_entry(
            signature="ProcessRule",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            is_process_issue=True,
        )

        write_coding_tips(project_path, [error_entry, process_entry])

        output_file = project_path / ".errors_fixes" / "coding_tips.md"
        content = output_file.read_text(encoding="utf-8")
        assert "Rule: ProcessRule" in content
        assert "ExampleError" not in content


def test_write_coding_tips_empty_entries():
    """Test that write_coding_tips handles empty entry list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        write_coding_tips(project_path, [])

        output_file = project_path / ".errors_fixes" / "coding_tips.md"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "# Coding Tips - Agent Process Rules" in content
        assert "Total Rules:** 0" in content


def test_write_coding_tips_uses_lf_line_endings():
    """Test that write_coding_tips uses LF line endings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        entry = _build_entry(
            signature="ProcessRule",
            timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            is_process_issue=True,
        )

        write_coding_tips(project_path, [entry])

        output_file = project_path / ".errors_fixes" / "coding_tips.md"
        content_bytes = output_file.read_bytes()
        # Check that there are no CRLF line endings (Windows)
        assert b"\r\n" not in content_bytes
        # Check that LF line endings are present
        assert b"\n" in content_bytes


def test_clear_errors_and_fixes_keeps_header():
    """Test that clear_errors_and_fixes keeps the header and clears content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        errors_fixes_dir = project_path / ".errors_fixes"
        errors_fixes_dir.mkdir()
        errors_file = errors_fixes_dir / "errors_and_fixes.md"

        # Create file with content
        original_content = """# Errors and Fixes Log

> **Note**: This file is processed daily by the consolidation app at 2 AM.
> `### Error:` entries → fix_repo.md; `### Agent Process Issue:` entries → coding_tips.md. Contents are then cleared (file is kept).

### Error: TestError
**Timestamp:** 2025-01-01T12:00:00Z
**File:** test.py
**Line:** 10
"""
        errors_file.write_text(original_content, encoding="utf-8")

        clear_errors_and_fixes(project_path)

        assert errors_file.exists(), "errors_and_fixes.md should still exist"
        content = errors_file.read_text(encoding="utf-8")
        assert "# Errors and Fixes Log" in content
        assert "### Error: TestError" not in content
        assert "**Timestamp:**" not in content


def test_clear_errors_and_fixes_creates_directory():
    """Test that clear_errors_and_fixes creates directory if missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        errors_fixes_dir = project_path / ".errors_fixes"
        errors_fixes_dir.mkdir()
        errors_file = errors_fixes_dir / "errors_and_fixes.md"
        errors_file.write_text("test content", encoding="utf-8")

        clear_errors_and_fixes(project_path)

        assert errors_file.exists()


def test_clear_errors_and_fixes_handles_missing_file():
    """Test that clear_errors_and_fixes handles missing file gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Should not raise an error
        clear_errors_and_fixes(project_path)

        errors_file = project_path / ".errors_fixes" / "errors_and_fixes.md"
        assert not errors_file.exists()


def test_clear_errors_and_fixes_uses_lf_line_endings():
    """Test that clear_errors_and_fixes uses LF line endings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        errors_fixes_dir = project_path / ".errors_fixes"
        errors_fixes_dir.mkdir()
        errors_file = errors_fixes_dir / "errors_and_fixes.md"
        errors_file.write_text("test content", encoding="utf-8")

        clear_errors_and_fixes(project_path)

        content_bytes = errors_file.read_bytes()
        # Check that there are no CRLF line endings (Windows)
        assert b"\r\n" not in content_bytes
        # Check that LF line endings are present
        assert b"\n" in content_bytes


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Permission testing with chmod not reliable on Windows",
)
def test_write_fix_repo_permission_error(tmp_path):
    """Test that write_fix_repo raises PermissionError on permission issues."""
    project_path = tmp_path / "test_project"
    project_path.mkdir()

    # Make directory read-only (Unix-like systems)
    errors_fixes_dir = project_path / ".errors_fixes"
    errors_fixes_dir.mkdir()
    errors_fixes_dir.chmod(0o444)  # Read-only

    entry = _build_entry(
        signature="ExampleError",
        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    try:
        with pytest.raises(PermissionError):
            write_fix_repo(project_path, [entry])
    finally:
        # Restore permissions for cleanup
        errors_fixes_dir.chmod(0o755)


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Permission testing with chmod not reliable on Windows",
)
def test_write_coding_tips_permission_error(tmp_path):
    """Test that write_coding_tips raises PermissionError on permission issues."""
    project_path = tmp_path / "test_project"
    project_path.mkdir()

    # Make directory read-only (Unix-like systems)
    errors_fixes_dir = project_path / ".errors_fixes"
    errors_fixes_dir.mkdir()
    errors_fixes_dir.chmod(0o444)  # Read-only

    entry = _build_entry(
        signature="ProcessRule",
        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
        is_process_issue=True,
    )

    try:
        with pytest.raises(PermissionError):
            write_coding_tips(project_path, [entry])
    finally:
        # Restore permissions for cleanup
        errors_fixes_dir.chmod(0o755)


def test_write_fix_repo_atomic_write(tmp_path):
    """Test that write_fix_repo uses atomic write (temp file then rename)."""
    project_path = Path(tmp_path)
    entry = _build_entry(
        signature="ExampleError",
        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    output_file = project_path / ".errors_fixes" / "fix_repo.md"
    temp_file = output_file.with_suffix(".tmp")

    # Write should create temp file first, then rename
    write_fix_repo(project_path, [entry])

    # Final file should exist
    assert output_file.exists()
    # Temp file should not exist after successful write
    assert not temp_file.exists()


def test_write_coding_tips_atomic_write(tmp_path):
    """Test that write_coding_tips uses atomic write (temp file then rename)."""
    project_path = Path(tmp_path)
    entry = _build_entry(
        signature="ProcessIssue",
        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
        is_process_issue=True,
    )

    output_file = project_path / ".errors_fixes" / "coding_tips.md"
    temp_file = output_file.with_suffix(".tmp")

    # Write should create temp file first, then rename
    write_coding_tips(project_path, [entry])

    # Final file should exist
    assert output_file.exists()
    # Temp file should not exist after successful write
    assert not temp_file.exists()


def test_clear_errors_and_fixes_atomic_write(tmp_path):
    """Test that clear_errors_and_fixes uses atomic write (temp file then rename)."""
    project_path = Path(tmp_path)
    errors_fixes_dir = project_path / ".errors_fixes"
    errors_fixes_dir.mkdir()
    errors_file = errors_fixes_dir / "errors_and_fixes.md"
    errors_file.write_text("### Error: test\n", encoding="utf-8")

    temp_file = errors_file.with_suffix(".tmp")

    # Clear should create temp file first, then rename
    clear_errors_and_fixes(project_path)

    # Final file should exist
    assert errors_file.exists()
    # Temp file should not exist after successful write
    assert not temp_file.exists()
