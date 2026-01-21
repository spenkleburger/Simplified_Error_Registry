"""Tests for the consolidation app generator."""

from datetime import datetime, timezone

from src.consolidation_app import generator
from src.consolidation_app.parser import ErrorEntry


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


def test_generate_fix_repo_single_entry():
    entry = _build_entry(
        signature="ExampleError",
        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
        success_count=1,
    )
    output = generator.generate_fix_repo_markdown([entry])
    assert "# Fix Repository" in output
    assert "Total Entries:** 1" in output
    assert "## ExampleError" in output
    assert "Success Count: 1" in output
    assert "**Projects:** src/app/example.py" in output


def test_generate_fix_repo_multiple_same_error_orders_success_counts():
    entries = [
        _build_entry(
            signature="SameError",
            timestamp=datetime(2025, 1, 2, 10, 0, tzinfo=timezone.utc),
            success_count=1,
        ),
        _build_entry(
            signature="SameError",
            timestamp=datetime(2025, 1, 3, 10, 0, tzinfo=timezone.utc),
            success_count=5,
            tags=["tag-b"],
        ),
    ]
    output = generator.generate_fix_repo_markdown(entries)
    first_index = output.index("Success Count: 5")
    second_index = output.index("Success Count: 1")
    assert first_index < second_index
    assert output.count("## SameError") == 1


def test_generate_fix_repo_multiple_different_errors():
    entries = [
        _build_entry(
            signature="AlphaError",
            timestamp=datetime(2025, 1, 4, 1, 0, tzinfo=timezone.utc),
            success_count=2,
        ),
        _build_entry(
            signature="BetaError",
            timestamp=datetime(2025, 1, 4, 2, 0, tzinfo=timezone.utc),
            success_count=3,
        ),
    ]
    output = generator.generate_fix_repo_markdown(entries)
    assert "## AlphaError" in output
    assert "## BetaError" in output


def test_generate_coding_tips_process_issues():
    issue = _build_entry(
        signature="Process: keep context",
        timestamp=datetime(2025, 2, 1, 9, 0, tzinfo=timezone.utc),
        is_process_issue=True,
        tags=["process"],
        error_type="agent-process",
        result="✅ Documented",
    )
    other = _build_entry(
        signature="Process: ask user",
        timestamp=datetime(2025, 2, 2, 9, 0, tzinfo=timezone.utc),
        is_process_issue=True,
        tags=["process"],
        error_type="agent-process",
        result="✅ Documented",
    )
    output = generator.generate_coding_tips_markdown([issue, other])
    assert "# Coding Tips - Agent Process Rules" in output
    assert "Total Rules:** 2" in output
    assert "## process" in output
    assert "### Rule: Process: keep context" in output
    assert "**Examples:**" in output


def test_generators_handle_empty_inputs():
    assert "Total Entries:** 0" in generator.generate_fix_repo_markdown([])
    assert "##" not in generator.generate_fix_repo_markdown([])
    assert "Total Rules:** 0" in generator.generate_coding_tips_markdown([])
    assert "##" not in generator.generate_coding_tips_markdown([])


def test_format_tags_escapes_backticks():
    """Test that tags with backticks are properly escaped."""
    tags = ["normal-tag", "tag`with`backticks", "another-tag"]
    result = generator.format_tags(tags)
    assert "normal-tag" in result
    assert r"\`" in result  # Escaped backticks
    assert "tag`with`backticks" not in result  # Original not present
    assert "another-tag" in result


def test_format_tags_handles_empty_list():
    """Test that empty tag list returns 'None'."""
    assert generator.format_tags([]) == "None"


def test_header_escaping_in_fix_repo():
    """Test that markdown special characters in error signatures are escaped."""
    entry = _build_entry(
        signature="Error with # special * characters [and] (more)",
        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    output = generator.generate_fix_repo_markdown([entry])
    # Check that special characters are escaped
    assert r"\#" in output or "#" not in output.split("##")[1]  # Escaped in header
    assert r"\*" in output or "*" not in output.split("##")[1]  # Escaped in header


def test_header_escaping_in_coding_tips():
    """Test that markdown special characters in rule titles are escaped."""
    issue = _build_entry(
        signature="Rule with # special * characters",
        timestamp=datetime(2025, 2, 1, 9, 0, tzinfo=timezone.utc),
        is_process_issue=True,
        tags=["process"],
    )
    output = generator.generate_coding_tips_markdown([issue])
    # Check that special characters are escaped in rule title
    assert "### Rule:" in output
    # The escaped version should be present
    assert r"\#" in output or "#" not in output.split("### Rule:")[1].split("\n")[0]


def test_timezone_naive_datetime_handling():
    """Test that naive datetimes are handled (assumed UTC)."""
    naive_dt = datetime(2025, 1, 1, 12, 0)  # No timezone
    entry = _build_entry(
        signature="TestError",
        timestamp=naive_dt,
    )
    output = generator.generate_fix_repo_markdown([entry])
    # Should still generate valid output
    assert "## TestError" in output
    assert "2025-01-01" in output  # Date should be present


def test_empty_optional_fields():
    """Test handling of empty strings in optional fields."""
    entry = ErrorEntry(
        error_signature="MinimalError",
        error_type="",
        file="",
        line=0,
        fix_code="",
        explanation="",
        result="",
        success_count=0,
        tags=[],
        timestamp=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
        is_process_issue=False,
    )
    output = generator.generate_fix_repo_markdown([entry])
    # Should handle gracefully with defaults
    assert "## MinimalError" in output
    assert "Fix" in output  # Default fix description
    assert "Unknown" in output  # Default for missing fields


def test_format_code_block_empty():
    """Test that empty code blocks are handled."""
    result = generator.format_code_block("", "python")
    assert result == "```python\n\n```"


def test_format_code_block_with_content():
    """Test that code blocks with content are formatted correctly."""
    code = "def hello():\n    print('world')"
    result = generator.format_code_block(code, "python")
    assert "```python" in result
    assert code in result
    assert result.endswith("```")
