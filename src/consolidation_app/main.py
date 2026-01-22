# main.py
# Main consolidation workflow (Phase 3.6).
# v1.0

"""
Orchestrate full consolidation: discover projects, parse, deduplicate,
tag, merge, write fix_repo/coding_tips, clear errors_and_fixes.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.consolidation_app.deduplicator import deduplicate_errors_exact
from src.consolidation_app.discovery import discover_projects
from src.consolidation_app.parser import (
    ErrorEntry,
    parse_coding_tips,
    parse_errors_and_fixes,
    parse_fix_repo,
)
from src.consolidation_app.tagger import apply_tags_to_entry
from src.consolidation_app.writer import (
    clear_errors_and_fixes,
    write_coding_tips,
    write_fix_repo,
)

logger = logging.getLogger(__name__)

_ERRORS_FIXES = ".errors_fixes/errors_and_fixes.md"
_FIX_REPO = ".errors_fixes/fix_repo.md"
_CODING_TIPS = ".errors_fixes/coding_tips.md"


@dataclass
class ConsolidationResult:
    """Result of consolidate_all_projects."""

    ok_count: int
    fail_count: int

    @property
    def all_ok(self) -> bool:
        return self.fail_count == 0


def consolidate_all_projects(
    root_path: Path,
    extra_projects: list[str] | None = None,
    *,
    dry_run: bool = False,
) -> ConsolidationResult:
    """
    Discover projects, consolidate each (parse, deduplicate, tag, write, clear).

    For each project:
    - Parse errors_and_fixes.md, fix_repo.md (if exists), coding_tips.md (if exists)
    - Deduplicate errors and process issues separately
    - Generate tags (merge with existing)
    - Write fix_repo.md, coding_tips.md; clear errors_and_fixes.md (unless dry_run)

    Continues on per-project failure; logs errors. Returns ok_count and fail_count.

    Args:
        root_path: Root directory to search for projects.
        extra_projects: Optional list of project paths to include.
        dry_run: If True, do not write files; only log intended actions.

    Returns:
        ConsolidationResult(ok_count, fail_count).
    """
    ok_count = 0
    fail_count = 0

    try:
        projects = discover_projects(root_path, extra_projects=extra_projects)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        logger.error("Discovery failed: %s", e)
        return ConsolidationResult(ok_count=0, fail_count=1)

    if not projects:
        logger.info("No projects found under %s", root_path)
        return ConsolidationResult(ok_count=0, fail_count=0)

    logger.info("Consolidating %d project(s) (dry_run=%s)", len(projects), dry_run)

    for project in projects:
        err_file = project / ".errors_fixes" / "errors_and_fixes.md"
        if not err_file.exists():
            logger.warning(
                "Missing %s for project %s (skipping)", _ERRORS_FIXES, project
            )
            continue

        try:
            _consolidate_one_project(project, dry_run=dry_run)
            ok_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(
                "Consolidation failed for project %s: %s",
                project,
                e,
                exc_info=True,
            )

    logger.info(
        "Consolidation complete: %d ok, %d failed",
        ok_count,
        fail_count,
    )
    return ConsolidationResult(ok_count=ok_count, fail_count=fail_count)


def _consolidate_one_project(project: Path, *, dry_run: bool = False) -> None:
    """Run full consolidate workflow for a single project."""

    errors_file = project / ".errors_fixes" / "errors_and_fixes.md"
    fix_repo_file = project / _FIX_REPO
    coding_tips_file = project / _CODING_TIPS

    new_entries = parse_errors_and_fixes(errors_file)
    new_errors = [e for e in new_entries if not e.is_process_issue]
    new_process = [e for e in new_entries if e.is_process_issue]

    existing_errors = parse_fix_repo(fix_repo_file) if fix_repo_file.exists() else []
    existing_process = (
        parse_coding_tips(coding_tips_file) if coding_tips_file.exists() else []
    )

    consolidated_errors = deduplicate_errors_exact(new_errors, existing_errors)
    consolidated_process = deduplicate_errors_exact(new_process, existing_process)

    consolidated_errors = [apply_tags_to_entry(e) for e in consolidated_errors]
    consolidated_process = [apply_tags_to_entry(e) for e in consolidated_process]

    all_consolidated: List[ErrorEntry] = consolidated_errors + consolidated_process

    logger.info(
        "Project %s: %d error(s), %d process issue(s) consolidated",
        project,
        len(consolidated_errors),
        len(consolidated_process),
    )

    if dry_run:
        logger.info(
            "[dry-run] Would write fix_repo (%d), coding_tips (%d), clear errors_and_fixes",
            len(consolidated_errors),
            len(consolidated_process),
        )
        return

    write_fix_repo(project, all_consolidated)
    write_coding_tips(project, all_consolidated)
    clear_errors_and_fixes(project)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consolidate errors_and_fixes into fix_repo and coding_tips."
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory to search for projects (.errors_fixes/errors_and_fixes.md)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional config file (reserved for future use)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; only log intended actions",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entrypoint. Returns 0 on success, 1 on failure."""
    args = _parse_args()

    try:
        from config.logging import setup_logging
    except ImportError:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        setup_logging()

    if args.config is not None:
        logger.debug("Config file (ignored): %s", args.config)

    root = args.root.resolve()
    if not root.exists():
        logger.error("Root path does not exist: %s", root)
        return 1
    if not root.is_dir():
        logger.error("Root path is not a directory: %s", root)
        return 1

    result = consolidate_all_projects(root, extra_projects=None, dry_run=args.dry_run)
    return 0 if result.all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
