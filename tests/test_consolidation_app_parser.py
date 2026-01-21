"""Tests for the consolidation app parser."""

from datetime import datetime
from pathlib import Path
from textwrap import dedent

from src.consolidation_app import parser


def _write_tmp(tmp_path: Path, content: str) -> Path:
    target = tmp_path / "errors_and_fixes.md"
    target.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return target


def test_parse_valid_error_entry(tmp_path):
    path = _write_tmp(
        tmp_path,
        """
        ### Error: TypeError: Example failure

        **Timestamp:** 2025-12-01T12:00:00Z
        **File:** `src/example.py`
        **Line:** 88
        **Error Type:** `TypeError`
        **Tags:** `tag-a`, `tag-b`

        **Error Context:**
        ```
        Traceback (most recent call last):
          ...
        ```

        **Fix Applied:**
        ```python
        fixed_value = 1
        ```

        **Explanation:** This fixes the type mismatch.
        **Result:** ✅ Solved
        **Success Count:** 3
        """,
    )

    entries = parser.parse_errors_and_fixes(path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.error_signature == "TypeError: Example failure"
    assert entry.error_type == "TypeError"
    assert entry.file == "src/example.py"
    assert entry.line == 88
    assert "fixed_value" in entry.fix_code
    assert entry.explanation == "This fixes the type mismatch."
    assert entry.result == "✅ Solved"
    assert entry.success_count == 3
    assert entry.tags == ["tag-a", "tag-b"]
    assert entry.timestamp == datetime.fromisoformat("2025-12-01T12:00:00+00:00")
    assert entry.is_process_issue is False


def test_parse_valid_process_issue_entry(tmp_path):
    path = _write_tmp(
        tmp_path,
        """
        ### Agent Process Issue: Persisted state was lost

        **Timestamp:** 2025-12-02T09:30:00Z
        **Issue Type:** `agent-process`
        **Tags:** `agent`, `state`

        **Issue Description:**
        The agent dropped the cached state during restart.

        **Rule Established:**
        Always reload cached state before running a new step.
        **Result:** ✅ Documented
        """,
    )

    entries = parser.parse_errors_and_fixes(path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.is_process_issue
    assert entry.error_type == "agent-process"
    assert "cached state" in entry.explanation
    assert "reload cached state" in entry.fix_code
    assert entry.result == "✅ Documented"
    assert entry.tags == ["agent", "state"]


def test_parse_multiple_entries(tmp_path):
    # Combine an error entry with a process issue
    content = """
    ### Error: ValueError: Missing info

    **Timestamp:** 2025-12-03T00:00:00Z
    **Error Type:** `ValueError`
    **Result:** ❌ Failed

    **Fix Applied:**
    ```python
    raise ValueError("fixed")
    ```

    **Explanation:** Always set defaults.
    **Success Count:** 1

    ---

    ### Agent Process Issue: Agent ignored reminder

    **Timestamp:** 2025-12-03T01:00:00Z
    **Issue Type:** `agent-process`
    **Result:** ✅ Documented

    **Issue Description:**
    Reminder message was never surfaced.

    **Rule Established:**
    Surface reminders before shutdown.
    """
    path = _write_tmp(tmp_path, content)
    entries = parser.parse_errors_and_fixes(path)
    assert len(entries) == 2
    assert not entries[0].is_process_issue
    assert entries[1].is_process_issue


def test_missing_fields_use_defaults(tmp_path):
    path = _write_tmp(
        tmp_path,
        """
        ### Error: KeyError: Bare minimum

        **Timestamp:** 2025-12-04T05:00:00Z
        **Error Type:** `KeyError`

        **Fix Applied:**
        ```python
        value = defaults.get("key")
        ```

        **Explanation:** Provide defaults.
        """,
    )

    entries = parser.parse_errors_and_fixes(path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.line == 0
    assert entry.file == ""
    assert entry.success_count == 0
    assert entry.result == ""
    assert entry.tags == []


def test_malformed_markdown_is_skipped(tmp_path):
    path = _write_tmp(
        tmp_path,
        """
        ### Error: Broken entry

        **Timestamp:** not-a-date
        **Error Type:** `RuntimeError`
        """,
    )

    entries = parser.parse_errors_and_fixes(path)
    assert entries == []


def test_empty_file_returns_no_entries(tmp_path):
    path = tmp_path / "errors_and_fixes.md"
    path.write_text("", encoding="utf-8")
    assert parser.parse_errors_and_fixes(path) == []
