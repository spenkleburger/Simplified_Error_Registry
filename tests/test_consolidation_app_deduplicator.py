"""Tests for the consolidation app deduplicator."""

from datetime import datetime

from src.consolidation_app.deduplicator import (
    deduplicate_errors_exact,
    merge_entries,
)
from src.consolidation_app.parser import ErrorEntry


def _create_entry(
    signature: str = "TestError",
    error_type: str = "TypeError",
    file: str = "test.py",
    line: int = 10,
    fix_code: str = "fix = 1",
    success_count: int = 1,
    timestamp: datetime | None = None,
) -> ErrorEntry:
    """Helper to create test ErrorEntry."""
    if timestamp is None:
        timestamp = datetime(2025, 1, 1, 12, 0, 0)
    return ErrorEntry(
        error_signature=signature,
        error_type=error_type,
        file=file,
        line=line,
        fix_code=fix_code,
        explanation="Test explanation",
        result="✅ Solved",
        success_count=success_count,
        tags=["test"],
        timestamp=timestamp,
        is_process_issue=False,
    )


def test_exact_match_deduplication():
    """Test that exact matches are merged."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",
        success_count=3,
    )
    new = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",  # Same fix
        success_count=2,
    )

    result = deduplicate_errors_exact([new], [existing])
    assert len(result) == 1
    merged = result[0]
    assert merged.success_count == 5  # 3 + 2
    assert merged.error_signature == "TypeError: test"


def test_no_match_adds_new_entry():
    """Test that non-matching entries are added as new."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
    )
    new = _create_entry(
        signature="ValueError: different",
        error_type="ValueError",
        file="other.py",
    )

    result = deduplicate_errors_exact([new], [existing])
    assert len(result) == 2
    assert any(e.error_signature == "TypeError: test" for e in result)
    assert any(e.error_signature == "ValueError: different" for e in result)


def test_same_fix_increments_success_count():
    """Test that same fix code increments success count."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",
        success_count=5,
    )
    new = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",  # Same fix
        success_count=3,
    )

    result = deduplicate_errors_exact([new], [existing])
    assert len(result) == 1
    assert result[0].success_count == 8  # 5 + 3


def test_different_fix_keeps_both_variants():
    """Test that different fix codes keep both entries as variants."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",
        success_count=5,
    )
    new = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 2",  # Different fix
        success_count=3,
    )

    result = deduplicate_errors_exact([new], [existing])
    assert len(result) == 2
    # Both entries should be present
    signatures = [e.error_signature for e in result]
    assert signatures.count("TypeError: test") == 2
    # Check that both fix codes are present
    fix_codes = [e.fix_code for e in result]
    assert "x = 1" in fix_codes
    assert "x = 2" in fix_codes


def test_empty_new_entries_returns_existing():
    """Test that empty new entries list returns existing unchanged."""
    existing = [
        _create_entry(signature="Error1"),
        _create_entry(signature="Error2"),
    ]

    result = deduplicate_errors_exact([], existing)
    assert len(result) == 2
    assert result == existing


def test_empty_existing_entries_returns_new():
    """Test that empty existing entries list returns all new entries."""
    new = [
        _create_entry(signature="Error1"),
        _create_entry(signature="Error2"),
    ]

    result = deduplicate_errors_exact(new, [])
    assert len(result) == 2
    assert result == new


def test_empty_both_lists_returns_empty():
    """Test that empty lists return empty list."""
    result = deduplicate_errors_exact([], [])
    assert result == []


def test_match_criteria_all_three_fields():
    """Test that all three fields (signature, type, file) must match."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
    )
    # Different signature
    new1 = _create_entry(
        signature="TypeError: different",
        error_type="TypeError",
        file="test.py",
    )
    # Different type
    new2 = _create_entry(
        signature="TypeError: test",
        error_type="ValueError",
        file="test.py",
    )
    # Different file
    new3 = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="other.py",
    )

    result1 = deduplicate_errors_exact([new1], [existing])
    assert len(result1) == 2  # No match

    result2 = deduplicate_errors_exact([new2], [existing])
    assert len(result2) == 2  # No match

    result3 = deduplicate_errors_exact([new3], [existing])
    assert len(result3) == 2  # No match


def test_merge_entries_updates_timestamp():
    """Test that merge_entries uses newer timestamp."""
    older = _create_entry(
        timestamp=datetime(2025, 1, 1, 10, 0, 0),
        success_count=2,
    )
    newer = _create_entry(
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        success_count=3,
    )

    merged = merge_entries(older, newer)
    assert merged.timestamp == datetime(2025, 1, 1, 12, 0, 0)
    assert merged.success_count == 5  # 2 + 3


def test_merge_entries_combines_tags():
    """Test that merge_entries combines tags without duplicates."""
    existing = ErrorEntry(
        error_signature="Test",
        error_type="TypeError",
        file="test.py",
        line=10,
        fix_code="x = 1",
        explanation="Test",
        result="✅ Solved",
        success_count=1,
        tags=["tag1", "tag2"],
        timestamp=datetime(2025, 1, 1, 10, 0, 0),
        is_process_issue=False,
    )
    new = ErrorEntry(
        error_signature="Test",
        error_type="TypeError",
        file="test.py",
        line=10,
        fix_code="x = 1",
        explanation="Test",
        result="✅ Solved",
        success_count=1,
        tags=["tag2", "tag3"],  # tag2 is duplicate
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        is_process_issue=False,
    )

    merged = merge_entries(existing, new)
    assert set(merged.tags) == {"tag1", "tag2", "tag3"}
    assert len(merged.tags) == 3


def test_merge_entries_prefers_solved_result():
    """Test that merge_entries prefers '✅ Solved' result."""
    existing = ErrorEntry(
        error_signature="Test",
        error_type="TypeError",
        file="test.py",
        line=10,
        fix_code="x = 1",
        explanation="Test",
        result="❌ Failed",
        success_count=1,
        tags=[],
        timestamp=datetime(2025, 1, 1, 10, 0, 0),
        is_process_issue=False,
    )
    new = ErrorEntry(
        error_signature="Test",
        error_type="TypeError",
        file="test.py",
        line=10,
        fix_code="x = 1",
        explanation="Test",
        result="✅ Solved",
        success_count=1,
        tags=[],
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        is_process_issue=False,
    )

    merged = merge_entries(existing, new)
    assert "✅" in merged.result


def test_multiple_matches_handled_correctly():
    """Test that multiple new entries matching same existing are handled."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",
        success_count=1,
    )
    new1 = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",  # Same fix
        success_count=2,
    )
    new2 = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",  # Same fix
        success_count=3,
    )

    result = deduplicate_errors_exact([new1, new2], [existing])
    assert len(result) == 1
    # Should merge all three: 1 + 2 + 3 = 6
    assert result[0].success_count == 6


def test_fix_code_normalization():
    """Test that fix code matching normalizes whitespace."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x = 1",
    )
    new = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
        fix_code="x  =  1",  # Different whitespace, but same code
    )

    result = deduplicate_errors_exact([new], [existing])
    assert len(result) == 1  # Should match and merge
    assert result[0].success_count == 2  # 1 + 1
