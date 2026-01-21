# File: scripts/bootstrap_errors_fixes.py
# Description: Bootstrap script to create .errors_fixes/ folder structure with template files
# Version: 1.0
# Usage: python scripts/bootstrap_errors_fixes.py <project_path> [--no-gitignore]

import argparse
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Setup basic logging (console only for bootstrap script)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Template content for each file
ERRORS_AND_FIXES_HEADER = """# Errors and Fixes Log

> **Note**: This file is processed daily by the consolidation app at 2 AM.
> `### Error:` entries → fix_repo.md; `### Agent Process Issue:` entries → coding_tips.md. Contents are then cleared (file is kept).

"""

FIX_REPO_HEADER = """# Fix Repository

> **Last Updated:** {timestamp}
> **Total Entries:** 0
> **Consolidated from:** 0 projects

"""

CODING_TIPS_HEADER = """# Coding Tips - Agent Process Rules

> **Last Updated:** {timestamp}
> **Total Rules:** 0

"""


def create_errors_fixes_directory(project_path: Path) -> Path:
    """
    Create .errors_fixes/ directory in the project root.

    Args:
        project_path: Path to the project root

    Returns:
        Path to the created .errors_fixes directory

    Raises:
        PermissionError: If directory cannot be created due to permissions
        OSError: If directory creation fails for other reasons
    """
    errors_fixes_dir = project_path / ".errors_fixes"

    try:
        errors_fixes_dir.mkdir(exist_ok=True)
        logger.info(f"Created directory: {errors_fixes_dir}")
        return errors_fixes_dir
    except PermissionError:
        logger.error(f"Permission denied creating directory: {errors_fixes_dir}")
        raise
    except OSError as e:
        logger.error(f"Failed to create directory: {errors_fixes_dir} - {e}")
        raise


def create_errors_and_fixes_file(errors_fixes_dir: Path) -> None:
    """
    Create errors_and_fixes.md file with header.

    Args:
        errors_fixes_dir: Path to .errors_fixes directory

    Raises:
        PermissionError: If file cannot be created due to permissions
        OSError: If file creation fails for other reasons
    """
    file_path = errors_fixes_dir / "errors_and_fixes.md"

    try:
        if file_path.exists():
            logger.warning(f"File already exists: {file_path} (skipping)")
            return

        # Write with LF line endings directly
        content = ERRORS_AND_FIXES_HEADER.replace("\r\n", "\n").replace("\r", "\n")
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        logger.info(f"Created file: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied creating file: {file_path}")
        raise
    except OSError as e:
        logger.error(f"Failed to create file: {file_path} - {e}")
        raise


def create_fix_repo_file(errors_fixes_dir: Path) -> None:
    """
    Create fix_repo.md file with header.

    Args:
        errors_fixes_dir: Path to .errors_fixes directory

    Raises:
        PermissionError: If file cannot be created due to permissions
        OSError: If file creation fails for other reasons
    """
    file_path = errors_fixes_dir / "fix_repo.md"
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        if file_path.exists():
            logger.warning(f"File already exists: {file_path} (skipping)")
            return

        # Write with LF line endings directly
        content = (
            FIX_REPO_HEADER.format(timestamp=timestamp)
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        logger.info(f"Created file: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied creating file: {file_path}")
        raise
    except OSError as e:
        logger.error(f"Failed to create file: {file_path} - {e}")
        raise


def create_coding_tips_file(errors_fixes_dir: Path) -> None:
    """
    Create coding_tips.md file with header.

    Args:
        errors_fixes_dir: Path to .errors_fixes directory

    Raises:
        PermissionError: If file cannot be created due to permissions
        OSError: If file creation fails for other reasons
    """
    file_path = errors_fixes_dir / "coding_tips.md"
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        if file_path.exists():
            logger.warning(f"File already exists: {file_path} (skipping)")
            return

        # Write with LF line endings directly
        content = (
            CODING_TIPS_HEADER.format(timestamp=timestamp)
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        logger.info(f"Created file: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied creating file: {file_path}")
        raise
    except OSError as e:
        logger.error(f"Failed to create file: {file_path} - {e}")
        raise


def update_gitignore(project_path: Path) -> None:
    """
    Update .gitignore file to add .errors_fixes/ entry if not already present.

    Args:
        project_path: Path to the project root

    Raises:
        PermissionError: If .gitignore cannot be read/written due to permissions
        OSError: If file operations fail for other reasons
    """
    gitignore_path = project_path / ".gitignore"
    entry = ".errors_fixes/"

    try:
        # Read existing .gitignore if it exists
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")

            # Check if entry already exists
            if entry in content or entry.rstrip("/") in content:
                logger.info(f"Entry '{entry}' already exists in .gitignore (skipping)")
                return

            # Add entry (with newline if file doesn't end with one)
            if not content.endswith("\n"):
                content += "\n"
            content += f"{entry}\n"
        else:
            # Create new .gitignore with entry
            content = f"{entry}\n"
            logger.info(f"Creating new .gitignore file: {gitignore_path}")

        # Write updated content with LF line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        with open(gitignore_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        logger.info(f"Updated .gitignore: added '{entry}'")
    except PermissionError:
        logger.error(f"Permission denied accessing .gitignore: {gitignore_path}")
        raise
    except OSError as e:
        logger.error(f"Failed to update .gitignore: {gitignore_path} - {e}")
        raise


def bootstrap_project(project_path: Path, update_gitignore_flag: bool = True) -> None:
    """
    Bootstrap .errors_fixes/ folder structure for a project.

    Args:
        project_path: Path to the project root
        update_gitignore_flag: Whether to update .gitignore (default: True)

    Raises:
        FileNotFoundError: If project_path does not exist
        PermissionError: If operations fail due to permissions
        OSError: If file operations fail
    """
    # Validate project path exists
    if not project_path.exists():
        error_msg = f"Project path does not exist: {project_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    if not project_path.is_dir():
        error_msg = f"Project path is not a directory: {project_path}"
        logger.error(error_msg)
        raise NotADirectoryError(error_msg)

    logger.info(f"Bootstrapping .errors_fixes/ for project: {project_path}")

    try:
        # Create directory
        errors_fixes_dir = create_errors_fixes_directory(project_path)

        # Create files
        create_errors_and_fixes_file(errors_fixes_dir)
        create_fix_repo_file(errors_fixes_dir)
        create_coding_tips_file(errors_fixes_dir)

        # Update .gitignore if requested
        if update_gitignore_flag:
            update_gitignore(project_path)
        else:
            logger.info("Skipping .gitignore update (--no-gitignore flag set)")

        logger.info("Bootstrap completed successfully")
    except (PermissionError, OSError) as e:
        logger.error(f"Bootstrap failed: {e}")
        raise


def main() -> int:
    """Main entry point for bootstrap script."""
    parser = argparse.ArgumentParser(
        description="Bootstrap .errors_fixes/ folder structure for a project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "project_path",
        type=str,
        help="Path to the project root directory",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Skip updating .gitignore file",
    )

    args = parser.parse_args()

    # Resolve and validate project path
    try:
        project_path = Path(args.project_path).resolve()
    except Exception as e:
        logger.error(f"Invalid project path: {args.project_path} - {e}")
        return 1

    try:
        bootstrap_project(project_path, update_gitignore_flag=not args.no_gitignore)
        return 0
    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError) as e:
        logger.error(f"Bootstrap failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error during bootstrap: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
