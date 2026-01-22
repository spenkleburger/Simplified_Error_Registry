# Consolidation App Usage Guide

> **Last Updated:** 2026-01-21  
> **Status:** Step 3 Complete (Core functionality available)

This guide explains how to use the consolidation app to process session logs and generate consolidated fix repositories and coding tips.

---

## Overview

The consolidation app processes `.errors_fixes/errors_and_fixes.md` files across multiple projects, deduplicates errors, generates tags, and produces consolidated `fix_repo.md` and `coding_tips.md` files.

**Key Features:**
- Discovers projects automatically (recursive search)
- Parses session logs and existing consolidated files
- Deduplicates errors using exact match (AI semantic matching coming in Step 4)
- Generates rule-based tags (AI tagging coming in Step 4)
- Atomic writes (prevents partial file corruption)
- Path validation (prevents directory traversal attacks)
- Error isolation (one project failure doesn't stop others)

---

## Quick Start

### Basic Usage

```bash
# Consolidate all projects under a root directory
python -m src.consolidation_app.main --root /path/to/projects

# Dry-run mode (preview changes without writing)
python -m src.consolidation_app.main --root /path/to/projects --dry-run
```

### With Extra Projects

```bash
# Include projects outside the scan root
python -m src.consolidation_app.main \
  --root /path/to/projects \
  --extra /other/project1 /other/project2
```

**Note:** Extra projects are validated for security. Suspicious paths (e.g., `../../etc/passwd`) are rejected.

---

## Command-Line Arguments

### `--root` (required)

Root directory to search for projects. The app recursively searches for `.errors_fixes/errors_and_fixes.md` files.

**Example:**
```bash
python -m src.consolidation_app.main --root /home/user/projects
```

### `--config` (optional)

Config file path. Currently reserved for future use (ignored, logged as debug).

**Example:**
```bash
python -m src.consolidation_app.main --root /path/to/projects --config config.yaml
```

### `--dry-run`

Preview changes without writing files. Logs what would be written but doesn't modify any files.

**Example:**
```bash
python -m src.consolidation_app.main --root /path/to/projects --dry-run
```

**Output:**
```
[dry-run] Would write fix_repo (5), coding_tips (2), clear errors_and_fixes
```

---

## Workflow

### Per-Project Processing

For each discovered project, the app:

1. **Parses session log** (`errors_and_fixes.md`)
   - Extracts error entries and process issues
   - Handles missing files gracefully (skips project)

2. **Parses existing consolidated files** (if they exist)
   - `fix_repo.md` → existing error entries
   - `coding_tips.md` → existing process issue entries

3. **Deduplicates**
   - Merges new errors with existing (exact match on signature/type/file)
   - Merges new process issues with existing
   - Increments success counts for matching fixes
   - Keeps variants for different fixes

4. **Generates tags**
   - Applies rule-based tagging (error type, framework, domain, platform)
   - Merges with existing tags

5. **Writes consolidated files**
   - `fix_repo.md` (error entries only)
   - `coding_tips.md` (process issues only)
   - Uses atomic writes (temp file + rename)

6. **Clears session log**
   - Replaces `errors_and_fixes.md` with header only
   - Keeps file structure intact

### Error Handling

- **Per-project failures:** Logged as errors, processing continues with other projects
- **Missing files:** Logged as warnings, project skipped
- **Parse errors:** Logged as errors, project skipped
- **Write failures:** Logged as errors, project marked as failed

**Result:** Returns `ConsolidationResult` with `ok_count` and `fail_count`.

---

## Output

### Console Output

```
2026-01-21 12:00:00 - src.consolidation_app.discovery - INFO - Discovering projects from root: /path/to/projects
2026-01-21 12:00:00 - src.consolidation_app.discovery - INFO - Found 3 projects via rglob
2026-01-21 12:00:00 - __main__ - INFO - Consolidating 3 project(s) (dry_run=False)
2026-01-21 12:00:01 - __main__ - INFO - Project /path/to/projects/proj1: 5 error(s), 2 process issue(s) consolidated
2026-01-21 12:00:01 - __main__ - INFO - Project /path/to/projects/proj2: 3 error(s), 1 process issue(s) consolidated
2026-01-01 12:00:02 - __main__ - INFO - Consolidation complete: 3 ok, 0 failed
```

### Exit Codes

- `0`: All projects processed successfully
- `1`: One or more projects failed

---

## Security Features

### Atomic Writes

All file writes use a temp file + atomic rename pattern:

```python
temp_file = output_file.with_suffix(".tmp")
temp_file.write_text(content, encoding="utf-8", newline="\n")
temp_file.replace(output_file)  # Atomic on most filesystems
```

**Benefits:**
- Prevents partial writes on interruption (power loss, crash, etc.)
- Temp files cleaned up on errors
- Atomic rename on Windows, Linux, macOS

### Path Validation

`extra_projects` paths are validated before processing:

- **Rejects:** Directory traversal patterns (`../..`, `..\\..`, `/../`, `\\..\\`)
- **Rejects:** Empty or whitespace-only paths
- **Logs warnings:** For suspicious patterns
- **Accepts:** Valid absolute and relative paths (resolved to absolute)

**Example:**
```python
# Rejected:
"../../etc/passwd"  # Traversal pattern
"   "               # Whitespace only

# Accepted:
"/home/user/project"  # Absolute path
"project"             # Relative path (resolved to absolute)
```

---

## Integration with Scheduling

### Manual Execution

Run manually when needed:

```bash
python -m src.consolidation_app.main --root /path/to/projects
```

### Cron Schedule (Coming in Step 5)

Once Docker and scheduling are implemented (Step 5), the app will run automatically at 2 AM daily:

```yaml
# docker-compose.yml (future)
services:
  consolidation-app:
    environment:
      - CONSOLIDATION_SCHEDULE="0 2 * * *"
```

---

## Troubleshooting

### No Projects Found

**Symptom:** `No projects found under /path/to/projects`

**Solutions:**
- Verify projects have `.errors_fixes/errors_and_fixes.md` files
- Check root path is correct
- Use `--extra` to include projects outside scan root
- Run bootstrap script if files are missing: `python scripts/bootstrap_errors_fixes.py /path/to/project`

### Permission Errors

**Symptom:** `Permission denied writing fix_repo.md`

**Solutions:**
- Check file/directory permissions
- Ensure write access to `.errors_fixes/` directory
- Run with appropriate user permissions

### Parse Errors

**Symptom:** `Parse error for errors_and_fixes.md`

**Solutions:**
- Check markdown format matches specification (see `.cursor/rules/global/errors.mdc` "Entry Format" section)
- Verify timestamps are valid ISO8601 format (YYYY-MM-DDTHH:MM:SSZ)
- Check for malformed markdown (unclosed code blocks, missing headers, etc.)
- Ensure entries use exact format: `### Error:` or `### Agent Process Issue:` headers
- Verify all required fields are present (see `errors.mdc` for complete field list)
- Reference template: `docs/templates/errors_fixes_template/errors_and_fixes.md` for examples
- Review logs for specific error details

### Dry-Run Shows Changes But Write Fails

**Symptom:** Dry-run succeeds but actual write fails

**Solutions:**
- Check disk space
- Verify directory permissions
- Check for file locks (other processes accessing files)
- Review error logs for specific failure reason

---

## Examples

### Example 1: Basic Consolidation

```bash
# Consolidate all projects under ~/projects
python -m src.consolidation_app.main --root ~/projects
```

**Result:**
- Processes all projects with `.errors_fixes/errors_and_fixes.md`
- Writes `fix_repo.md` and `coding_tips.md` for each
- Clears `errors_and_fixes.md` (keeps header)

### Example 2: Preview Before Writing

```bash
# See what would be written without actually writing
python -m src.consolidation_app.main --root ~/projects --dry-run
```

**Result:**
- Logs what would be written
- No files modified
- Useful for testing or verification

### Example 3: Include External Projects

```bash
# Consolidate projects in ~/projects plus external ones
python -m src.consolidation_app.main \
  --root ~/projects \
  --extra /mnt/external/project1 /mnt/external/project2
```

**Result:**
- Processes projects under `~/projects` (via recursive search)
- Also processes `/mnt/external/project1` and `/mnt/external/project2`
- Validates external paths (rejects suspicious patterns)

---

## API Usage

### Programmatic Usage

```python
from pathlib import Path
from src.consolidation_app.main import consolidate_all_projects

# Consolidate all projects
result = consolidate_all_projects(
    Path("/path/to/projects"),
    extra_projects=None,
    dry_run=False
)

print(f"Processed {result.ok_count} projects, {result.fail_count} failed")
if result.all_ok:
    print("All projects consolidated successfully!")
```

### Per-Project Processing

```python
from pathlib import Path
from src.consolidation_app.main import _consolidate_one_project

# Process a single project
_consolidate_one_project(Path("/path/to/project"), dry_run=False)
```

---

## Related Documentation

- **`docs/API_REFERENCE.md`** - Complete API reference for all modules
- **`docs/SER_IMPLEMENTATION_PLAN.md`** - Detailed implementation plan
- **`docs/SER_PLAN.md`** - Project architecture and design decisions
- **`README.md`** - Project overview and setup

---

## Version Information

**Current Version:** v1.0 (Step 3 Complete)

**Implemented Features:**
- ✅ Discovery (recursive search, extra_projects support)
- ✅ Parser integration (session logs, existing consolidated files)
- ✅ Exact match deduplication
- ✅ Rule-based tagging
- ✅ Atomic writes
- ✅ Path validation
- ✅ CLI with dry-run mode
- ✅ Error isolation

**Coming in Step 4:**
- ⬜ AI semantic deduplication
- ⬜ AI-powered tagging
- ⬜ LLM client integration
- ⬜ Fix merging logic
- ⬜ Rule extraction

**Coming in Step 5:**
- ⬜ Docker containerization
- ⬜ Cron scheduling
- ⬜ ENV-first configuration
- ⬜ Logging and monitoring

---

**Last Updated:** 2026-01-21
