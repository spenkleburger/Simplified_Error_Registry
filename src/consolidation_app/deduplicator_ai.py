# deduplicator_ai.py
# AI-powered semantic deduplication for consolidation workflow (Phase 4.2).
# v1.0

"""
AI-based deduplication: use LLM to find semantically similar errors
and merge them based on similarity threshold (default 0.85).

Falls back to exact match deduplication if LLM fails.
"""

from __future__ import annotations

import json
import logging
from typing import List

from src.consolidation_app.deduplicator import (
    deduplicate_errors_exact,
    merge_entries,
)
from src.consolidation_app.llm_client import call_llm
from src.consolidation_app.parser import ErrorEntry

logger = logging.getLogger(__name__)

# Default similarity threshold
DEFAULT_SIMILARITY_THRESHOLD = 0.85


def _build_similarity_prompt(entry1: ErrorEntry, entry2: ErrorEntry) -> str:
    """
    Build LLM prompt for comparing two error entries.

    Args:
        entry1: First error entry to compare.
        entry2: Second error entry to compare.

    Returns:
        Formatted prompt string for LLM.
    """
    prompt = f"""Compare these two error entries and determine if they represent the same underlying error.

Error Entry 1:
- Error Signature: {entry1.error_signature}
- Error Type: {entry1.error_type}
- File: {entry1.file}
- Line: {entry1.line}
- Error Context: {entry1.explanation[:500] if entry1.explanation else "N/A"}
- Fix Code: {entry1.fix_code[:300] if entry1.fix_code else "N/A"}

Error Entry 2:
- Error Signature: {entry2.error_signature}
- Error Type: {entry2.error_type}
- File: {entry2.file}
- Line: {entry2.line}
- Error Context: {entry2.explanation[:500] if entry2.explanation else "N/A"}
- Fix Code: {entry2.fix_code[:300] if entry2.fix_code else "N/A"}

Analyze if these errors are semantically similar (represent the same underlying issue, even if wording differs).

Respond with a JSON object in this exact format:
{{
    "similarity": 0.95,
    "reason": "Both errors are FileNotFoundError when trying to open a config file, just different file paths"
}}

Similarity score should be:
- 0.9-1.0: Same error (different wording, same root cause)
- 0.7-0.89: Similar error (related but different root cause)
- 0.0-0.69: Different errors

Only respond with the JSON object, no additional text."""
    return prompt


