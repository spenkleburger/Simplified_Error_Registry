# Dependency Management Guide

**Last Updated:** 2026-01-22

## Overview

This guide explains how to manage dependencies in the Simplified Error Registry project, including how to verify that `requirements.txt` contains all required dependencies.

---

## Quick Start

### Check if requirements.txt is Complete

```bash
# Use task automation (recommended)
task check:deps

# Or run script directly
python scripts/check_dependencies.py
```

This script:
- Scans all Python files in `src/` and `scripts/` directories
- Identifies third-party packages (excludes standard library)
- Compares against `requirements.txt`
- Reports missing dependencies
- Reports potentially unused packages

---

## Dependency Files

### requirements.txt

**Purpose:** Production dependencies (packages needed to run the application)

**Current Status:**
- Contains template with many commented packages
- Only active packages are actually used
- Should be updated after installing new packages

**How to Update:**
```bash
# Option 1: Freeze and audit (recommended)
task freeze
# Or: python scripts/freeze_and_audit.py

# Option 2: Simple freeze
pip freeze > requirements.txt
```

### requirements-dev.txt

**Purpose:** Development dependencies (testing, linting, formatting tools)

**Status:** ✅ Complete - contains all dev tools needed

**Installation:**
```bash
pip install -r requirements-dev.txt
```

### requirements.in

**Purpose:** Direct dependencies only (for pip-tools workflow)

**Status:** Template file - mostly commented out

**Usage (Alternative Workflow):**
```bash
# 1. Edit requirements.in to list direct dependencies
# 2. Generate requirements.txt with all transitive dependencies
pip-compile requirements.in

# 3. Update dependencies
pip-compile --upgrade requirements.in
```

---

## Verifying Dependencies

### Method 1: Automated Check (Recommended)

Use the dependency checker script:

```bash
task check:deps
```

**What it does:**
1. Scans all `.py` files in `src/` and `scripts/`
2. Extracts import statements
3. Identifies third-party packages (excludes stdlib)
4. Compares against `requirements.txt`
5. Reports:
   - Missing dependencies (used but not in requirements.txt)
   - Potentially unused packages (in requirements.txt but not used)

**Example Output:**
```
======================================================================
Dependency Checker
======================================================================

Scanning codebase for imports...

[*] Scanning src...
[*] Scanning scripts...

[OK] Found 2 third-party modules in use
[*] Found 8 packages in requirements.txt

======================================================================
RESULTS
======================================================================

[OK] All used dependencies are in requirements.txt

[?] POTENTIALLY UNUSED PACKAGES (5):
----------------------------------------------------------------------
  (These are in requirements.txt but not directly imported)
  (They might be used indirectly or are commented out)
  - fastapi
  - flask
  - python-dateutil
  - pytz
  - tqdm

[ACTION] Review if these are needed

======================================================================
SUMMARY
======================================================================
Third-party modules used: 2
Packages in requirements.txt: 8
Missing packages: 0
Potentially unused packages: 5

[OK] requirements.txt appears COMPLETE
```

**Understanding the Output:**
- **Missing Dependencies:** Packages used in code but not in `requirements.txt` - these need to be added
- **Potentially Unused Packages:** Packages in `requirements.txt` but not directly imported - these might be:
  - Template entries (commented or for future use)
  - Dependencies of other packages (transitive dependencies)
  - Used indirectly (e.g., via command-line tools)
  
**Note:** The script correctly excludes local project modules (`src`, `config`, `scripts`) from the check.

### Method 2: Manual Check

1. **List all imports in your code:**
   ```bash
   # Find all import statements
   grep -r "^import \|^from " src/ scripts/ | grep -v "from src\|from config\|from tests"
   ```

2. **Check each package:**
   - Identify third-party packages (not stdlib)
   - Check if they're in `requirements.txt`
   - Add missing ones

