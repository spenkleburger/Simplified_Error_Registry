"""Tests for the consolidation app merger (Phase 4.4)."""

from __future__ import annotations

from datetime import datetime
from typing import List

from src.consolidation_app.merger import (
    Fix,
    SIMILARITY_THRESHOLD,
    calculate_fix_similarity,
    group_similar_fixes,
    merge_fixes,
)
from src.consolidation_app.parser import ErrorEntry


def _create_entry(
    signature: str = "TypeError: test",
    error_type: str = "TypeError",
    file: str = "test.py",
    line: int = 10,
    fix_code: str = "x = 1",
    explanation: str = "Test explanation",
    success_count: int = 1,
    tags: List[str] | None = None,
    timestamp: datetime | None = None,
) -> ErrorEntry:
    """Helper to create test ErrorEntry. All share same signature/type/file for merge_fixes."""
    if tags is None:
        tags = ["test"]
    if timestamp is None:
        timestamp = datetime(2025, 1, 1, 12, 0, 0)
    return ErrorEntry(
        error_signature=signature,
        error_type=error_type,
        file=file,
        line=line,
        fix_code=fix_code,
        explanation=explanation,
        result="✅ Solved",
        success_count=success_count,
        tags=tags,
        timestamp=timestamp,
        is_process_issue=False,
    )


def _fix(code: str, success: int = 1, explanation: str = "") -> Fix:
    return Fix(
        fix_code=code,
        explanation=explanation or "expl",
        result="✅",
        success_count=success,
        error_type="TypeError",
        file="test.py",
        line=0,
        tags=[],
    )


# --- calculate_fix_similarity ---


def test_calculate_fix_similarity_identical():
    """Same fix code yields 1.0."""
    a = _fix("x = 1")
    b = _fix("x = 1")
    assert calculate_fix_similarity(a, b) == 1.0


def test_calculate_fix_similarity_different():
    """Completely different code yields low similarity."""
    a = _fix("x = 1")
    b = _fix("y = 2 + 3")
    assert calculate_fix_similarity(a, b) < 0.5


def test_calculate_fix_similarity_normalizes_whitespace():
    """Whitespace differences are normalized."""
    a = _fix("x = 1")
    b = _fix("x  =  1")
    assert calculate_fix_similarity(a, b) == 1.0


def test_calculate_fix_similarity_normalizes_comments():
    """Line comments are stripped for comparison."""
    a = _fix("x = 1")
    b = _fix("x = 1  # comment")
    assert calculate_fix_similarity(a, b) == 1.0


def test_calculate_fix_similarity_empty_both():
    """Both empty => 1.0."""
    a = _fix("")
    b = _fix("")
    assert calculate_fix_similarity(a, b) == 1.0


def test_calculate_fix_similarity_empty_one():
    """One empty => 0.0."""
    a = _fix("x = 1")
    b = _fix("")
    assert calculate_fix_similarity(a, b) == 0.0


# --- group_similar_fixes ---


def test_group_similar_fixes_same_fixes():
    """Same fixes end up in one group."""
    fixes = [_fix("x = 1"), _fix("x = 1"), _fix("x  =  1")]  # whitespace-normalized same
    groups = group_similar_fixes(fixes, threshold=0.9)
    assert len(groups) == 1
    assert len(groups[0]) == 3


def test_group_similar_fixes_different_fixes():
    """Different fixes end up in separate groups."""
    fixes = [_fix("x = 1"), _fix("y = 2"), _fix("z = 3")]
    groups = group_similar_fixes(fixes, threshold=0.9)
    assert len(groups) == 3
    assert [len(g) for g in groups] == [1, 1, 1]


def test_group_similar_fixes_empty():
    """Empty list => empty groups."""
    assert group_similar_fixes([]) == []


def test_group_similar_fixes_single():
    """Single fix => one group of one."""
    fixes = [_fix("x = 1")]
    groups = group_similar_fixes(fixes)
    assert len(groups) == 1
    assert len(groups[0]) == 1


def test_group_similar_fixes_similar_but_not_identical():
    """Fixes with similarity > 0.9 group together."""
    # "x = 1" vs "x  =  1" normalize to same (whitespace collapsed)
    fixes = [_fix("x = 1"), _fix("x  =  1")]
    groups = group_similar_fixes(fixes, threshold=0.9)
    assert len(groups) == 1
    assert len(groups[0]) == 2


# --- merge_fixes ---


