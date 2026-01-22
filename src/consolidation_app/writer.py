# File: src/consolidation_app/writer.py
# Description: Writer module for consolidation app - writes fix_repo.md, coding_tips.md, and clears errors_and_fixes.md
# Version: 1.0

"""Write consolidated markdown files and clear session logs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from src.consolidation_app.generator import (
    generate_coding_tips_markdown,
    generate_fix_repo_markdown,
)
from src.consolidation_app.parser import ErrorEntry

logger = logging.getLogger(__name__)

_ERRORS_AND_FIXES_HEADER = """# Errors and Fixes Log

> **Note**: This file is processed daily by the consolidation app at 2 AM.
> `### Error:` entries → fix_repo.md; `### Agent Process Issue:` entries → coding_tips.md. Contents are then cleared (file is kept).

"""


def write_fix_repo(project_path: Path, consolidated_entries: List[ErrorEntry]) -> None:
    """Write fix_repo.md with consolidated error entries.

    Filters entries where is_process_issue=False, generates markdown using
    generator, and writes to project_path/.errors_fixes/fix_repo.md.

    Creates directory if missing. Uses UTF-8 encoding and LF line endings.

    Args:
        project_path: Path to project root directory.
        consolidated_entries: List of consolidated ErrorEntry objects.

    Raises:
        PermissionError: If file cannot be written due to permissions.
        OSError: If file operations fail for other reasons.
    """
    errors_fixes_dir = project_path / ".errors_fixes"
    output_file = errors_fixes_dir / "fix_repo.md"

    try:
        # Create directory if missing
        errors_fixes_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured directory exists: %s", errors_fixes_dir)

        # Filter entries (only non-process-issue entries)
        error_entries = [e for e in consolidated_entries if not e.is_process_issue]
        logger.info(
            "Writing fix_repo.md for project %s with %d error entry(ies)",
            project_path,
            len(error_entries),
        )

        # Generate markdown
        markdown_content = generate_fix_repo_markdown(error_entries)

        # Atomic write: write to temp file, then rename (prevents partial writes)
        temp_file = output_file.with_suffix(".tmp")
        try:
            temp_file.write_text(markdown_content, encoding="utf-8", newline="\n")
            temp_file.replace(output_file)  # Atomic on most filesystems
            logger.info("Successfully wrote fix_repo.md: %s", output_file)
        except Exception:
            # Clean up temp file on error
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
            raise

    except PermissionError:
        logger.error("Permission denied writing fix_repo.md: %s", output_file)
        raise
    except OSError as e:
        logger.error("Failed to write fix_repo.md: %s - %s", output_file, e)
        raise


def write_coding_tips(project_path: Path, process_entries: List[ErrorEntry]) -> None:
    """Write coding_tips.md with consolidated process issue entries.

    Filters entries where is_process_issue=True, generates markdown using
    generator, and writes to project_path/.errors_fixes/coding_tips.md.

    Creates directory if missing. Uses UTF-8 encoding and LF line endings.

    Args:
        project_path: Path to project root directory.
        process_entries: List of ErrorEntry objects (should be process issues).

    Raises:
        PermissionError: If file cannot be written due to permissions.
        OSError: If file operations fail for other reasons.
    """
    errors_fixes_dir = project_path / ".errors_fixes"
    output_file = errors_fixes_dir / "coding_tips.md"

    try:
        # Create directory if missing
        errors_fixes_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured directory exists: %s", errors_fixes_dir)

        # Filter entries (only process-issue entries)
        process_list = [e for e in process_entries if e.is_process_issue]
        logger.info(
            "Writing coding_tips.md for project %s with %d process issue(s)",
            project_path,
            len(process_list),
        )

        # Generate markdown
        markdown_content = generate_coding_tips_markdown(process_list)

        # Atomic write: write to temp file, then rename (prevents partial writes)
        temp_file = output_file.with_suffix(".tmp")
        try:
            temp_file.write_text(markdown_content, encoding="utf-8", newline="\n")
            temp_file.replace(output_file)  # Atomic on most filesystems
            logger.info("Successfully wrote coding_tips.md: %s", output_file)
        except Exception:
            # Clean up temp file on error
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
            raise

    except PermissionError:
        logger.error("Permission denied writing coding_tips.md: %s", output_file)
        raise
    except OSError as e:
        logger.error("Failed to write coding_tips.md: %s - %s", output_file, e)
        raise


def clear_errors_and_fixes(project_path: Path) -> None:
    """Clear errors_and_fixes.md but keep the file with header only.

    Reads current errors_and_fixes.md, replaces contents with header only,
    and writes back. Keeps the file (doesn't delete it).

    Uses UTF-8 encoding and LF line endings.

    Args:
        project_path: Path to project root directory.

    Raises:
        PermissionError: If file cannot be read/written due to permissions.
        OSError: If file operations fail for other reasons.
    """
    errors_fixes_dir = project_path / ".errors_fixes"
    errors_file = errors_fixes_dir / "errors_and_fixes.md"

    try:
        if not errors_file.exists():
            logger.warning(
                "errors_and_fixes.md does not exist: %s (skipping clear)",
                errors_file,
            )
            return

        logger.info("Clearing errors_and_fixes.md for project %s", project_path)

        # Atomic write: write to temp file, then rename (prevents partial writes)
        temp_file = errors_file.with_suffix(".tmp")
        try:
            temp_file.write_text(
                _ERRORS_AND_FIXES_HEADER, encoding="utf-8", newline="\n"
            )
            temp_file.replace(errors_file)  # Atomic on most filesystems
            logger.info("Successfully cleared errors_and_fixes.md: %s", errors_file)
        except Exception:
            # Clean up temp file on error
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
            raise

    except PermissionError:
        logger.error("Permission denied clearing errors_and_fixes.md: %s", errors_file)
        raise
    except OSError as e:
        logger.error("Failed to clear errors_and_fixes.md: %s - %s", errors_file, e)
        raise
