# tagger.py
# Basic tagging (rule-based) for consolidation workflow (Phase 3.4).
# v1.0

"""
Rule-based tag generation: extract error type, framework/library,
domain, and platform tags from ErrorEntry fields.
"""

from __future__ import annotations

import logging
from typing import List

from src.consolidation_app.parser import ErrorEntry

logger = logging.getLogger(__name__)

# Error type to domain tag mapping
_ERROR_TYPE_TO_DOMAIN: dict[str, str] = {
    "FileNotFoundError": "file-io",
    "PermissionError": "file-io",
    "IOError": "file-io",
    "OSError": "file-io",
    "TypeError": "type-conversion",
    "ValueError": "type-conversion",
    "AttributeError": "type-conversion",
    "KeyError": "data-structure",
    "IndexError": "data-structure",
    "ConnectionRefusedError": "networking",
    "ConnectionError": "networking",
    "TimeoutError": "networking",
    "ImportError": "imports",
    "ModuleNotFoundError": "imports",
    "SyntaxError": "syntax",
    "IndentationError": "syntax",
    "NameError": "syntax",
    "AssertionError": "testing",
}

# Framework/library detection patterns (file paths, imports, error context)
_FRAMEWORK_PATTERNS: dict[str, List[str]] = {
    "docker": ["docker", "docker-compose", "Dockerfile", "container"],
    "django": ["django", "manage.py", "settings.py", "models.py", "views.py"],
    "flask": ["flask", "app.py", "blueprint"],
    "fastapi": ["fastapi", "uvicorn", "starlette"],
    "pytest": ["pytest", "conftest.py", "test_"],
    "react": ["react", "jsx", "tsx", "component"],
    "vue": ["vue", ".vue"],
    "postgres": ["postgres", "postgresql", "psycopg"],
    "mysql": ["mysql", "mysqldb", "pymysql"],
    "sqlite": ["sqlite", ".db", ".sqlite"],
    "redis": ["redis"],
    "celery": ["celery"],
    "sqlalchemy": ["sqlalchemy", "orm"],
}

# Domain detection patterns (file paths, error context)
_DOMAIN_PATTERNS: dict[str, List[str]] = {
    "networking": ["network", "socket", "http", "tcp", "udp", "connection", "connect"],
    "database": ["database", "db", "query", "sql", "migration", "schema"],
    "authentication": ["auth", "login", "password", "token", "session", "jwt"],
    "file-io": ["file", "read", "write", "open", "path", "directory", "folder"],
    "api": ["api", "endpoint", "route", "request", "response"],
    "testing": ["test", "spec", "fixture", "mock"],
    "logging": ["log", "logger", "debug", "trace"],
    "configuration": ["config", "settings", "env", "environment"],
}

# Platform detection patterns (error messages, file paths)
_PLATFORM_PATTERNS: dict[str, List[str]] = {
    "windows": ["winerror", "windows", "win32", "\\", "c:\\", "d:\\"],
    "linux": ["linux", "/usr", "/var", "/etc", "posix"],
    "macos": ["darwin", "macos", "/users", "/applications"],
}


def generate_tags_rule_based(entry: ErrorEntry) -> List[str]:
    """
    Generate tags for an entry using rule-based detection.

    Extracts:
    - Error type tag (from error_type field)
    - Framework/library tag (from file path or error context)
    - Domain tag (from error context or file location)
    - Platform tag (from error message or file path)

    Args:
        entry: ErrorEntry to generate tags for.

    Returns:
        List of tags (3-5 tags typically).
    """
    tags: List[str] = []

    # 1. Extract error type tag
    error_type_tag = _extract_error_type_tag(entry.error_type)
    if error_type_tag:
        tags.append(error_type_tag)

    # 2. Extract framework/library tag
    framework_tag = _extract_framework_tag(
        entry.file, entry.explanation, entry.error_signature
    )
    if framework_tag:
        tags.append(framework_tag)

    # 3. Extract domain tag
    domain_tag = _extract_domain_tag(
        entry.error_type, entry.file, entry.explanation, entry.error_signature
    )
    if domain_tag:
        tags.append(domain_tag)

    # 4. Extract platform tag
    platform_tag = _extract_platform_tag(
        entry.file, entry.error_signature, entry.explanation
    )
    if platform_tag:
        tags.append(platform_tag)

    # Deduplicate and sort tags
    unique_tags = sorted(set(tags))

    logger.debug(
        "Generated %d tag(s) for entry %s: %s",
        len(unique_tags),
        entry.error_signature[:50] if entry.error_signature else "unknown",
        unique_tags,
    )

    return unique_tags


