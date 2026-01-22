"""Tests for the consolidation app rule extractor (Phase 4.5)."""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.consolidation_app.parser import ErrorEntry
from src.consolidation_app.rule_extractor import (
    ProcessRule,
    _basic_rule_extraction,
    _group_by_issue_type,
    _parse_llm_rules_response,
    extract_process_rules,
    extract_rules_from_group,
)


def _process_issue(
    signature: str = "Use pathlib for paths",
    issue_type: str = "agent-process",
    description: str = "Agent used string concatenation for paths.",
    rule: str = "Use pathlib.Path for file paths.",
    result: str = "Rule established.",
    tags: list[str] | None = None,
) -> ErrorEntry:
    """Create a process-issue ErrorEntry."""
    return ErrorEntry(
        error_signature=signature,
        error_type=issue_type,
        file="",
        line=0,
        fix_code=rule,
        explanation=description,
        result=result,
        success_count=0,
        tags=tags or [],
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        is_process_issue=True,
    )


def _error_entry(signature: str = "TypeError", error_type: str = "TypeError") -> ErrorEntry:
    """Create a non–process-issue ErrorEntry."""
    return ErrorEntry(
        error_signature=signature,
        error_type=error_type,
        file="foo.py",
        line=1,
        fix_code="x = 1",
        explanation="Test",
        result="✅ Solved",
        success_count=1,
        tags=[],
        timestamp=datetime(2025, 1, 1),
        is_process_issue=False,
    )


def test_group_by_issue_type():
    """Test grouping process issues by error_type (issue type)."""
    a = _process_issue(issue_type="path-handling")
    b = _process_issue(issue_type="path-handling", signature="Avoid os.path")
    c = _process_issue(issue_type="docker")
    grouped = _group_by_issue_type([a, b, c])
    assert set(grouped.keys()) == {"path-handling", "docker"}
    assert len(grouped["path-handling"]) == 2
    assert len(grouped["docker"]) == 1


def test_group_by_issue_type_general_for_empty_type():
    """Test that missing error_type becomes 'General'."""
    a = _process_issue(issue_type="")
    grouped = _group_by_issue_type([a])
    assert "General" in grouped
    assert grouped["General"][0] == a


def test_extract_process_rules_filters_non_process_issues():
    """Test that extract_process_rules only processes is_process_issue=True."""
    err = _error_entry()
    proc = _process_issue()
    with patch("src.consolidation_app.rule_extractor.call_llm") as mock_llm:
        mock_llm.return_value = json.dumps({
            "rules": [{
                "title": "R",
                "rule": "Do X.",
                "why": "Because.",
                "examples_good": ["ok"],
                "examples_bad": ["bad"],
                "related_errors": [],
            }],
        })
        rules = extract_process_rules([err, proc], use_llm=True, fallback_to_basic=False)
    assert len(rules) == 1
    assert rules[0].title == "R"
    mock_llm.assert_called_once()


def test_extract_process_rules_empty_if_no_process_issues():
    """Test that extract_process_rules returns [] when no process issues."""
    rules = extract_process_rules([_error_entry(), _error_entry()])
    assert rules == []


