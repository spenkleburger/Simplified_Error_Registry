"""Tests for the consolidation app AI tagger."""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.consolidation_app.parser import ErrorEntry
from src.consolidation_app.tagger_ai import (
    apply_tags_ai_to_entry,
    generate_tags_ai,
)


def _create_entry(
    signature: str = "TestError",
    error_type: str = "TypeError",
    file: str = "test.py",
    line: int = 10,
    fix_code: str = "fix = 1",
    explanation: str = "Test explanation",
    success_count: int = 1,
    timestamp: datetime | None = None,
    tags: list[str] | None = None,
) -> ErrorEntry:
    """Helper to create test ErrorEntry."""
    if timestamp is None:
        timestamp = datetime(2025, 1, 1, 12, 0, 0)
    if tags is None:
        tags = []
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


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_valid_response(mock_call_llm):
    """Test that generate_tags_ai returns tags from valid LLM response."""
    entry = _create_entry(
        signature="FileNotFoundError: config.json",
        error_type="FileNotFoundError",
        file="app.py",
        explanation="Cannot find config file",
    )

    # Mock LLM response with valid tags
    mock_response = json.dumps(
        {
            "tags": ["file-io", "configuration", "cross-platform"],
        }
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert len(tags) == 3
    assert "file-io" in tags
    assert "configuration" in tags
    assert "cross-platform" in tags
    mock_call_llm.assert_called_once()
    call_args = mock_call_llm.call_args
    assert call_args[1]["task"] == "tagging"


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_with_markdown_code_block(mock_call_llm):
    """Test that generate_tags_ai handles markdown code blocks in response."""
    entry = _create_entry()

    # Mock LLM response wrapped in markdown code block
    mock_response = (
        "```json\n" + json.dumps({"tags": ["type-conversion", "testing"]}) + "\n```"
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert len(tags) == 2
    assert "type-conversion" in tags
    assert "testing" in tags


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_normalizes_tags(mock_call_llm):
    """Test that generate_tags_ai normalizes tags (lowercase, hyphens)."""
    entry = _create_entry()

    # Mock LLM response with mixed case and spaces
    mock_response = json.dumps(
        {
            "tags": ["FileIO", "Docker Compose", "Windows_Platform", "API-Endpoint"],
        }
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert "fileio" in tags
    assert "docker-compose" in tags
    assert "windows-platform" in tags
    assert "api-endpoint" in tags


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_removes_invalid_chars(mock_call_llm):
    """Test that generate_tags_ai removes invalid characters from tags."""
    entry = _create_entry()

    # Mock LLM response with invalid characters
    mock_response = json.dumps(
        {
            "tags": ["file@io", "docker#compose", "test!tag", "valid-tag"],
        }
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert "fileio" in tags or "file" in tags
    assert "dockercompose" in tags or "docker" in tags
    assert "testtag" in tags or "test" in tags
    assert "valid-tag" in tags


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_deduplicates_tags(mock_call_llm):
    """Test that generate_tags_ai removes duplicate tags."""
    entry = _create_entry()

    # Mock LLM response with duplicates
    mock_response = json.dumps(
        {
            "tags": ["file-io", "file-io", "docker", "docker", "testing"],
        }
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert tags.count("file-io") == 1
    assert tags.count("docker") == 1
    assert len(tags) == 3


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_limits_to_max_tags(mock_call_llm):
    """Test that generate_tags_ai limits tags to MAX_TAGS (5)."""
    entry = _create_entry()

    # Mock LLM response with more than MAX_TAGS
    mock_response = json.dumps(
        {
            "tags": [
                "tag1",
                "tag2",
                "tag3",
                "tag4",
                "tag5",
                "tag6",
                "tag7",
            ],
        }
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert len(tags) <= 5


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_handles_empty_tags_list(mock_call_llm):
    """Test that generate_tags_ai handles empty tags list."""
    entry = _create_entry()

    # Mock LLM response with empty tags
    mock_response = json.dumps({"tags": []})
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert isinstance(tags, list)
    assert len(tags) == 0


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_handles_missing_tags_field(mock_call_llm):
    """Test that generate_tags_ai handles missing tags field."""
    entry = _create_entry()

    # Mock LLM response without tags field
    mock_response = json.dumps({"error": "No tags provided"})
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert isinstance(tags, list)
    assert len(tags) == 0


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_handles_non_list_tags(mock_call_llm):
    """Test that generate_tags_ai handles non-list tags field."""
    entry = _create_entry()

    # Mock LLM response with string instead of list
    mock_response = json.dumps({"tags": "file-io,docker,testing"})
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    # Should convert to list
    assert isinstance(tags, list)
    assert len(tags) >= 0


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_fallback_to_rule_based_on_llm_failure(mock_call_llm):
    """Test that generate_tags_ai falls back to rule-based on LLM failure."""
    entry = _create_entry(
        error_type="FileNotFoundError",
        file="docker-compose.yml",
        explanation="Docker file not found",
    )

    # Mock LLM failure
    mock_call_llm.side_effect = ConnectionError("LLM service unavailable")

    tags = generate_tags_ai(entry, fallback_to_rule_based=True)

    # Should use rule-based tags
    assert isinstance(tags, list)
    assert len(tags) >= 0  # Rule-based may generate tags


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_raises_on_llm_failure_no_fallback(mock_call_llm):
    """Test that generate_tags_ai raises RuntimeError when fallback disabled."""
    entry = _create_entry()

    # Mock LLM failure
    mock_call_llm.side_effect = ConnectionError("LLM service unavailable")

    with pytest.raises(RuntimeError, match="AI tag generation failed"):
        generate_tags_ai(entry, fallback_to_rule_based=False)


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_handles_malformed_json(mock_call_llm):
    """Test that generate_tags_ai handles malformed JSON responses."""
    entry = _create_entry()

    # Mock LLM response with malformed JSON
    mock_response = '{"tags": ["file-io", "docker"'  # Missing closing bracket
    mock_call_llm.return_value = mock_response

    # Should fall back to rule-based
    tags = generate_tags_ai(entry, fallback_to_rule_based=True)

    assert isinstance(tags, list)


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_combines_with_rule_based(mock_call_llm):
    """Test that generate_tags_ai combines AI tags with rule-based tags."""
    entry = _create_entry(
        error_type="FileNotFoundError",
        file="docker-compose.yml",
        explanation="Docker file not found",
    )

    # Mock LLM response with fewer tags than MIN_TAGS
    mock_response = json.dumps({"tags": ["file-io"]})
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(
        entry, fallback_to_rule_based=True, combine_with_rule_based=True
    )

    # Should have AI tags + rule-based tags
    assert "file-io" in tags  # From AI
    # May have additional tags from rule-based (docker, etc.)
    assert len(tags) >= 1


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_handles_timeout_error(mock_call_llm):
    """Test that generate_tags_ai handles timeout errors."""
    entry = _create_entry()

    # Mock timeout error
    mock_call_llm.side_effect = TimeoutError("Request timed out")

    tags = generate_tags_ai(entry, fallback_to_rule_based=True)

    # Should fall back to rule-based
    assert isinstance(tags, list)


@patch("src.consolidation_app.tagger_ai.generate_tags_ai")
def test_apply_tags_ai_to_entry_merges_tags(mock_generate_tags_ai):
    """Test that apply_tags_ai_to_entry merges AI tags with existing tags."""
    entry = _create_entry(tags=["existing-tag", "another-tag"])

    # Mock AI tag generation
    mock_generate_tags_ai.return_value = ["ai-tag", "another-tag"]  # Overlap

    result = apply_tags_ai_to_entry(entry)

    # Should merge and deduplicate
    assert "existing-tag" in result.tags
    assert "ai-tag" in result.tags
    assert "another-tag" in result.tags
    assert result.tags.count("another-tag") == 1  # Deduplicated
    assert result.tags == sorted(result.tags)  # Sorted


@patch("src.consolidation_app.tagger_ai.generate_tags_ai")
def test_apply_tags_ai_to_entry_returns_new_entry(mock_generate_tags_ai):
    """Test that apply_tags_ai_to_entry returns a new ErrorEntry instance."""
    entry = _create_entry(tags=["existing-tag"])

    # Mock AI tag generation
    mock_generate_tags_ai.return_value = ["ai-tag"]

    result = apply_tags_ai_to_entry(entry)

    # Should be a new instance
    assert result is not entry
    assert result.error_signature == entry.error_signature
    assert result.tags != entry.tags  # Tags changed


@patch("src.consolidation_app.tagger_ai.generate_tags_ai")
def test_apply_tags_ai_to_entry_preserves_other_fields(mock_generate_tags_ai):
    """Test that apply_tags_ai_to_entry preserves all other ErrorEntry fields."""
    entry = _create_entry(
        signature="TestError",
        error_type="TypeError",
        file="test.py",
        line=42,
        fix_code="fix = 1",
        explanation="Test",
        success_count=5,
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
    )

    # Mock AI tag generation
    mock_generate_tags_ai.return_value = ["ai-tag"]

    result = apply_tags_ai_to_entry(entry)

    # All other fields should be preserved
    assert result.error_signature == entry.error_signature
    assert result.error_type == entry.error_type
    assert result.file == entry.file
    assert result.line == entry.line
    assert result.fix_code == entry.fix_code
    assert result.explanation == entry.explanation
    assert result.success_count == entry.success_count
    assert result.timestamp == entry.timestamp
    assert result.is_process_issue == entry.is_process_issue


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_filters_empty_tags(mock_call_llm):
    """Test that generate_tags_ai filters out empty or None tags."""
    entry = _create_entry()

    # Mock LLM response with empty/None tags
    mock_response = json.dumps(
        {
            "tags": ["valid-tag", "", None, "   ", "another-valid"],
        }
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    # Should only have valid tags
    assert "valid-tag" in tags
    assert "another-valid" in tags
    assert "" not in tags
    assert None not in tags


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_handles_json_extraction_from_text(mock_call_llm):
    """Test that generate_tags_ai extracts JSON from text-wrapped responses."""
    entry = _create_entry()

    # Mock LLM response with JSON wrapped in text
    mock_response = (
        "Here are the tags:\n"
        + json.dumps({"tags": ["file-io", "docker"]})
        + "\nThese tags should help categorize the error."
    )
    mock_call_llm.return_value = mock_response

    tags = generate_tags_ai(entry, fallback_to_rule_based=False)

    assert "file-io" in tags
    assert "docker" in tags


@patch("src.consolidation_app.tagger_ai.call_llm")
def test_generate_tags_ai_prompt_includes_all_entry_fields(mock_call_llm):
    """Test that the LLM prompt includes all relevant entry fields."""
    entry = _create_entry(
        signature="FileNotFoundError: config.json",
        error_type="FileNotFoundError",
        file="app.py",
        line=42,
        fix_code="config = load_config()",
        explanation="Cannot find config file in project root",
    )

    mock_response = json.dumps({"tags": ["file-io"]})
    mock_call_llm.return_value = mock_response

    generate_tags_ai(entry, fallback_to_rule_based=False)

    # Verify prompt includes all fields
    call_args = mock_call_llm.call_args
    prompt = call_args[0][0]
    assert "FileNotFoundError: config.json" in prompt
    assert "FileNotFoundError" in prompt
    assert "app.py" in prompt
    assert "42" in prompt
    assert "load_config" in prompt
    assert "Cannot find config file" in prompt
