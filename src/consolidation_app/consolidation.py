# consolidation.py
# Parser integration into consolidation workflow (Phase 3.2).
# v1.0

"""
Integrate parser with discovery: read errors_and_fixes.md per project,
parse entries, separate by is_process_issue, group by project.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.consolidation_app.discovery import discover_projects
from src.consolidation_app.parser import ErrorEntry, parse_errors_and_fixes

logger = logging.getLogger(__name__)

_ERRORS_FIXES_FILE = ".errors_fixes/errors_and_fixes.md"


@dataclass
class ProjectEntries:
    """Entries parsed from one project, split by type."""

    project: Path
    errors: List[ErrorEntry]
    process_issues: List[ErrorEntry]


def process_projects(
    root_path: Path,
    extra_projects: list[str] | None = None,
) -> List[ProjectEntries]:
    """
    Discover projects, read and parse errors_and_fixes.md for each,
    separate by is_process_issue, group by project.

    Skips projects with missing files (logs warning). On parse/IO errors,
    logs error and continues with other projects. Empty files yield
    ProjectEntries with empty errors/process_issues lists.

    Args:
        root_path: Root directory to search for projects.
        extra_projects: Optional list of project paths to include.

    Returns:
        List of ProjectEntries, one per successfully processed project.
    """
    projects = discover_projects(root_path, extra_projects=extra_projects)
    logger.info("Processing %d project(s)", len(projects))

    results: List[ProjectEntries] = []
    errors_encountered = 0

    for project in projects:
        errors_file = project / ".errors_fixes" / "errors_and_fixes.md"

        if not errors_file.exists():
            logger.warning(
                "Missing %s for project %s (skipping)",
                _ERRORS_FIXES_FILE,
                project,
            )
            continue

        try:
            entries = parse_errors_and_fixes(errors_file)
        except OSError as e:
            logger.error(
                "Failed to read %s for project %s: %s",
                errors_file,
                project,
                e,
                exc_info=False,
            )
            errors_encountered += 1
            continue
        except Exception as e:
            logger.error(
                "Parse error for %s (project %s): %s",
                errors_file,
                project,
                e,
                exc_info=True,
            )
            errors_encountered += 1
            continue

        errors_list: List[ErrorEntry] = []
        process_list: List[ErrorEntry] = []
        for e in entries:
            if e.is_process_issue:
                process_list.append(e)
            else:
                errors_list.append(e)

        logger.info(
            "Project %s: %d error(s), %d process issue(s)",
            project,
            len(errors_list),
            len(process_list),
        )
        results.append(
            ProjectEntries(project=project, errors=errors_list, process_issues=process_list)
        )

    if errors_encountered:
        logger.warning("Encountered %d error(s) during parsing", errors_encountered)

    logger.info(
        "Consolidation complete: %d project(s) processed, %d error(s) encountered",
        len(results),
        errors_encountered,
    )
    return results
