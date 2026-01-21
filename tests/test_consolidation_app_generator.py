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
