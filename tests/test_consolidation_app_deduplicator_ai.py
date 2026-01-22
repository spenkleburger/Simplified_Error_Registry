"""Tests for the consolidation app AI deduplicator."""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.consolidation_app.deduplicator_ai import (
    calculate_similarity,
    deduplicate_errors_ai,
)
from src.consolidation_app.parser import ErrorEntry


def _create_entry(
    signature: str = "TestError",
    error_type: str = "TypeError",
    file: str = "test.py",
    line: int = 10,
    fix_code: str = "fix = 1",
    explanation: str = "Test explanation",
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
        explanation=explanation,
        result="✅ Solved",
        success_count=success_count,
        tags=["test"],
        timestamp=timestamp,
        is_process_issue=False,
    )


@patch("src.consolidation_app.deduplicator_ai.call_llm")
def test_calculate_similarity_high_score(mock_call_llm):
    """Test that calculate_similarity returns high score for similar errors."""
    entry1 = _create_entry(
        signature="FileNotFoundError: config.json",
        error_type="FileNotFoundError",
        file="app.py",
        explanation="Cannot find config file",
    )
    entry2 = _create_entry(
        signature="FileNotFoundError: config.json not found",
        error_type="FileNotFoundError",
        file="app.py",
        explanation="Config file missing",
    )

    # Mock LLM response with high similarity
    mock_response = json.dumps(
        {
            "similarity": 0.95,
            "reason": "Both are FileNotFoundError for config.json",
        }
    )
    mock_call_llm.return_value = mock_response

    similarity = calculate_similarity(entry1, entry2)

    assert similarity == 0.95
    mock_call_llm.assert_called_once()
    call_args = mock_call_llm.call_args
    assert call_args[1]["task"] == "deduplication"


@patch("src.consolidation_app.deduplicator_ai.call_llm")
def test_calculate_similarity_low_score(mock_call_llm):
    """Test that calculate_similarity returns low score for different errors."""
    entry1 = _create_entry(
        signature="TypeError: cannot add int and str",
        error_type="TypeError",
    )
    entry2 = _create_entry(
        signature="FileNotFoundError: missing file",
        error_type="FileNotFoundError",
    )

    # Mock LLM response with low similarity
    mock_response = json.dumps(
        {
            "similarity": 0.2,
            "reason": "Completely different error types",
        }
    )
    mock_call_llm.return_value = mock_response

    similarity = calculate_similarity(entry1, entry2)

    assert similarity == 0.2


@patch("src.consolidation_app.deduplicator_ai.call_llm")
def test_calculate_similarity_with_markdown_code_block(mock_call_llm):
    """Test that calculate_similarity handles markdown code blocks in response."""
    entry1 = _create_entry()
    entry2 = _create_entry()

    # Mock LLM response wrapped in markdown code block
    mock_response = (
        "```json\n" + json.dumps({"similarity": 0.85, "reason": "Similar"}) + "\n```"
    )
    mock_call_llm.return_value = mock_response

    similarity = calculate_similarity(entry1, entry2)

    assert similarity == 0.85


@patch("src.consolidation_app.deduplicator_ai.call_llm")
def test_calculate_similarity_clamps_invalid_scores(mock_call_llm):
    """Test that calculate_similarity clamps invalid scores to [0.0, 1.0]."""
    entry1 = _create_entry()
    entry2 = _create_entry()

    # Test score > 1.0
    mock_response = json.dumps({"similarity": 1.5, "reason": "Test"})
    mock_call_llm.return_value = mock_response

    similarity = calculate_similarity(entry1, entry2)
    assert similarity == 1.0

    # Test score < 0.0
    mock_response = json.dumps({"similarity": -0.5, "reason": "Test"})
    mock_call_llm.return_value = mock_response

    similarity = calculate_similarity(entry1, entry2)
    assert similarity == 0.0


