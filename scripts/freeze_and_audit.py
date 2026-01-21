# File: scripts/freeze_and_audit.py
# Description: Freeze dependencies and check for security vulnerabilities
# Combines pip freeze with pip-audit for a complete dependency snapshot

import subprocess
import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent


def run_command(cmd, description, capture_output=True):
    """Run a command and report results."""
    print(f"\n{'=' * 60}")
    print(f"{description}...")
    print("=" * 60)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=project_root,
            capture_output=capture_output,
            text=True,
        )

        if capture_output and result.stdout:
            print(result.stdout)
        if capture_output and result.stderr:
            print(result.stderr, file=sys.stderr)

        return result
    except Exception as e:
        print(f"❌ ERROR: Error running {description}: {e}")
        return None


def main():
    """Freeze dependencies and check for vulnerabilities."""
    print("=" * 60)
    print("Freeze Dependencies and Security Audit")
    print("=" * 60)
    print("This will freeze your current dependencies and check for vulnerabilities.\n")

    # Step 1: Freeze dependencies
    print("Step 1: Freezing dependencies...")
    result = run_command(
        f"{sys.executable} -m pip freeze",
        "Running pip freeze",
        capture_output=True,
    )

    if result is None or result.returncode != 0:
        print("❌ FAILED: Could not freeze dependencies")
        return 1

    # Write to requirements.txt
    requirements_file = project_root / "requirements.txt"
    requirements_file.write_text(result.stdout)
    print(f"\n✅ Dependencies frozen to {requirements_file}")
    print(f"   ({len(result.stdout.strip().split(chr(10)))} packages)")

    # Step 2: Check for vulnerabilities
    print("\nStep 2: Checking for vulnerable dependencies...")

    # Ensure pip-audit is installed
    _ = run_command(
        f"{sys.executable} -m pip install pip-audit --quiet",
        "Installing pip-audit (if needed)",
        capture_output=False,
    )

    # Run pip-audit
    audit_result = run_command(
        f"{sys.executable} -m pip_audit --desc",
        "Running pip-audit (dependency vulnerability scan)",
        capture_output=True,
    )

    if audit_result is None:
        print("⚠️  WARNING: Could not run pip-audit")
        print("   Dependencies frozen, but vulnerability check failed")
        return 1

    # Final summary
    print("\n" + "=" * 60)
    if audit_result.returncode == 0:
        print("✅ SUCCESS: Dependencies frozen and no known vulnerabilities found")
        print("=" * 60)
        return 0
    else:
        print("⚠️  WARNING: Dependencies frozen, but vulnerabilities found")
        print("=" * 60)
        print(
            "\nPlease review the vulnerabilities above and update packages as needed."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
