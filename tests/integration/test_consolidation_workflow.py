"""Integration tests for the full consolidation workflow (Phase 3.6)."""

from __future__ import annotations

import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from src.consolidation_app.main import consolidate_all_projects


def _mk_project(root: Path, name: str, errors_content: str) -> Path:
    """Create project dir with .errors_fixes/errors_and_fixes.md; return project path."""
    proj = root / name
    proj.mkdir(parents=True, exist_ok=True)
    ef = proj / ".errors_fixes"
    ef.mkdir(exist_ok=True)
    (ef / "errors_and_fixes.md").write_text(
        dedent(errors_content).strip() + "\n", encoding="utf-8", newline="\n"
    )
    return proj


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

_HEADER_ONLY = """# Errors and Fixes Log

> **Note**: This file is processed daily by the consolidation app at 2 AM.
> `### Error:` entries → fix_repo.md; `### Agent Process Issue:` entries → coding_tips.md. Contents are then cleared (file is kept).

"""


@pytest.mark.integration
def test_multiple_projects():
    """Test consolidation with multiple projects under root."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _mk_project(
            root, "proj_a", _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        )
        _mk_project(
            root, "proj_b", _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        )

        result = consolidate_all_projects(root, dry_run=False)

        assert result.ok_count == 2
        assert result.fail_count == 0
        for name in ("proj_a", "proj_b"):
            proj = root / name
            assert (proj / ".errors_fixes" / "fix_repo.md").exists()
            assert (proj / ".errors_fixes" / "coding_tips.md").exists()
            assert "**Timestamp:**" not in (
                proj / ".errors_fixes" / "errors_and_fixes.md"
            ).read_text(encoding="utf-8")


@pytest.mark.integration
def test_existing_fix_repo_and_coding_tips():
    """Test consolidation when fix_repo.md and coding_tips.md already exist."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        proj = _mk_project(
            root, "proj", _MINIMAL_ERROR.strip() + "\n\n" + _MINIMAL_PROCESS.strip()
        )
        ef = proj / ".errors_fixes"
        (ef / "fix_repo.md").write_text("# Fix Repository\n\n---\n\n", encoding="utf-8")
        (ef / "coding_tips.md").write_text(
            "# Coding Tips - Agent Process Rules\n\n---\n\n", encoding="utf-8"
        )

        result = consolidate_all_projects(root, dry_run=False)

        assert result.ok_count == 1
        assert result.fail_count == 0
        fix_repo = (ef / "fix_repo.md").read_text(encoding="utf-8")
        coding_tips = (ef / "coding_tips.md").read_text(encoding="utf-8")
        assert "## " in fix_repo
        assert "TypeError" in fix_repo
        assert "Rule" in coding_tips or "Rule X" in coding_tips


@pytest.mark.integration
def test_empty_projects():
    """Test consolidation with projects that have header-only errors_and_fixes."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        proj = _mk_project(root, "empty", _HEADER_ONLY)

        result = consolidate_all_projects(root, dry_run=False)

        assert result.ok_count == 1
        assert result.fail_count == 0
        fix_repo = proj / ".errors_fixes" / "fix_repo.md"
        coding_tips = proj / ".errors_fixes" / "coding_tips.md"
        assert fix_repo.exists()
        assert coding_tips.exists()
        assert "Total Entries: 0" in fix_repo.read_text(
            encoding="utf-8"
        ) or "---" in fix_repo.read_text(encoding="utf-8")
        assert "**Timestamp:**" not in (
            proj / ".errors_fixes" / "errors_and_fixes.md"
        ).read_text(encoding="utf-8")
