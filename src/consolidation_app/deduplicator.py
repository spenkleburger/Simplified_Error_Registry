# deduplicator.py
# Basic deduplication (exact match) for consolidation workflow (Phase 3.3).
# v1.0

"""
Exact match deduplication: merge entries with identical error_signature,
error_type, and file. If fix_code matches, increment success_count.
If fix_code differs, keep both entries as variants.
"""

from __future__ import annotations

import logging
from typing import List

from src.consolidation_app.parser import ErrorEntry

logger = logging.getLogger(__name__)


def deduplicate_errors_exact(
    new_entries: List[ErrorEntry], existing_entries: List[ErrorEntry]
) -> List[ErrorEntry]:
    """
    Deduplicate new entries against existing entries using exact match.

    Match criteria (all must match exactly):
    - error_signature
    - error_type
    - file

    If match found:
    - If fix_code is same: merge (increment success_count, use newer timestamp)
    - If fix_code is different: keep both entries (variants)

    If no match: add as new entry.

    Args:
        new_entries: New entries to deduplicate.
        existing_entries: Existing entries to match against.

    Returns:
        Consolidated list with duplicates merged where possible.
    """
    if not new_entries:
        logger.debug("No new entries to deduplicate")
        return existing_entries.copy()

    if not existing_entries:
        logger.debug("No existing entries, returning all new entries")
        return new_entries.copy()

    # Build lookup dict for existing entries: (signature, type, file) -> index in result
    existing_lookup: dict[tuple[str, str, str], int] = {}
    consolidated: List[ErrorEntry] = existing_entries.copy()

    # Build lookup mapping keys to indices in consolidated list
    for idx, entry in enumerate(consolidated):
        key = (entry.error_signature, entry.error_type, entry.file)
        existing_lookup[key] = idx

    merged_count = 0
    variant_count = 0
    new_count = 0

    for new_entry in new_entries:
        key = (new_entry.error_signature, new_entry.error_type, new_entry.file)
        existing_idx = existing_lookup.get(key)

        if existing_idx is None:
            # No match: add as new entry
            consolidated.append(new_entry)
            existing_lookup[key] = len(consolidated) - 1
            new_count += 1
            continue

        existing = consolidated[existing_idx]

        # Match found: check if fix_code is same
        if _fix_codes_match(existing.fix_code, new_entry.fix_code):
            # Same fix: merge entries (replace existing with merged)
            merged = merge_entries(existing, new_entry)
            consolidated[existing_idx] = merged
            merged_count += 1
            logger.debug(
                "Merged duplicate entry: %s (success_count: %d -> %d)",
                new_entry.error_signature,
                existing.success_count,
                merged.success_count,
            )
        else:
            # Different fix: keep both as variants (add new entry)
            consolidated.append(new_entry)
            variant_count += 1
            logger.debug(
                "Found variant fix for: %s (keeping both entries)",
                new_entry.error_signature,
            )

    logger.info(
        "Deduplication complete: %d merged, %d variants, %d new entries",
        merged_count,
        variant_count,
        new_count,
    )
    return consolidated


def merge_entries(existing: ErrorEntry, new: ErrorEntry) -> ErrorEntry:
    """
    Merge two entries with matching signature/type/file and same fix_code.

    Updates:
    - timestamp: use newer timestamp
    - success_count: sum of both counts
    - tags: union of both tag lists (deduplicated)
    - result: prefer "✅ Solved" if either is solved, otherwise keep existing
    - explanation: use existing (or new if existing is empty)

    Args:
        existing: Existing entry to merge into.
        new: New entry to merge.

    Returns:
        New ErrorEntry with merged data.
    """
    # Use newer timestamp
    merged_timestamp = max(existing.timestamp, new.timestamp)

    # Sum success counts
    merged_success_count = existing.success_count + new.success_count

    # Union of tags (deduplicated, sorted)
    merged_tags = sorted(set(existing.tags) | set(new.tags))

    # Prefer "✅ Solved" result if either is solved
    if "✅" in new.result or "✅" in existing.result:
        merged_result = "✅ Solved" if "✅" in new.result else existing.result
    else:
        merged_result = existing.result if existing.result else new.result

    # Use existing explanation, or new if existing is empty
    merged_explanation = existing.explanation or new.explanation

    # Use existing fix_code (should be same as new, but prefer existing)
    merged_fix_code = existing.fix_code or new.fix_code

    return ErrorEntry(
        error_signature=existing.error_signature,
        error_type=existing.error_type,
        file=existing.file,
        line=existing.line,  # Keep existing line
        fix_code=merged_fix_code,
        explanation=merged_explanation,
        result=merged_result,
        success_count=merged_success_count,
        tags=merged_tags,
        timestamp=merged_timestamp,
        is_process_issue=existing.is_process_issue,
    )


def _fix_codes_match(fix1: str, fix2: str) -> bool:
    """
    Check if two fix codes are the same (normalized comparison).

    Normalizes whitespace and compares. Empty strings are considered
    matching (both empty).

    Args:
        fix1: First fix code.
        fix2: Second fix code.

    Returns:
        True if fix codes match after normalization.
    """
    if not fix1 and not fix2:
        return True

    if not fix1 or not fix2:
        return False

    # Normalize whitespace: strip and normalize internal whitespace
    normalized1 = " ".join(fix1.split())
    normalized2 = " ".join(fix2.split())

    return normalized1 == normalized2
