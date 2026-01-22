"""Parser for errors_and_fixes markdown entries."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_ENTRY_HEADER = re.compile(
    r"(?m)^###\s+(?P<entry_type>Error|Agent Process Issue):\s*(?P<header>.*)$"
)
_METADATA_RE = re.compile(r"\*\*(?P<key>[^:]+):\*\*\s*(?P<value>.*)")

DEFAULT_TIMESTAMP = datetime(1970, 1, 1)


@dataclass(frozen=True)
class ErrorEntry:
    """Normalized representation of an error/session entry."""

    error_signature: str
    error_type: str
    file: str
    line: int
    fix_code: str
    explanation: str
    result: str
    success_count: int
    tags: List[str]
    timestamp: datetime
    is_process_issue: bool


def parse_errors_and_fixes(file_path: Path) -> List[ErrorEntry]:
    """Return parsed entries from a session log."""

    if not file_path.exists():
        logger.debug("Missing errors_and_fixes log: %s", file_path)
        return []

    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return []

    matches = list(_ENTRY_HEADER.finditer(text))
    if not matches:
        return []

    entries: List[ErrorEntry] = []
    for index, match in enumerate(matches):
        entry_type = match.group("entry_type")
        header_text = match.group("header").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        if not block:
            continue

        parser = (
            parse_error_block if entry_type == "Error" else parse_process_issue_block
        )
        try:
            entry = parser(block, header_text)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to parse %s block: %s", entry_type, exc)
            entry = None

        if entry:
            entries.append(entry)

    return entries


def parse_error_block(block: str, header_text: str) -> Optional[ErrorEntry]:
    """Parse a single error entry block."""

    if not block:
        return None

    metadata = extract_metadata(block)
    timestamp = (
        parse_timestamp(metadata["timestamp"])
        if metadata.get("timestamp")
        else DEFAULT_TIMESTAMP
    )
    tags = parse_tags(metadata.get("tags", ""))
    success_count = _parse_int(metadata.get("success_count"))
    line = _parse_int(metadata.get("line"))
    file_path = metadata.get("file", "")
    explanation = extract_section(block, "Explanation")
    fix_code = extract_code_block(block, "Fix Applied")
    result = metadata.get("result", "")

    signature = header_text or metadata.get("error_signature", "")
    _, header_type = _split_header(header_text)
    error_type = metadata.get("error_type") or header_type

    if not timestamp:
        timestamp = DEFAULT_TIMESTAMP

    return ErrorEntry(
        error_signature=signature,
        error_type=error_type,
        file=file_path,
        line=line,
        fix_code=fix_code,
        explanation=explanation,
        result=result,
        success_count=success_count,
        tags=tags,
        timestamp=timestamp,
        is_process_issue=False,
    )


def parse_process_issue_block(block: str, header_text: str) -> Optional[ErrorEntry]:
    """Parse an Agent Process Issue block."""

    if not block:
        return None

    metadata = extract_metadata(block)
    timestamp = (
        parse_timestamp(metadata["timestamp"])
        if metadata.get("timestamp")
        else DEFAULT_TIMESTAMP
    )
    tags = parse_tags(metadata.get("tags", ""))
    explanation = extract_section(block, "Issue Description")
    rule = extract_section(block, "Rule Established")
    result = metadata.get("result", "")
    issue_type = metadata.get("issue_type") or "agent-process"

    if not timestamp:
        timestamp = DEFAULT_TIMESTAMP

    return ErrorEntry(
        error_signature=header_text or metadata.get("issue_description", ""),
        error_type=issue_type,
        file="",
        line=0,
        fix_code=rule,
        explanation=explanation or rule,
        result=result,
        success_count=0,
        tags=tags,
        timestamp=timestamp,
        is_process_issue=True,
    )


def extract_metadata(block: str) -> Dict[str, str]:
    """Return metadata key/value pairs from the block."""

    metadata: Dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        match = _METADATA_RE.match(line)
        if not match:
            continue
        key = match.group("key").strip().lower().replace(" ", "_")
        value = match.group("value").strip().strip("`")
        metadata[key] = value

    return metadata


def extract_code_block(block: str, section: str) -> str:
    """Extract the code block that follows a titled section."""

    pattern = re.compile(
        rf"\*\*{re.escape(section)}:\*\*\s*\n```[^\n]*\n(?P<code>.*?)(?=\n```)",
        re.DOTALL,
    )
    match = pattern.search(block)
    if not match:
        return ""

    return match.group("code").rstrip()


def extract_section(block: str, section: str) -> str:
    """Extract a paragraph section that can span multiple lines."""

    pattern = re.compile(
        rf"\*\*{re.escape(section)}:\*\*\s*(?P<value>.*?)(?=\n\*\*[^\n]+:\*\*|\Z)",
        re.DOTALL,
    )
    match = pattern.search(block)
    if not match:
        return ""

    return match.group("value").strip()


def parse_tags(raw: str) -> List[str]:
    """Normalize tag lists into simple strings."""

    if not raw:
        return []
    return [tag.strip(" `") for tag in raw.split(",") if tag.strip(" `")]


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamps, accepting suffixed Z for UTC."""

    normalized = timestamp_str.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"

    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        logger.warning("Unable to parse timestamp '%s': %s", timestamp_str, exc)
        raise


def _parse_int(value: Optional[str], default: int = 0) -> int:
    """Convert number strings while guarding against malformed inputs."""

    if not value:
        return default

    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid integer value for metadata: %s", value)
        return default


def _split_header(header: str) -> Tuple[str, str]:
    """Return signature and fallback type from the header line."""

    text = header.strip()
    if ":" in text:
        entry_type, remainder = text.split(":", 1)
        return remainder.strip(), entry_type.strip()

    return text, text