def test_extract_process_rules_groups_and_extracts():
    """Test grouping by issue type and extracting rules per group."""
    g1a = _process_issue(issue_type="paths", signature="Path A")
    g1b = _process_issue(issue_type="paths", signature="Path B")
    g2 = _process_issue(issue_type="docker", signature="Docker rule")
    with patch("src.consolidation_app.rule_extractor.call_llm") as mock_llm:
        def side_effect(prompt, task):
            # Discriminate by "Issue Type: X" (unique per group). Avoid "path"/"paths":
            # the shared template contains "pathlib.Path" and "file paths".
            if "Issue Type: paths" in prompt:
                return json.dumps({
                    "rules": [{
                        "title": "Path rule",
                        "rule": "Use pathlib.",
                        "why": "Cross-platform.",
                        "examples_good": ["Path('x')"],
                        "examples_bad": ["'x'"],
                        "related_errors": ["FileNotFoundError"],
                    }],
                })
            if "Issue Type: docker" in prompt:
                return json.dumps({
                    "rules": [{
                        "title": "Docker rule",
                        "rule": "Use docker compose.",
                        "why": "Reproducibility.",
                        "examples_good": ["docker compose up"],
                        "examples_bad": ["manual run"],
                        "related_errors": [],
                    }],
                })
            raise ValueError("Unexpected prompt: no known issue type")

        mock_llm.side_effect = side_effect
        rules = extract_process_rules([g1a, g1b, g2], use_llm=True, fallback_to_basic=False)

    assert len(rules) == 2
    titles = {r.title for r in rules}
    assert "Path rule" in titles
    assert "Docker rule" in titles
    assert mock_llm.call_count == 2


@patch("src.consolidation_app.rule_extractor.call_llm")
def test_extract_rules_from_group_llm_success(mock_call_llm):
    """Test extract_rules_from_group with valid LLM response."""
    group = [
        _process_issue(signature="S1", rule="R1"),
        _process_issue(signature="S2", rule="R2"),
    ]
    mock_call_llm.return_value = json.dumps({
        "rules": [
            {
                "title": "T1",
                "rule": "Rule 1.",
                "why": "Why 1.",
                "examples_good": ["g1"],
                "examples_bad": ["b1"],
                "related_errors": ["e1"],
            },
        ],
    })

    rules = extract_rules_from_group(group, use_llm=True, fallback_to_basic=False)

    assert len(rules) == 1
    assert rules[0].title == "T1"
    assert rules[0].rule == "Rule 1."
    assert rules[0].why == "Why 1."
    assert rules[0].examples_good == ["g1"]
    assert rules[0].examples_bad == ["b1"]
    assert rules[0].related_errors == ["e1"]
    mock_call_llm.assert_called_once()
    assert mock_call_llm.call_args[1]["task"] == "rule_extraction"


@patch("src.consolidation_app.rule_extractor.call_llm")
def test_extract_rules_from_group_markdown_code_block(mock_call_llm):
    """Test that LLM response with markdown code fence is parsed."""
    group = [_process_issue()]
    raw = json.dumps({
        "rules": [{
            "title": "T",
            "rule": "R",
            "why": "W",
            "examples_good": ["g"],
            "examples_bad": ["b"],
            "related_errors": [],
        }],
    })
    mock_call_llm.return_value = "```json\n" + raw + "\n```"

    rules = extract_rules_from_group(group, use_llm=True, fallback_to_basic=False)

    assert len(rules) == 1
    assert rules[0].title == "T"


def test_extract_rules_from_group_empty():
    """Test extract_rules_from_group returns [] for empty group."""
    assert extract_rules_from_group([]) == []


@patch("src.consolidation_app.rule_extractor.call_llm")
def test_extract_rules_from_group_llm_failure_fallback(mock_call_llm):
    """Test fallback to basic extraction when LLM fails."""
    mock_call_llm.side_effect = RuntimeError("LLM unavailable")
    group = [
        _process_issue(signature="Sig1", rule="Rule1", description="Desc1", result="Res1"),
    ]

    rules = extract_rules_from_group(group, use_llm=True, fallback_to_basic=True)

    assert len(rules) == 1
    assert rules[0].title == "Sig1"
    assert rules[0].rule == "Rule1"
    assert rules[0].why == "Desc1"
    assert rules[0].examples_bad == ["Res1"]


@patch("src.consolidation_app.rule_extractor.call_llm")
def test_extract_rules_from_group_llm_failure_no_fallback_raises(mock_call_llm):
    """Test that LLM failure raises when fallback_to_basic=False."""
    mock_call_llm.side_effect = RuntimeError("LLM unavailable")
    group = [_process_issue()]

    with pytest.raises(RuntimeError, match="Rule extraction failed"):
        extract_rules_from_group(group, use_llm=True, fallback_to_basic=False)


