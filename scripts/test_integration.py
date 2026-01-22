# File: scripts/test_integration.py
# Description: Run integration tests with smart detection (only when API schemas change)
# Usage: python scripts/test_integration.py
# This detects API schema changes since last commit and runs integration tests
# Output is automatically copied to clipboard for easy sharing
#
# ============================================================================
# PROJECT-SPECIFIC CUSTOMIZATION
# ============================================================================
# When copying this script to your project template, customize these sections:
#
# 1. API SCHEMA PATTERNS (line ~257):
#    - Update `api_schema_patterns` list to match your API schema locations
#    - Default: ["src/schemas/", "src/api/v1/"]
#    - This determines when integration tests run automatically
#
# 2. COMMAND HEADER (line ~173):
#    - Update command string to match your task runner command
#    - Default: "Command: task test:integration"
#
# 3. PROJECT-SPECIFIC CODE (lines ~47-52, ~295, ~380-399):
#    - Remove the VERIFICATION_TEST_FILE constant and all references to it
#    - Search for "VERIFICATION_TEST_FILE" and "PROJECT-SPECIFIC" comments
#    - This is only needed for this project's verification workflow
#
# The core functionality (error extraction, clipboard copying) is generic and
# works for any project using pytest with integration markers. Only the above
# sections need customization.
# ============================================================================

import argparse
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

# ============================================================================
# PROJECT-SPECIFIC CONFIGURATION
# ============================================================================
# When copying this script to a template, REMOVE the following constant and
# all references to it (search for "VERIFICATION_TEST_FILE").
# This is only needed for this specific project's verification workflow.
VERIFICATION_TEST_FILE = "tests/test_verify_integration_output_capture.py"
# ============================================================================


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


