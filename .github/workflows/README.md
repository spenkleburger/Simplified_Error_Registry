# CI/CD Pipeline Documentation

This directory contains GitHub Actions workflows for automated code quality checks and testing.

## Available Workflows

### `ci.yml` - Standard CI Pipeline

A comprehensive CI pipeline that runs on every push and pull request to main/master/develop branches.

**What it does:**
- ✅ Checks code formatting with Black
- ✅ Runs linting with Ruff
- ✅ Performs type checking with mypy
- ✅ **Security scanning** with pip-audit (dependencies) and bandit (code)
- ✅ Runs tests with pytest and coverage
- ✅ Tests against multiple Python versions (3.10, 3.11, 3.12)

## Quick Start

### For New Projects

1. **Copy the workflow file:**
   ```bash
   # If you're using the TRADITIONAL template, the workflow is already included
   # For other projects, copy .github/workflows/ci.yml to your project
   ```

2. **Customize if needed:**
   - Adjust Python versions in the `strategy.matrix` section
   - Modify branches that trigger the workflow
   - Enable/disable specific checks
   - Add deployment steps if needed

3. **Push to GitHub:**
   ```bash
   git add .github/workflows/ci.yml
   git commit -m "Add CI pipeline"
   git push
   ```

4. **View results:**
   - Go to your GitHub repository
   - Click on the "Actions" tab
   - See workflow runs and results

## Workflow Details

### Code Quality Job

