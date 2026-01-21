# File: scripts/test_integration.py
# Description: Run integration tests with smart detection (only when API schemas change)
# Usage: python scripts/test_integration.py
# This detects API schema changes since last commit and runs integration tests
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


def filter_api_schema_files(changed_files):
    """Filter changed files to only API schema files."""
    api_schema_patterns = [
        "src/schemas/",
        "src/api/v1/",
    ]

    api_files = []
    for file in changed_files:
        if any(file.startswith(pattern) for pattern in api_schema_patterns):
            api_files.append(file)

    return api_files


def run_integration_tests():
    """Run integration tests."""
    print("\n" + "=" * 70)
    print("🔗 Running Integration Tests")
    print("=" * 70)
    print("Integration tests verify backend-frontend contract compatibility.")
    print(
        "These tests are slower and require services (database, Redis) to be running.\n"
    )

    # Build pytest command for integration tests
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",  # Verbose output
        "-m",
        "integration",  # Only run integration tests
        "--maxfail=5",  # Stop after 5 failures
        "--tb=short",  # Short traceback
    ]

    # Set environment to force non-interactive mode
    env = os.environ.copy()
    env["PYTEST_CURRENT_TEST"] = ""  # Clear any existing test context

    # Run pytest with timeout (integration tests can take longer)
    try:
        result = subprocess.run(  # nosec B603 - developer tooling invocation
            pytest_cmd,
            cwd=project_root,
            stdin=subprocess.DEVNULL,  # Prevent waiting for input
            env=env,
            timeout=600,  # 10 minute timeout for integration tests
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("\n⚠️  Integration tests timed out after 10 minutes")
        print("   This may indicate hanging tests or services not running")
        return False


def main():
    """Main integration test runner."""
    # Capture all output to buffer and print to console
    with OutputCapture() as captured_output:
        print("=" * 70)
        print("🔗 Integration Test Runner")
        print("=" * 70)
        print("Detecting API schema changes since last commit...\n")

        # Get changed files
        changed_files = get_changed_files()

        if not changed_files:
            print("✅ No changed files detected since last commit.")
            print("   Run 'task test:integration' to run all integration tests")
            return 0

        # Filter to API schema files only
        api_files = filter_api_schema_files(changed_files)

        if not api_files:
            print("✅ No API schema files changed - skipping integration tests")
            print("   Integration tests run automatically when API schemas change")
            print(
                "   Run 'task test:integration' manually to run all integration tests"
            )
            return 0

        print(f"Found {len(api_files)} changed API schema file(s):")
        for f in api_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(api_files) > 10:
            print(f"  ... and {len(api_files) - 10} more")

        print("\n⚠️  API SCHEMAS CHANGED - Running Integration Tests")
        print("API contract changes detected. Running integration tests to verify")
        print(
            "backend-frontend compatibility. Agent should create/update tests as needed."
        )

        # Run integration tests
        all_passed = run_integration_tests()

        # Summary
        print("\n" + "=" * 70)
        if all_passed:
            print("✅ All integration tests passed!")
        else:
            print("❌ Some integration tests failed")

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
