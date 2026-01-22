# API Reference - Consolidation App

> **Last Updated:** 2026-01-21  
> **Status:** Step 3 Complete (All core modules implemented)

This document provides API reference for the consolidation app modules implemented in Steps 1-3.

---

## Table of Contents

1. [Parser Module](#parser-module)
2. [Generator Module](#generator-module)
3. [Discovery Module](#discovery-module)
4. [Deduplicator Module](#deduplicator-module)
5. [Tagger Module](#tagger-module)
6. [Writer Module](#writer-module)
7. [Main Module](#main-module)
8. [Data Structures](#data-structures)
9. [Security Considerations](#security-considerations)

---

## Parser Module

**Location:** `src/consolidation_app/parser.py`

### `ErrorEntry`

```python
@dataclass(frozen=True)
class ErrorEntry:
    """Normalized representation of an error/session entry."""
    
    error_signature: str
    error_type: str
    file: str
    line: int
    fix_code: str
    explanation: str
    result: str
    success_count: int
    tags: List[str]
    timestamp: datetime
    is_process_issue: bool
```

**Description:** Immutable dataclass representing a parsed error entry or agent process issue.

**Fields:**
- `error_signature`: Error message or issue description (from header)
- `error_type`: Exception class name or issue type
- `file`: File path where error occurred (empty for process issues)
- `line`: Line number (0 if not specified)
- `fix_code`: Code fix or rule established
- `explanation`: Explanation of fix or issue description
- `result`: Result status (✅ Solved, ❌ Failed, ✅ Documented, etc.)
- `success_count`: Number of times fix succeeded (0 for process issues)
- `tags`: List of context tags
- `timestamp`: When error/issue occurred (defaults to 1970-01-01 if missing)
- `is_process_issue`: True for Agent Process Issues, False for errors

### `parse_errors_and_fixes(file_path: Path) -> List[ErrorEntry]`

**Description:** Parse a markdown file containing error entries and process issues.

**Parameters:**
- `file_path` (Path): Path to `errors_and_fixes.md` file

**Returns:**
- `List[ErrorEntry]`: List of parsed entries (empty list if file missing/empty)

**Behavior:**
- Returns empty list if file doesn't exist
- Returns empty list if file is empty
- Skips malformed entries (logs warning)
- Handles missing fields with defaults (line=0, file="", success_count=0, etc.)
- Parses both `### Error:` and `### Agent Process Issue:` headers

**Example:**
```python
from pathlib import Path
from src.consolidation_app.parser import parse_errors_and_fixes

entries = parse_errors_and_fixes(Path(".errors_fixes/errors_and_fixes.md"))
for entry in entries:
    print(f"{entry.error_signature}: {entry.result}")
```

**Edge Cases:**
- Missing timestamp → Uses `DEFAULT_TIMESTAMP` (1970-01-01)
- Malformed timestamp → Logs warning, skips entry
- Missing metadata fields → Uses empty string or 0
- Empty code blocks → Returns empty string
- Invalid markdown → Logs warning, skips entry

### `parse_fix_repo(file_path: Path) -> List[ErrorEntry]`

**Description:** Parse `fix_repo.md` (generator output) back into ErrorEntry list. Enables incremental consolidation by reading existing consolidated files.

**Parameters:**
- `file_path` (Path): Path to `fix_repo.md` file

**Returns:**
- `List[ErrorEntry]`: List of parsed error entries (all `is_process_issue=False`)

**Behavior:**
- Returns empty list if file doesn't exist
- Returns empty list if file is empty
- Parses `##` sections (error signatures) and `### Fix N:` blocks
- Unescapes markdown headers (reverses generator escaping)
- Handles "None" tags (treats as empty list)

**Example:**
```python
from pathlib import Path
from src.consolidation_app.parser import parse_fix_repo

existing_errors = parse_fix_repo(Path(".errors_fixes/fix_repo.md"))
# Use with deduplicator to merge new entries with existing
```

### `parse_coding_tips(file_path: Path) -> List[ErrorEntry]`

**Description:** Parse `coding_tips.md` (generator output) back into ErrorEntry list. Enables incremental consolidation.

**Parameters:**
- `file_path` (Path): Path to `coding_tips.md` file

**Returns:**
- `List[ErrorEntry]`: List of parsed process issue entries (all `is_process_issue=True`)

**Behavior:**
- Returns empty list if file doesn't exist
- Returns empty list if file is empty
- Parses `##` sections (categories) and `### Rule:` blocks
- Unescapes markdown headers
- Extracts success count from "Related Errors" section if present

**Example:**
```python
from pathlib import Path
from src.consolidation_app.parser import parse_coding_tips

existing_rules = parse_coding_tips(Path(".errors_fixes/coding_tips.md"))
# Use with deduplicator to merge new process issues with existing
```

---

## Generator Module

**Location:** `src/consolidation_app/generator.py`

### `generate_fix_repo_markdown(entries: Iterable[ErrorEntry]) -> str`

**Description:** Generate consolidated markdown for fix repository, grouping fixes by error signature.

**Parameters:**
- `entries` (Iterable[ErrorEntry]): Error entries to consolidate

**Returns:**
- `str`: Markdown content for `fix_repo.md`

**Behavior:**
- Filters out process issues (`is_process_issue=False`)
- Groups entries by exact error signature match
- Orders fixes within each group by success count (descending)
- Escapes markdown special characters in headers
- Handles empty input (returns header only)
- Aggregates metadata (first seen, last updated, all tags)

**Security:**
- Escapes markdown special characters in error signatures (#, *, [, ], etc.)
- Escapes backticks in tags
- Prevents markdown injection

**Example:**
```python
from src.consolidation_app.generator import generate_fix_repo_markdown

markdown = generate_fix_repo_markdown(entries)
with open(".errors_fixes/fix_repo.md", "w", encoding="utf-8") as f:
    f.write(markdown)
```

**Output Format:**
```markdown
# Fix Repository

> **Last Updated:** 2026-01-21T12:00:00Z
> **Total Entries:** 5
> **Consolidated from:** 2 projects

## ErrorSignature: Error message

**Tags:** `tag1`, `tag2`
**First Seen:** 2026-01-15
**Last Updated:** 2026-01-20
**Total Occurrences:** 3

### Fix 1: ErrorType (Success Count: 5)

**Code:**
```python
fix_code_here
```

**Why this works:** Explanation
**Result:** ✅ Solved
**Projects:** src/app/example.py
**Last Updated:** 2026-01-20T10:00:00Z

---
```

**v1 Limitations:**
- Uses `error_type` as fix description (future: extract from explanation)
- Uses file path for project name (future: extract project name)
- Exact signature matching only (future: semantic matching)

### `generate_coding_tips_markdown(entries: Iterable[ErrorEntry]) -> str`

**Description:** Generate consolidated markdown for coding tips, organizing agent process rules by category.

**Parameters:**
- `entries` (Iterable[ErrorEntry]): Process issue entries to consolidate

**Returns:**
- `str`: Markdown content for `coding_tips.md`

**Behavior:**
- Filters for process issues (`is_process_issue=True`)
- Groups entries by category (first tag, or error_type, or "General")
- Escapes markdown special characters in headers
- Handles empty input (returns header only)

**Security:**
- Escapes markdown special characters in category and rule titles
- Prevents markdown injection

**Example:**
```python
from src.consolidation_app.generator import generate_coding_tips_markdown

markdown = generate_coding_tips_markdown(entries)
with open(".errors_fixes/coding_tips.md", "w", encoding="utf-8") as f:
    f.write(markdown)
```

**Output Format:**
```markdown
# Coding Tips - Agent Process Rules

> **Last Updated:** 2026-01-21T12:00:00Z
> **Total Rules:** 3

## Category Name

### Rule: Rule title

**Why:** Explanation of why this rule is important.

**Examples:**
- ✅ Good example that follows the rule
- ❌ Bad example that violates the rule

**Related Errors:**
- `ErrorType`: Error message (success count: 0)

---
```

**v1 Limitations:**
- Uses first tag as category (future: explicit category field)
- Generates single good/bad example (future: aggregate multiple)
- Uses success_count for related errors (future: occurrence count)

### Helper Functions

#### `format_code_block(code: str, language: str = "python") -> str`

**Description:** Format code as a markdown fenced code block.

**Parameters:**
- `code` (str): Code content
- `language` (str): Language identifier (default: "python")

**Returns:**
- `str`: Fenced code block markdown

**Example:**
```python
code = "def hello():\n    print('world')"
formatted = format_code_block(code, "python")
# Returns: "```python\ndef hello():\n    print('world')\n```"
```

#### `format_tags(tags: List[str]) -> str`

**Description:** Format tag list as markdown-safe representation.

**Parameters:**
- `tags` (List[str]): List of tag strings

**Returns:**
- `str`: Formatted tags (e.g., "`tag1`, `tag2`") or "None" if empty

**Security:**
- Escapes backticks in tags to prevent markdown breaking

**Example:**
```python
tags = ["python", "docker", "tag`with`backticks"]
formatted = format_tags(tags)
# Returns: "`python`, `docker`, `tag\`with\`backticks`"
```

#### `format_timestamp(dt: datetime) -> str`

**Description:** Serialize datetime to UTC ISO8601 string with Z suffix.

**Parameters:**
- `dt` (datetime): Datetime object (naive or aware)

**Returns:**
- `str`: ISO8601 timestamp (e.g., "2026-01-21T12:00:00Z")

**Behavior:**
- Assumes naive datetimes are UTC (v1 limitation)
- Logs debug message when naive datetime encountered
- Converts to UTC, removes microseconds, uses Z suffix

**Example:**
```python
from datetime import datetime, timezone

dt = datetime(2026, 1, 21, 12, 0, tzinfo=timezone.utc)
formatted = format_timestamp(dt)
# Returns: "2026-01-21T12:00:00Z"
```

---

## Discovery Module

**Location:** `src/consolidation_app/discovery.py`

### `discover_projects(root_path: Path, extra_projects: list[str] | None = None) -> list[Path]`

**Description:** Discover all projects with `.errors_fixes/errors_and_fixes.md` files.

**Parameters:**
- `root_path` (Path): Root directory to search recursively
- `extra_projects` (list[str] | None): Optional list of project paths outside scan root

**Returns:**
- `list[Path]`: List of project root paths (deduplicated, order preserved)

**Behavior:**
- Uses `rglob()` to find all `.errors_fixes/errors_and_fixes.md` files
- For `extra_projects`: validates paths, auto-bootstraps if missing, resolves to absolute
- Deduplicates projects (preserves order)
- Handles permission errors gracefully (continues with extra_projects)

**Security:**
- Validates `extra_projects` paths to reject directory traversal patterns
- Rejects empty/whitespace-only paths
- Logs warnings for suspicious paths

**Example:**
```python
from pathlib import Path
from src.consolidation_app.discovery import discover_projects

projects = discover_projects(Path("/home/user/projects"))
# Returns: [Path('/home/user/projects/proj1'), Path('/home/user/projects/proj2')]

# With extra projects
projects = discover_projects(
    Path("/home/user/projects"),
    extra_projects=["/other/project1", "/other/project2"]
)
```

**Raises:**
- `FileNotFoundError`: If root_path doesn't exist
- `NotADirectoryError`: If root_path is not a directory
- `ValueError`: If extra_projects contains invalid paths

---

## Deduplicator Module

**Location:** `src/consolidation_app/deduplicator.py`

### `deduplicate_errors_exact(new_entries: List[ErrorEntry], existing_entries: List[ErrorEntry]) -> List[ErrorEntry]`

**Description:** Deduplicate new entries against existing entries using exact match.

**Parameters:**
- `new_entries` (List[ErrorEntry]): New entries to deduplicate
- `existing_entries` (List[ErrorEntry]): Existing entries to match against

**Returns:**
- `List[ErrorEntry]`: Consolidated list with duplicates merged where possible

**Match Criteria:**
- `error_signature` (exact match)
- `error_type` (exact match)
- `file` (exact match)

**Behavior:**
- If match found and `fix_code` is same: merges entries (increments success_count)
- If match found but `fix_code` differs: keeps both as variants
- If no match: adds as new entry
- Returns existing entries if new_entries is empty
- Returns new entries if existing_entries is empty

**Example:**
```python
from src.consolidation_app.deduplicator import deduplicate_errors_exact

consolidated = deduplicate_errors_exact(new_entries, existing_entries)
# Merges duplicates, keeps variants, adds new entries
```

### `merge_entries(existing: ErrorEntry, new: ErrorEntry) -> ErrorEntry`

**Description:** Merge two entries with matching signature/type/file and same fix_code.

**Parameters:**
- `existing` (ErrorEntry): Existing entry to merge into
- `new` (ErrorEntry): New entry to merge

**Returns:**
- `ErrorEntry`: New ErrorEntry with merged data

**Merging Logic:**
- `timestamp`: Uses newer timestamp
- `success_count`: Sums both counts
- `tags`: Union of both tag lists (deduplicated, sorted)
- `result`: Prefers "✅ Solved" if either is solved
- `explanation`: Uses existing (or new if existing is empty)

---

## Tagger Module

**Location:** `src/consolidation_app/tagger.py`

### `generate_tags_rule_based(entry: ErrorEntry) -> List[str]`

**Description:** Generate tags for an entry using rule-based detection.

**Parameters:**
- `entry` (ErrorEntry): ErrorEntry to generate tags for

**Returns:**
- `List[str]`: List of tags (typically 3-5 tags)

**Tag Types Generated:**
1. **Error type tag**: From `error_type` field (e.g., "file-io", "type-conversion")
2. **Framework/library tag**: From file path or error context (e.g., "docker", "django", "pytest")
3. **Domain tag**: From error context or file location (e.g., "networking", "database", "authentication")
4. **Platform tag**: From error message or file path (e.g., "windows", "linux", "macos")

**Example:**
```python
from src.consolidation_app.tagger import generate_tags_rule_based

tags = generate_tags_rule_based(entry)
# Returns: ["file-io", "docker", "networking", "linux"]
```

### `apply_tags_to_entry(entry: ErrorEntry) -> ErrorEntry`

**Description:** Merge rule-based tags with entry's existing tags and return a new ErrorEntry.

**Parameters:**
- `entry` (ErrorEntry): ErrorEntry to enhance with generated tags

**Returns:**
- `ErrorEntry`: New ErrorEntry with tags = sorted(set(entry.tags) | set(generated))

**Example:**
```python
from src.consolidation_app.tagger import apply_tags_to_entry

# Entry has existing tags: ["custom-tag"]
enhanced = apply_tags_to_entry(entry)
# Enhanced has: ["custom-tag", "file-io", "docker", "linux"] (merged and sorted)
```

---

## Writer Module

**Location:** `src/consolidation_app/writer.py`

### `write_fix_repo(project_path: Path, consolidated_entries: List[ErrorEntry]) -> None`

**Description:** Write `fix_repo.md` with consolidated error entries.

**Parameters:**
- `project_path` (Path): Path to project root directory
- `consolidated_entries` (List[ErrorEntry]): List of consolidated ErrorEntry objects

**Behavior:**
- Filters entries where `is_process_issue=False`
- Generates markdown using `generate_fix_repo_markdown()`
- Writes to `project_path/.errors_fixes/fix_repo.md`
- Creates directory if missing
- Uses UTF-8 encoding and LF line endings
- **Atomic write**: Writes to temp file, then renames (prevents partial writes)

**Raises:**
- `PermissionError`: If file cannot be written due to permissions
- `OSError`: If file operations fail for other reasons

**Example:**
```python
from pathlib import Path
from src.consolidation_app.writer import write_fix_repo

write_fix_repo(Path("/path/to/project"), consolidated_entries)
```

### `write_coding_tips(project_path: Path, process_entries: List[ErrorEntry]) -> None`

**Description:** Write `coding_tips.md` with consolidated process issue entries.

**Parameters:**
- `project_path` (Path): Path to project root directory
- `process_entries` (List[ErrorEntry]): List of ErrorEntry objects (should be process issues)

**Behavior:**
- Filters entries where `is_process_issue=True`
- Generates markdown using `generate_coding_tips_markdown()`
- Writes to `project_path/.errors_fixes/coding_tips.md`
- Creates directory if missing
- Uses UTF-8 encoding and LF line endings
- **Atomic write**: Writes to temp file, then renames

**Raises:**
- `PermissionError`: If file cannot be written due to permissions
- `OSError`: If file operations fail for other reasons

### `clear_errors_and_fixes(project_path: Path) -> None`

**Description:** Clear `errors_and_fixes.md` but keep the file with header only.

**Parameters:**
- `project_path` (Path): Path to project root directory

**Behavior:**
- Replaces file contents with header only (preserves file structure)
- Keeps the file (doesn't delete it)
- Uses UTF-8 encoding and LF line endings
- **Atomic write**: Writes to temp file, then renames
- Logs warning if file doesn't exist (skips operation)

**Raises:**
- `PermissionError`: If file cannot be read/written due to permissions
- `OSError`: If file operations fail for other reasons

---

## Main Module

**Location:** `src/consolidation_app/main.py`

### `consolidate_all_projects(root_path: Path, extra_projects: list[str] | None = None, *, dry_run: bool = False) -> ConsolidationResult`

**Description:** Discover projects, consolidate each (parse, deduplicate, tag, write, clear).

**Parameters:**
- `root_path` (Path): Root directory to search for projects
- `extra_projects` (list[str] | None): Optional list of project paths to include
- `dry_run` (bool): If True, do not write files; only log intended actions

**Returns:**
- `ConsolidationResult`: Dataclass with `ok_count`, `fail_count`, and `all_ok` property

**Workflow (per project):**
1. Parse `errors_and_fixes.md`
2. Parse `fix_repo.md` (if exists)
3. Parse `coding_tips.md` (if exists)
4. Deduplicate errors (new vs existing from fix_repo)
5. Deduplicate process issues (new vs existing from coding_tips)
6. Apply tags (merge with existing)
7. Write `fix_repo.md`, `coding_tips.md`
8. Clear `errors_and_fixes.md` (unless dry_run)

**Error Handling:**
- Continues processing other projects if one fails
- Logs errors for each project
- Returns success/failure counts

**Example:**
```python
from pathlib import Path
from src.consolidation_app.main import consolidate_all_projects

result = consolidate_all_projects(Path("/home/user/projects"), dry_run=False)
print(f"Processed {result.ok_count} projects, {result.fail_count} failed")
```

### `ConsolidationResult`

**Description:** Result of `consolidate_all_projects()`.

**Fields:**
- `ok_count` (int): Number of projects successfully consolidated
- `fail_count` (int): Number of projects that failed

**Properties:**
- `all_ok` (bool): True if `fail_count == 0`

### CLI Usage

```bash
# Run consolidation
python -m src.consolidation_app.main --root /path/to/projects

# Dry-run (preview without writing)
python -m src.consolidation_app.main --root /path/to/projects --dry-run

# With config file (reserved for future use)
python -m src.consolidation_app.main --root /path/to/projects --config config.yaml
```

**Arguments:**
- `--root` (required): Root directory to search for projects
- `--config` (optional): Config file path (currently ignored, reserved for future)
- `--dry-run`: Do not write files; only log intended actions

**Exit Codes:**
- `0`: All projects processed successfully
- `1`: One or more projects failed

---

## Data Structures

### ErrorEntry

See [Parser Module](#errorentry) for full definition.

**Default Values:**
- `line`: 0
- `file`: "" (empty string)
- `success_count`: 0
- `tags`: [] (empty list)
- `timestamp`: `DEFAULT_TIMESTAMP` (1970-01-01) if missing
- `result`: "" (empty string) if missing

**Validation:**
- All fields are required (no Optional types)
- Dataclass is frozen (immutable)
- Timestamp parsing validates ISO8601 format

---

## Security Considerations

### Markdown Injection Prevention

**Tag Escaping:**
- Backticks in tags are escaped: `` `tag` `` → `` \`tag\` ``
- Prevents markdown code block injection

**Header Escaping:**
- Special characters in headers are escaped: `#`, `*`, `[`, `]`, `(`, `)`, `<`, `>`, `` ` ``, `_`, `~`
- Prevents markdown header/list/link injection

**Implementation:**
- `format_tags()`: Escapes backticks
- `_escape_markdown_header()`: Escapes all markdown special characters

### Input Validation

**Parser:**
- Validates timestamp format (ISO8601)
- Handles malformed entries gracefully (logs warning, skips)
- No file path traversal (uses provided Path object)

**Generator:**
- No direct file I/O (pure transformation)
- All input comes from parsed ErrorEntry objects
- No user input accepted

**Discovery:**
- Validates `extra_projects` paths to reject directory traversal patterns
- Rejects empty/whitespace-only paths
- Logs warnings for suspicious paths
- Uses `Path.resolve()` to normalize paths

### Atomic Writes

**Writer Module:**
- All file writes use temp file + atomic rename pattern
- Prevents partial writes on interruption (power loss, crash, etc.)
- Temp files are cleaned up on errors
- Atomic rename on most filesystems (Windows, Linux, macOS)

**Implementation:**
```python
temp_file = output_file.with_suffix(".tmp")
temp_file.write_text(content, encoding="utf-8", newline="\n")
temp_file.replace(output_file)  # Atomic rename
```

### Path Security

**Discovery Module:**
- Validates `extra_projects` input strings before resolution
- Rejects patterns like `../../etc/passwd`, `..\\..\\windows\\system32`
- Uses `Path.resolve()` for normalization
- Validates paths exist and are directories before processing

### Logging

**Debug Logging:**
- Entry counts, grouping operations
- Empty input handling
- Timezone assumptions (naive datetime handling)

**Security Logging:**
- Malformed entry warnings
- Timestamp parsing failures

---

## Usage Examples

### Complete Workflow

```python
from pathlib import Path
from src.consolidation_app.parser import parse_errors_and_fixes
from src.consolidation_app.generator import (
    generate_fix_repo_markdown,
    generate_coding_tips_markdown,
)

# Parse session log
project_path = Path("/path/to/project")
log_file = project_path / ".errors_fixes" / "errors_and_fixes.md"
entries = parse_errors_and_fixes(log_file)

# Generate consolidated files
fix_repo_md = generate_fix_repo_markdown(entries)
coding_tips_md = generate_coding_tips_markdown(entries)

# Write consolidated files
(project_path / ".errors_fixes" / "fix_repo.md").write_text(
    fix_repo_md, encoding="utf-8"
)
(project_path / ".errors_fixes" / "coding_tips.md").write_text(
    coding_tips_md, encoding="utf-8"
)
```

### Filtering Entries

```python
# Get only error entries
error_entries = [e for e in entries if not e.is_process_issue]

# Get only process issues
process_issues = [e for e in entries if e.is_process_issue]

# Filter by tag
docker_errors = [e for e in entries if "docker" in e.tags]
```

### Accessing Entry Data

```python
for entry in entries:
    print(f"Error: {entry.error_signature}")
    print(f"Type: {entry.error_type}")
    print(f"File: {entry.file}:{entry.line}")
    print(f"Success Count: {entry.success_count}")
    print(f"Tags: {', '.join(entry.tags)}")
    print(f"Timestamp: {entry.timestamp}")
    print(f"Fix Code:\n{entry.fix_code}")
    print("---")
```

---

## Version Information

**Current Version:** v1.0 (Step 3 Complete)

**Implemented Modules:**
- ✅ Parser (`parser.py`) - Step 1.3, 3.6 (enhanced with parse_fix_repo, parse_coding_tips)
- ✅ Generator (`generator.py`) - Step 1.4
- ✅ Discovery (`discovery.py`) - Step 3.1
- ✅ Deduplicator (`deduplicator.py`) - Step 3.3
- ✅ Tagger (`tagger.py`) - Step 3.4
- ✅ Writer (`writer.py`) - Step 3.5
- ✅ Main (`main.py`) - Step 3.6

**Planned Modules (Future Steps):**
- ⬜ LLM Client (`llm_client.py`) - Step 4.1
- ⬜ AI Deduplication (enhancement) - Step 4.2
- ⬜ AI Tagging (enhancement) - Step 4.3
- ⬜ Fix Merging Logic - Step 4.4
- ⬜ Rule Extraction - Step 4.5

**Known Limitations (v1):**
- Exact signature matching only (no semantic matching - coming in Step 4)
- First tag used as category (no explicit category field)
- Naive datetimes assumed UTC
- Single example per rule (no aggregation)
- File path used as project name (no extraction)
- Rule-based tagging only (no AI tagging - coming in Step 4)

**Security Features (v1):**
- ✅ Atomic writes (temp file + rename)
- ✅ Path validation (rejects directory traversal)
- ✅ Markdown injection prevention (tag/header escaping)
- ✅ Error isolation (per-project failures don't stop others)
- ✅ Comprehensive logging (DEBUG, INFO, WARNING, ERROR)

---

## Related Documentation

- **`docs/SER_PLAN.md`** - Project architecture and design decisions
- **`docs/SER_IMPLEMENTATION_PLAN.md`** - Detailed implementation plan
- **`docs/PROJECT_STATUS.md`** - Current implementation status
- **`README.md`** - Project overview and setup
