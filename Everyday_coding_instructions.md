# Instructions While Coding

## Git pre-commit, add, commit and push (presumes git already set up - see Connect Local Repository to Remote)

### Quick Workflow (Recommended)
```bash
# Step 1: Run comprehensive pre-commit checks
task checks

# Step 2: Interactive git workflow (stages, commits, pushes)
task push
# This will:
# - Stage all changes (git add .)
# - Prompt for commit message
# - Commit with your message
# - Push to remote
```

### Manual Workflow (Alternative)
```bash
# Step 1: Run comprehensive pre-commit checks
task checks
# Or: python scripts/pre_commit_checks.py

# This runs: black, ruff, bandit, pip-audit (if needed), mypy, pytest
# You'll be prompted to choose scope (changed files vs all files)

# Alternative: Quick format only (if you just want formatting/linting)
task format
# Or: python scripts/pre_commit_format.py

# Step 2: Stage ALL files (including any newly formatted ones)
git add .

# Step 3: Commit and push
git commit -m "Commit message"
git push
```

## Task Automation Quick Reference

This project uses **taskipy** for task automation. All common commands are available via `task <command>`.

### Most Common Tasks

```bash
task push      # Interactive git workflow: add, commit (with prompt), push
task checks    # Run comprehensive pre-commit checks (format, lint, security, test)
task freeze    # Freeze dependencies and audit for vulnerabilities
task format    # Quick format only (Black + Ruff auto-fix)
task lint      # Lint code only (no fixes)
task test      # Run tests
task clean     # Clean temporary files (__pycache__, .pytest_cache, etc.)
task help      # List all available tasks
```

**See `docs/TASK_AUTOMATION.md` for complete documentation, setup instructions, and all available tasks.**

## Quick Daily Tasks

### Update Dependencies

After installing new packages:

```bash
# Option 1: Freeze and audit (recommended - includes security check)
task freeze
# Or: python scripts/freeze_and_audit.py
# This runs: pip freeze + pip-audit (checks for vulnerabilities)

# Option 2: Simple freeze (captures exact versions)
pip freeze > requirements.txt

# Option 3: Use pip-tools for better dependency management
pip install pip-tools

# Create requirements.in with your direct dependencies (e.g., requests>=2.31.0)
# Then compile to generate requirements.txt with all dependencies
pip-compile requirements.in  # Creates requirements.txt
```

**Note:** `requirements.in` is your source file listing only direct dependencies. `pip-compile` generates `requirements.txt` with all transitive dependencies. For more details, see the "Core Dependencies" section in `README.md`.

**Why use `task freeze`?** It combines dependency freezing with security auditing, so you know immediately if any of your dependencies have known vulnerabilities.

## Git Branching Strategy

### Branch Types

Use prefixes to keep them organized:

- `feature/...` - New features (e.g., `feature/telegram-notifications`)
- `refactor/...` - Structural or cleanup work (e.g., `refactor/extraction-pipeline`)
- `fix/...` - Bug fixes (e.g., `fix/pdf-encoding-bug`)

### When to Create a Branch

Create a branch if:

- You're letting AI rewrite or heavily refactor a critical script
- You're changing multiple related scripts at once
- You're unsure if you'll keep the changes
- You want to be able to throw the experiment away cleanly

### Branch Commands

```bash
# Create and switch to new branch
git switch -c feature/new-report-layout

# Work, edit, test
git add .
git commit -m "WIP: new report layout"
git push

# When happy, merge to main
git switch main
git merge feature/new-report-layout
git push

# If you decide it's bad, delete the branch
git branch -D feature/new-report-layout
```

## Useful Commands Reference

### Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
start.bat
```

### Pre-Commit Checks

```bash
# Run comprehensive pre-commit checks (recommended)
task checks

# Or run Python script directly
python scripts/pre_commit_checks.py
```

### Code Quality

```bash
# Format code
black .

# Lint and check imports (ruff replaces flake8 + isort)
ruff check .          # Linting
ruff check --fix .    # Linting with auto-fix
ruff format .         # Formatting (alternative to black, but black recommended)

# Type checking
mypy .

# Run tests
pytest                     # Full suite (mirrors CI test job)
```

**Note:** Prefer running `task checks` (or `scripts/pre_commit_checks.py`) so Black, Ruff, Bandit, pip-audit (when needed), mypy, and pytest all run together (with a scope prompt for changed files vs all files). Use the individual commands above only when you need to re-run a single tool.

### CI/CD

**Important:** Always run checks locally before pushing! CI is a safety net, not a replacement.

**Before pushing (run locally):**
```bash
# Comprehensive checks (recommended - does everything)
task checks
# Or: python scripts/pre_commit_checks.py
# Includes: black, ruff, bandit, pip-audit (if needed), mypy, pytest

# Or run individual checks:
task format                          # Formatting and linting only
task test                            # Tests only
task freeze                          # Dependency security (includes pip-audit)
bandit -r src/ config/ scripts/      # Code security
```

**After pushing:**
```bash
# CI pipeline (.github/workflows/ci.yml) runs:
# - quality job: Black, Ruff, mypy
# - security job: pip-audit + Bandit (warnings by default)
# - test job: pytest with coverage on Python 3.10/3.11/3.12

# View CI results:
# 1. Go to GitHub repository
# 2. Click "Actions" tab
# 3. See workflow runs and results
```

**Why run locally first:**
- ✅ Faster feedback (seconds vs minutes)
- ✅ Avoid broken commits
- ✅ Fix issues immediately
- ✅ CI is a backup safety net

**Note:** CI pipeline is configured in `.github/workflows/ci.yml`. See `.github/workflows/README.md` for customization options.

### Docker

**Note:** Docker templates are provided in `Dockerfile.template` and `docker-compose.yml.template`. Copy and customize these files for your project.

**Basic Docker commands:**
```bash
# Build image (after copying Dockerfile.template to Dockerfile)
docker build -t project-name .

# Run container
docker run -d --name project-name project-name

# View logs
docker logs project-name

# Stop container
docker stop project-name

# Use docker-compose (after copying docker-compose.yml.template)
docker-compose up -d
docker-compose down
```

**See the Docker Setup section in `Project_Setup_Instructions.md` for more details.**

