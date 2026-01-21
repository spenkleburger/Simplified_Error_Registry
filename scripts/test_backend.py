# File: scripts/test_backend.py
# Description: Run backend tests with smart detection (only changed files)
# Usage: python scripts/test_backend.py
# This detects backend files changed since last commit and runs appropriate tests
# Output is automatically copied to clipboard for easy sharing

import os
import subprocess  # nosec B404 - only invoked with trusted developer tools
import sys
from io import StringIO
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

project_root = Path(__file__).parent.parent
GIT_BINARY = "git"


class OutputCapture:
    """Capture stdout/stderr while still printing to console."""

    def __init__(self):
        self.buffer = StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text):
        """Write to both buffer and original stdout/stderr."""
        self.buffer.write(text)
        self.original_stdout.write(text)
        self.original_stdout.flush()

    def flush(self):
        """Flush both buffer and original stdout/stderr."""
        self.buffer.flush()
        self.original_stdout.flush()

    def get_value(self):
        """Get captured output as string."""
        return self.buffer.getvalue()

    def __enter__(self):
        sys.stdout = self
        sys.stderr = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True if successful."""
    try:
        if sys.platform == "win32":
            # Use Windows clip command
            process = (
                subprocess.Popen(  # nosec B603 B607 - developer tooling invocation
                    ["clip"],
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                )
            )
            process.communicate(input=text, timeout=5)
            return process.returncode == 0
        else:
            # For Linux/Mac, try xclip or pbcopy
            if sys.platform == "darwin":
                cmd = ["pbcopy"]
            else:
                cmd = ["xclip", "-selection", "clipboard"]
            process = subprocess.Popen(  # nosec B603 - developer tooling invocation
                cmd,
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
            process.communicate(input=text, timeout=5)
            return process.returncode == 0
    except Exception:
        return False


def get_changed_files():
    """Get all changed files since last commit (including untracked)."""
    files = []

    try:
        # Get modified/staged files since HEAD
        result = subprocess.run(  # nosec B603 - arguments are static git invocations
            [GIT_BINARY, "diff", "HEAD", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            cwd=project_root,
            check=False,
            stdin=subprocess.DEVNULL,  # Prevent waiting for input
        )

        if result.returncode == 0:
            files.extend(result.stdout.strip().split("\n"))

        # Get untracked files
        result_untracked = (
            subprocess.run(  # nosec B603 - arguments are static git invocations
                [GIT_BINARY, "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                cwd=project_root,
                check=False,
                stdin=subprocess.DEVNULL,  # Prevent waiting for input
            )
        )

        if result_untracked.returncode == 0:
            files.extend(result_untracked.stdout.strip().split("\n"))
    except FileNotFoundError:
        print("❌ Error: Git not found. Please ensure Git is installed and in PATH.")
        return []
    except Exception as e:
        print(f"❌ Error getting changed files: {e}")
        return []

    # Remove empty strings
    return [f for f in files if f]


def filter_backend_files(changed_files):
    """Filter changed files to only backend Python files."""
    backend_patterns = [
        "src/",
        "config/",
        "tests/",
        "scripts/",
        "alembic/",
    ]

    backend_files = []
    for file in changed_files:
        if file.endswith(".py") and any(
            file.startswith(pattern) for pattern in backend_patterns
        ):
            backend_files.append(file)

    return backend_files


def map_files_to_tests(changed_files):
    """Map changed source files to their corresponding test files."""
    test_files = []

    for file in changed_files:
        # Convert src/module.py -> tests/test_module.py
        if file.startswith("src/"):
            test_file = file.replace("src/", "tests/test_")
            if (project_root / test_file).exists() and test_file not in test_files:
                test_files.append(test_file)
        # If it's already a test file, include it
        elif file.startswith("tests/"):
            if file not in test_files:
                test_files.append(file)
        # Convert scripts/script.py -> tests/test_script.py
        elif file.startswith("scripts/"):
            test_file = file.replace("scripts/", "tests/test_")
            if (project_root / test_file).exists() and test_file not in test_files:
                test_files.append(test_file)
        # Convert config/module.py -> tests/test_config_module.py
        elif file.startswith("config/"):
            test_file = file.replace("config/", "tests/test_config_")
            if (project_root / test_file).exists() and test_file not in test_files:
                test_files.append(test_file)

    return test_files


def run_backend_tests(changed_files=None):
    """Run backend tests - only for changed files if provided."""
    print("\n" + "=" * 70)
    print("🧪 Running Backend Tests")
    print("=" * 70)

    if not changed_files:
        print("⚠️  No changed files provided - running all backend tests")
        print("   Run 'task test' to run all backend tests")
        pytest_cmd = [sys.executable, "-m", "pytest", "-v", "--maxfail=5", "--tb=short"]
    else:
        # Filter to only Python source files
        python_source_files = [
            f
            for f in changed_files
            if f.endswith(".py")
            and any(f.startswith(p) for p in ["src/", "config/", "scripts/", "tests/"])
        ]

        if not python_source_files:
            print("✅ No Python source files changed - skipping backend tests")
            print("   Changed files are docs/config only, no code changes to test")
            return True

        # Map changed files to test files
        test_files = map_files_to_tests(python_source_files)

        if not test_files:
            print("⚠️  No corresponding test files found for changed Python files")
            print("   Changed files:")
            for f in python_source_files[:3]:
                print(f"     - {f}")
            if len(python_source_files) > 3:
                print(f"     ... and {len(python_source_files) - 3} more")
            print("\n   Skipping backend tests (no test files to run)")
            print("   This is normal if you haven't written tests yet.")
            print("   Run 'task test' manually to run all tests if needed.")
            return True

        print(f"Running tests for {len(test_files)} test file(s):")
        for tf in test_files[:5]:  # Show first 5
            print(f"  - {tf}")
        if len(test_files) > 5:
            print(f"  ... and {len(test_files) - 5} more")

        # Build pytest command with early exit options
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-v",  # Verbose output
            "--maxfail=5",  # Stop after 5 failures
            "--tb=short",  # Short traceback (faster)
        ]
        pytest_cmd.extend(test_files)

    # Set environment to force non-interactive mode
    env = os.environ.copy()
    env["PYTEST_CURRENT_TEST"] = ""  # Clear any existing test context

    # Run pytest normally (no timeout - let it complete)
    result = subprocess.run(  # nosec B603 - developer tooling invocation
        pytest_cmd,
        cwd=project_root,
        stdin=subprocess.DEVNULL,  # Prevent waiting for input
        env=env,
    )
    return result.returncode == 0


def main():
    """Main backend test runner."""
    # Capture all output to buffer and print to console
    with OutputCapture() as captured_output:
        print("=" * 70)
        print("🐍 Backend Test Runner")
        print("=" * 70)
        print("Detecting changed files since last commit...\n")

        # Get changed files
        changed_files = get_changed_files()

        if not changed_files:
            print("✅ No changed files detected since last commit.")
            print("   Run 'task test' to run all backend tests")
            return 0

        # Filter to backend files only
        backend_files = filter_backend_files(changed_files)

        if not backend_files:
            print("✅ No backend files changed - skipping backend tests")
            print("   Changed files are frontend/docs only, no backend code changes")
            return 0

        print(f"Found {len(backend_files)} changed backend file(s):")
        for f in backend_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(backend_files) > 10:
            print(f"  ... and {len(backend_files) - 10} more")

        # Run backend tests
        all_passed = run_backend_tests(backend_files)

        # Summary
        print("\n" + "=" * 70)
        if all_passed:
            print("✅ All backend tests passed!")
        else:
            print("❌ Some backend tests failed")

        # Copy all output to clipboard
        try:
            captured_output_value = captured_output.get_value()
            if copy_to_clipboard(captured_output_value):
                print("\n📋 Test results copied to clipboard! You can paste them now.")
            else:
                print(
                    "\n⚠️  Failed to copy results to clipboard (but output is shown above)."
                )
        except Exception as e:
            print(f"\n⚠️  Error copying to clipboard: {e} (but output is shown above).")

        # Flush output before returning
        sys.stdout.flush()
        sys.stderr.flush()

        return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