@patch("src.consolidation_app.deduplicator_ai.call_llm")
def test_calculate_similarity_handles_missing_similarity_field(mock_call_llm):
    """Test that calculate_similarity handles missing similarity field."""
    entry1 = _create_entry()
    entry2 = _create_entry()

    mock_response = json.dumps({"reason": "No similarity field"})
    mock_call_llm.return_value = mock_response

    similarity = calculate_similarity(entry1, entry2)
    assert similarity == 0.0


@patch("src.consolidation_app.deduplicator_ai.call_llm")
def test_calculate_similarity_raises_on_llm_failure(mock_call_llm):
    """Test that calculate_similarity raises RuntimeError on LLM failure."""
    entry1 = _create_entry()
    entry2 = _create_entry()

    mock_call_llm.side_effect = ConnectionError("LLM service unavailable")

    with pytest.raises(RuntimeError, match="LLM similarity calculation failed"):
        calculate_similarity(entry1, entry2)


@patch("src.consolidation_app.deduplicator_ai.calculate_similarity")
def test_deduplicate_errors_ai_merges_similar_entries(mock_calc_sim):
    """Test that deduplicate_errors_ai merges entries with similarity >= threshold."""
    existing = _create_entry(
        signature="FileNotFoundError: config.json",
        error_type="FileNotFoundError",
        file="app.py",
        fix_code="config = load_config()",
        success_count=3,
    )
    new = _create_entry(
        signature="FileNotFoundError: config.json not found",
        error_type="FileNotFoundError",
        file="app.py",
        fix_code="config = load_config()",  # Same fix
        success_count=2,
    )

    # Mock high similarity
    mock_calc_sim.return_value = 0.95

    result = deduplicate_errors_ai([new], [existing], similarity_threshold=0.85)

    assert len(result) == 1
    merged = result[0]
    assert merged.success_count == 5  # 3 + 2
    assert merged.error_signature == existing.error_signature


@patch("src.consolidation_app.deduplicator_ai.calculate_similarity")
def test_deduplicate_errors_ai_keeps_different_entries_separate(mock_calc_sim):
    """Test that deduplicate_errors_ai keeps entries with similarity < threshold separate."""
    existing = _create_entry(
        signature="TypeError: cannot add int and str",
        error_type="TypeError",
    )
    new = _create_entry(
        signature="FileNotFoundError: missing file",
        error_type="FileNotFoundError",
    )

    # Mock low similarity
    mock_calc_sim.return_value = 0.3

    result = deduplicate_errors_ai([new], [existing], similarity_threshold=0.85)

    assert len(result) == 2
    signatures = [e.error_signature for e in result]
    assert "TypeError: cannot add int and str" in signatures
    assert "FileNotFoundError: missing file" in signatures


@patch("src.consolidation_app.deduplicator_ai.calculate_similarity")
def test_deduplicate_errors_ai_handles_variant_fixes(mock_calc_sim):
    """Test that deduplicate_errors_ai keeps variant fixes separate."""
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

    # Mock high similarity (same error, different fix)
    mock_calc_sim.return_value = 0.95

    result = deduplicate_errors_ai([new], [existing], similarity_threshold=0.85)

    assert len(result) == 2  # Both kept as variants
    fix_codes = [e.fix_code for e in result]
    assert "x = 1" in fix_codes
    assert "x = 2" in fix_codes


@patch("src.consolidation_app.deduplicator_ai.calculate_similarity")
def test_deduplicate_errors_ai_selects_best_match(mock_calc_sim):
    """Test that deduplicate_errors_ai selects the entry with highest similarity."""
    existing1 = _create_entry(
        signature="Error1",
        success_count=1,
    )
    existing2 = _create_entry(
        signature="Error2",
        success_count=2,
    )
    new = _create_entry(
        signature="Error3",
        fix_code="same fix",
        success_count=3,
    )

    # Mock different similarities
    def mock_similarity(entry1, entry2):
        if entry2.error_signature == "Error1":
            return 0.80  # Below threshold
        elif entry2.error_signature == "Error2":
            return 0.90  # Above threshold, best match
        return 0.0

    mock_calc_sim.side_effect = mock_similarity

    # Set same fix code for existing2 to allow merge
    existing2 = _create_entry(
        signature="Error2",
        fix_code="same fix",
        success_count=2,
    )

    result = deduplicate_errors_ai(
        [new],
        [existing1, existing2],
        similarity_threshold=0.85,
    )

    # Should merge with existing2 (best match)
    assert len(result) == 2  # existing1 + merged existing2/new
    # Find merged entry
    merged = next((e for e in result if e.error_signature == "Error2"), None)
    assert merged is not None
    assert merged.success_count == 5  # 2 + 3