3. **Common stdlib modules (don't need to be in requirements.txt):**
   - `json`, `logging`, `os`, `sys`, `pathlib`, `datetime`, `typing`
   - `collections`, `dataclasses`, `argparse`, `re`, `subprocess`
   - See full list in `scripts/check_dependencies.py`

### Method 3: Test Installation

Create a clean virtual environment and test:

```bash
# Create new venv
python -m venv test_venv
source test_venv/bin/activate  # On Windows: test_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Try to run the application
python -m src.consolidation_app.main --help

# If ImportError occurs, the missing package is the issue
```

---

## Current Dependencies

### Actually Used (Based on Code Analysis)

**Production Dependencies (Verified with `task check:deps`):**
- `python-dotenv>=1.0.0` - Environment variable loading (used in `llm_client.py`, `config/`)
- `requests>=2.31.0` - HTTP client for LLM APIs (used in `llm_client.py`)

**Status:** ✅ Both are correctly listed in `requirements.txt`

**Development Dependencies:**
- See `requirements-dev.txt` for complete list

### Not Currently Used (In requirements.txt Template)

These packages are in `requirements.txt` but not currently used in the codebase:
- `fastapi`, `flask` - Web frameworks (not used yet)
- `tqdm` - Progress bars (not used yet)
- `pytz`, `python-dateutil` - Date/time utilities (not used yet)

**Note:** These are template entries. The dependency checker will flag them as "potentially unused packages". You can:
- Keep them if you plan to use them soon
- Comment them out to reduce false positives
- Remove them if you're certain they won't be needed

**Other commented packages in template:**
- `pandas`, `numpy` - Data analysis (commented out)
- `pydantic`, `PyYAML` - Data validation (commented out)
- And others...

These won't appear in the dependency check since they're commented out.

---

## Best Practices

### 1. Keep requirements.txt Up to Date

**After installing a new package:**
```bash
# Install the package
pip install package-name

# Immediately update requirements.txt
task freeze
```

### 2. Use Version Constraints

**In requirements.txt template:**
- Use `>=` for flexibility: `requests>=2.31.0`
- After `pip freeze`: Exact versions are pinned: `requests==2.31.0`

### 3. Separate Production and Development

- **requirements.txt**: Only production dependencies
- **requirements-dev.txt**: Development tools (pytest, black, ruff, etc.)

### 4. Regular Dependency Checks

**Before committing:**
```bash
# Check if requirements.txt is complete
task check:deps

# If missing dependencies found, add them and freeze
task freeze
```

### 5. Security Audits

**Regular security checks:**
```bash
# Freeze and audit (includes security check)
task freeze

# Or just audit existing requirements
pip-audit
```

---

## Troubleshooting

### Issue: ImportError after installing from requirements.txt

**Symptom:** `ImportError: No module named 'package'`

**Solution:**
1. Run `task check:deps` to identify missing dependencies
2. Add missing packages to `requirements.txt`
3. Run `task freeze` to update with exact versions

### Issue: Too Many Packages in requirements.txt

**Symptom:** `requirements.txt` has many unused packages

**Solution:**
1. Run `task check:deps` to see potentially unused packages
2. Review if packages are used indirectly (as dependencies of other packages)
3. Remove only packages you're certain are not needed
4. Test in clean environment to ensure nothing breaks

### Issue: Version Conflicts

**Symptom:** Package version conflicts when installing

**Solution:**
1. Use `pip-tools` with `requirements.in` for better dependency resolution
2. Or manually resolve conflicts by updating version constraints
3. Test in clean environment

---

## Workflow Summary

### Adding a New Dependency

1. **Install the package:**
   ```bash
   pip install package-name
   ```

2. **Use it in your code:**
   ```python
   import package_name
   ```

3. **Update requirements.txt:**
   ```bash
   task freeze
   ```

4. **Verify it's tracked:**
   ```bash
   task check:deps
   ```

### Removing a Dependency

1. **Remove from code:**
   - Remove all `import` statements
   - Remove all usage

2. **Verify it's not needed:**
   ```bash
   task check:deps
   ```

3. **Remove from requirements.txt:**
   - Delete the line
   - Or comment it out if it might be needed later

4. **Test:**
   ```bash
   # Create clean venv and test
   python -m venv test_venv
   source test_venv/bin/activate
   pip install -r requirements.txt
   # Test your application
   ```

---

## Related Documentation

- `scripts/check_dependencies.py` - Dependency checker script
- `scripts/freeze_and_audit.py` - Freeze and security audit script
- `Project_Setup_Instructions.md` - Project setup and dependency installation
- `docs/TESTING.md` - Testing guide (includes test dependencies)

---

## Tools Reference

### pip freeze
```bash
# Generate requirements.txt from current environment
pip freeze > requirements.txt
```

### pip-tools
```bash
# Install
pip install pip-tools

# Generate requirements.txt from requirements.in
pip-compile requirements.in

# Update all packages
pip-compile --upgrade requirements.in

# Update specific package
pip-compile --upgrade-package package-name requirements.in
```

### pip-audit
```bash
# Check for vulnerabilities
pip-audit

# With descriptions
pip-audit --desc
```

---

## Notes

- **Standard Library:** Modules from Python's standard library don't need to be in `requirements.txt`
- **Type Stubs:** `types-*` packages are for type checking only (mypy) and are in `requirements-dev.txt`
- **Indirect Dependencies:** Some packages might be dependencies of other packages (transitive dependencies). `pip freeze` captures these automatically.
- **Windows Compatibility:** All dependency management tools work on Windows, Linux, and macOS.
