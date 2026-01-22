# tagger_ai.py
# AI-powered tag generation for consolidation workflow (Phase 4.3).
# v1.0

"""
AI-based tag generation: use LLM to generate context tags for error entries.

Falls back to rule-based tagging if LLM fails.
Optionally combines AI tags with rule-based tags for comprehensive coverage.
"""

from __future__ import annotations

import json
import logging
import re
from typing import List

from src.consolidation_app.llm_client import call_llm
from src.consolidation_app.parser import ErrorEntry
from src.consolidation_app.tagger import generate_tags_rule_based

logger = logging.getLogger(__name__)

# Default tag count range
MIN_TAGS = 3
MAX_TAGS = 5


def _build_tagging_prompt(entry: ErrorEntry) -> str:
    """
    Build LLM prompt for generating tags for an error entry.

    Args:
        entry: ErrorEntry to generate tags for.

    Returns:
        Formatted prompt string for LLM.
    """
    # Truncate long fields for prompt efficiency
    error_context = entry.explanation[:500] if entry.explanation else "N/A"
    fix_code = entry.fix_code[:300] if entry.fix_code else "N/A"

    prompt = f"""Generate context tags for this error entry. Tags should help categorize and find this error in a registry.

Error Entry Details:
- Error Signature: {entry.error_signature}
- Error Type: {entry.error_type}
- File: {entry.file}
- Line: {entry.line}
- Error Context: {error_context}
- Fix Code: {fix_code[:300] if fix_code else "N/A"}

Generate 3-5 tags that categorize this error. Tags should include:
1. Error type category (e.g., "file-io", "type-conversion", "networking", "syntax")
2. Framework/library (e.g., "docker", "django", "pytest", "react")
3. Domain/context (e.g., "database", "authentication", "api", "testing")
4. Platform (e.g., "windows", "linux", "macos", "cross-platform")
5. Additional context tags if relevant (e.g., "async", "threading", "caching")

Tag Guidelines:
- Use lowercase with hyphens (e.g., "file-io", not "FileIO" or "file_io")
- Be specific but concise (single words or short phrases)
- Focus on tags that help with lookup and categorization
- Avoid redundant tags (e.g., don't include both "file-io" and "file-system")

Respond with a JSON object in this exact format:
{{
    "tags": ["file-io", "docker", "configuration", "cross-platform"]
}}

Only respond with the JSON object, no additional text."""
    return prompt


def generate_tags_ai(
    entry: ErrorEntry,
    fallback_to_rule_based: bool = True,
    combine_with_rule_based: bool = False,
) -> List[str]:
    """
    Generate tags for an entry using AI (LLM).

    Args:
        entry: ErrorEntry to generate tags for.
        fallback_to_rule_based: If True, fall back to rule-based tagging on LLM failure.
        combine_with_rule_based: If True, combine AI tags with rule-based tags (AI tags as primary).

    Returns:
        List of tags (3-5 tags typically).

    Raises:
        RuntimeError: If LLM fails and fallback_to_rule_based=False.
    """
    logger.debug(
        "Generating AI tags for entry: %s",
        entry.error_signature[:50] if entry.error_signature else "unknown",
    )

    prompt = _build_tagging_prompt(entry)

    try:
        # Call LLM with task="tagging" to use task-specific model if configured
        response = call_llm(prompt, task="tagging")

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
            json_match = re.search(r'\{[^{}]*"tags"[^{}]*\}', response)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                raise ValueError(
                    f"Could not parse JSON from LLM response: {response[:200]}"
                ) from e

        tags = result.get("tags", [])
        if not isinstance(tags, list):
            logger.warning(
                "LLM returned non-list tags: %s, converting to list",
                type(tags).__name__,
            )
            tags = [str(tag) for tag in tags] if tags else []

        # Validate and normalize tags
        normalized_tags = []
        for tag in tags:
            if not tag or not isinstance(tag, str):
                continue
            # Normalize: lowercase, replace spaces/underscores with hyphens
            normalized = re.sub(r"[_\s]+", "-", tag.lower().strip())
            normalized = re.sub(r"[^a-z0-9-]", "", normalized)  # Remove invalid chars
            if normalized and normalized not in normalized_tags:
                normalized_tags.append(normalized)

        # Ensure we have at least MIN_TAGS tags if possible
        if len(normalized_tags) < MIN_TAGS and combine_with_rule_based:
            logger.debug(
                "AI generated only %d tags, combining with rule-based tags",
                len(normalized_tags),
            )

        logger.debug(
            "AI generated %d tag(s): %s",
            len(normalized_tags),
            normalized_tags,
        )

        # Combine with rule-based tags if requested
        if combine_with_rule_based:
            rule_based_tags = generate_tags_rule_based(entry)
            # Merge: AI tags as primary, add rule-based tags for missing categories
            all_tags = normalized_tags.copy()
            for rule_tag in rule_based_tags:
                if rule_tag not in all_tags:
                    all_tags.append(rule_tag)
            normalized_tags = sorted(set(all_tags))

        # Limit to MAX_TAGS if exceeded
        if len(normalized_tags) > MAX_TAGS:
            logger.debug(
                "AI generated %d tags, limiting to %d",
                len(normalized_tags),
                MAX_TAGS,
            )
            normalized_tags = normalized_tags[:MAX_TAGS]

        return normalized_tags

    except Exception as e:
        logger.error(
            "Failed to generate AI tags: %s: %s",
            type(e).__name__,
            e,
        )

        if fallback_to_rule_based:
            logger.info(
                "Falling back to rule-based tagging for entry: %s",
                entry.error_signature[:50] if entry.error_signature else "unknown",
            )
            return generate_tags_rule_based(entry)
        else:
            raise RuntimeError(f"AI tag generation failed: {e}") from e


def apply_tags_ai_to_entry(
    entry: ErrorEntry,
    fallback_to_rule_based: bool = True,
    combine_with_rule_based: bool = False,
) -> ErrorEntry:
    """
    Generate AI tags and merge with entry's existing tags, returning a new ErrorEntry.

    Uses generate_tags_ai(entry), then union with entry.tags,
    deduplicated and sorted. ErrorEntry is immutable; returns new instance.

    Args:
        entry: ErrorEntry to enhance with AI-generated tags.
        fallback_to_rule_based: If True, fall back to rule-based tagging on LLM failure.
        combine_with_rule_based: If True, combine AI tags with rule-based tags.

    Returns:
        New ErrorEntry with tags = sorted(set(entry.tags) | set(ai_generated)).
    """
    ai_tags = generate_tags_ai(
        entry,
        fallback_to_rule_based=fallback_to_rule_based,
        combine_with_rule_based=combine_with_rule_based,
    )
    merged = sorted(set(entry.tags) | set(ai_tags))
    return ErrorEntry(
        error_signature=entry.error_signature,
        error_type=entry.error_type,
        file=entry.file,
        line=entry.line,
        fix_code=entry.fix_code,
        explanation=entry.explanation,
        result=entry.result,
        success_count=entry.success_count,
        tags=merged,
        timestamp=entry.timestamp,
        is_process_issue=entry.is_process_issue,
    )
