# merger.py
# Fix merging logic: group by code similarity, merge same fixes, keep variants (Phase 4.4).
# v1.0

"""
Group fixes by fuzzy code similarity, merge identical fixes (increment success_count),
keep different fixes as variants. Sort merged fixes by success_count (highest first).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List

from src.consolidation_app.parser import ErrorEntry

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.9


@dataclass
class Fix:
    """Minimal fix representation for similarity grouping and merging."""

    fix_code: str
    explanation: str
    result: str
    success_count: int
    error_type: str
    file: str
    line: int
    tags: List[str]


def _normalize_code(code: str) -> str:
    """Normalize fix code for comparison: whitespace, strip line comments."""
    if not code:
        return ""
    # Remove # line comments (rest of line)
    lines = []
    for line in code.splitlines():
        # Naive: strip from # not inside string (good enough for fuzzy match)
        idx = line.find("#")
        if idx >= 0:
            line = line[:idx]
        lines.append(line)
    text = "\n".join(lines)
    # Collapse whitespace: normalize newlines and spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_fix_similarity(fix1: Fix, fix2: Fix) -> float:
    """
    Compare two fixes by normalized code; return similarity 0.0–1.0.

    Normalizes code (whitespace, line comments) then uses sequence matching.

    Args:
        fix1: First fix.
        fix2: Second fix.

    Returns:
        Similarity score in [0.0, 1.0].
    """
    n1 = _normalize_code(fix1.fix_code)
    n2 = _normalize_code(fix2.fix_code)
    if not n1 and not n2:
        return 1.0
    if not n1 or not n2:
        return 0.0
    matcher = SequenceMatcher(None, n1, n2)
    return matcher.ratio()


def group_similar_fixes(fixes: List[Fix], threshold: float = SIMILARITY_THRESHOLD) -> List[List[Fix]]:
    """
    Group fixes by code similarity (fuzzy match).

    Puts fixes with similarity > threshold in the same group. Uses first-fit:
    each fix joins the first group with at least one member above threshold, else new group.

    Args:
        fixes: List of Fix objects.
        threshold: Minimum similarity to group (default 0.9).

    Returns:
        List of groups, each group a list of Fix.
    """
    if not fixes:
        return []

    groups: List[List[Fix]] = []

    for fix in fixes:
        placed = False
        for group in groups:
            for member in group:
                if calculate_fix_similarity(fix, member) >= threshold:
                    group.append(fix)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            groups.append([fix])

    return groups


def _entry_to_fix(entry: ErrorEntry) -> Fix:
    """Build Fix from ErrorEntry."""
    return Fix(
        fix_code=entry.fix_code or "",
        explanation=entry.explanation or "",
        result=entry.result or "",
        success_count=entry.success_count,
        error_type=entry.error_type or "",
        file=entry.file or "",
        line=entry.line or 0,
        tags=list(entry.tags) if entry.tags else [],
    )


def _merge_fix_group(
    group: List[Fix],
    template: ErrorEntry,
) -> ErrorEntry:
    """Merge a group of similar fixes into one ErrorEntry. Template supplies metadata."""
    total_success = sum(f.success_count for f in group)
    canonical = max(group, key=lambda f: (f.success_count, len(f.fix_code)))
    all_tags = [tag for f in group for tag in f.tags]
    merged_tags = sorted(set(all_tags)) if all_tags else list(template.tags)
    if not merged_tags and template.tags:
        merged_tags = sorted(set(template.tags))
    best_result = canonical.result
    for f in group:
        if "✅" in f.result:
            best_result = f.result
            break
    return ErrorEntry(
        error_signature=template.error_signature,
        error_type=canonical.error_type or template.error_type,
        file=template.file,
        line=template.line,
        fix_code=canonical.fix_code,
        explanation=canonical.explanation or template.explanation,
        result=best_result,
        success_count=total_success,
        tags=merged_tags,
        timestamp=template.timestamp,
        is_process_issue=template.is_process_issue,
    )


def merge_fixes(entries: List[ErrorEntry], threshold: float = SIMILARITY_THRESHOLD) -> List[ErrorEntry]:
    """
    Group fixes by code similarity, merge same fixes, keep variants, sort by success_count.

    Expects entries that share the same (error_signature, error_type, file). Groups
    their fixes by fuzzy similarity (> threshold). Same fix → one entry with summed
    success_count. Different fix → separate variant. Result sorted by success_count
    descending.

    Args:
        entries: List of ErrorEntry (same signature/type/file).
        threshold: Similarity threshold for grouping (default 0.9).

    Returns:
        List of merged ErrorEntry, sorted by success_count descending.
    """
    if not entries:
        return []

    fixes = [_entry_to_fix(e) for e in entries]
    # Build Fix with ref to original for template (signature, file, tags, etc.)
    template = entries[0]
    groups = group_similar_fixes(fixes, threshold=threshold)

    merged: List[ErrorEntry] = []
    for group in groups:
        ent = _merge_fix_group(group, template)
        merged.append(ent)

    merged.sort(key=lambda e: e.success_count, reverse=True)
    return merged
