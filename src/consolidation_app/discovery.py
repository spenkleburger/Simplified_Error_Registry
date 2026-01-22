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
    1. Checks immediate subdirectories of root_path (non-recursive)
       - Each subdirectory is expected to be a project
       - Looks for .errors_fixes/errors_and_fixes.md at the project root level
    2. Processes extra_projects list (paths outside the scan root)

    For extra_projects, if errors_and_fixes.md is missing, the function will
    automatically bootstrap the project (create the .errors_fixes/ folder structure).

    Args:
        root_path: Root directory containing project subdirectories.
                  Each immediate subdirectory is checked for .errors_fixes/errors_and_fixes.md
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
        >>> projects = discover_projects(Path("/projects"))
        >>> print(projects)
        [Path('/projects/proj1'), Path('/projects/proj2')]
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

    target_file = Path(".errors_fixes") / "errors_and_fixes.md"

    # Step 0: Check if root_path itself is a project (for testing/single-project scenarios)
    # In production, C:\Projects contains project folders, but we support root being a project too
    root_errors_fixes_path = root_path / target_file
    if root_errors_fixes_path.is_file():
        projects.append(root_path.resolve())
        logger.debug(f"Found project at root: {root_path}")

    # Step 1: Discover projects by checking immediate subdirectories only
    # Each subdirectory under root_path is expected to be a project
    # with .errors_fixes/errors_and_fixes.md at the project root level
    try:
        logger.debug(f"Checking immediate subdirectories of {root_path} for projects")

        checked_count = 0

        # Iterate over immediate subdirectories only (not recursive)
        for item in root_path.iterdir():
            if not item.is_dir():
                continue

            checked_count += 1
            # Optimize: Avoid resolve() until we know we have a project
            # This reduces slow Docker mount calls when checking many directories
            # Only resolve when we actually find a project with .errors_fixes/

            # Optimize: Use is_file() which checks both existence and type in one call
            # This reduces file system operations on Docker mounts (from 2 calls to 1)
            errors_fixes_path = item / target_file
            if errors_fixes_path.is_file():
                # Only resolve when we actually have a project (reduces resolve() calls)
                projects.append(item.resolve())
                logger.debug(f"Found project: {item}")
            else:
                logger.debug(f"Skipping {item.name}: missing {target_file}")

        logger.info(
            f"Checked root + {checked_count} subdirectories, found {len(projects)} project(s)"
        )
    except PermissionError as e:
        logger.warning(f"Permission denied while scanning {root_path}: {e}")
        # Continue with extra_projects even if scan fails
    except Exception as e:
        logger.error(f"Unexpected error during project discovery: {e}", exc_info=True)
        # Continue with extra_projects even if scan fails

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
                # Optimize: Use is_file() which checks both existence and type in one call
                errors_fixes_file = extra_path / ".errors_fixes" / "errors_and_fixes.md"

                if not errors_fixes_file.is_file():
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