# --- fix_repo.md / coding_tips.md parsers (reverse of generator output) ---

_FIX_REPO_SECTION = re.compile(r"(?m)^##\s+(.+)$")
_FIX_REPO_FIX_BLOCK = re.compile(
    r"###\s+Fix\s+\d+:\s+(.+?)\s+\(Success\s+Count:\s+(\d+)\)"
)


def _unescape_markdown_header(text: str) -> str:
    """Reverse _escape_markdown_header: remove backslash escapes."""

    replacements = [
        (r"\#", "#"),
        (r"\*", "*"),
        (r"\[", "["),
        (r"\]", "]"),
        (r"\(", "("),
        (r"\)", ")"),
        (r"\<", "<"),
        (r"\>", ">"),
        (r"\`", "`"),
        (r"\_", "_"),
        (r"\~", "~"),
    ]
    out = text
    for escaped, char in replacements:
        out = out.replace(escaped, char)
    return out


def parse_fix_repo(file_path: Path) -> List[ErrorEntry]:
    """
    Parse fix_repo.md (generator output) back into ErrorEntry list.

    Skips header (before first ##). Each ## section is one signature;
    ### Fix N blocks are individual entries. Returns [] if file missing or empty.

    Args:
        file_path: Path to fix_repo.md.

    Returns:
        List of ErrorEntry (all is_process_issue=False).
    """

    if not file_path.exists():
        logger.debug("Missing fix_repo: %s", file_path)
        return []

    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return []

    sections = list(_FIX_REPO_SECTION.finditer(text))
    # First ## is sometimes after ---; skip header
    entries: List[ErrorEntry] = []
    for i, sig_match in enumerate(sections):
        signature_raw = sig_match.group(1).strip()
        signature = _unescape_markdown_header(signature_raw)
        start = sig_match.end()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
        block = text[start:end].strip()
        if not block:
            continue

        meta = extract_metadata(block)
        raw_tags = meta.get("tags", "").strip()
        section_tags = [] if raw_tags == "None" else parse_tags(raw_tags)
        fix_matches = list(_FIX_REPO_FIX_BLOCK.finditer(block))
        for j, fm in enumerate(fix_matches):
            error_type = fm.group(1).strip()
            success_count = int(fm.group(2))
            fix_start = fm.end()
            fix_end = (
                fix_matches[j + 1].start() if j + 1 < len(fix_matches) else len(block)
            )
            fix_block = block[fix_start:fix_end].strip()
            fix_meta = extract_metadata(fix_block)
            fix_code = extract_code_block(fix_block, "Code")
            explanation = (
                fix_meta.get("why this works") or fix_meta.get("why_this_works") or ""
            )
            result = fix_meta.get("result", "")
            file_path_str = (
                fix_meta.get("projects") or fix_meta.get("file") or ""
            ).strip()
            ts_str = (
                fix_meta.get("last updated")
                or fix_meta.get("last_updated")
                or meta.get("last updated")
                or meta.get("last_updated")
                or ""
            )
            try:
                ts = parse_timestamp(ts_str) if ts_str else DEFAULT_TIMESTAMP
            except Exception:
                ts = DEFAULT_TIMESTAMP
            entry = ErrorEntry(
                error_signature=signature,
                error_type=error_type,
                file=file_path_str,
                line=0,
                fix_code=fix_code,
                explanation=explanation,
                result=result,
                success_count=success_count,
                tags=section_tags.copy(),
                timestamp=ts,
                is_process_issue=False,
            )
            entries.append(entry)

    return entries


_CODING_TIPS_SECTION = re.compile(r"(?m)^##\s+(.+)$")
_CODING_TIPS_RULE = re.compile(r"(?m)^###\s+Rule:\s+(.+)$")


def parse_coding_tips(file_path: Path) -> List[ErrorEntry]:
    """
    Parse coding_tips.md (generator output) back into ErrorEntry list.

    Skips header. Each ## is category; ### Rule: blocks are process issues.
    Returns [] if file missing or empty.

    Args:
        file_path: Path to coding_tips.md.

    Returns:
        List of ErrorEntry (all is_process_issue=True).
    """

    if not file_path.exists():
        logger.debug("Missing coding_tips: %s", file_path)
        return []

    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return []

    sections = list(_CODING_TIPS_SECTION.finditer(text))
    entries: List[ErrorEntry] = []
    for i, cat_match in enumerate(sections):
        category = _unescape_markdown_header(cat_match.group(1).strip())
        start = cat_match.end()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
        block = text[start:end].strip()
        if not block:
            continue

        rule_matches = list(_CODING_TIPS_RULE.finditer(block))
        for k, rm in enumerate(rule_matches):
            rule_title = _unescape_markdown_header(rm.group(1).strip())
            rule_start = rm.end()
            rule_end = (
                rule_matches[k + 1].start() if k + 1 < len(rule_matches) else len(block)
            )
            rule_block = block[rule_start:rule_end].strip()
            meta = extract_metadata(rule_block)
            why = meta.get("why") or meta.get("explanation") or ""
            result = meta.get("result", "")
            related = meta.get("related errors") or meta.get("related_errors") or ""
            sc = 0
            if "success count:" in related.lower():
                m = re.search(r"success\s+count:\s*(\d+)", related, re.I)
                if m:
                    sc = int(m.group(1))
            entry = ErrorEntry(
                error_signature=rule_title,
                error_type=meta.get("issue_type") or "agent-process",
                file="",
                line=0,
                fix_code=why,
                explanation=why,
                result=result,
                success_count=sc,
                tags=[category] if category else [],
                timestamp=DEFAULT_TIMESTAMP,
                is_process_issue=True,
            )
            entries.append(entry)

    return entries