@patch("src.consolidation_app.deduplicator_ai.calculate_similarity")
def test_deduplicate_errors_ai_fallback_to_exact_on_llm_failure(mock_calc_sim):
    """Test that deduplicate_errors_ai falls back to exact match on LLM failure."""
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
        fix_code="x = 1",  # Same fix, should merge
        success_count=2,
    )

    # Mock LLM failure
    mock_calc_sim.side_effect = RuntimeError("LLM service unavailable")

    result = deduplicate_errors_ai(
        [new],
        [existing],
        similarity_threshold=0.85,
        fallback_to_exact=True,
    )

    # Should fall back to exact match and merge
    assert len(result) == 1
    assert result[0].success_count == 5  # 3 + 2


@patch("src.consolidation_app.deduplicator_ai.calculate_similarity")
def test_deduplicate_errors_ai_no_fallback_on_llm_failure(mock_calc_sim):
    """Test that deduplicate_errors_ai adds as new when fallback disabled."""
    existing = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
    )
    new = _create_entry(
        signature="TypeError: test",
        error_type="TypeError",
        file="test.py",
    )

    # Mock LLM failure
    mock_calc_sim.side_effect = RuntimeError("LLM service unavailable")

    result = deduplicate_errors_ai(
        [new],
        [existing],
        similarity_threshold=0.85,
        fallback_to_exact=False,
    )

    # Should add as new entry (no fallback)
    assert len(result) == 2


def test_deduplicate_errors_ai_empty_new_entries():
    """Test that empty new entries list returns existing unchanged."""
    existing = [
        _create_entry(signature="Error1"),
        _create_entry(signature="Error2"),
    ]

    result = deduplicate_errors_ai([], existing)
    assert len(result) == 2
    assert result == existing


def test_deduplicate_errors_ai_empty_existing_entries():
    """Test that empty existing entries list returns all new entries."""
    new = [
        _create_entry(signature="Error1"),
        _create_entry(signature="Error2"),
    ]

    result = deduplicate_errors_ai(new, [])
    assert len(result) == 2
    assert result == new


def test_deduplicate_errors_ai_validates_threshold():
    """Test that deduplicate_errors_ai validates and clamps threshold."""
    existing = _create_entry()
    new = _create_entry()

    # Test threshold > 1.0 (should use default)
    result = deduplicate_errors_ai([new], [existing], similarity_threshold=1.5)
    # Should still process (threshold clamped internally)
    assert len(result) >= 1

    # Test threshold < 0.0 (should use default)
    result = deduplicate_errors_ai([new], [existing], similarity_threshold=-0.5)
    # Should still process (threshold clamped internally)
    assert len(result) >= 1


@patch("src.consolidation_app.deduplicator_ai.calculate_similarity")
def test_deduplicate_errors_ai_handles_partial_llm_failures(mock_calc_sim):
    """Test that deduplicate_errors_ai handles partial LLM failures gracefully."""
    existing1 = _create_entry(signature="Error1")
    existing2 = _create_entry(signature="Error2")
    new = _create_entry(signature="Error3")

    # Mock: first comparison fails, second succeeds
    call_count = 0

    def mock_similarity(entry1, entry2):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("First comparison failed")
        return 0.3  # Low similarity, no match

    mock_calc_sim.side_effect = mock_similarity

    result = deduplicate_errors_ai(
        [new],
        [existing1, existing2],
        similarity_threshold=0.85,
        fallback_to_exact=False,
    )

    # Should continue processing and add as new entry
    assert len(result) == 3
    assert call_count == 2  # Should have tried both existing entries
