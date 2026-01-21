# Task Automation Setup

This template provides task automation using **taskipy**, which replaces the old `.bat` files.

## Quick Answer

**Taskipy requires `pyproject.toml`** - there's no standalone `tasks.py` option. However, you can use a **minimal** `pyproject.toml` with just the taskipy section.

## Two Options

### Option 1: Full `pyproject.toml` (Recommended for new projects)

Use the full `pyproject.toml` file that includes:
- Project metadata
- Taskipy tasks
- Tool configurations (Black, etc.)

**Best for:** New projects using modern Python standards

### Option 2: Minimal `pyproject.toml` (For existing projects)

Use `pyproject.toml.minimal` - copy it to your project root as `pyproject.toml` and it contains **only** the taskipy tasks section.

**Best for:** Existing projects that don't want to migrate to full `pyproject.toml` yet

## Setup

1. **Install taskipy:**
   ```bash
   pip install taskipy
   ```

2. **Choose your config:**
   - **New project:** Use `pyproject.toml` (already in template)
   - **Existing project:** Copy `pyproject.toml.minimal` to your project root as `pyproject.toml`

3. **Use tasks:**
   ```bash
   task push      # Interactive git add, commit, push
   task checks    # Run pre-commit checks
   task freeze     # Freeze dependencies
   task format    # Format code
   task lint      # Lint code
   task test      # Run tests
   task clean     # Clean temporary files
   task help      # List all tasks
   ```

## What Replaced the .bat Files?

- ❌ `checks.bat` → ✅ `task checks`
- ❌ `freeze.bat` → ✅ `task freeze`
- ✅ `start.bat` → Keep (useful for activating venv)

## Why Taskipy Over Make?

- ✅ Works natively on Windows (no extra setup)
- ✅ Python-based (fits Python projects)
- ✅ Modern standard (`pyproject.toml`)
- ✅ Cross-platform commands

