"""Discovery module for finding projects with .errors_fixes/ folder structure."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Import bootstrap function from scripts
# We need to add the scripts directory to the path temporarily
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from bootstrap_errors_fixes import bootstrap_project
except ImportError:
    # Fallback if import fails - we'll handle this in the function
    bootstrap_project = None

logger = logging.getLogger(__name__)


def _validate_extra_project_path(path_str: str) -> bool:
    """
    Validate that an extra project path string is safe.

    Checks for:
    - Suspicious traversal patterns (../, ..\\)
    - Empty or whitespace-only paths
    - Paths that would resolve outside expected boundaries

    Args:
        path_str: Path string to validate.

    Returns:
        True if path appears safe, False otherwise.
    """
    if not path_str or not path_str.strip():
        return False

    # Check for obvious traversal patterns before resolution
    normalized = path_str.replace("\\", "/")
    if ".." in normalized:
        # Allow .. if it's part of a valid relative path that will be resolved
        # But flag if it's clearly trying to escape (e.g., ../../etc/passwd)
        suspicious_patterns = ["../..", "..\\..", "/../", "\\..\\"]
        if any(pattern in normalized for pattern in suspicious_patterns):
            logger.warning(
                "Suspicious path pattern detected in extra_projects: %s", path_str
            )
            return False

    return True


def discover_projects(
    root_path: Path, extra_projects: list[str] | None = None
) -> list[Path]:
    """
    Discover all projects with .errors_fixes/errors_and_fixes.md files.

    This function searches for projects in two ways:
    1. Recursively searches from root_path for .errors_fixes/errors_and_fixes.md files
    2. Processes extra_projects list (paths outside the scan root)

    For extra_projects, if errors_and_fixes.md is missing, the function will
    automatically bootstrap the project (create the .errors_fixes/ folder structure).

    Args:
        root_path: Root directory to search for projects
        extra_projects: Optional list of project paths (strings) to include.
                       These paths are resolved and checked. If errors_and_fixes.md
                       is missing, bootstrap is called automatically.

    Returns:
        List of project root paths (deduplicated)

    Raises:
        FileNotFoundError: If root_path does not exist
        PermissionError: If root_path cannot be accessed
        ValueError: If extra_projects contains invalid paths

    Example:
        >>> from pathlib import Path
        >>> projects = discover_projects(Path("/home/user/projects"))
        >>> print(projects)
        [Path('/home/user/projects/proj1'), Path('/home/user/projects/proj2')]
    """
    # Validate root_path
    if not root_path.exists():
        error_msg = f"Root path does not exist: {root_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    if not root_path.is_dir():
        error_msg = f"Root path is not a directory: {root_path}"
        logger.error(error_msg)
        raise NotADirectoryError(error_msg)

    logger.info(f"Discovering projects from root: {root_path}")

    projects: list[Path] = []

    # Step 1: Discover projects via rglob
    try:
        logger.debug(f"Searching for .errors_fixes/errors_and_fixes.md in {root_path}")
        found_files = list(root_path.rglob(".errors_fixes/errors_and_fixes.md"))

        for file_path in found_files:
            # Get project root: file_path is .errors_fixes/errors_and_fixes.md
            # So project root is file_path.parent.parent
            project_root = file_path.parent.parent.resolve()
            projects.append(project_root)
            logger.debug(f"Found project via rglob: {project_root}")

        logger.info(f"Found {len(found_files)} projects via rglob")
    except PermissionError as e:
        logger.warning(f"Permission denied while searching {root_path}: {e}")
        # Continue with extra_projects even if rglob fails
    except Exception as e:
        logger.error(f"Unexpected error during rglob discovery: {e}", exc_info=True)
        # Continue with extra_projects even if rglob fails

    # Step 2: Process extra_projects list
    if extra_projects:
        logger.info(f"Processing {len(extra_projects)} extra projects")
        for extra_path_str in extra_projects:
            try:
                # Validate path string before processing
                if not _validate_extra_project_path(extra_path_str):
                    logger.warning(
                        f"Invalid or suspicious extra project path: {extra_path_str} (skipping)"
                    )
                    continue

                # Resolve the path (normalizes and makes absolute)
                extra_path = Path(extra_path_str).resolve()

                # Check if it exists
                if not extra_path.exists():
                    logger.warning(
                        f"Extra project path does not exist: {extra_path_str} (skipping)"
                    )
                    continue

                if not extra_path.is_dir():
                    logger.warning(
                        f"Extra project path is not a directory: {extra_path_str} (skipping)"
                    )
                    continue

                # Check if errors_and_fixes.md exists
                errors_fixes_file = extra_path / ".errors_fixes" / "errors_and_fixes.md"

                if not errors_fixes_file.exists():
                    logger.info(
                        f"errors_and_fixes.md not found in {extra_path}, bootstrapping..."
                    )

                    # Auto-bootstrap if bootstrap function is available
                    if bootstrap_project is None:
                        logger.error(
                            "Bootstrap function not available. Cannot auto-bootstrap project. "
                            "Please run bootstrap_errors_fixes.py manually."
                        )
                        raise ValueError(
                            f"Cannot bootstrap {extra_path_str}: bootstrap function unavailable"
                        )

                    try:
                        # Bootstrap with update_gitignore=False to avoid modifying gitignore
                        # during consolidation (this is an internal operation)
                        bootstrap_project(extra_path, update_gitignore_flag=False)
                        logger.info(f"Successfully bootstrapped project: {extra_path}")
                    except Exception as e:
                        logger.error(
                            f"Failed to bootstrap project {extra_path}: {e}",
                            exc_info=True,
                        )
                        raise ValueError(
                            f"Failed to bootstrap {extra_path_str}: {e}"
                        ) from e

                # Add to projects list
                projects.append(extra_path)
                logger.debug(f"Added extra project: {extra_path}")

            except (ValueError, PermissionError, OSError) as e:
                logger.error(f"Error processing extra project {extra_path_str}: {e}")
                raise
            except Exception as e:
                logger.error(
                    f"Unexpected error processing extra project {extra_path_str}: {e}",
                    exc_info=True,
                )
                raise ValueError(f"Invalid extra project path: {extra_path_str}") from e

    # Step 3: Deduplicate projects
    # Use dict.fromkeys() to preserve order while removing duplicates
    unique_projects = list(dict.fromkeys(projects))

    logger.info(
        f"Discovery complete: {len(unique_projects)} unique projects found "
        f"(from {len(projects)} total entries)"
    )

    return unique_projects
