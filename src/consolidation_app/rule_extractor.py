# rule_extractor.py
# Rule extraction from Agent Process Issues for consolidation workflow (Phase 4.5).
# v1.0

"""
Extract general process rules from Agent Process Issue entries using LLM.

Filters entries with is_process_issue=True only, groups by issue type,
and uses LLM to extract actionable rules (title, rule, why, examples, related errors).
Falls back to basic rule extraction (one rule per entry) on LLM failure.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import List

from src.consolidation_app.llm_client import call_llm
from src.consolidation_app.parser import ErrorEntry

logger = logging.getLogger(__name__)


@dataclass
class ProcessRule:
    """Extracted process rule for coding_tips-style documentation."""

    title: str
    rule: str
    why: str
    examples_good: List[str]
    examples_bad: List[str]
    related_errors: List[str]


def _group_by_issue_type(entries: List[ErrorEntry]) -> dict[str, List[ErrorEntry]]:
    """Group process-issue entries by error_type (issue type)."""
    grouped: dict[str, List[ErrorEntry]] = defaultdict(list)
    for entry in entries:
        key = entry.error_type or "General"
        grouped[key].append(entry)
    return grouped


def _build_rule_extraction_prompt(group: List[ErrorEntry]) -> str:
    """
    Build LLM prompt for extracting general rules from a group of process issues.

    Args:
        group: List of process-issue ErrorEntry objects (same issue type).

    Returns:
        Formatted prompt string for LLM.
    """
    parts = [
        "You are given a set of Agent Process Issues (workflow/process problems encountered during coding).",
        "Extract 1–3 general, actionable rules that would prevent or address these issues.",
        "Each rule should have: a short title, a clear rule statement, why it matters, "
        "good/bad examples, and related error signatures.",
        "",
        "Process issues in this group:",
        "",
    ]
    for i, entry in enumerate(group, 1):
        desc = (entry.explanation or "")[:600]
        rule_est = (entry.fix_code or "")[:400]
        sig = (entry.error_signature or entry.error_type or "N/A")[:200]
        parts.append(f"--- Issue {i} ---")
        parts.append(f"Summary: {sig}")
        parts.append(f"Issue Type: {entry.error_type or 'N/A'}")
        parts.append(f"Description: {desc}")
        parts.append(f"Rule Established: {rule_est}")
        if entry.result:
            parts.append(f"Result: {entry.result}")
        parts.append("")

    parts.extend([
        "Respond with a JSON object containing a single key \"rules\" whose value is an array of rule objects.",
        "Each rule object must have:",
        "  - \"title\": short rule title (string)",
        "  - \"rule\": the rule statement (string)",
        "  - \"why\": why this rule is needed (string)",
        "  - \"examples_good\": array of 1–3 good example strings",
        "  - \"examples_bad\": array of 1–3 bad example strings",
        "  - \"related_errors\": array of related error signatures or types (strings)",
        "",
        "Example format:",
        "{\"rules\": [{\"title\": \"Use pathlib for paths\", \"rule\": \"Always use pathlib.Path for file paths.\", "
        "\"why\": \"Avoids string concat and OS differences.\", "
        "\"examples_good\": [\"Path('config') / 'app.yaml'\"], "
        "\"examples_bad\": [\"'config' + '/' + 'app.yaml'\"], "
        "\"related_errors\": [\"FileNotFoundError\", \"path-concatenation\"]}]}",
        "",
        "Only respond with the JSON object, no additional text.",
    ])
    return "\n".join(parts)


def _basic_rule_extraction(group: List[ErrorEntry]) -> List[ProcessRule]:
    """
    Create one ProcessRule per entry without LLM (fallback when LLM fails).

    Uses entry fields directly: title from signature/type, rule from fix_code,
    why from explanation, examples from explanation/result, related_errors from type/signature.
    """
    rules: List[ProcessRule] = []
    for entry in group:
        title = (entry.error_signature or entry.error_type or "Process rule").strip()
        if not title:
            title = "Process rule"
        rule_text = (entry.fix_code or entry.explanation or "Follow established process.").strip()
        why_text = (entry.explanation or entry.fix_code or "Avoid recurrence of this issue.").strip()
        good = [entry.explanation[:200]] if entry.explanation else ["Follows the rule."]
        bad = [entry.result] if entry.result else ["Rule violation observed."]
        related = [entry.error_type] if entry.error_type else []
        if entry.error_signature and entry.error_signature not in related:
            related.append(entry.error_signature)
        rules.append(
            ProcessRule(
                title=title[:200],
                rule=rule_text[:500],
                why=why_text[:500],
                examples_good=good,
                examples_bad=bad,
                related_errors=related[:10],
            )
        )
    return rules


def _parse_llm_rules_response(response: str) -> List[ProcessRule]:
    """
    Parse LLM JSON response into List[ProcessRule].

    Handles markdown code fences. Expects {"rules": [ {...}, ... ]}.
    """
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from LLM response: {text[:300]}") from e

    raw_rules = data.get("rules", [])
    if not isinstance(raw_rules, list):
        logger.warning("LLM returned non-list 'rules': %s", type(raw_rules).__name__)
        return []

    result: List[ProcessRule] = []
    for r in raw_rules:
        if not isinstance(r, dict):
            continue
        title = str(r.get("title", "")).strip() or "Unnamed rule"
        rule = str(r.get("rule", "")).strip() or "Rule statement missing."
        why = str(r.get("why", "")).strip() or "Rationale pending."
        eg = r.get("examples_good", [])
        eb = r.get("examples_bad", [])
        examples_good = [str(x).strip() for x in (eg if isinstance(eg, list) else []) if x]
        examples_bad = [str(x).strip() for x in (eb if isinstance(eb, list) else []) if x]
        if not examples_good:
            examples_good = ["Follows the rule."]
        if not examples_bad:
            examples_bad = ["Rule violation observed."]
        rel = r.get("related_errors", [])
        related_errors = [str(x).strip() for x in (rel if isinstance(rel, list) else []) if x]
        result.append(
            ProcessRule(
                title=title[:200],
                rule=rule[:500],
                why=why[:500],
                examples_good=examples_good[:5],
                examples_bad=examples_bad[:5],
                related_errors=related_errors[:10],
            )
        )
    return result


def extract_rules_from_group(
    group: List[ErrorEntry],
    use_llm: bool = True,
    fallback_to_basic: bool = True,
) -> List[ProcessRule]:
    """
    Extract ProcessRules from a group of process-issue entries.

    Uses LLM when use_llm=True; on failure and fallback_to_basic=True,
    uses basic rule extraction (one rule per entry).

    Args:
        group: List of process-issue ErrorEntry objects.
        use_llm: Whether to call LLM for rule extraction.
        fallback_to_basic: If True, use basic extraction on LLM failure.

    Returns:
        List of ProcessRule objects.
    """
    if not group:
        return []

    if use_llm:
        try:
            prompt = _build_rule_extraction_prompt(group)
            response = call_llm(prompt, task="rule_extraction")
            rules = _parse_llm_rules_response(response)
            if rules:
                logger.debug("Extracted %d rule(s) from group of %d issue(s) via LLM", len(rules), len(group))
                return rules
            logger.warning("LLM returned no valid rules, falling back to basic extraction")
        except Exception as e:
            logger.error(
                "Rule extraction via LLM failed: %s: %s; falling back to basic extraction",
                type(e).__name__,
                e,
            )
            if not fallback_to_basic:
                raise RuntimeError(f"Rule extraction failed: {e}") from e

    if fallback_to_basic:
        rules = _basic_rule_extraction(group)
        logger.debug("Used basic rule extraction: %d rule(s) from %d issue(s)", len(rules), len(group))
        return rules

    return []


def extract_process_rules(
    entries: List[ErrorEntry],
    use_llm: bool = True,
    fallback_to_basic: bool = True,
) -> List[ProcessRule]:
    """
    Extract process rules from entries, using only those with is_process_issue=True.

    Groups by issue type (error_type), then extracts rules per group via LLM
    (or basic extraction on failure).

    Args:
        entries: All parsed ErrorEntry objects.
        use_llm: Whether to use LLM for rule extraction.
        fallback_to_basic: If True, fall back to basic extraction on LLM failure.

    Returns:
        List of ProcessRule objects from all groups.
    """
    process_only = [e for e in entries if e.is_process_issue]
    if not process_only:
        logger.debug("No process issues to extract rules from")
        return []

    grouped = _group_by_issue_type(process_only)
    all_rules: List[ProcessRule] = []
    for issue_type, group in sorted(grouped.items(), key=lambda x: x[0]):
        rules = extract_rules_from_group(
            group,
            use_llm=use_llm,
            fallback_to_basic=fallback_to_basic,
        )
        all_rules.extend(rules)

    logger.info(
        "Extracted %d process rule(s) from %d process issue(s) in %d group(s)",
        len(all_rules),
        len(process_only),
        len(grouped),
    )
    return all_rules