def test_merge_fixes_same_fix_increments_success_count():
    """Same fix: single merged entry with summed success_count."""
    entries = [
        _create_entry(fix_code="x = 1", success_count=2),
        _create_entry(fix_code="x = 1", success_count=3),
        _create_entry(fix_code="x = 1", success_count=1),
    ]
    result = merge_fixes(entries)
    assert len(result) == 1
    assert result[0].success_count == 6
    assert result[0].fix_code.strip() == "x = 1"


def test_merge_fixes_different_fixes_keep_variants():
    """Different fixes: separate entries (variants)."""
    entries = [
        _create_entry(fix_code="x = 1", success_count=2),
        _create_entry(fix_code="y = 2", success_count=1),
        _create_entry(fix_code="z = 3", success_count=1),
    ]
    result = merge_fixes(entries)
    assert len(result) == 3
    fix_codes = {e.fix_code.strip() for e in result}
    assert fix_codes == {"x = 1", "y = 2", "z = 3"}


def test_merge_fixes_sort_by_success_count():
    """Output sorted by success_count descending."""
    entries = [
        _create_entry(fix_code="a", success_count=1),
        _create_entry(fix_code="b", success_count=5),
        _create_entry(fix_code="c", success_count=3),
    ]
    result = merge_fixes(entries)
    assert len(result) == 3
    assert [e.success_count for e in result] == [5, 3, 1]
    assert [e.fix_code.strip() for e in result] == ["b", "c", "a"]


def test_merge_fixes_single_entry():
    """Single entry => single result."""
    entries = [_create_entry(fix_code="x = 1", success_count=1)]
    result = merge_fixes(entries)
    assert len(result) == 1
    assert result[0].success_count == 1
    assert result[0].fix_code.strip() == "x = 1"


def test_merge_fixes_empty_returns_empty():
    """No entries => empty list."""
    assert merge_fixes([]) == []


def test_merge_fixes_same_and_different():
    """Mix: same fixes merged, different kept as variants."""
    entries = [
        _create_entry(fix_code="x = 1", success_count=2),
        _create_entry(fix_code="x = 1", success_count=1),
        _create_entry(fix_code="y = 2", success_count=4),
    ]
    result = merge_fixes(entries)
    assert len(result) == 2
    by_code = {e.fix_code.strip(): e for e in result}
    assert by_code["x = 1"].success_count == 3
    assert by_code["y = 2"].success_count == 4
    # Sorted by success: y first, then x
    assert result[0].fix_code.strip() == "y = 2"
    assert result[1].fix_code.strip() == "x = 1"


def test_merge_fixes_fuzzy_same_grouped():
    """Fuzzy-similar fixes (whitespace/comments) are grouped."""
    entries = [
        _create_entry(fix_code="x = 1", success_count=2),
        _create_entry(fix_code="x  =  1", success_count=1),
        _create_entry(fix_code="x = 1  # comment", success_count=1),
    ]
    result = merge_fixes(entries, threshold=0.9)
    assert len(result) == 1
    assert result[0].success_count == 4


def test_merge_fixes_tags_union():
    """Tags from all grouped fixes are combined."""
    entries = [
        _create_entry(fix_code="x = 1", tags=["a", "b"]),
        _create_entry(fix_code="x = 1", tags=["b", "c"]),
    ]
    result = merge_fixes(entries)
    assert len(result) == 1
    assert set(result[0].tags) == {"a", "b", "c"}


def test_merge_fixes_preserves_signature_type_file():
    """Metadata (signature, type, file) preserved from template."""
    entries = [
        _create_entry(
            signature="ValueError: bad",
            error_type="ValueError",
            file="foo.py",
            fix_code="x = 1",
        ),
    ]
    result = merge_fixes(entries)
    assert len(result) == 1
    assert result[0].error_signature == "ValueError: bad"
    assert result[0].error_type == "ValueError"
    assert result[0].file == "foo.py"


def test_merge_fixes_prefers_solved_result():
    """When merging, prefer result containing ✅."""
    entries = [
        _create_entry(fix_code="x = 1", success_count=1),
    ]
    # Override result via raw ErrorEntry
    solved = ErrorEntry(
        error_signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        line=10,
        fix_code="x = 1",
        explanation="Test",
        result="✅ Solved",
        success_count=1,
        tags=["test"],
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        is_process_issue=False,
    )
    failed = ErrorEntry(
        error_signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        line=10,
        fix_code="x = 1",
        explanation="Test",
        result="❌ Failed",
        success_count=1,
        tags=["test"],
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        is_process_issue=False,
    )
    result = merge_fixes([failed, solved])
    assert len(result) == 1
    assert "✅" in result[0].result


def test_similarity_threshold_constant():
    """SIMILARITY_THRESHOLD is 0.9."""
    assert SIMILARITY_THRESHOLD == 0.9
