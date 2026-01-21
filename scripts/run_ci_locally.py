# File: scripts/run_ci_locally.py
# Description: Run CI checks locally (mirrors .github/workflows/ci.yml)
# Usage: python scripts/run_ci_locally.py
# This runs the exact same checks that GitHub Actions runs, locally

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
            process = subprocess.Popen(  # nosec B603 - developer tooling invocation
                ["clip"],
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-8",
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


def run_command(
    cmd: list[str], description: str, check: bool = True, timeout: int | None = None
) -> bool:
    """Run a command and report results."""
    print(f"\n{'=' * 70}")
    print(f"🔍 {description}")
    print("=" * 70)
    print(f"Command: {' '.join(cmd)}")
    if timeout:
        print(f"Timeout: {timeout} seconds")
    print()

    try:
        # Capture subprocess output and print it line-by-line for real-time viewing
        # This ensures all output is captured by OutputCapture while still showing progress
        process = subprocess.Popen(  # nosec B603 - developer tooling invocation
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        # Print output line by line for real-time viewing
        if process.stdout:
            for line in process.stdout:
                print(line, end="")
                sys.stdout.flush()
        returncode = process.wait(timeout=timeout)
        if returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code {returncode})")
            return False
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        print(f"⏱️  {description} - TIMEOUT (exceeded {timeout} seconds)")
        print("   This may indicate a hanging test or slow operation.")
        return False
    except subprocess.CalledProcessError:
        print(f"❌ {description} - FAILED")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  {description} - INTERRUPTED by user")
        print("   This is normal if you canceled the operation.")
        return False
    except Exception as e:
        print(f"❌ ERROR running {description}: {e}")
        return False


def main():
    """Run all CI checks locally."""
    # Capture all output
    with OutputCapture() as capture:
        print("=" * 70)
        print("🚀 Running CI Checks Locally")
        print("=" * 70)
        print("This mirrors the exact checks run in GitHub Actions CI")
        print()

        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"Python version: {python_version}")

        all_passed = True

        # ========================================================================
        # Code Quality Checks (mirrors quality job in CI)
        # ========================================================================
        print("\n" + "=" * 70)
        print("📋 CODE QUALITY CHECKS")
        print("=" * 70)

        # Check code formatting with Black (matches CI line 58)
        all_passed &= run_command(
            [sys.executable, "-m", "black", "--check", "--diff", "."],
            "Checking code formatting with Black",
            check=False,
        )

        # Run Ruff linter (matches CI line 62)
        all_passed &= run_command(
            [sys.executable, "-m", "ruff", "check", "."],
            "Running Ruff linter",
            check=False,
        )

        # Run type checking with mypy (matches CI line 66)
        # Note: CI uses continue-on-error: true, so we don't fail the build
        all_passed &= run_command(
            [sys.executable, "-m", "mypy", "src/", "config/", "scripts/"],
            "Running type checking with mypy",
            check=False,  # CI uses continue-on-error: true
        )

        # ========================================================================
        # Security Checks (mirrors security job in CI)
        # ========================================================================
        print("\n" + "=" * 70)
        print("🔒 SECURITY CHECKS")
        print("=" * 70)

        # Check for vulnerable dependencies (pip-audit) (matches CI line 101)
        # Note: CI uses continue-on-error: true, so we don't fail here
        run_command(
            [sys.executable, "-m", "pip_audit", "--desc"],
            "Checking for vulnerable dependencies (pip-audit)",
            check=False,
        )

        # Scan code for security issues (bandit) (matches CI line 107)
        # Note: CI uses continue-on-error: true, so we don't fail here
        run_command(
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                "src/",
                "config/",
                "scripts/",
                "--exclude",
                "tests/",
            ],
            "Scanning code for security issues (bandit)",
            check=False,
        )

        # ========================================================================
        # Tests (mirrors test job in CI)
        # ========================================================================
        print("\n" + "=" * 70)
        print("🧪 TESTS")
        print("=" * 70)

        # Run tests with pytest (EXACT same command as GitHub CI line 144)
        # This MUST match .github/workflows/ci.yml exactly to catch the same errors
        # The timeout is only to prevent hanging - it doesn't affect test execution
        all_passed &= run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",  # Quiet mode: shows dots for passed tests, not full names
                "--tb=short",  # Short traceback format for failures
                "--cov=src",
                "--cov-report=xml",
                "--cov-report=term-missing",
            ],
            "Running tests with pytest",
            check=False,
            # Timeout prevents hanging but is generous (30 min) to allow full test suite
            # CI has a 6-hour job timeout, but 30min is reasonable for local runs
            timeout=1800,  # 30 minute total timeout
        )

        # ========================================================================
        # Summary
        # ========================================================================
        print("\n" + "=" * 70)
        if all_passed:
            print("✅ ALL CI CHECKS PASSED!")
            print("=" * 70)
            print("\nYour code should pass CI. Safe to push! 🚀")
            exit_code = 0
        else:
            print("❌ SOME CI CHECKS FAILED")
            print("=" * 70)
            print("\n⚠️  Fix the errors above before pushing.")
            print("   CI will fail with the same errors.")
            exit_code = 1

        # Copy all output to clipboard
        captured_output = capture.get_value()
        if copy_to_clipboard(captured_output):
            print("\n📋 Test results copied to clipboard! You can paste them now.")
        else:
            print(
                "\n⚠️  Failed to copy results to clipboard (but output is shown above)."
            )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