def extract_error_sections(full_output: str) -> str:
    """
    Extract only the relevant error sections from pytest output.

    Captures:
    - === FAILURES === section (detailed error tracebacks)
    - === ERRORS === section (collection/import errors)
    - === short test summary info === section (concise summary)

    Excludes:
    - Passing test output
    - Test collection info
    - Coverage reports
    - Other irrelevant sections
    """
    lines = full_output.split("\n")
    extracted = []
    in_failures = False
    in_errors = False
    in_summary = False
    capture_buffer = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for section markers (pytest uses === with many equals signs)
        # Format: ================================== FAILURES ===================================
        if "FAILURES" in line and "===" in line:
            in_failures = True
            in_errors = False
            in_summary = False
            if capture_buffer:
                extracted.extend(capture_buffer)
                capture_buffer = []
            extracted.append(line)
        elif "ERRORS" in line and "===" in line:
            in_errors = True
            in_failures = False
            in_summary = False
            if capture_buffer:
                extracted.extend(capture_buffer)
                capture_buffer = []
            extracted.append(line)
        elif "short test summary info" in line and "===" in line:
            in_summary = True
            in_failures = False
            in_errors = False
            if capture_buffer:
                extracted.extend(capture_buffer)
                capture_buffer = []
            extracted.append(line)
        elif in_failures or in_errors or in_summary:
            # Continue capturing until next section or end
            # Check if this line is a new section marker
            is_failures_marker = "FAILURES" in line and "===" in line
            is_errors_marker = "ERRORS" in line and "===" in line
            is_summary_marker = "short test summary" in line and "===" in line

            # If we hit a different section marker, switch to that section
            if is_failures_marker and not in_failures:
                # Switching to failures section
                in_failures = True
                in_errors = False
                in_summary = False
                extracted.append(line)
            elif is_errors_marker and not in_errors:
                # Switching to errors section
                in_errors = True
                in_failures = False
                in_summary = False
                extracted.append(line)
            elif is_summary_marker and not in_summary:
                # Switching to summary section
                in_summary = True
                in_failures = False
                in_errors = False
                extracted.append(line)
            elif is_failures_marker or is_errors_marker or is_summary_marker:
                # Same section marker repeated (shouldn't happen, but handle it)
                extracted.append(line)
            else:
                # Regular content line - capture it
                extracted.append(line)
        else:
            # Not in any error section, but buffer lines that might be part of a section
            # (handles cases where section marker might be split across lines)
            # Check for pytest format: === with FAILURES/ERRORS/short test summary
            if (
                ("===" in line and "FAILURES" in line)
                or ("===" in line and "ERRORS" in line)
                or ("===" in line and "short test summary" in line)
            ):
                capture_buffer.append(line)
            elif capture_buffer:
                # Clear buffer if we're clearly not in an error section
                capture_buffer = []

        i += 1

    # Add any remaining buffered lines
    if capture_buffer:
        extracted.extend(capture_buffer)

    result = "\n".join(extracted)

    # If no error sections found, return empty (tests passed)
    # Check for pytest format (=== with FAILURES/ERRORS)
    if ("FAILURES" not in result or "===" not in result) and (
        "ERRORS" not in result or "===" not in result
    ):
        return ""

    # Add header with test command info
    # CUSTOMIZE: Update command string to match your task runner
    header = "Test Output (Error Sections Only)\n"
    header += "=" * 70 + "\n"
    header += "Command: task test:integration\n"  # ← CUSTOMIZE THIS
    header += "=" * 70 + "\n\n"

    return header + result


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
    except subprocess.TimeoutExpired:
        print(f"⚠️  Clipboard operation timed out", file=sys.stderr)
        return False
    except FileNotFoundError as e:
        print(f"⚠️  Clipboard command not found: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"⚠️  Clipboard operation failed: {e}", file=sys.stderr)
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
    # CUSTOMIZE: Update these patterns to match your API schema locations
    # Integration tests will run automatically when files matching these patterns change
    api_schema_patterns = [
        "src/schemas/",
        "src/api/v1/",
    ]  # ← CUSTOMIZE THIS LIST

    api_files = []
    for file in changed_files:
        if any(file.startswith(pattern) for pattern in api_schema_patterns):
            api_files.append(file)
        # PROJECT-SPECIFIC: Remove this block when copying to template
        # This allows verification tests to trigger integration test runs
        elif file == VERIFICATION_TEST_FILE:
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

    # Run pytest and capture output so it goes through OutputCapture
    try:
        result = subprocess.run(  # nosec B603 - developer tooling invocation
            pytest_cmd,
            cwd=project_root,
            stdin=subprocess.DEVNULL,  # Prevent waiting for input
            env=env,
            timeout=600,  # 10 minute timeout for integration tests
            capture_output=True,  # Capture output so we can print it through OutputCapture
            text=True,
            encoding="utf-8",
        )
        # Print captured output (stdout and stderr) so it goes through OutputCapture
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("\n⚠️  Integration tests timed out after 10 minutes")
        print("   This may indicate hanging tests or services not running")
        return False


def main():
    """Main integration test runner."""
    parser = argparse.ArgumentParser(
        description="Run integration tests (auto-runs when API schemas change, or use --force)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run all integration tests regardless of API schema changes",
    )
    args = parser.parse_args()

    # Capture all output to buffer and print to console
    with OutputCapture() as captured_output:
        print("=" * 70)
        print("🔗 Integration Test Runner")
        print("=" * 70)

        # If --force is provided, skip API schema check and run all tests
        if args.force:
            print("🚀 Force mode: Running all integration tests\n")
            all_passed = run_integration_tests()
        else:
            print("Detecting API schema changes since last commit...\n")

            # Get changed files
            changed_files = get_changed_files()

            if not changed_files:
                print("✅ No changed files detected since last commit.")
                print("   Use 'task test:integration --force' to run all integration tests")
                return 0

            # Filter to API schema files only
            api_files = filter_api_schema_files(changed_files)

            if not api_files:
                print("✅ No API schema files changed - skipping integration tests")
                print("   Integration tests run automatically when API schemas change")
                print(
                    "   Use 'task test:integration --force' to run all integration tests"
                )
                return 0

            # PROJECT-SPECIFIC: Remove this block when copying to template
            # This provides special messaging for verification test runs
            has_verification_test = any(VERIFICATION_TEST_FILE in f for f in api_files)

            print(f"Found {len(api_files)} changed file(s):")
            for f in api_files[:10]:  # Show first 10
                print(f"  - {f}")
            if len(api_files) > 10:
                print(f"  ... and {len(api_files) - 10} more")

            # PROJECT-SPECIFIC: Remove this conditional when copying to template
            if has_verification_test:
                print("\n🧪 VERIFICATION TEST DETECTED - Running Integration Tests")
                print("Running integration tests for output capture verification.")
            else:
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

        # Extract and copy only error sections to clipboard
        try:
            captured_output_value = captured_output.get_value()
            error_sections = extract_error_sections(captured_output_value)

            # Copy error sections if tests failed, otherwise copy nothing
            if error_sections:
                if copy_to_clipboard(error_sections):
                    print(
                        "\n📋 Test error sections copied to clipboard! You can paste them now."
                    )
                    print("   (Only FAILURES/ERRORS and summary sections included)")
                else:
                    print(
                        "\n⚠️  Failed to copy results to clipboard (but output is shown above)."
                    )
            elif not all_passed:
                # Tests failed but no error sections found - copy full output as fallback
                if copy_to_clipboard(captured_output_value):
                    print(
                        "\n📋 Test results copied to clipboard! You can paste them now."
                    )
                    print("   (Full output - error sections not detected)")
                else:
                    print(
                        "\n⚠️  Failed to copy results to clipboard (but output is shown above)."
                    )
            else:
                # All tests passed - no need to copy anything
                print("\n✅ All tests passed - nothing copied to clipboard")
        except Exception as e:
            print(f"\n⚠️  Error copying to clipboard: {e} (but output is shown above).")

        # Flush output before returning
        sys.stdout.flush()
        sys.stderr.flush()

        return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
