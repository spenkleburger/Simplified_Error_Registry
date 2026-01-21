# File: scripts/git_push.py
# Description: Interactive git add, commit, and push workflow
# Usage: python scripts/git_push.py

import shutil
import subprocess  # nosec B404 - only invoked with trusted developer tools
import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent
GIT_BINARY = shutil.which("git") or "git"


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=project_root,
        check=check,
        capture_output=False,  # Show output in real-time
    )
    return result


def main() -> int:
    """Main function to handle git add, commit, and push."""
    try:
        # Step 1: git add .
        print("\n📦 Staging all changes...")
        run_command([GIT_BINARY, "add", "."])
        print("✅ All changes staged\n")

        # Step 2: Get commit message from user
        print("Enter commit message (or press Enter to cancel):")
        commit_message = input("> ").strip()

        if not commit_message:
            print("\n❌ Commit cancelled (empty message)")
            return 1

        # Step 3: git commit -m "<message>"
        print(f"\n💾 Committing with message: '{commit_message}'...")
        run_command([GIT_BINARY, "commit", "-m", commit_message])
        print("✅ Changes committed\n")

        # Step 4: git push
        print("🚀 Pushing to remote...")
        run_command([GIT_BINARY, "push"])
        print("✅ Changes pushed successfully!\n")

        return 0

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Command failed with exit code {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
