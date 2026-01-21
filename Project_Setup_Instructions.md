# Project Setup Instructions

> **Complete guide for setting up a new Python project using traditional tooling (requirements.txt, setup.cfg, ruff.toml)**

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Setup Checklist (For Experienced Users)](#quick-setup-checklist-for-experienced-users)
- [Initial Project Setup Checklist](#initial-project-setup-checklist)
  - [1. Virtual Environment](#1-virtual-environment)
  - [2. Core Dependencies](#2-core-dependencies)
  - [3. Configuration Files](#3-configuration-files)
  - [4. Project Documentation](#4-project-documentation)
  - [5. Version Control](#5-version-control)
  - [6. Logging Setup](#6-logging-setup)
  - [7. Environment Variables](#7-environment-variables)
  - [8. Port Management](#8-port-management)
  - [9. Standard Project Structure](#9-standard-project-structure)
  - [10. CI/CD Pipeline Setup (Optional)](#10-cicd-pipeline-setup-optional)
- [Development Workflow](#development-workflow)
- [Best Practices Summary](#best-practices-summary)
- [Docker Setup (Optional)](#docker-setup-optional)
- [Additional Tools & Resources](#additional-tools--resources)

---

## Prerequisites

### Cursor Rules Consolidation Project

**Purpose:** Central repository for consolidated Cursor rules and commands that apply globally across all projects via symlinks.

#### Set up 
**New project** (future projects)

Edit the `-ProjectPath` value for the project you want to wire up.

```powershell
# Example: set up a new project at C:\Projects\MyNewProject
$ProjectPath = "C:\Projects\MyNewProject"

cd "C:\Projects\Cursor_Rules"

# Create links + bootstrap rule (junctions by default; no admin required)
.\scripts\create_symlinks.ps1 -ProjectPath $ProjectPath

# Verify
.\scripts\verify_symlinks.ps1 -ProjectPath $ProjectPath
```

---

## Quick Setup Checklist (For Experienced Users)

If you're familiar with Python project setup, here's a quick checklist:

1. ✅ **Ensure prerequisites are met**: CUrsor Rules symlinks created
2. ✅ **Copy TRADITIONAL folder** to your new project directory
3. ✅ **Create virtual environment**: `python -m venv .venv` (or `.venv`)
4. ✅ **Activate venv**: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
5. ✅ **Install dev tools**: `pip install -r requirements-dev.txt`
6. ✅ **Edit requirements.txt**: Uncomment packages you need, then `pip install -r requirements.txt`
7. ✅ **Run GER installer**: `python ../Global_Error_Registry/scripts/install_global_error_registry.py . --docker`
8. ✅ **Create .env file**: Copy template from section 7, customize values (GER installer may have already configured some paths)
9. ✅ **Initialize git**: `git init`, `git add .`, `git commit -m "Initial project setup"`
10. ✅ **Start coding**: Folder structure is ready, config files are in place

**For detailed instructions, see sections below.**

---

## Initial Project Setup Checklist

### 1. Virtual Environment

Always start with a clean virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Core Dependencies

#### Installation Workflow

**Step 1: Install Development Tools (Always Required)**

Install essential development and quality assurance tools from `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

This installs:
- **Code Formatting**: `black`
- **Linting & Import Sorting**: `ruff` (replaces flake8 + isort)
- **Type Checking**: `mypy`
- **Testing**: `pytest`, `pytest-cov`, `pytest-mock`
- **Environment Management**: `python-dotenv`
- **Dependency Management**: `pip-tools`
- **Task Automation**: `taskipy` (replaces .bat files)

**Note:** This project uses a pre-commit formatting script (`scripts/pre_commit_format.py`) instead of pre-commit hooks, so the `pre-commit` package is not included.

**Step 2: Install Project Dependencies (As Needed)**

Edit `requirements.txt` to uncomment the packages your project needs, then install:

```bash
pip install -r requirements.txt
```

**Step 3: Update Requirements Files**

After installing new packages, update the requirements file:

```bash
# Option 1: Freeze and audit (recommended - includes security check)
# Use task automation (recommended)
task freeze

# Or run Python script directly
python scripts/freeze_and_audit.py
# This runs: pip freeze + pip-audit (checks for vulnerabilities)

# Option 2: Simple freeze (captures exact versions)
pip freeze > requirements.txt

# Option 3: Use pip-tools with requirements.in (alternative approach)
# If you prefer managing direct dependencies separately:
# 1. Edit requirements.in to list only your direct dependencies
# 2. Run: pip-compile requirements.in
# 3. This generates requirements.txt with all dependencies pinned
# See requirements.in template file for more details
```

#### Requirements Files Structure

**`requirements-dev.txt`** - Development tools (always install this first)
- Contains all development and quality assurance tools
- Use version constraints (>=) for flexibility
- Install with: `pip install -r requirements-dev.txt`

**`requirements.txt`** - Project dependencies (customize as needed)
- Contains common libraries organized by category
- All entries are commented out by default
- Uncomment packages you need for your project
- Use version constraints (>=) in template, exact pins after `pip freeze`

#### Common Libraries Available in `requirements.txt`

The template includes commonly used libraries (all commented out - uncomment as needed):

- **Environment & Configuration**: `python-dotenv`
- **Logging**: `logging`
- **HTTP Requests**: `requests`, `httpx`
- **Data Handling**: `pandas`, `numpy`
- **Data Validation**: `pydantic`, `PyYAML`
- **Database**: `psycopg2-binary`, `sqlalchemy`
- **Date/Time**: `python-dateutil`, `pytz`
- **Utilities**: `tqdm`, `click`, `python-slugify`
- **File Processing**: `openpyxl`, `Pillow`
- **Web Frameworks**: `fastapi`, `flask`, `django`
- **Type Stubs**: `types-requests`, `types-python-dateutil`, etc.

See `requirements.txt` and `requirements-dev.txt` in this `TRADITIONAL/` folder for the complete baseline templates.

### 3. Configuration Files

#### `setup.cfg`

Create a `setup.cfg` file in the project root for tool configurations.

**See the `setup.cfg` template file in this `TRADITIONAL/` folder for the complete baseline configuration.**

**Note:** 
- Ruff configuration goes in `ruff.toml` (see below)
- Black formatter prefers `pyproject.toml` but can use command-line options or defaults
- The `setup.cfg` file contains configurations for `mypy`, `pytest`, and `coverage`
- Coverage is provided by `pytest-cov` (included in `requirements-dev.txt`)

#### `ruff.toml`

Create a `ruff.toml` file in the project root for Ruff linting and import sorting configuration.

**See the `ruff.toml` template file in this `TRADITIONAL/` folder for the complete baseline configuration.**

**Why ruff.toml?** Ruff doesn't natively support `setup.cfg`. Use `ruff.toml` for Ruff configuration, and `setup.cfg` for mypy configuration.

#### `.editorconfig`

Create `.editorconfig` in the root.

**See the `.editorconfig` template file in this `TRADITIONAL/` folder for the complete baseline configuration.**

#### `.gitattributes`

Create `.gitattributes` in the root.

**See the `.gitattributes` template file in this `TRADITIONAL/` folder for the complete baseline configuration.**

#### `.gitignore`

Create a `.gitignore` file in the project root to exclude files from version control.

**See the `.gitignore` template file in this `TRADITIONAL/` folder for the complete baseline configuration.**

#### Pre-commit Formatting Script

This project uses a Python script for pre-commit formatting instead of pre-commit hooks.

**See the `scripts/pre_commit_format.py` file in this `TRADITIONAL/` folder for the complete implementation.**

**Usage:**
```bash
# Before committing, run the formatting script
python scripts/pre_commit_format.py

# Then stage and commit
git add .
git commit -m "Your commit message"
```

**What it does:**
- Formats code with Black
- Lints and auto-fixes with Ruff (replaces flake8 + isort)

**Note:** This approach is simpler than pre-commit hooks and doesn't require the `pre-commit` package. See `Everyday_coding_instructions.md` for the complete workflow.

#### Use `.cursor/rules.mdc` (Optional)

Create Cursor AI rules file (max 200 lines, split if needed):
- `rules.mdc` - Core project rules
- `rules-testing.mdc` - Testing-specific rules
- `rules-deployment.mdc` - Docker/deployment rules
- `rules-code-style.mdc` - Code formatting/style rules
- etc.

Cursor includes a toggle for when to use additional rules files, but we can also add Project-Specific Rules to your main .cursor/rules.mdc:
- If working on API endpoints, refer to `.cursor/rules.fastapi.mdc`
- If refactoring code, refer to `.cursor/rules.refactoring.mdc`
- If debugging issues, refer to `.cursor/rules.debugging.mdc`
These examples show how to create specialized rules for different contexts while keeping your main rules file generic.

### 4. Project Documentation

#### `README.md`

Create a comprehensive README.md that includes:
- Project overview and purpose
- Installation instructions
- Environment variables setup
- How to run the project
- Folder structure
- Key configuration files
- Architecture overview
- FAQ / Common issues

See the root `EXAMPLES/README.md` for a reference example (from another project).

Use \docs\ folder for larger projects.

#### `{PROJECT_NAME}_PLAN.md`
Create a comprehensive, detailed working plan and project structure based on the template.
#### `{PROJECT_NAME}_IMPLEMENTATION_PLAN.md`
Create a comprehensive, detailed implementation and development plan based on the template.
#### `PROJECT_STATUS.md`
Create a project status file based on the template. This will be used by the Idea_Engine to track the project.

### 5. Version Control

#### Git Repository Setup

```bash
# Initialize repository
git init

# Create initial commit
git add .
git commit -m "Initial project setup"

# Connect to remote repo
git remote add origin <repo-url>
# Confirm remote repo
git remote -v
# Do first push
git push -u origin main
```

#### Branching Strategy

Use a simple two-layer branching model:

- **`main`** - Always relatively stable/working
- **Topic branches** - Short-lived branches for specific work

**Branch naming conventions:**
- `feature/...` - New features (e.g., `feature/telegram-notifications`)
- `refactor/...` - Structural or cleanup work (e.g., `refactor/extraction-pipeline`)
- `fix/...` - Bug fixes (e.g., `fix/pdf-encoding-bug`)

**When to work directly on `main`:**
- Small/medium, low-risk changes
- Tweaking logic in a limited way
- Updating docs, comments, small utilities

**When to create a branch:**
- AI rewriting or heavily refactoring critical scripts
- Changing multiple related scripts at once
- Unsure if changes will be kept
- Want to be able to throw the experiment away cleanly

**Branch commands:**
```bash
# Create and switch to new branch
git switch -c feature/new-feature

# Work, edit, test
git add .
git commit -m "WIP: new feature"

# When happy, merge to main
git switch main
git merge feature/new-feature
git push

# If you decide it's bad, delete the branch
git branch -D feature/new-feature
```

### 6. Logging Setup

#### Standard Logging Configuration

Create `config/logging.py`:

**See the `config/logging.py` template file in this `TRADITIONAL/` folder for the complete baseline implementation.**

**Features:**
- Automatic log rotation (10MB max file size, keeps 5 backup files)
- Configurable via environment variables (LOG_FILE_MAX_SIZE, LOG_BACKUP_COUNT)
- Console and file logging
- UTF-8 encoding
- Date-based log file naming

**Usage in your scripts:**
```python
from config.logging import setup_logging
logger = setup_logging()  # Uses .env variables automatically
logger.info("Application started")
```

**Environment Variables:**
```bash
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE=True                  # Enable/disable file logging
LOG_TO_CONSOLE=True               # Enable/disable console logging
LOG_DIR=./logs                    # Log file directory
LOG_FILE_MAX_SIZE=10MB            # Max log file size before rotation (e.g., "10MB", "500KB")
LOG_BACKUP_COUNT=5                # Number of backup log files to keep
```

#### Error Handling with Custom Exceptions

The template includes `config/exceptions.py` with a complete custom exception hierarchy for consistent error handling.

**Available Custom Exceptions:**
- `ProjectBaseException` - Base exception for all project errors
- `ConfigurationError` - Invalid or missing configuration
- `ValidationError` - Data validation failures
- `DataProcessingError` - Data processing/transformation failures
- `APIError` - API operation failures
- `DatabaseError` - Database operation failures
- `FileOperationError` - File I/O failures

**Quick Example:**
```python
from config.exceptions import ConfigurationError, ValidationError

# Validate configuration
if not api_key:
    raise ConfigurationError("API key is required", {"config_file": "config.json"})

# Validate input data
if not email_valid(email):
    raise ValidationError("Invalid email format", {"email": email})
```

**See `docs/ERROR_HANDLING.md` for comprehensive error handling patterns, real-world examples, and best practices.**

**Quick Control via .env:**
- **Development (verbose):** Set `LOG_LEVEL=DEBUG` and `DEBUG=True` in `.env`
- **Production (minimal):** Set `LOG_LEVEL=WARNING` and `DEBUG=False` in `.env`
- **Disable file logging:** Set `LOG_TO_FILE=False` in `.env`
- **Disable console logging:** Set `LOG_TO_CONSOLE=False` in `.env`

### 7. Environment Variables

#### `.env` File Setup

**Step 1: Copy the template**

Copy `.env.example` to `.env` in your project root:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Step 2: Customize values**

Edit `.env` and replace placeholder values with your actual configuration:

- Replace `your-api-key-here` with your actual API keys
- Update database connection strings
- Adjust ports if needed
- Modify log settings as desired

**AI Infrastructure & GER Configuration:**

If you ran the GER installer (see section 0), the following variables should already be configured in your `.env` file:

```bash
# AI Infrastructure & GER Config
OLLAMA_HOST=http://host.docker.internal:11434
REGISTRY_PATH=/app/ger_knowledge
```

If these are not present, add them manually. These settings enable:
- **OLLAMA_HOST**: Connection to Ollama running on the host machine (for Docker containers)
- **REGISTRY_PATH**: Path to the mounted GER knowledge volume within the container

**Important:** The `.env` file is gitignored and should never be committed to version control. Only `.env.example` (the template) is tracked in git.

#### Loading Environment Variables

The template's `config/settings.py` automatically loads environment variables from `.env` and provides type-safe access.

**✅ Recommended: Use config/settings.py (already configured in template)**
```python
from config.settings import API_PORT, DATABASE_URL, DEBUG, API_KEY

# Variables are already converted to correct types (int, bool, etc.)
port = API_PORT  # Already an int, no conversion needed
is_debug = DEBUG  # Already a bool
```

**❌ Avoid: Direct access via os.getenv**
```python
# Don't do this - use config/settings.py instead
import os
port = os.getenv("API_PORT")  # Returns string, needs manual conversion
```

**Benefits of using config/settings.py:**
- Automatic type conversion (strings → ints, bools)
- Centralized configuration management
- Consistent access patterns across your project
- Default values already configured
- Validation available via `validate_settings()` function

**Note:** The `config/settings.py` template already handles loading `.env` files via `python-dotenv`. You don't need to call `load_dotenv()` manually.

### 8. Port Management

#### Port Registry

Maintain a `PORTS.md` or `docs/PORTS.md` file to track all ports used by your project.

**See the `docs/PORTS.md` template file in this `TRADITIONAL/` folder for a complete example** that includes:
- Development and production port tables
- Port conflict troubleshooting
- Port configuration in code examples
- Guidelines for adding new services

#### Port Configuration in Code

Ports are automatically configured via `config/settings.py` from your `.env` file:

```python
# ✅ Recommended: Use config/settings.py (already configured in template)
from config.settings import API_PORT, WEB_PORT, DATABASE_PORT

# Ports are already converted to integers, ready to use
server_port = API_PORT
```

**Note:** The template's `config/settings.py` already handles port configuration from environment variables. You don't need to manually parse them - just import and use.

### 9. Standard Project Structure

**Note:** If you're using the TRADITIONAL folder as a template, the complete folder structure is already implemented. Simply copy the entire TRADITIONAL folder to your new project directory.

#### Recommended Folder Tree

```
project-name/
├── .cursor/                    # Cursor AI rules (optional)
│   ├── rules.mdc
│   ├── rules-testing.mdc
│   ├── rules-deployment.mdc
│   └── rules-code-style.mdc
├── .github/                    # GitHub workflows (optional)
│   └── workflows/
│       └── ci.yml
├── config/                     # Configuration files
│   ├── logging.py
│   └── settings.py
├── docs/                       # Documentation
│   ├── PORTS.md
│   ├── ARCHITECTURE.md
│   └── API.md
├── logs/                       # Log files (gitignored)
│   └── .gitkeep
├── scripts/                    # Executable scripts
│   ├── run.py
│   └── setup.py
├── src/                        # Source code (or use project name)
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── tests/
├── tests/                      # Test files (alternative location)
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── venv/                       # Virtual environment (gitignored)
├── .env                        # Environment variables (gitignored, use template from section 7)
├── .editorconfig
├── .gitattributes
├── .gitignore
├── Dockerfile                  # Docker configuration (copy from Dockerfile.template)
├── docker-compose.yml          # Docker Compose (copy from docker-compose.yml.template)
├── README.md
├── requirements.txt
├── requirements-dev.txt        # Development-only dependencies
├── setup.cfg                   # mypy configuration
└── ruff.toml                   # Ruff linting configuration
```

#### Alternative Structure (Scripts-based)

For simpler projects with scripts:

```
project-name/
├── scripts/                    # All Python scripts
│   ├── main.py
│   ├── utils.py
│   └── config.py
├── config/                     # Configuration files
├── data/                       # Data files (gitignored)
├── logs/                       # Log files (gitignored)
├── tests/                      # Test files
├── .env                        # Environment variables (copy from .env.example)
├── README.md
├── requirements.txt
├── setup.cfg                   # mypy configuration
└── ruff.toml                   # Ruff linting configuration
```

### 10. Test Suite Overview

The template includes example tests to help you get started:

- **`tests/conftest.py`** – Shared test setup and helper functions that all your tests can use
- **`tests/test_config_logging.py`** – Tests that verify logging works correctly (file creation, log levels, etc.)
- **`tests/test_config_settings.py`** – Tests that verify configuration loading works properly
- **`tests/test_example.py`** – Simple example tests showing common testing patterns

**What are tests?** Tests are small programs that automatically check if your code works correctly. They help catch bugs before they cause problems.

**Why write tests?** 
- They give you confidence that your code works
- They help catch bugs when you make changes
- They serve as documentation showing how your code should be used
- They make it safer to refactor (improve) your code later

**Test Coverage Explained:**
- **Coverage** means "how much of your code is tested"
- 100% coverage means every line of code is tested
- You don't need 100% coverage - aim for testing the important parts
- Focus on testing:
  - Core business logic (the main things your code does)
  - Error handling (what happens when things go wrong)
  - Edge cases (unusual inputs or situations)

**Running tests:**
```bash
# Run all tests
pytest

# Run tests with coverage report (shows what's tested)
pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in your browser to see the report
```

Use these test files as templates when adding tests for your own code (API endpoints, data processing functions, etc.). Add shared test helpers to `conftest.py` so they're available to all your tests.

---

## Development Workflow

### Daily Coding Practices

#### 1. Pre-commit Checks

Before committing, run checks to ensure code quality:

```bash
# Comprehensive checks (recommended - does everything)
# Use task automation (recommended)
task checks

# Or run Python script directly
python scripts/pre_commit_checks.py

# Then stage and commit
git add .
git commit -m "Your commit message"
```

**What the comprehensive script does:**
- Formats code with Black
- Lints and auto-fixes with Ruff (replaces flake8 + isort)
- Security scanning with Bandit (code)
- Dependency vulnerability check with pip-audit (if requirements changed)
- Type checking with mypy
- Runs tests with pytest

**Quick format only (alternative):**
```bash
# If you just want formatting/linting
task format    # Or: python scripts/pre_commit_format.py
```

**Note:** See `Everyday_coding_instructions.md` for the complete daily workflow. The comprehensive checks script prompts you to choose scope (changed files vs all files) for mypy and pytest.

#### 2. Running Tests Locally

```bash
# Full suite (recommended)
pytest

# Map changes to tests (faster, prompted inside checks script)
python scripts/pre_commit_checks.py

# Specific file or test
pytest tests/test_config_settings.py -k validate_settings
```

- Prefer `checks.bat` (or the Python script) so formatting, security scans, mypy, and pytest run together.
- Pytest exit code 5 (“no tests found”) is treated as a warning in the script—normal if you delete tests.

#### 3. Documentation Updates

- Update README.md as the project evolves
- Document new features, configuration changes, and breaking changes
- Keep architecture diagrams and flow charts current
- Update port registry when adding new services

**Note:** AI (via `.cursor/rules.mdc`) will remind you to update documentation when making significant changes.

#### 4. Backup Strategy

**Code Backups:**
- Use Git for version control (commit frequently)
- Push to remote repository regularly
- Use branches for experimental work

**Data Backups:**
- Document backup procedures in README
- Use automated backup scripts if needed
- Store backups in separate locations

**Configuration Backups:**
- Keep `.env` template in README.md updated
- Document all required environment variables
- Version control configuration templates

#### 5. Task Automation

This project uses **taskipy** for task automation (replaces `.bat` files):

- `task push` → Interactive git workflow: stages all changes, prompts for commit message, commits, and pushes
- `task checks` → Runs comprehensive pre-commit checks (Black, Ruff, Bandit, pip-audit when needed, mypy, pytest; prompts for "changed files" vs "all files" scope)
- `task freeze` → Runs `scripts/freeze_and_audit.py` to write a fresh `requirements.txt` (`pip freeze`) and immediately audit dependencies with `pip-audit`. Run after adding/updating packages
- `task format` → Quick format only (Black + Ruff auto-fix)
- `task lint` → Lint code only (no fixes)
- `task test` → Run tests
- `task clean` → Clean temporary files
- `task help` → List all available tasks

**See `docs/TASK_AUTOMATION.md` for complete documentation.**

---

## Best Practices Summary

### Code Quality
- ✅ Use Black for consistent code formatting
- ✅ Use Ruff for linting and import sorting (replaces flake8 + isort)
- ✅ Use mypy for type checking (gradually adopt)
- ✅ Write tests with pytest
- ✅ Use pre-commit formatting script (`scripts/pre_commit_format.py`) before commits

### Documentation
- ✅ Maintain comprehensive README.md
- ✅ Document architecture and design decisions
- ✅ Keep inline comments for complex logic
- ✅ Update documentation as code changes
- ✅ Document API endpoints and usage

### Version Control
- ✅ Commit frequently with clear messages
- ✅ Use meaningful branch names
- ✅ Keep main branch stable
- ✅ Use branches for risky changes
- ✅ Write clear commit messages

### Environment Management
- ✅ Use virtual environments
- ✅ Track dependencies in requirements.txt
- ✅ Use .env for secrets (never commit)
- ✅ Provide .env template in README.md
- ✅ Document all environment variables

### Logging & Debugging
- ✅ Use structured logging
- ✅ Set appropriate log levels
- ✅ Rotate log files
- ✅ Include context in log messages
- ✅ Use exception handling with logging

### Security
- ✅ Never commit secrets or API keys
- ✅ Use environment variables for sensitive data
- ✅ Keep dependencies updated
- ✅ Review security advisories
- ✅ Use strong passwords and keys

### Testing
- ✅ Write unit tests for core functionality
- ✅ Test error cases and edge cases
- ✅ Aim for reasonable test coverage
- ✅ Run tests before committing
- ✅ Use fixtures and mocks appropriately

---

## CI/CD Pipeline Setup (Optional)

### What is CI/CD?

**CI (Continuous Integration)** = Automated testing and quality checks that run when you push code to GitHub.

**CD (Continuous Deployment)** = Automatically deploying code to production (only needed if you publish/deploy your project).

For most projects, **CI is useful** even if you don't deploy. It provides:
- Automated quality checks on every push
- Testing in different environments
- Historical record of code quality
- Safety net if you forget to run checks locally

### Quick Setup

The TRADITIONAL template includes a ready-to-use CI pipeline in `.github/workflows/ci.yml`.

**To enable CI:**

1. **Push your project to GitHub** (if not already done):
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **The CI pipeline is already included** - it will automatically run on your first push!

3. **View results:**
   - Go to your GitHub repository
   - Click the "Actions" tab
   - See workflow runs and results

### What the CI Pipeline Does

The included `ci.yml` workflow creates three jobs that run on every push/PR:

1. **quality** – installs dev dependencies, runs Black (`--check`), Ruff, and mypy (gradual: `continue-on-error` so you can tighten later).
2. **security** – optional job that installs `pip-audit` + Bandit, scans dependencies (`pip-audit --desc`) and code (`bandit -r src/ config/ scripts/ --exclude tests/`), both currently marked `continue-on-error` so they warn instead of fail.
3. **test** – installs dependencies per Python version (3.10/3.11/3.12) and runs the bundled pytest suite with coverage (`pytest --cov=src --cov-report=xml --cov-report=term-missing`). This exercises `tests/test_config_logging.py`, `tests/test_config_settings.py`, and any additional tests you add.

### Customization

See `.github/workflows/README.md` for detailed customization options:

- Adjust Python versions
- Change trigger branches
- Make mypy strict (remove `continue-on-error`)
- Add security scanning
- Add dependency vulnerability checks
- Add deployment steps (when you start publishing)

### Local vs CI

**Local workflow (recommended sequence):**
```bash
task checks         # Runs formatting, linting, security scans, mypy, pytest
# (or) python scripts/pre_commit_checks.py
task freeze         # After dependency changes (pip freeze + pip-audit)
```

**CI workflow mirrors:**
- `quality` job ↔ Black, Ruff, mypy portions of `pre_commit_checks.py`
- `security` job ↔ pip-audit + Bandit (same tools as `freeze.bat`/`checks.bat`)
- `test` job ↔ pytest run (same suite you run locally)
- Clean environments + multiple Python versions provide extra assurance

### When to Use CI

**Use CI if:**
- ✅ You want automated quality checks
- ✅ You want to test in different environments
- ✅ You work with others (team projects)
- ✅ You want a safety net for forgotten checks
- ✅ You want a historical record of code quality

**CI is optional if:**
- You're very disciplined about running checks locally
- You're just learning/experimenting
- You don't use GitHub

**Note:** CI is free for public repos and has a free tier for private repos on GitHub.

### Troubleshooting

**CI fails on formatting:**
- Run `black .` locally, commit, and push

**CI fails on linting:**
- Run `ruff check --fix .` locally, commit, and push

**CI fails on tests:**
- Check Python version differences
- Ensure all dependencies are in `requirements-dev.txt`
- Test locally first

See `.github/workflows/README.md` for more troubleshooting tips.

---

## Docker Setup (Optional)

If you need to containerize your application, template files are provided:

1. **Copy `Dockerfile.template` to `Dockerfile`** and customize for your project
2. **Copy `docker-compose.yml.template` to `docker-compose.yml`** and customize as needed
3. **Copy `.dockerignore`** to exclude unnecessary files from Docker builds

**See the template files in this `TRADITIONAL/` folder for complete Docker configuration examples.**

**AI Infrastructure & GER Integration:**

The `docker-compose.yml.template` is pre-configured for the "Sidecar" AI Architecture:

- **Host Communication**: The `app` service includes `extra_hosts` configuration to enable communication with Ollama running on the host machine via `host.docker.internal`
- **GER Knowledge Volume**: The template mounts the external `ger_knowledge_volume` at `/app/ger_knowledge` in the container
- **Environment Variables**: Ensure your `.env` file includes `OLLAMA_HOST` and `REGISTRY_PATH` (these are automatically added by the GER installer)

**Note:** Docker is optional and only needed if you plan to deploy your application in containers. Most development work can be done without Docker.

---

## Additional Tools & Resources

### Recommended VS Code/Cursor Extensions

Install these extensions through the IDE's extension marketplace (not via pip):

- **Python** - Python language support
- **Pylance** - Type checking and IntelliSense
- **Black Formatter** - Integrates with Black (Black must be installed via pip first - see `requirements-dev.txt`)
- **Ruff** - Integrates with Ruff for linting and import sorting (Ruff must be installed via pip first - see `requirements-dev.txt`)
- **GitLens** - Enhanced Git integration
- **Error Lens** - Shows errors and warnings inline

**Note:** Black and Ruff must be installed via pip (included in `requirements-dev.txt`) before their extensions will work properly.

**See `Everyday_coding_instructions.md` for daily coding tasks and useful commands reference.**

---

## Template Files Location

All baseline template files are located in this `TRADITIONAL/` folder:

**Core Configuration:**
- `requirements-dev.txt` - Development tools baseline
- `requirements.txt` - Common libraries baseline (all commented - uncomment as needed)
- `requirements.in` - Template for pip-tools workflow (alternative to requirements.txt)
- `setup.cfg` - Tool configurations (mypy, pytest, coverage)
- `ruff.toml` - Ruff linting configuration
- `.gitignore` - Files to exclude from version control
- `.gitattributes` - Git file handling configuration
- `.editorconfig` - Editor formatting configuration
- `.dockerignore` - Files to exclude from Docker builds

**Environment & Setup:**
- `.env.example` - Environment variables template (copy to `.env` and customize)
- `LICENSE` - MIT License template (customize with your name/year)

**Docker (Optional):**
- `Dockerfile.template` - Docker container template (copy to `Dockerfile` and customize)
- `docker-compose.yml.template` - Docker Compose template (copy to `docker-compose.yml` and customize)

**Packaging (Optional):**
- `MANIFEST.in` - Package distribution configuration (only needed if distributing as package)

**Documentation:**
- `README.md` - Project overview and quick start
- `Project_Setup_Instructions.md` - This comprehensive setup guide
- `Everyday_coding_instructions.md` - Daily coding workflow and commands
- `docs/` - Additional documentation (error handling, ports, task automation)

**Reference examples** (from another project) are in the root `EXAMPLES/` folder for reference only.

**Important:** These are baseline templates. Adapt them to your specific project needs rather than using them as-is.

---

## Maintenance

This template should be updated as you:
- Discover new best practices
- Encounter common issues that should be documented
- Find better tools or configurations
- Learn from mistakes or successes

Keep this template current so it remains a valuable starting point for future projects.

---

## License

[Specify license if applicable]

---

## Contributing

This is a personal project template. Adapt it to your needs and update it as you learn and grow as a developer.

