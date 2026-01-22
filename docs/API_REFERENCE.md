# API Reference - Consolidation App

> **Last Updated:** 2026-01-21  
> **Status:** Step 1 Complete (Parser & Generator modules)

This document provides API reference for the consolidation app modules implemented in Step 1.

---

## Table of Contents

1. [Parser Module](#parser-module)
2. [Generator Module](#generator-module)
3. [Data Structures](#data-structures)
4. [Security Considerations](#security-considerations)

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

**Current Version:** v1.0 (Step 1 Complete)

**Implemented Modules:**
- ✅ Parser (`parser.py`)
- ✅ Generator (`generator.py`)

**Planned Modules (Future Steps):**
- ⬜ Discovery (`discovery.py`) - Step 3.1
- ⬜ Deduplicator (`deduplicator.py`) - Step 3.3, 4.2
- ⬜ Tagger (`tagger.py`) - Step 3.4, 4.3
- ⬜ Writer (`writer.py`) - Step 3.5
- ⬜ Main (`main.py`) - Step 3.6

**Known Limitations (v1):**
- Exact signature matching only (no semantic matching)
- First tag used as category (no explicit category field)
- Naive datetimes assumed UTC
- Single example per rule (no aggregation)
- File path used as project name (no extraction)

---

## Related Documentation

- **`docs/SER_PLAN.md`** - Project architecture and design decisions
- **`docs/SER_IMPLEMENTATION_PLAN.md`** - Detailed implementation plan
- **`docs/PROJECT_STATUS.md`** - Current implementation status
- **`README.md`** - Project overview and setup
