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
