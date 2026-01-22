# File: scripts/test_backend.py
# Description: Run backend tests with smart detection (only changed files)
# Usage: python scripts/test_backend.py
# This detects backend files changed since last commit and runs appropriate tests
# Output is automatically copied to clipboard for easy sharing
#
# ============================================================================
# PROJECT-SPECIFIC CUSTOMIZATION
# ============================================================================
# When copying this script to your project template, customize these sections:
#
# 1. BACKEND PATTERNS (line ~277):
#    - Update `backend_patterns` list to match your project's directory structure
#    - Default: ["src/", "config/", "tests/", "scripts/", "alembic/"]
#
# 2. TEST FILE MAPPING (line ~295):
#    - Update `map_files_to_tests()` function to match your test naming conventions
#    - Default: src/module.py -> tests/test_module.py
#
# 3. COMMAND HEADER (line ~193):
#    - Update command string to match your task runner command
#    - Default: "Command: task test:backend"
#
# 4. SOURCE FILE PATHS (line ~339):
#    - Update Python source file path patterns if different
#    - Default: ["src/", "config/", "scripts/", "tests/"]
#
# The core functionality (error extraction, clipboard copying) is generic and
# works for any project using pytest. Only the above sections need customization.
# ============================================================================

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

            # Stop capturing if we hit coverage section or final summary
            is_coverage_section = "tests coverage" in line and "===" in line
            is_final_summary = (
                ("failed" in line.lower() or "passed" in line.lower())
                and "in " in line.lower()
                and ("s ==" in line or "s ===" in line)
            )

            if is_coverage_section or is_final_summary:
                # Stop capturing - we've reached coverage or final summary
                in_failures = False
                in_errors = False
                in_summary = False
            # If we hit a different section marker, switch to that section
            elif is_failures_marker and not in_failures:
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
                # Regular content line - capture it (but skip coverage warnings)
                if (
                    "CoverageWarning" not in line
                    and "coverage" not in line.lower()
                    or "===" in line
                ):
                    extracted.append(line)
        else:
            # Not in any error section, but buffer lines that might be part of a section
            # (handles cases where section marker might be split across lines)
            # Check for pytest format: === with FAILURES/ERRORS/short test summary
            # Skip coverage sections and warnings
            is_coverage = "tests coverage" in line or "CoverageWarning" in line
            if not is_coverage and (
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
    header += "Command: task test:backend\n"  # ← CUSTOMIZE THIS
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


def filter_backend_files(changed_files):
    """Filter changed files to only backend Python files."""
    # CUSTOMIZE: Update these patterns to match your project's directory structure
    backend_patterns = [
        "src/",
        "config/",
        "tests/",
        "scripts/",
        "alembic/",
    ]  # ← CUSTOMIZE THIS LIST

    backend_files = []
    for file in changed_files:
        if file.endswith(".py") and any(
            file.startswith(pattern) for pattern in backend_patterns
        ):
            backend_files.append(file)

    return backend_files


def map_files_to_tests(changed_files):
    """Map changed source files to their corresponding test files."""
    # CUSTOMIZE: Update this function to match your test file naming conventions
    test_files = []

    for file in changed_files:
        # Convert src/module.py -> tests/test_module.py
        # Also src/package/module.py -> tests/test_package_module.py (flatten with _)
        if file.startswith("src/"):
            rest = file[4:]  # drop "src/"
            candidates = [
                f"tests/test_{rest}",  # tests/test_foo.py or tests/test_pkg/foo.py
                f"tests/test_{rest.replace('/', '_')}",  # tests/test_pkg_foo.py
            ]
            for test_file in candidates:
                if (project_root / test_file).exists() and test_file not in test_files:
                    test_files.append(test_file)
                    break
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
    # ← CUSTOMIZE: Add more mapping rules if your project uses different conventions

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
        # CUSTOMIZE: Update these path patterns if your project uses different directories
        python_source_files = [
            f
            for f in changed_files
            if f.endswith(".py")
            and any(
                f.startswith(p) for p in ["src/", "config/", "scripts/", "tests/"]
            )  # ← CUSTOMIZE THIS
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

    # Run pytest and capture output so it goes through OutputCapture
    result = subprocess.run(  # nosec B603 - developer tooling invocation
        pytest_cmd,
        cwd=project_root,
        stdin=subprocess.DEVNULL,  # Prevent waiting for input
        env=env,
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
