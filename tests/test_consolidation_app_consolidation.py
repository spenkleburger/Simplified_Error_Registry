"""Tests for consolidation app parser integration (Phase 3.2)."""

import logging
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

from src.consolidation_app.consolidation import ProjectEntries, process_projects


def _write_errors_and_fixes(path: Path, content: str) -> None:
    (path / ".errors_fixes").mkdir(parents=True, exist_ok=True)
    (path / ".errors_fixes" / "errors_and_fixes.md").write_text(
        dedent(content).strip() + "\n", encoding="utf-8"
    )


def test_process_projects_parses_and_splits_entries(tmp_path):
    """Process projects: parse entries and separate by is_process_issue."""
    proj = tmp_path / "proj"
    proj.mkdir()
    _write_errors_and_fixes(
        proj,
        """
        ### Error: TypeError: Example

        **Timestamp:** 2025-12-01T12:00:00Z
        **Error Type:** `TypeError`
        **Result:** ✅ Solved

        **Fix Applied:**
        ```python
        x = 1
        ```
        **Explanation:** Fix.

        ### Agent Process Issue: Lost state

        **Timestamp:** 2025-12-02T09:00:00Z
        **Issue Type:** `agent-process`
        **Result:** ✅ Documented

        **Issue Description:** State lost.
        **Rule Established:** Reload state.
        """,
    )

    results = process_projects(tmp_path)

    assert len(results) == 1
    pe = results[0]
    assert isinstance(pe, ProjectEntries)
    assert pe.project == proj.resolve()
    assert len(pe.errors) == 1
    assert len(pe.process_issues) == 1
    assert not pe.errors[0].is_process_issue
    assert pe.process_issues[0].is_process_issue


def test_process_projects_empty_file(tmp_path):
    """Empty errors_and_fixes.md yields ProjectEntries with empty lists."""
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".errors_fixes").mkdir()
    (proj / ".errors_fixes" / "errors_and_fixes.md").write_text("", encoding="utf-8")

    results = process_projects(tmp_path)

    assert len(results) == 1
    assert results[0].project == proj.resolve()
    assert results[0].errors == []
    assert results[0].process_issues == []


def test_process_projects_missing_file_skipped(tmp_path, caplog):
    """Missing errors_and_fixes.md: skip project, log warning."""
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".errors_fixes").mkdir()
    caplog.set_level(logging.INFO)

    with patch(
        "src.consolidation_app.consolidation.discover_projects",
        return_value=[proj.resolve()],
    ):
        results = process_projects(tmp_path)

    assert len(results) == 0
    assert "Missing" in caplog.text
    assert "skipping" in caplog.text.lower()


def test_process_projects_parse_error_continues(tmp_path, caplog):
    """On parse/read error: log error, continue with other projects."""
    caplog.set_level(logging.INFO)

    proj = tmp_path / "proj"
    proj.mkdir()
    _write_errors_and_fixes(proj, "### Error: X\n**Timestamp:** 2025-12-01T12:00:00Z\n**Error Type:** `X`\n**Fix Applied:**\n```\na\n```\n**Explanation:** x\n")

    def raise_err(_path):
        raise ValueError("parse fail")

    with patch(
        "src.consolidation_app.consolidation.parse_errors_and_fixes",
        side_effect=raise_err,
    ):
        with patch(
            "src.consolidation_app.consolidation.discover_projects",
            return_value=[proj.resolve()],
        ):
            results = process_projects(tmp_path)

    assert len(results) == 0
    assert "Parse error" in caplog.text or "parse fail" in caplog.text


def test_process_projects_io_error_continues(tmp_path, caplog):
    """On IO error: log error, continue with other projects."""
    caplog.set_level(logging.INFO)

    proj = tmp_path / "proj"
    proj.mkdir()
    _write_errors_and_fixes(proj, "### Error: X\n**Timestamp:** 2025-12-01T12:00:00Z\n**Error Type:** `X`\n**Fix Applied:**\n```\na\n```\n**Explanation:** x\n")

    def raise_io(_path):
        raise OSError("read fail")

    with patch(
        "src.consolidation_app.consolidation.parse_errors_and_fixes",
        side_effect=raise_io,
    ):
        with patch(
            "src.consolidation_app.consolidation.discover_projects",
            return_value=[proj.resolve()],
        ):
            results = process_projects(tmp_path)

    assert len(results) == 0
    assert "Failed to read" in caplog.text or "read fail" in caplog.text


def test_process_projects_logs_stats(tmp_path, caplog):
    """Log number of projects processed and entries per project."""
    caplog.set_level(logging.INFO)

    proj = tmp_path / "proj"
    proj.mkdir()
    _write_errors_and_fixes(
        proj,
        """
        ### Error: E: One

        **Timestamp:** 2025-12-01T12:00:00Z
        **Error Type:** `E`
        **Fix Applied:**\n```\na\n```
        **Explanation:** x
        """,
    )

    process_projects(tmp_path)

    assert "Processing 1 project" in caplog.text or "Processing 1 project(s)" in caplog.text
    assert "1 error" in caplog.text and "0 process" in caplog.text
    assert "Consolidation complete" in caplog.text


def test_process_projects_multiple_projects(tmp_path):
    """Multiple projects: each contributes ProjectEntries."""
    for name in ("a", "b"):
        p = tmp_path / name
        p.mkdir()
        _write_errors_and_fixes(
            p,
            """
            ### Error: X: %s

            **Timestamp:** 2025-12-01T12:00:00Z
            **Error Type:** `X`
            **Fix Applied:**\n```\n1\n```
            **Explanation:** x
            """ % name,
        )

    results = process_projects(tmp_path)

    assert len(results) == 2
    projects = {pe.project.name for pe in results}
    assert projects == {"a", "b"}
