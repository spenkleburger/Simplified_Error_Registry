"""Tests for the consolidation app main workflow (Phase 3.6)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from src.consolidation_app.main import (
    ConsolidationResult,
    _consolidate_one_project,
    consolidate_all_projects,
)


def _mk_project_with_errors_fixes(root: Path, content: str) -> Path:
    """Create .errors_fixes/errors_and_fixes.md under root; return project path."""
    d = root / ".errors_fixes"
    d.mkdir(parents=True, exist_ok=True)
    (d / "errors_and_fixes.md").write_text(
        dedent(content).strip() + "\n", encoding="utf-8", newline="\n"
    )
    return root


_MINIMAL_ERROR = """
### Error: TypeError: test

**Timestamp:** 2025-01-01T12:00:00Z
**File:** `src/a.py`
**Line:** 1
**Error Type:** `TypeError`
**Tags:** `tag1`

**Fix Applied:**
```python
x = 1
```
**Explanation:** Fix.
**Result:** ✅ Solved
**Success Count:** 1
"""

_MINIMAL_PROCESS = """
### Agent Process Issue: Rule X

**Timestamp:** 2025-01-01T12:00:00Z
**Issue Type:** `agent-process`
**Tags:** `agent`

**Issue Description:** Desc.
**Rule Established:** Do X.
**Result:** ✅ Documented
"""


def test_full_consolidation_workflow():
    """Test full consolidation: parse, dedupe, tag, write, clear."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        proj = _mk_project_with_errors_fixes(
            root, _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        )

        result = consolidate_all_projects(root, dry_run=False)

        assert result.ok_count == 1
        assert result.fail_count == 0
        fix_repo = proj / ".errors_fixes" / "fix_repo.md"
        coding_tips = proj / ".errors_fixes" / "coding_tips.md"
        errors_file = proj / ".errors_fixes" / "errors_and_fixes.md"
        assert fix_repo.exists()
        assert coding_tips.exists()
        assert "# Fix Repository" in fix_repo.read_text(encoding="utf-8")
        assert "TypeError" in fix_repo.read_text(encoding="utf-8")
        assert "# Coding Tips" in coding_tips.read_text(encoding="utf-8")
        assert "Rule X" in coding_tips.read_text(encoding="utf-8")
        text = errors_file.read_text(encoding="utf-8")
        assert "Errors and Fixes Log" in text
        assert "**Timestamp:**" not in text, "Entry blocks should be cleared"


def test_dry_run_mode():
    """Test dry-run: no files written, errors_and_fixes not cleared."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        content = _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        proj = _mk_project_with_errors_fixes(root, content)
        fix_repo = proj / ".errors_fixes" / "fix_repo.md"
        coding_tips = proj / ".errors_fixes" / "coding_tips.md"
        errors_file = proj / ".errors_fixes" / "errors_and_fixes.md"

        result = consolidate_all_projects(root, dry_run=True)

        assert result.ok_count == 1
        assert result.fail_count == 0
        assert not fix_repo.exists()
        assert not coding_tips.exists()
        assert "### Error:" in errors_file.read_text(encoding="utf-8")
        assert "### Agent Process Issue:" in errors_file.read_text(encoding="utf-8")


def test_error_handling_one_fails_others_continue():
    """Test that one project failure does not stop others."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ok_proj = root / "ok"
        ok_proj.mkdir()
        _mk_project_with_errors_fixes(
            ok_proj, _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        )
        bad_proj = root / "bad"
        bad_proj.mkdir()
        _mk_project_with_errors_fixes(
            bad_proj, _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        )

        orig = _consolidate_one_project

        def wrap(project: Path, *, dry_run: bool = False) -> None:
            if project == bad_proj:
                raise RuntimeError("simulated failure")
            orig(project, dry_run=dry_run)

        with patch(
            "src.consolidation_app.main._consolidate_one_project",
            side_effect=wrap,
        ):
            result = consolidate_all_projects(root, dry_run=False)

        assert result.ok_count == 1
        assert result.fail_count == 1
        assert (ok_proj / ".errors_fixes" / "fix_repo.md").exists()
        assert not (bad_proj / ".errors_fixes" / "fix_repo.md").exists()


def test_consolidation_result_all_ok():
    """Test ConsolidationResult.all_ok."""
    assert ConsolidationResult(1, 0).all_ok is True
    assert ConsolidationResult(0, 1).all_ok is False
    assert ConsolidationResult(2, 1).all_ok is False


def test_consolidate_one_project_dry_run():
    """Test _consolidate_one_project with dry_run does not write."""
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        _mk_project_with_errors_fixes(
            proj, _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        )

        _consolidate_one_project(proj, dry_run=True)

        assert not (proj / ".errors_fixes" / "fix_repo.md").exists()
        assert not (proj / ".errors_fixes" / "coding_tips.md").exists()
        assert "### Error:" in (
            proj / ".errors_fixes" / "errors_and_fixes.md"
        ).read_text(encoding="utf-8")