def calculate_similarity(entry1: ErrorEntry, entry2: ErrorEntry) -> float:
    """
    Calculate semantic similarity between two error entries using LLM.

    Args:
        entry1: First error entry to compare.
        entry2: Second error entry to compare.

    Returns:
        Similarity score between 0.0 and 1.0.

    Raises:
        ValueError: If LLM response cannot be parsed.
        RuntimeError: If LLM call fails (caller should handle fallback).
    """
    prompt = _build_similarity_prompt(entry1, entry2)

    logger.debug(
        "Calculating similarity between entries: '%s' vs '%s'",
        entry1.error_signature[:50],
        entry2.error_signature[:50],
    )

    try:
        # Call LLM with task="deduplication" to use task-specific model if configured
        response = call_llm(prompt, task="deduplication")

        # Parse JSON response
        response = response.strip()
        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
        response = response.strip()

        try:
            result = json.loads(response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response if wrapped in text
            import re

            json_match = re.search(r"\{[^{}]*\"similarity\"[^{}]*\}", response)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                raise ValueError(
                    f"Could not parse JSON from LLM response: {response[:200]}"
                ) from e

        similarity = float(result.get("similarity", 0.0))
        reason = result.get("reason", "No reason provided")

        # Validate similarity score is in valid range
        if not 0.0 <= similarity <= 1.0:
            logger.warning(
                "LLM returned invalid similarity score %f, clamping to [0.0, 1.0]",
                similarity,
            )
            similarity = max(0.0, min(1.0, similarity))

        logger.debug(
            "Similarity calculated: %.2f (reason: %s)",
            similarity,
            reason[:100],
        )

        return similarity

    except Exception as e:
        logger.error(
            "Failed to calculate similarity via LLM: %s: %s",
            type(e).__name__,
            e,
        )
        raise RuntimeError(f"LLM similarity calculation failed: {e}") from e


def deduplicate_errors_ai(
    new_entries: List[ErrorEntry],
    existing_entries: List[ErrorEntry],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    fallback_to_exact: bool = True,
) -> List[ErrorEntry]:
    """
    Deduplicate new entries against existing entries using AI semantic similarity.

    For each new entry:
    1. Compare with all existing entries using LLM similarity
    2. If similarity >= threshold: merge into best matching existing entry
    3. If no match: add as new entry

    Falls back to exact match deduplication if:
    - LLM fails and fallback_to_exact=True
    - No existing entries to compare against

    Args:
        new_entries: New entries to deduplicate.
        existing_entries: Existing entries to match against.
        similarity_threshold: Minimum similarity score to consider a match (0.0-1.0).
        fallback_to_exact: If True, fall back to exact match on LLM failure.

    Returns:
        Consolidated list with duplicates merged where similarity >= threshold.
    """
    if not new_entries:
        logger.debug("No new entries to deduplicate")
        return existing_entries.copy()

    if not existing_entries:
        logger.debug("No existing entries, returning all new entries")
        return new_entries.copy()

    # Validate threshold
    if not 0.0 <= similarity_threshold <= 1.0:
        logger.warning(
            "Invalid similarity threshold %f, using default %f",
            similarity_threshold,
            DEFAULT_SIMILARITY_THRESHOLD,
        )
        similarity_threshold = DEFAULT_SIMILARITY_THRESHOLD

    consolidated: List[ErrorEntry] = existing_entries.copy()
    merged_count = 0
    variant_count = 0
    new_count = 0
    llm_failure_count = 0

    for new_entry in new_entries:
        best_match_idx = None
        best_similarity = 0.0

        # Try to find best matching existing entry using LLM
        try:
            for idx, existing_entry in enumerate(consolidated):
                try:
                    similarity = calculate_similarity(new_entry, existing_entry)
                    if (
                        similarity >= similarity_threshold
                        and similarity > best_similarity
                    ):
                        best_similarity = similarity
                        best_match_idx = idx
                except RuntimeError:
                    # LLM failed for this comparison, continue with next
                    llm_failure_count += 1
                    continue

        except Exception as e:
            # Unexpected error during similarity calculation
            logger.error(
                "Unexpected error during AI deduplication: %s: %s",
                type(e).__name__,
                e,
            )
            # Fall through to fallback or add as new

        # If LLM failed for all comparisons and fallback is enabled
        if best_match_idx is None and llm_failure_count > 0 and fallback_to_exact:
            logger.info(
                "LLM failed for entry '%s', falling back to exact match deduplication",
                new_entry.error_signature[:50],
            )
            # Use exact match deduplication for this entry only
            exact_result = deduplicate_errors_exact([new_entry], consolidated)
            # Update consolidated list (exact deduplication may have added or merged)
            if len(exact_result) > len(consolidated):
                # New entry was added
                consolidated = exact_result
                new_count += 1
            elif len(exact_result) == len(consolidated):
                # Check if entry was merged
                found = False
                for i, entry in enumerate(consolidated):
                    if (
                        entry.error_signature == new_entry.error_signature
                        and entry.error_type == new_entry.error_type
                        and entry.file == new_entry.file
                    ):
                        if entry.success_count > existing_entries[i].success_count:
                            # Was merged
                            consolidated = exact_result
                            merged_count += 1
                            found = True
                            break
                if not found:
                    # Variant or new entry
                    consolidated = exact_result
                    variant_count += 1
            continue

        # Process match or new entry
        if best_match_idx is not None:
            # Found similar entry: merge
            existing = consolidated[best_match_idx]
            logger.debug(
                "Merging similar entries: '%s' (similarity: %.2f)",
                new_entry.error_signature[:50],
                best_similarity,
            )

            # Check if fix codes are the same (normalize whitespace)
            def _fix_codes_match(fix1: str, fix2: str) -> bool:
                """Check if two fix codes match after normalization."""
                if not fix1 and not fix2:
                    return True
                if not fix1 or not fix2:
                    return False
                normalized1 = " ".join(fix1.split())
                normalized2 = " ".join(fix2.split())
                return normalized1 == normalized2

            if _fix_codes_match(existing.fix_code, new_entry.fix_code):
                # Same fix: merge entries
                merged = merge_entries(existing, new_entry)
                consolidated[best_match_idx] = merged
                merged_count += 1
                logger.debug(
                    "Merged similar entry: %s (success_count: %d -> %d)",
                    new_entry.error_signature[:50],
                    existing.success_count,
                    merged.success_count,
                )
            else:
                # Different fix: keep both as variants
                consolidated.append(new_entry)
                variant_count += 1
                logger.debug(
                    "Found variant fix for similar error: %s (keeping both entries)",
                    new_entry.error_signature[:50],
                )
        else:
            # No match: add as new entry
            consolidated.append(new_entry)
            new_count += 1
            logger.debug(
                "No similar entry found, adding as new: %s",
                new_entry.error_signature[:50],
            )

    logger.info(
        "AI deduplication complete: %d merged (similarity >= %.2f), %d variants, %d new entries, %d LLM failures",
        merged_count,
        similarity_threshold,
        variant_count,
        new_count,
        llm_failure_count,
    )

    return consolidated