Runs on every push/PR:
- **Black**: Checks code formatting (doesn't modify, just reports)
- **Ruff**: Lints code and reports issues
- **mypy**: Type checking (set to `continue-on-error: true` for gradual typing)

### Security Job

Runs on every push/PR:
- **pip-audit**: Scans dependencies for known vulnerabilities
- **bandit**: Scans code for security issues (hardcoded secrets, SQL injection, etc.)
- Both set to `continue-on-error: true` by default (warnings, not blockers)

### Test Job

Runs on every push/PR:
- **pytest**: Runs all tests in the `tests/` directory
- **Coverage**: Generates coverage reports
- **Multiple Python versions**: Tests against 3.10, 3.11, and 3.12

## Customization

### Adjust Python Versions

Edit the `strategy.matrix` section:

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11"]  # Remove 3.12 if not needed
```

### Change Trigger Branches

Edit the `on` section:

```yaml
on:
  push:
    branches: [main, develop]  # Add/remove branches
  pull_request:
    branches: [main, develop]
```

### Make mypy Strict

Remove `continue-on-error: true` from the mypy step:

```yaml
- name: Run type checking with mypy
  run: |
    mypy src/ config/ scripts/
  # Remove: continue-on-error: true
```

### Skip Tests if None Exist

Add `continue-on-error: true` to the pytest step:

```yaml
- name: Run tests with pytest
  run: |
    pytest --cov=src --cov-report=xml --cov-report=term-missing
  continue-on-error: true  # Add this if tests are optional
```

### Make Security Checks Required

Remove `continue-on-error: true` from security steps to make them fail CI:

```yaml
- name: Check for vulnerable dependencies (pip-audit)
  run: |
    pip-audit --desc
  # Remove: continue-on-error: true

- name: Scan code for security issues (bandit)
  run: |
    bandit -r src/ config/ scripts/
  # Remove: continue-on-error: true
```

### Exclude Test Files from Bandit

Test files often have false positives. Exclude them:

```yaml
- name: Scan code for security issues (bandit)
  run: |
    bandit -r src/ config/ scripts/ --exclude tests/
```

## Troubleshooting

### Workflow Fails on Formatting

**Problem:** Black check fails because code isn't formatted.

**Solution:**
1. Run `black .` locally to format code
2. Commit and push the formatted code
3. Or change the workflow to auto-format (not recommended for CI)

### Workflow Fails on Linting

**Problem:** Ruff finds code style issues.

**Solution:**
1. Run `ruff check --fix .` locally to auto-fix issues
2. Commit and push the fixes
3. Or adjust `ruff.toml` to ignore specific rules

### Tests Fail

**Problem:** Tests are failing in CI but pass locally.

**Solution:**
1. Check Python version differences
2. Ensure all dependencies are in `requirements-dev.txt`
3. Check for environment-specific issues (paths, permissions, etc.)

### mypy Errors

**Problem:** mypy reports type errors.

**Solution:**
1. Fix type errors in your code
2. Or adjust `setup.cfg` mypy configuration
3. Or add `# type: ignore` comments for specific lines
4. Or keep `continue-on-error: true` for gradual typing

### Security Scanning Warnings

**Problem:** pip-audit or bandit report security issues.

**Solution:**
1. **For pip-audit:** Update vulnerable dependencies to safe versions
2. **For bandit:** Review flagged code and fix security issues
3. **False positives:** Exclude test files or specific paths from bandit
4. **Make it strict:** Remove `continue-on-error: true` if you want security issues to fail CI

## Best Practices

1. **Keep workflows simple:** Don't over-complicate the pipeline
2. **Test locally first:** Run the same checks locally before pushing
3. **Fix issues promptly:** Don't let CI failures accumulate
4. **Use matrix for multiple versions:** Test against all supported Python versions
5. **Cache dependencies:** The workflow uses pip caching automatically
6. **Document customizations:** If you modify the workflow, document why

## Integration with Local Workflow

### Should You Still Run Checks Locally?

**Yes! Always run checks locally before pushing.** CI is a safety net, not a replacement.

**Why run locally first:**
1. **Faster feedback** - Find issues in seconds, not minutes
2. **Avoid broken commits** - Don't push code that will fail CI
3. **Save time** - Fix issues immediately, don't wait for CI to fail
4. **Better workflow** - Catch issues while the code is fresh in your mind
5. **CI can be slow** - Local checks are instant, CI takes time

**What CI adds:**
- ✅ Tests in clean environments (catches environment-specific issues)
- ✅ Tests multiple Python versions (catches version-specific bugs)
- ✅ Historical record (see when issues were introduced)
- ✅ Safety net (catches things you forgot to run)
- ✅ Different environment (might catch issues your local setup doesn't)

### Recommended Workflow

**Before pushing:**
```bash
# 1. Run formatting and linting
python scripts/pre_commit_format.py

# 2. Run tests
pytest

# 3. (Optional) Run security checks
pip-audit
bandit -r src/ config/ scripts/

# 4. If everything passes, push
git add .
git commit -m "message"
git push
```

**After pushing:**
- CI runs automatically as a backup check
- View results in GitHub Actions tab
- Fix any issues CI finds that you missed

### This CI Pipeline Mirrors Your Local Workflow

**Local:**
```bash
python scripts/pre_commit_format.py  # Runs black + ruff
pytest                                # Runs tests
```

**CI:**
```yaml
- black --check .                     # Checks formatting
- ruff check .                        # Checks linting
- pytest                              # Runs tests
- pip-audit                           # Security (dependencies)
- bandit                              # Security (code)
```

The CI pipeline ensures that code pushed to GitHub meets the same quality standards as your local checks, and provides additional safety through clean environments and multi-version testing.

## Other Optional Checks You Could Add

### Code Complexity Checks

Monitor code complexity to maintain code quality:

```yaml
- name: Check code complexity
  run: |
    pip install radon
    radon cc src/ --min B  # Warn on complexity B or higher
```

### Documentation Build (if using Sphinx/MkDocs)

```yaml
- name: Build documentation
  run: |
    pip install sphinx
    sphinx-build -b html docs/ docs/_build/
```

### Package Build Verification (if publishing to PyPI)

```yaml
- name: Build package
  run: |
    pip install build
    python -m build
```

### License Compliance

```yaml
- name: Check licenses
  run: |
    pip install pip-licenses
    pip-licenses --format=json
```

## Next Steps

- ✅ CI pipeline is set up and working
- ✅ Security scanning included (pip-audit, bandit)
- ⏳ Consider adding CD (deployment) steps when you start publishing
- ⏳ Configure branch protection rules in GitHub to require CI passes
- ⏳ Add other optional checks based on project needs

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)

