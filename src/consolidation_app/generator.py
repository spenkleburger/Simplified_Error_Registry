"""Generate consolidated markdown for fix_repo and coding tips."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Iterable, List

from src.consolidation_app.parser import ErrorEntry

logger = logging.getLogger(__name__)


def generate_fix_repo_markdown(entries: Iterable[ErrorEntry]) -> str:
    """Return markdown that showcases fixes grouped by signature."""

    clean_entries = [entry for entry in entries if not entry.is_process_issue]
    logger.debug("Generating fix_repo markdown for %d entries", len(clean_entries))
    header_lines = _build_fix_repo_header(clean_entries)
    if not clean_entries:
        logger.debug("No error entries to generate, returning header only")
        return "\n".join(header_lines)

    body: List[str] = []
    grouped = _group_by_signature(clean_entries)
    logger.debug("Grouped into %d unique error signatures", len(grouped))
    for signature, group in sorted(grouped.items(), key=lambda item: item[0] or ""):
        # Escape markdown special characters in header
        escaped_signature = _escape_markdown_header(signature or "Untitled Error")
        body.append(f"## {escaped_signature}")
        first_seen = min(entry.timestamp for entry in group)
        last_updated = max(entry.timestamp for entry in group)
        all_tags = sorted({tag for entry in group for tag in entry.tags})
        body.append("")
        body.append(f"**Tags:** {format_tags(all_tags)}")
        body.append(f"**First Seen:** {_format_date(first_seen)}")
        body.append(f"**Last Updated:** {_format_date(last_updated)}")
        body.append(f"**Total Occurrences:** {len(group)}")
        body.append("")
        for idx, entry in enumerate(
            sorted(group, key=lambda item: item.success_count, reverse=True), start=1
        ):
            # Note: v1 uses error_type as fix description; future versions may extract description
            body.append(
                f"### Fix {idx}: {entry.error_type or 'Fix'} (Success Count: {entry.success_count})"
            )
            body.append("")
            body.append("**Code:**")
            body.append(format_code_block(entry.fix_code or ""))
            body.append("")
            body.append(
                f"**Why this works:** {entry.explanation or 'Describes why the fix succeeds.'}"
            )
            body.append(f"**Result:** {entry.result or 'Unknown'}")
            # Note: v1 uses file path; future versions may extract project name
            body.append(f"**Projects:** {entry.file or 'Unknown'}")
            body.append(f"**Last Updated:** {format_timestamp(entry.timestamp)}")
            body.append("")
        body.append("---")
        body.append("")

    return "\n".join(header_lines + body).rstrip()


def generate_coding_tips_markdown(entries: Iterable[ErrorEntry]) -> str:
    """Return markdown that documents agent process rules."""

    issues = [entry for entry in entries if entry.is_process_issue]
    logger.debug("Generating coding_tips markdown for %d process issues", len(issues))
    header_lines = _build_coding_tips_header(issues)
    if not issues:
        logger.debug("No process issues to generate, returning header only")
        return "\n".join(header_lines)

    sections: List[str] = []
    grouped = _group_by_category(issues)
    logger.debug("Grouped into %d categories", len(grouped))
    for category, items in sorted(grouped.items(), key=lambda item: item[0]):
        # Escape markdown special characters in category header
        escaped_category = _escape_markdown_header(category or "General")
        sections.append(f"## {escaped_category}")
        sections.append("")
        for entry in items:
            # Escape markdown special characters in rule title
            escaped_rule = _escape_markdown_header(
                entry.error_signature or entry.error_type
            )
            sections.append(f"### Rule: {escaped_rule}")
            sections.append("")
            sections.append(
                f"**Why:** {entry.explanation or entry.fix_code or 'Rule rationale pending.'}"
            )
            sections.append("")
            sections.append("**Examples:**")
            # Note: v1 generates single good/bad example; future versions may aggregate multiple
            sections.append(
                f"- ✅ {entry.explanation or entry.error_signature or 'Follows the rule.'}"
            )
            sections.append(
                f"- ❌ {entry.result or 'Rule violation observed in agent session.'}"
            )
            sections.append("")
            sections.append("**Related Errors:**")
            related_signature = entry.error_signature or entry.error_type or "Unknown"
            # Note: v1 uses success_count; future versions may track occurrence count separately
            sections.append(
                f"- `{entry.error_type or 'rule'}`: {related_signature} (success count: {entry.success_count})"
            )
            sections.append("")
        sections.append("---")
        sections.append("")

    return "\n".join(header_lines + sections).rstrip()


def format_code_block(code: str, language: str = "python") -> str:
    """Return a fenced code block, even when the snippet is empty."""

    cleaned = code.rstrip()
    if not cleaned:
        return f"```{language}\n\n```"
    return f"```{language}\n{cleaned}\n```"


def format_tags(tags: List[str]) -> str:
    """Return markdown-safe representation of tag collections.

    Escapes backticks in tags to prevent markdown injection.
    """

    if not tags:
        return "None"
    # Escape backticks in tags to prevent markdown breaking
    escaped_tags = [tag.replace("`", r"\`") for tag in tags]
    return ", ".join(f"`{escaped_tag}`" for escaped_tag in escaped_tags)


def format_timestamp(dt: datetime) -> str:
    """Serialize timestamps into UTC ISO8601 strings.

    Assumes naive datetimes are UTC (v1 limitation).
    """

    if not dt.tzinfo:
        logger.debug("Naive datetime encountered, assuming UTC: %s", dt)
    aware = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    iso = aware.astimezone(timezone.utc).replace(microsecond=0).isoformat()
    return iso.replace("+00:00", "Z")


def _build_fix_repo_header(entries: List[ErrorEntry]) -> List[str]:
    last_updated = (
        max(entry.timestamp for entry in entries)
        if entries
        else datetime.now(timezone.utc)
    )
    project_count = len({entry.file for entry in entries if entry.file})
    return [
        "# Fix Repository",
        "",
        f"> **Last Updated:** {format_timestamp(last_updated)}  ",
        f"> **Total Entries:** {len(entries)}  ",
        f"> **Consolidated from:** {project_count} projects",
        "",
        "---",
        "",
    ]


def _build_coding_tips_header(entries: List[ErrorEntry]) -> List[str]:
    last_updated = (
        max(entry.timestamp for entry in entries)
        if entries
        else datetime.now(timezone.utc)
    )
    return [
        "# Coding Tips - Agent Process Rules",
        "",
        f"> **Last Updated:** {format_timestamp(last_updated)}  ",
        f"> **Total Rules:** {len(entries)}  ",
        "",
        "---",
        "",
    ]


def _group_by_signature(entries: List[ErrorEntry]) -> dict[str, List[ErrorEntry]]:
    grouped: dict[str, List[ErrorEntry]] = defaultdict(list)
    for entry in entries:
        grouped[entry.error_signature].append(entry)
    return grouped


def _group_by_category(entries: List[ErrorEntry]) -> dict[str, List[ErrorEntry]]:
    """Group entries by category.

    Note: v1 uses first tag as category; future versions may use explicit category field.
    """
    grouped: dict[str, List[ErrorEntry]] = defaultdict(list)
    for entry in entries:
        if entry.tags:
            key = entry.tags[0]
        else:
            key = entry.error_type or "General"
        grouped[key].append(entry)
    return grouped


def _format_date(dt: datetime) -> str:
    """Return the YYYY-MM-DD portion of an ISO timestamp."""

    return format_timestamp(dt).split("T")[0]


def _escape_markdown_header(text: str) -> str:
    """Escape markdown special characters in header text.

    Prevents markdown injection in error signatures and category names.
    Escapes: #, *, [, ], (, ), <, >, `, _, ~
    """
    # Escape markdown special characters that could break headers
    replacements = {
        "#": r"\#",
        "*": r"\*",
        "[": r"\[",
        "]": r"\]",
        "(": r"\(",
        ")": r"\)",
        "<": r"\<",
        ">": r"\>",
        "`": r"\`",
        "_": r"\_",
        "~": r"\~",
    }
    escaped = text
    for char, replacement in replacements.items():
        escaped = escaped.replace(char, replacement)
    return escaped