@patch("src.consolidation_app.rule_extractor.call_llm")
def test_extract_rules_from_group_malformed_json_fallback(mock_call_llm):
    """Test fallback to basic extraction on malformed JSON."""
    mock_call_llm.return_value = "not valid json at all"
    group = [_process_issue(signature="X", rule="Y")]

    rules = extract_rules_from_group(group, use_llm=True, fallback_to_basic=True)

    assert len(rules) == 1
    assert rules[0].title == "X"
    assert rules[0].rule == "Y"


def test_basic_rule_extraction():
    """Test _basic_rule_extraction produces one rule per entry."""
    a = _process_issue(signature="A", rule="Ra", description="Da", result="Ok")
    b = _process_issue(signature="B", rule="Rb", issue_type="t2")

    rules = _basic_rule_extraction([a, b])

    assert len(rules) == 2
    assert rules[0].title == "A"
    assert rules[0].rule == "Ra"
    assert rules[0].why == "Da"
    assert "Ok" in rules[0].examples_bad
    assert rules[1].title == "B"
    assert rules[1].rule == "Rb"
    assert "t2" in rules[1].related_errors


def test_basic_rule_extraction_empty():
    """Test _basic_rule_extraction returns [] for empty group."""
    assert _basic_rule_extraction([]) == []


def test_parse_llm_rules_response_valid():
    """Test _parse_llm_rules_response with valid JSON."""
    raw = json.dumps({
        "rules": [
            {
                "title": "T",
                "rule": "R",
                "why": "W",
                "examples_good": ["g1", "g2"],
                "examples_bad": ["b1"],
                "related_errors": ["e1"],
            },
        ],
    })
    rules = _parse_llm_rules_response(raw)
    assert len(rules) == 1
    assert rules[0].examples_good == ["g1", "g2"]
    assert rules[0].examples_bad == ["b1"]


def test_parse_llm_rules_response_defaults():
    """Test defaults when optional fields missing."""
    raw = json.dumps({
        "rules": [{
            "title": "T",
            "rule": "R",
            "why": "",
            "examples_good": [],
            "examples_bad": [],
            "related_errors": [],
        }],
    })
    rules = _parse_llm_rules_response(raw)
    assert len(rules) == 1
    assert rules[0].why == "Rationale pending."
    assert rules[0].examples_good == ["Follows the rule."]
    assert rules[0].examples_bad == ["Rule violation observed."]


def test_parse_llm_rules_response_invalid_json_raises():
    """Test _parse_llm_rules_response raises on invalid JSON."""
    with pytest.raises(ValueError, match="Could not parse JSON"):
        _parse_llm_rules_response("not json")


def test_parse_llm_rules_response_empty_rules():
    """Test _parse_llm_rules_response returns [] when rules is empty."""
    raw = json.dumps({"rules": []})
    assert _parse_llm_rules_response(raw) == []


def test_process_rule_dataclass():
    """Test ProcessRule structure."""
    r = ProcessRule(
        title="T",
        rule="R",
        why="W",
        examples_good=["g"],
        examples_bad=["b"],
        related_errors=["e"],
    )
    assert r.title == "T"
    assert r.rule == "R"
    assert r.why == "W"
    assert r.examples_good == ["g"]
    assert r.examples_bad == ["b"]
    assert r.related_errors == ["e"]


@patch("src.consolidation_app.rule_extractor.call_llm")
def test_extract_rules_from_group_no_llm_uses_basic(mock_call_llm):
    """Test extract_rules_from_group with use_llm=False uses basic extraction."""
    group = [_process_issue(signature="S", rule="R")]
    rules = extract_rules_from_group(group, use_llm=False, fallback_to_basic=True)
    assert len(rules) == 1
    assert rules[0].title == "S"
    mock_call_llm.assert_not_called()
