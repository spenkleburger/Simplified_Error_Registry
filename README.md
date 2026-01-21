# Project Setup Template

This folder contains a standardized project setup template and guidelines for starting new Python projects. This is **not a coding project itself**, but rather a collection of best practices, configuration templates, and setup procedures that should be applied to every new project.

## Purpose

This template provides:
- Standardized project structure and file organization
- Pre-configured development tools (formatting, linting, type checking)
- Best practices for logging, debugging, and error handling
- Configuration templates for common tools
- Guidelines for documentation, version control, and deployment
- Standard libraries and dependencies baseline
- **CI/CD pipeline template** (GitHub Actions) for automated quality checks

## Quick Start

When starting a new project:

1. Review this README and the template files in this folder and the \docs\ folder
2. Copy and adapt the template files to your new project
3. Follow the setup steps in Project_Setup_Instructions.md
4. Customize configurations based on project needs
5. Set up CI/CD pipeline - see `.github/workflows/README.md`
6. Update this template as you discover new best practices

## Important Note on pyproject.toml

**This template uses a minimal `pyproject.toml` ONLY for taskipy task automation.** It does NOT use pyproject.toml for dependency management (that's what the PYPROJECT folder is for). Dependencies are managed via `requirements.txt` and `pip freeze`, as per traditional Python workflow.

If you prefer not to use taskipy, you can delete `pyproject.toml` and use the scripts directly (e.g., `python scripts/pre_commit_checks.py`).

## Included Tooling & Tests

- **Task Automation (taskipy)** → Cross-platform task runner replacing `.bat` files:
  - `task push` → Interactive git workflow: stages, commits (with prompt), pushes
  - `task checks` → Runs comprehensive pre-commit checks (Black, Ruff, Bandit, pip-audit when needed, mypy, pytest; scope selectable per prompt)
  - `task freeze` → Freezes dependencies and audits with `pip-audit`
  - `task format` → Quick format only (Black + Ruff auto-fix)
  - `task lint` → Lint code only (no fixes)
  - `task test` → Run tests
  - `task clean` → Clean temporary files
  - See `docs/TASK_AUTOMATION.md` for complete documentation
- **`start.bat`** → Activates virtual environment (Windows convenience script)
- **`config/`** → Configuration templates:
  - `config/logging.py` → Standardized logging with automatic log rotation (10MB max, 5 backups)
  - `config/settings.py` → Type-safe configuration management from environment variables
  - `config/exceptions.py` → Custom exception hierarchy for consistent error handling
- **`docs/ERROR_HANDLING.md`** → Comprehensive error handling patterns guide with examples
- **`tests/`** → Bundled pytest suite covering `config/logging.py`, `config/settings.py`, and illustrative examples (`tests/test_config_logging.py`, `tests/test_config_settings.py`, `tests/test_example.py`). Use `task checks` or `pytest` to run locally; the CI workflow runs the same tests on every push/PR.