def apply_tags_to_entry(entry: ErrorEntry) -> ErrorEntry:
    """
    Merge rule-based tags with entry's existing tags and return a new ErrorEntry.

    Uses generate_tags_rule_based(entry), then union with entry.tags,
    deduplicated and sorted. ErrorEntry is immutable; returns new instance.

    Args:
        entry: ErrorEntry to enhance with generated tags.

    Returns:
        New ErrorEntry with tags = sorted(set(entry.tags) | set(generated)).
    """
    generated = generate_tags_rule_based(entry)
    merged = sorted(set(entry.tags) | set(generated))
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


def _extract_error_type_tag(error_type: str) -> str | None:
    """
    Extract error type tag from error_type field.

    Maps common Python exception types to domain tags.
    Unknown error types return None (will be handled by domain detection).

    Args:
        error_type: Exception class name.

    Returns:
        Tag string or None if unknown.
    """
    if not error_type:
        return None

    # Normalize: remove common prefixes/suffixes
    normalized = error_type.strip()
    if not normalized:
        return None

    # Direct mapping
    tag = _ERROR_TYPE_TO_DOMAIN.get(normalized)
    if tag:
        return tag

    # Fallback: use lowercase error type as tag
    # (e.g., "CustomError" -> "customerror")
    return (
        normalized.lower().replace("error", "").replace("exception", "").strip() or None
    )


def _extract_framework_tag(
    file: str, explanation: str, error_signature: str
) -> str | None:
    """
    Extract framework/library tag from file path, explanation, or error signature.

    Checks for common frameworks/libraries in file paths and error context.

    Args:
        file: File path where error occurred.
        explanation: Error explanation text.
        error_signature: Error message/signature.

    Returns:
        Framework tag or None if not detected.
    """
    # Combine all text sources for pattern matching
    text = " ".join([file, explanation, error_signature]).lower()

    # Check each framework pattern
    for framework, patterns in _FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text:
                logger.debug(
                    "Detected framework '%s' from pattern '%s'", framework, pattern
                )
                return framework

    return None


def _extract_domain_tag(
    error_type: str, file: str, explanation: str, error_signature: str
) -> str | None:
    """
    Extract domain tag from file path, explanation, or error signature.

    Note: Error type mapping is handled separately in _extract_error_type_tag.
    This function focuses on detecting domain from file/context patterns.

    Args:
        error_type: Exception class name (used for fallback only).
        file: File path where error occurred.
        explanation: Error explanation text.
        error_signature: Error message/signature.

    Returns:
        Domain tag or None if not detected.
    """
    # Combine all text sources for pattern matching
    text = " ".join([file, explanation, error_signature]).lower()

    # Check each domain pattern
    for domain, patterns in _DOMAIN_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text:
                logger.debug("Detected domain '%s' from pattern '%s'", domain, pattern)
                return domain

    # Fallback: try error type mapping if no pattern match
    if error_type:
        domain_from_type = _ERROR_TYPE_TO_DOMAIN.get(error_type)
        if domain_from_type:
            return domain_from_type

    return None


def _extract_platform_tag(
    file: str, error_signature: str, explanation: str
) -> str | None:
    """
    Extract platform tag from file path, error message, or explanation.

    Detects Windows, Linux, macOS, or cross-platform.

    Args:
        file: File path where error occurred.
        error_signature: Error message/signature.
        explanation: Error explanation text.

    Returns:
        Platform tag ("windows", "linux", "macos") or None if cross-platform/unknown.
    """
    # Combine all text sources for pattern matching
    text = " ".join([file, error_signature, explanation]).lower()

    # Check each platform pattern
    for platform, patterns in _PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text:
                logger.debug(
                    "Detected platform '%s' from pattern '%s'", platform, pattern
                )
                return platform

    # Default: cross-platform (no tag)
    return None
