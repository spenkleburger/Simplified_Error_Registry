# Simplified Error Registry: Architecture & Implementation Plan (V2)

> **A streamlined, markdown-based approach for personal-scale error tracking and agent process documentation**  
> **V2:** SQT-refined (redundancies removed, simplifications applied, ENV-first config). See `SIMPLIFIED_ERROR_REGISTRY_SQT.md` for the assessment.

**Last Updated:** 2025-01-15  
**Status:** 🟡 Design Phase  
**Target Scale:** Personal projects (< 500 error entries)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [File Structure & Formats](#file-structure--formats)
4. [Workflow](#workflow)
5. [Consolidation App Design](#consolidation-app-design)
6. [Agent Rules & Integration](#agent-rules--integration)
7. [Portability & Setup](#portability--setup)
8. [Implementation Plan](#implementation-plan)
9. [Comparison with Current GER](#comparison-with-current-ger)
10. [Migration Strategy](#migration-strategy)

---

## Overview

### Philosophy

This simplified approach replaces the complex JSON-based Global Error Registry with a markdown-based system optimized for personal use. The system focuses on:

1. **Simplicity**: Human-readable markdown files instead of structured JSON
2. **Agent Process Tracking**: Built-in documentation of agent workflow issues
3. **AI-Powered Consolidation**: Daily batch processing to deduplicate and organize fixes
4. **Success-Based Ordering**: Fixes ordered by success count, no negative knowledge tracking
5. **Two-Tier Lookup**: Recent session log → Consolidated repository
6. **Portability**: Self-contained folder that can be copied to any project

### Key Design Decisions

| Decision | Rationale |
|----------|----------|
| **Markdown over JSON** | Human-readable, easy to edit, sufficient for personal scale |
| **No negative knowledge** | Simpler model: try fixes in order, document why different fixes work |
| **AI deduplication** | Semantic matching handles variations better than exact hash matching |
| **Daily consolidation** | Batch processing reduces overhead, acceptable latency for personal use |
| **Success count ordering** | Clear priority: most successful fixes tried first |
| **Separate process rules** | Agent workflow issues tracked separately from code errors |
| **Self-contained folder** | `.errors_fixes/` folder contains all files for easy portability |
| **Git-ignored** | Session logs are ephemeral, don't clutter version control |

### Scale Assumptions

- **Personal use**: Single developer or small team
- **Error volume**: < 500 consolidated entries
- **Project count**: 5-20 projects
- **Update frequency**: Daily consolidation acceptable
- **Query performance**: Linear search over markdown is acceptable at this scale

---

## Architecture

### High-Level Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Session                       │
│                                                              │
│  Agent fixes error → Documents in .errors_fixes/            │
│                    errors_and_fixes.md                      │
│                    ↓                                         │
│  Session ends → errors_and_fixes.md contains all fixes      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Daily Consolidation (2 AM)                     │
│                                                              │
│  1. Read all .errors_fixes/errors_and_fixes.md from all    │
│     projects                                                │
│  2. AI deduplication (semantic similarity matching)         │
│  3. AI tagging (generate context tags)                      │
│  4. Merge fixes by success count                            │
│  5. Write consolidated .errors_fixes/fix_repo.md to each    │
│     project                                                 │
│  6. Extract process rules → .errors_fixes/coding_tips.md   │
│  7. Clear contents of errors_and_fixes.md (keep file)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Next Development Session                        │
│                                                              │
│  Agent checks:                                               │
│  1. .errors_fixes/errors_and_fixes.md (recent session)      │
│  2. .errors_fixes/fix_repo.md (consolidated fixes)          │
│  3. .errors_fixes/coding_tips.md (agent process rules)       │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

#### 1. Session Log (`.errors_fixes/errors_and_fixes.md`)
- **Purpose**: Ephemeral log of errors and fixes during active development
- **Location**: `.errors_fixes/` folder (git-ignored)
- **Lifecycle**: Appended during session, processed by consolidation app, contents cleared after consolidation
- **Format**: Simple markdown with error descriptions and fixes

#### 2. Consolidated Repository (`.errors_fixes/fix_repo.md`)
- **Purpose**: Solutions to **errors in application and test code**. When application or test code fails at runtime, which code change resolved it. Deduplicated, AI-tagged, ordered by success count. Use **reactively** when an error occurs.
- **Location**: `.errors_fixes/` folder (updated by consolidation app)
- **Lifecycle**: Read-only during development, updated daily by consolidation
- **Format**: Structured markdown with tags, success counts, and ordered fixes

#### 3. Agent Process Rules (`.errors_fixes/coding_tips.md`)
- **Purpose**: **Agent process and workflow rules**. How the agent should behave (paths, commands, Docker, conventions) to avoid mistakes. Use **proactively** before and during coding. Built only from **Agent Process Issue** entries.
- **Location**: `.errors_fixes/` folder
- **Lifecycle**: Updated by consolidation app when process issues detected
- **Format**: Rule-based markdown with examples

#### 4. Consolidation App
- **Purpose**: Daily batch processing to consolidate fixes across projects
- **Location**: Docker container or standalone script
- **Schedule**: Daily at 2 AM (configurable)
- **Technology**: Python + LLM (Ollama or cloud API)

### fix_repo.md vs coding_tips.md: Clear Distinction

| | **fix_repo.md** | **coding_tips.md** |
|--|-----------------|---------------------|
| **Domain** | Application and test code failures (exceptions, test failures) | Agent process and workflow (how the agent should behave) |
| **Answers** | "This runtime/test error occurred — what code change fixes it?" | "How should I behave (paths, commands, Docker, etc.) to avoid mistakes?" |
| **When to use** | **Reactive**: after a runtime or test error occurs | **Proactive**: before and during coding |
| **Source in session log** | `### Error: ...` entries only | `### Agent Process Issue: ...` entries only |
| **Contains** | Error signature → fix(es) with success count | Rules, do's/don'ts, examples |

---

## File Structure & Formats

### Project Directory Structure

```
project_root/
├── .errors_fixes/              # Self-contained error registry system (git-ignored)
│   ├── errors_and_fixes.md     # Session log (ephemeral, contents cleared after consolidation)
│   ├── fix_repo.md             # Consolidated fixes (read-only during dev, updated by consolidation app)
│   ├── coding_tips.md           # Agent process rules (read-only during dev, updated by consolidation app)
│   └── README.md                # Quick reference for the system (optional)
├── .cursor/
│   ├── rules/
│   │   └── global/
│   │       └── errors.mdc      # Global agent instructions (references .errors_fixes/ paths)
│   └── commands/                # Optional: Custom commands
│       └── global/
│           └── test-and-fix.mdc # Optional: Global auto-fix command (see Test Execution Strategy)
└── (application code)
```

**Note**: The `.errors_fixes/` folder should be added to `.gitignore`:

```
# Error registry system (ephemeral session logs)
.errors_fixes/
```

### File Format: `.errors_fixes/errors_and_fixes.md`

**Purpose**: Session log of errors and fixes during active development.

**When to write which block:**

- **`### Error: ...`** — Application or test code raised an exception or a test failed; you have a traceback/error message and a **code change** that fixed it. → Consolidation sends these to **fix_repo.md** only.
- **`### Agent Process Issue: ...`** — The mistake was in **how the agent behaved** (e.g. path format, command, use of `localhost` in Docker). Record a **process/behavior rule** for next time. → Consolidation sends these to **coding_tips.md** only.

```markdown
# Errors and Fixes Log

> **Note**: This file is processed daily by the consolidation app at 2 AM. 
> `### Error:` entries → fix_repo.md; `### Agent Process Issue:` entries → coding_tips.md. Contents are then cleared (file is kept).

## 2025-01-15 Session

### Error: FileNotFoundError: [WinError 2] The system cannot find the file specified

**Timestamp:** 2025-01-15T14:32:00Z  
**File:** `tools/buffer_manager.py`  
**Line:** 42  
**Error Type:** `FileNotFoundError`  
**Tags:** `file-io`, `windows`, `path-handling` (auto-generated)

**Error Context:**
```
Traceback (most recent call last):
  File "tools/buffer_manager.py", line 42, in read_buffer
    with open('/data/buffer.json', 'r') as f:
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Fix Applied:**
```python
# Before
with open('/data/buffer.json', 'r') as f:

# After
from pathlib import Path
buffer_path = Path('data') / 'buffer.json'
with open(buffer_path, 'r', encoding='utf-8') as f:
```

**Explanation:** Used absolute Unix-style path which doesn't work on Windows. Changed to `pathlib.Path` for cross-platform compatibility.

**Result:** ✅ Solved  
**Success Count:** 1  
**Test Command:** `task test`  
**Test Result:** All tests passed

---

### Agent Process Issue: Unix-style paths don't work on Windows

**Timestamp:** 2025-01-15T14:35:00Z  
**Issue Type:** `agent-process`  
**Tags:** `agent-process`, `path-handling`, `windows`

**Issue Description:**
Agent attempted to use Unix-style absolute path `/data/file.json` which fails on Windows systems.

**Rule Established:**
Always use `pathlib.Path` or `os.path.join()` for file paths to ensure cross-platform compatibility.

**Example:**
- ✅ `Path('data') / 'file.json'`
- ✅ `os.path.join('data', 'file.json')`
- ❌ `'/data/file.json'` (Unix-only)

**Result:** ✅ Documented

---

### Error: TypeError: can only concatenate str (not "int") to str

**Timestamp:** 2025-01-15T15:10:00Z  
**File:** `src/payment.py`  
**Line:** 87  
**Error Type:** `TypeError`  
**Tags:** `type-conversion`, `string-formatting`, `python`

**Error Context:**
```python
total = 100
message = "Total: " + total  # TypeError
```

**Fix Applied:**
```python
# After
message = f"Total: {total}"
```

**Explanation:** Used f-string for automatic type conversion.

**Result:** ✅ Solved  
**Success Count:** 1  
**Test Command:** `task test`  
**Test Result:** All tests passed

---
```

### File Format: `.errors_fixes/fix_repo.md`

**Purpose**: Solutions to **errors in application and test code**. When runtime or test failures occur, which code change fixed them. Consolidated from `### Error:` entries only; deduplicated, AI-tagged, ordered by success count. Use **reactively** when you have an error to fix.

```markdown
# Fix Repository

> **Last Updated:** 2025-01-16T02:00:00Z  
> **Total Entries:** 127  
> **Consolidated from:** 5 projects

---

## ConnectionRefusedError: [Errno 111] Connect call failed

**Tags:** `docker`, `networking`, `connection-refused`, `postgres`, `database`  
**First Seen:** 2025-01-10  
**Last Updated:** 2025-01-15  
**Total Occurrences:** 8

### Fix 1: Use Docker service name (Success Count: 8)

**Code:**
```python
# Before
db_host = 'localhost'

# After
db_host = os.getenv('DB_HOST', 'postgres')  # Use service name from docker-compose
```

**Why this works:** Container networking requires service names from docker-compose, not 'localhost' which refers to the container itself.

**When to use:** Always in Docker environments when connecting to services defined in docker-compose.

**Projects:** CryptoBot, ToDoApp, PaymentAPI (3 projects)

---

### Fix 2: Use host.docker.internal (Success Count: 2)

**Code:**
```python
# After
db_host = 'host.docker.internal'
```

**Why this works:** Direct host access needed when service name unavailable or connecting to host services.

**When to use:** Connecting from container to services running on host machine (not in docker-compose).

**Projects:** DevTools, LocalAPI (2 projects)

---

## TypeError: can only concatenate str (not "int") to str

**Tags:** `type-conversion`, `string-formatting`, `python`, `type-error`  
**First Seen:** 2025-01-12  
**Last Updated:** 2025-01-15  
**Total Occurrences:** 15

### Fix 1: Use f-string (Success Count: 12)

**Code:**
```python
# Before
message = "Total: " + total

# After
message = f"Total: {total}"
```

**Why this works:** F-strings automatically handle type conversion, avoiding TypeError.

**When to use:** Python 3.6+ (f-strings available). Preferred method for string formatting.

**Projects:** PaymentAPI, CryptoBot, ToDoApp, DevTools (4 projects)

---

### Fix 2: Explicit str() conversion (Success Count: 3)

**Code:**
```python
# After
message = "Total: " + str(total)
```

**Why this works:** Explicit type conversion ensures string concatenation works.

**When to use:** Python < 3.6 (f-strings unavailable) or when f-strings cause issues in specific contexts.

**Projects:** LegacyApp, OldService (2 projects)

---

## FileNotFoundError: [WinError 2] The system cannot find the file specified

**Tags:** `file-io`, `windows`, `path-handling`, `cross-platform`  
**First Seen:** 2025-01-13  
**Last Updated:** 2025-01-15  
**Total Occurrences:** 6

### Fix 1: Use pathlib.Path (Success Count: 6)

**Code:**
```python
# Before
with open('/data/file.json', 'r') as f:

# After
from pathlib import Path
file_path = Path('data') / 'file.json'
with open(file_path, 'r', encoding='utf-8') as f:
```

**Why this works:** `pathlib.Path` provides cross-platform path handling, avoiding Windows/Unix path format issues.

**When to use:** Always for file paths to ensure cross-platform compatibility.

**Projects:** All projects (6 projects)

---
```

### File Format: `.errors_fixes/coding_tips.md`

**Purpose**: **Agent process and workflow rules**. How the agent should behave (paths, commands, Docker, conventions) to avoid causing errors or workflow failures. Built only from **`### Agent Process Issue:`** entries. Use **proactively** before and during coding.

```markdown
# Coding Tips - Agent Process Rules

> **Last Updated:** 2025-01-16T02:00:00Z  
> **Total Rules:** 23

---

## Path Handling

### Rule: Always use pathlib.Path for file paths

**Why:** Unix-style paths (`/path/to/file`) fail on Windows. `pathlib.Path` ensures cross-platform compatibility.

**Examples:**
- ✅ `Path('data') / 'file.json'`
- ✅ `os.path.join('data', 'file.json')`
- ❌ `'/data/file.json'` (Unix-only, fails on Windows)

**Related Errors:**
- `FileNotFoundError: [WinError 2]` (6 occurrences)
- `FileNotFoundError: [Errno 2]` (3 occurrences)

---

## Command Format

### Rule: Use `task test` not `task test --all` in this project

**Why:** The `--all` flag doesn't exist in this project's taskipy configuration. Using it causes command failures.

**Examples:**
- ✅ `task test` (runs surgical tests for modified files)
- ✅ `task test --all` (if flag exists in project)
- ❌ `task test --all` (when flag doesn't exist)

**Related Errors:**
- Command execution failures (2 occurrences)

---

## String Formatting

### Rule: Prefer f-strings for string formatting

**Why:** F-strings automatically handle type conversion, avoiding TypeError when concatenating strings with non-strings.

**Examples:**
- ✅ `f"Total: {total}"` (automatic type conversion)
- ✅ `"Total: " + str(total)` (explicit conversion, Python < 3.6)
- ❌ `"Total: " + total` (TypeError if total is not string)

**Related Errors:**
- `TypeError: can only concatenate str (not "int") to str` (15 occurrences)

---

## Docker Networking

### Rule: Use Docker service names, not 'localhost' in containers

**Why:** Inside Docker containers, 'localhost' refers to the container itself, not the host machine or other services.

**Examples:**
- ✅ `db_host = 'postgres'` (service name from docker-compose)
- ✅ `db_host = os.getenv('DB_HOST', 'postgres')` (configurable)
- ❌ `db_host = 'localhost'` (refers to container, not service)

**Related Errors:**
- `ConnectionRefusedError: [Errno 111]` (8 occurrences)

---
```

---

## Workflow

### Development Session Workflow

#### Default Workflow: Manual Test Execution

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Agent writes code                                        │
│    - Agent generates corresponding tests automatically      │
│    - Agent advises which test commands to run               │
│      (task test:backend, task test:frontend,                │
│       task test:integration)                                 │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. User reviews code and tests                              │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. User runs advised test command (e.g., `task test:backend`)│
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. If tests fail:                                           │
│    - User provides error output to agent                   │
│    - Agent checks lookup order (see Lookup order in Agent Rules) │
│    - Agent applies fix (tries fixes in order of success)    │
│    - Agent documents in .errors_fixes/errors_and_fixes.md   │
│    - User runs test command again                           │
│                                                              │
│    If tests pass:                                           │
│    - Agent documents success in .errors_fixes/              │
│      errors_and_fixes.md                                    │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Continue development...                                 │
└─────────────────────────────────────────────────────────────┘
```

#### Optional Workflow: Command-Based Auto-Fix

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Agent writes code                                        │
│    - Agent generates corresponding tests automatically      │
│    - Agent advises which test commands to run               │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. User reviews code and tests                              │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. User runs `.cursor/command test-and-fix` (global command)│
│    (or specific test command: test-and-fix:backend, etc.)   │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Agent runs appropriate test command automatically        │
│    (task test:backend, task test:frontend, or task test)    │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. If tests fail:                                           │
│    - Agent parses errors from test output                   │
│    - Agent checks lookup order (see Lookup order in Agent Rules) │
│    - Agent applies fixes for ALL errors                     │
│    - Agent documents all fixes in .errors_fixes/            │
│      errors_and_fixes.md                                    │
│    - Agent runs test command again                           │
│    - Repeats until all pass OR max iterations (5)          │
│                                                              │
│    If tests pass:                                           │
│    - Agent reports success                                  │
│    - Agent documents in .errors_fixes/errors_and_fixes.md   │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. User reviews final result                                │
└─────────────────────────────────────────────────────────────┘
```

**Note**: The command-based workflow is optional. The default is manual test execution for safety and user control.

### Daily Consolidation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Daily at 2 AM: Consolidation App Triggered                 │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. Discover all projects (scan for .errors_fixes/          │
│    errors_and_fixes.md)                                     │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Read all .errors_fixes/errors_and_fixes.md files        │
│    - Parse both `### Error:` and `### Agent Process Issue:` │
│    - Tag each: is_process_issue (→ coding_tips) or not      │
│      (→ fix_repo)                                           │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. AI Deduplication (for fix_repo only)                     │
│    - For each `### Error:` entry only (exclude Agent        │
│      Process Issue):                                        │
│      a. Use LLM to find semantically similar errors         │
│      b. Calculate similarity score (threshold: 0.85)        │
│      c. If similar: merge into existing entry               │
│      d. If new: create new entry                            │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. AI Tagging (for fix_repo only)                           │
│    - For each `### Error:` entry only:                      │
│      a. Use LLM to generate context tags                   │
│      b. Extract error type, framework, domain tags         │
│      c. Add tags to entry metadata                          │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Fix Merging & Ordering (→ fix_repo.md)                   │
│    - For each `### Error:` entry only:                      │
│      a. Group fixes by similarity                           │
│      b. If same fix: increment success count                │
│      c. If different fix: add as variant with explanation   │
│      d. Sort fixes by success count (highest first)         │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Process Rules Extraction (→ coding_tips.md only)         │
│    - From `### Agent Process Issue:` entries only           │
│    - Extract agent process/workflow rules and examples      │
│    - Generate .errors_fixes/coding_tips.md                  │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Write Consolidated Files                                │
│    - Write .errors_fixes/fix_repo.md to each project        │
│    - Write .errors_fixes/coding_tips.md to each project     │
│    - Clear contents of .errors_fixes/errors_and_fixes.md    │
│      (keep file, just clear contents)                        │
└─────────────────────────────────────────────────────────────┘
```

**Important**: After successful consolidation, the consolidation app **clears the contents** of `errors_and_fixes.md` but **keeps the file**. This ensures:
- The file exists for the next session
- No data loss if consolidation fails
- Clean slate for next development session

---

## Test Execution Strategy

### Overview

The Simplified Error Registry uses a **hybrid approach** to test execution that balances user control with agent autonomy:

- **Default (Manual)**: Agent writes code, user runs tests, user provides errors
- **Optional (Command-Based)**: User triggers auto-fix cycle, agent runs tests and fixes all errors

This approach provides safety, efficiency, and flexibility while integrating seamlessly with the Simplified Error Registry pipeline.

---

### Approach 1: Manual Test Execution (Default)

**Workflow**: Agent writes code → User runs tests → User provides errors → Agent fixes

#### When to Use
- Default for all code changes
- When you want to review code before testing
- For long-running test suites
- When you want full control over the testing process

#### Pros
- ✅ **User Control**: You decide when to test
- ✅ **Lower Token Usage**: Agent doesn't consume tokens on test runs
- ✅ **Safety**: No accidental test runs on broken code
- ✅ **Clear Separation**: Agent writes code, you validate
- ✅ **Better for Long Tests**: You can run in background
- ✅ **Code Review**: Review code before testing

#### Cons
- ❌ **Slower Feedback Loop**: Requires your action
- ❌ **More Manual Steps**: You must run tests and paste errors
- ❌ **Potential for Missed Errors**: You might forget to test
- ❌ **Less Autonomous**: Agent can't iterate independently
- ❌ **Inefficient for Quick Fixes**: Multiple back-and-forth cycles

#### Simplified Error Registry Integration
- Agent documents in `.errors_fixes/errors_and_fixes.md` after you report results
- Works well with "Responder" pattern
- You control when errors enter the pipeline

---

### Approach 2: Automatic Test Execution (Excluded)

**Workflow**: Agent writes code → Agent runs tests automatically → Agent fixes errors → Repeats until all pass

**Why excluded:** High token usage, safety risk (destructive tests, no user approval), infinite-loop risk. Not supported in the Simplified Error Registry design.

---

### Approach 3: Command-Based Test Execution (Optional Enhancement)

**Workflow**: Agent writes code → User reviews → User runs `.cursor/command test-and-fix` → Agent runs tests and fixes all errors → User reviews final result

#### When to Use
- After major refactoring
- When you want agent to fix all errors at once
- When you're confident in the code but expect multiple errors
- For comprehensive error fixing sessions

#### Pros
- ✅ **User Control**: You decide when to start test cycle
- ✅ **Autonomous Fix Loop**: Once started, agent fixes all errors
- ✅ **Efficient**: Agent handles multiple errors in one session
- ✅ **Safety**: You review code before starting test cycle
- ✅ **Lower Token Usage**: Only runs when you request it
- ✅ **Better Error Documentation**: Agent documents all fixes comprehensively
- ✅ **Clear Workflow**: Explicit "test and fix" command

#### Cons
- ⚠️ **Requires Command Setup**: Need to create `.cursor/command`
- ⚠️ **Still Requires User Action**: Not fully automatic
- ⚠️ **Potential for Long Sessions**: Agent might take time to fix all errors
- ⚠️ **Less Granular Control**: Can't easily stop mid-cycle
- ⚠️ **Token Usage**: Can be high if many errors need fixing

#### Simplified Error Registry Integration
- ✅ **Excellent Fit**: Agent documents all errors/fixes in one session
- ✅ **Comprehensive Updates**: Can update `.errors_fixes/errors_and_fixes.md` with all fixes
- ✅ **Natural Workflow**: You trigger → Agent fixes → Documents → You review

---

### Recommended Implementation: Hybrid Approach

**Default**: Use Approach 1 (Manual) for all code changes  
**Optional**: Use Approach 3 (Command-Based) when you want comprehensive auto-fixing

#### Implementation Structure

```
project_root/
├── .errors_fixes/              # Error registry system
├── .cursor/
│   ├── rules/
│   │   └── global/
│   │       └── errors.mdc     # Global agent rules (updated with hybrid approach)
│   └── commands/
│       └── global/
│           └── test-and-fix.mdc # Optional global command for auto-fix
└── (application code)
```

#### Command File: `.cursor/commands/global/test-and-fix.mdc`

**Full content:** See **Appendix E**. Safety limits: 5 iterations, 3 same-error retries. When to use: Approach 3 and Comparison Summary below.

---

### Comparison Summary

| Aspect | Manual (Default) | Command-Based (Optional) |
|--------|------------------|--------------------------|
| **User Control** | ✅ High | ✅ Medium (you trigger) |
| **Token Usage** | ✅ Low | ⚠️ Medium (only when triggered) |
| **Feedback Speed** | ⚠️ Depends on you | ✅ Fast (after trigger) |
| **Autonomy** | ❌ Low | ✅ High (after trigger) |
| **Safety** | ✅ High | ✅ High (you review first) |
| **Error Documentation** | ⚠️ One at a time | ✅ Comprehensive |
| **Multiple Errors** | ❌ One at a time | ✅ All at once |
| **Best For** | Daily development | Major refactoring, comprehensive fixes |

---

## Consolidation App Design

### Architecture

```python
# consolidation_app/
# ├── main.py                 # Entry point, scheduler
# ├── discovery.py            # Find all projects
# ├── parser.py                # Parse markdown files
# ├── deduplicator.py         # AI-based deduplication
# ├── tagger.py                # AI-based tagging
# ├── merger.py               # Merge fixes and order by success
# ├── rule_extractor.py        # Extract process rules
# ├── writer.py               # Write consolidated files
# ├── config.py               # Configuration
# └── requirements.txt        # Dependencies
```

### Core Components

#### 1. Discovery Module

```python
def discover_projects(root_path: Path, extra_projects: list[str] | None = None) -> list[Path]:
    """Find projects: rglob for .errors_fixes/errors_and_fixes.md; add extra_projects with auto-bootstrap when missing."""
    projects = []
    for path in root_path.rglob(".errors_fixes/errors_and_fixes.md"):
        projects.append(path.parent.parent)
    for p in extra_projects or []:
        project_root = Path(p).resolve()
        ef_md = project_root / ".errors_fixes" / "errors_and_fixes.md"
        if not ef_md.exists():
            bootstrap(project_root, update_gitignore=False)  # Phase 1 script
        projects.append(project_root)
    return list(dict.fromkeys(projects))
```

#### 2. Parser Module

`parse_errors_and_fixes(file_path) → List[ErrorEntry]`. Fields: error_signature, error_type, file, line, fix_code, explanation, result, success_count, tags, timestamp, is_process_issue. Regex-based for v1; see Appendix A. For complex nesting, consider a markdown parser later.

#### 3. Deduplicator Module (AI-Powered)

`deduplicate_errors(new_entries, existing_entries, similarity_threshold=0.85) → List[ErrorEntry]`. For each new entry, LLM similarity vs existing; if ≥ threshold merge else append. Phase 3 uses exact match only; AI in Phase 4. Full LLM prompts: Appendix B.

#### 4. Tagger Module (AI-Powered)

`generate_tags(entry) → List[str]`. LLM generates 3–5 context tags (error type, framework, domain, platform). Phase 3 uses rule-based tagging; AI in Phase 4. Full LLM prompts: Appendix B.

#### 5. Merger Module

```python
def merge_fixes(entry: ErrorEntry) -> ErrorEntry:
    """
    Merge multiple fixes for the same error, order by success count
    
    Strategy:
    1. Group fixes by code similarity (fuzzy match)
    2. If same fix: increment success_count
    3. If different fix: add as variant with explanation
    4. Sort all fixes by success_count (highest first)
    """
    # Group fixes by similarity
    fix_groups = group_similar_fixes(entry.fixes)
    
    merged_fixes = []
    for group in fix_groups:
        if len(group) == 1:
            # Unique fix
            merged_fixes.append(group[0])
        else:
            # Same fix, multiple occurrences
            total_success = sum(f.success_count for f in group)
            merged_fix = group[0]
            merged_fix.success_count = total_success
            merged_fixes.append(merged_fix)
    
    # Sort by success count
    merged_fixes.sort(key=lambda f: f.success_count, reverse=True)
    entry.fixes = merged_fixes
    
    return entry
```

#### 6. Rule Extractor Module

`extract_process_rules(entries) → List[ProcessRule]`. From `is_process_issue=True` only. LLM extracts rules (statement, why, examples ✅/❌, related_errors). Full LLM prompts: Appendix B.

#### 7. Writer Module

```python
def write_fix_repo(project_path: Path, consolidated_entries: List[ErrorEntry]):
    """Write consolidated fix_repo.md to project"""
    errors_fixes_dir = project_path / '.errors_fixes'
    errors_fixes_dir.mkdir(exist_ok=True)
    
    content = generate_fix_repo_markdown(consolidated_entries)
    file_path = errors_fixes_dir / 'fix_repo.md'
    file_path.write_text(content, encoding='utf-8')

def write_coding_tips(project_path: Path, rules: List[ProcessRule]):
    """Write coding_tips.md to project"""
    errors_fixes_dir = project_path / '.errors_fixes'
    errors_fixes_dir.mkdir(exist_ok=True)
    
    content = generate_coding_tips_markdown(rules)
    file_path = errors_fixes_dir / 'coding_tips.md'
    file_path.write_text(content, encoding='utf-8')

def clear_errors_and_fixes(project_path: Path):
    """
    Clear contents of errors_and_fixes.md after successful consolidation.
    Keep the file but reset to empty header.
    """
    errors_fixes_dir = project_path / '.errors_fixes'
    file_path = errors_fixes_dir / 'errors_and_fixes.md'
    
    # Reset to header only
    header = """# Errors and Fixes Log

> **Note**: This file is processed daily by the consolidation app at 2 AM.
> `### Error:` entries → fix_repo.md; `### Agent Process Issue:` entries → coding_tips.md. Contents are then cleared (file is kept).

"""
    file_path.write_text(header, encoding='utf-8')
```

### Docker Container Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV LLM_MODEL=ollama/qwen2.5-coder:14b
ENV CONSOLIDATION_SCHEDULE="0 2 * * *"  # 2 AM daily
ENV PROJECTS_ROOT=/projects
ENV SIMILARITY_THRESHOLD=0.85

# Run scheduler
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  consolidation-app:
    build: .
    volumes:
      - /path/to/projects:/projects:rw  # Read-write access to update files
    environment:
      - LLM_MODEL=ollama/qwen2.5-coder:14b
      - CONSOLIDATION_SCHEDULE="0 2 * * *"
      - PROJECTS_ROOT=/projects
    depends_on:
      - ollama
    
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

volumes:
  ollama_data:
```

---

## Agent Rules & Integration

### ⚠️ Critical: Careful Crafting Required

The `.cursor/rules/global/errors.mdc` rule is **critical** for the Simplified Error Registry system. It must be carefully crafted to:

1. **Avoid Token Bloat**: Do NOT use `alwaysApply: true` - this would load the rule into every prompt, causing unnecessary token usage
2. **Ensure Proper Triggering**: The frontmatter `description` field must accurately describe when the rule should be applied
3. **Match User Language**: The description should match common phrases users use when reporting errors

**Trigger Scenarios** (description should match these):
- User pastes errors from `task test:backend`, `task test:frontend`, `task test:integration` commands
- User says "There is an error in..." or "I'm getting an error..."
- User provides test failure output or stack traces
- User asks to "fix this error" or "resolve this test failure"

**Example Good Description**:
```yaml
description: Error resolution protocol using Simplified Error Registry. Apply when user pastes test errors from "task test:*" commands, reports "There is an error in...", provides test failure output, or requests error fixes. Check .errors_fixes/ files for fixes before attempting solutions.
```

**Example Bad Description** (too vague):
```yaml
description: Error handling
```

**Example Bad Description** (too broad):
```yaml
description: All coding tasks
```

### Ensuring Agent References `coding_tips.md`

**Critical**: The agent must proactively reference `.errors_fixes/coding_tips.md` to avoid common workflow issues, not just when errors occur. Several approaches are available:

#### Option 1: Enhanced Reference in `errors.mdc` (Recommended)

**Approach**: Add explicit proactive steps to the `errors.mdc` rule that instruct the agent to check `coding_tips.md` before starting work.

**Pros**:
- ✅ Single rule file to maintain
- ✅ Contextual - only loaded when errors occur
- ✅ No token bloat (only loaded when needed)

**Cons**:
- ⚠️ Only applies during error resolution workflows
- ⚠️ May miss proactive prevention opportunities

**Implementation**: Add a "Preventive Check" section to `errors.mdc`:
```markdown
## Preventive Checks

Before writing code or making changes, check `.errors_fixes/coding_tips.md` for:
- Path handling rules (use `pathlib.Path`)
- Command format rules (check taskipy config)
- String formatting best practices
- Docker networking rules
- Any other process rules that might prevent errors

Apply these rules proactively to avoid common mistakes.
```

#### Option 2: Separate `coding-tips.mdc` Rule File (Recommended for Proactive Use)

**Approach**: Create a dedicated `.cursor/rules/global/coding-tips.mdc` rule with `alwaysApply: false` and a description that triggers during code writing.

**Pros**:
- ✅ Separate concerns (error fixing vs. proactive prevention)
- ✅ Can be triggered independently
- ✅ More granular control over when it applies

**Cons**:
- ⚠️ Requires careful description crafting (like `errors.mdc`)
- ⚠️ Two files to maintain

**Implementation**:
```markdown
---
description: Agent process rules and workflow guidelines from Simplified Error Registry. Apply when writing code, creating files, using file paths, running commands, or working with Docker. Check .errors_fixes/coding_tips.md for specific rules before coding.
---

# Coding Tips Reference

Before writing code, always check `.errors_fixes/coding_tips.md` for:
- Path handling rules
- Command format requirements
- String formatting best practices
- Docker networking rules
- Any other process rules

These rules prevent common agent workflow issues and should be applied proactively.
```

**Alternatives:** Add to rules.mdc, User Rules, or docs-only — not recommended for reliability.

#### Recommended Approach: Hybrid (Options 1 + 2)

**Best Practice**: Use both approaches for maximum coverage:

1. **Enhanced `errors.mdc`**: Include proactive checks in the error resolution workflow
2. **Separate `coding-tips.mdc`**: Create a dedicated rule with a description that triggers during code writing tasks

**Why This Works**:
- `errors.mdc` ensures `coding_tips.md` is checked during error resolution
- `coding-tips.mdc` ensures `coding_tips.md` is checked proactively before errors occur
- Both use carefully crafted descriptions (no `alwaysApply: true`) to avoid token bloat
- Provides comprehensive coverage without redundancy

**Implementation Checklist**:
- [ ] Add "Preventive Checks" section to `errors.mdc`
- [ ] Create `.cursor/rules/global/coding-tips.mdc` with precise description
- [ ] Test that `coding-tips.mdc` triggers when user says "write code", "create file", "use file path", etc.
- [ ] Verify both rules reference `.errors_fixes/coding_tips.md` correctly
- [ ] Document the dual-rule approach in project setup

---

### Why `.cursor/rules/global/errors.mdc` Instead of `AGENTS.md`

**Recommendation**: Use `.cursor/rules/global/errors.mdc` with a carefully crafted frontmatter description (NOT `alwaysApply: true`) to avoid token bloat while ensuring it's triggered during error fix workflows.

(See the **Critical callout** immediately before the errors.mdc template below.)

**Comparison**:

| Feature | `.cursor/rules/global/errors.mdc` | `AGENTS.md` |
|---------|----------------------------------|-------------|
| **Reliability** | ✅ High (metadata control) | ⚠️ Medium (simple markdown) |
| **Token Efficiency** | ✅ Conditional (triggered by description) | ⚠️ Always loaded |
| **Metadata** | ✅ Full control (description, globs) | ❌ No metadata |
| **Version Control** | ✅ Yes (in `.cursor/rules/global/`) | ✅ Yes (project root) |
| **Global Sharing** | ✅ Automatically copied to all repos | ❌ Project-specific only |
| **Complexity** | Medium (MDC format) | Low (plain markdown) |
| **Crafting Required** | ⚠️ **Critical** - Description must be precise | ❌ Not applicable |

**Conclusion**: For critical error resolution workflows, `.cursor/rules/global/errors.mdc` with a carefully crafted frontmatter description ensures the agent follows the protocol when errors occur, without token bloat. The global location means it's automatically available in all projects. **The frontmatter description is critical** - it must accurately describe when this rule should be applied.

### Updated `.cursor/rules/global/errors.mdc`

**⚠️ CRITICAL**: This rule requires careful crafting of the frontmatter description. Do NOT use `alwaysApply: true` as it causes token bloat. Instead, craft a precise description that triggers the rule when:
- User pastes errors from `task test:*` commands
- User says "There is an error in..." or similar error-related phrases
- User provides test failure output
- User asks to fix errors or test failures

```markdown
---
description: Error resolution protocol using Simplified Error Registry. Apply when user pastes test errors from "task test:*" commands, reports "There is an error in...", provides test failure output, or requests error fixes. Check .errors_fixes/ files for fixes before attempting solutions.
---

# Error Resolution Protocol (Simplified)

## Role

You are a **Responder**. The User runs the tests; you provide the code.

---

## Test Generation Requirements

### Generate Tests for New Code

**CRITICAL**: When you create or modify code, you MUST also generate corresponding tests.

1. **For New Files**:
   - Create corresponding test file(s) in the appropriate test directory
   - For `src/backend/api.py` → Create `tests/test_api.py` or `tests/backend/test_api.py`
   - For `src/frontend/components/Button.tsx` → Create `tests/frontend/components/Button.test.tsx`
   - For integration code → Create `tests/integration/test_<feature>.py`

2. **For Modified Files**:
   - Check if test file exists
   - If missing: Create test file
   - If exists: Update test file to cover new functionality

3. **Test Coverage Requirements**:
   - **Unit Tests**: Test individual functions/methods
   - **Integration Tests**: Test component interactions (place in `tests/integration/`)
   - **Coverage**: Happy path, edge cases (None/Empty inputs), and mocked external calls

4. **Test File Naming**:
   - Python: `test_<module_name>.py` (mirrors source structure)
   - TypeScript/JavaScript: `<component>.test.tsx` or `<component>.test.ts`
   - Integration: `tests/integration/test_<feature>.py`

### Advise Test Commands After Code Generation

**After generating or modifying code**, you MUST advise the user which tests to run:

1. **Identify Code Type**:
   - Backend code (Python, APIs, services) → Advise: `task test:backend` or `task test` (if backend-only project)
   - Frontend code (React, Vue, TypeScript UI) → Advise: `task test:frontend`
   - Integration code (cross-component, end-to-end) → Advise: `task test:integration`
   - Mixed changes → Advise: Run all relevant test suites

2. **Format of Advice**:
   ```
   **Next Steps:**
   - Run tests: `task test:backend` (for backend changes)
   - Run tests: `task test:frontend` (for frontend changes)
   - Run tests: `task test:integration` (for integration changes)
   - Or run all: `task test` (if project supports unified test command)
   ```

3. **When to Advise**:
   - After creating new files
   - After modifying existing files
   - After refactoring code
   - After fixing errors (advise re-running tests)

**Example**:
```
I've created the new payment processing module at `src/payment.py` and corresponding tests at `tests/test_payment.py`.

**Next Steps:**
- Run backend tests: `task test:backend`
- The tests cover happy path, edge cases, and mocked external API calls.
```

---

## Test Execution Strategy

### Default Behavior: Manual Test Execution

**Do NOT run tests automatically after code changes.**

- Write code
- Wait for user to run `task test`
- Wait for user to provide error output if tests fail
- This gives user control and reduces token usage

### Optional: Command-Based Auto-Fix

**If user runs `.cursor/command test-and-fix` (from global commands):**

1. Run `task test` automatically
2. If tests pass:
   - Inform user: "All tests passed! ✅"
   - Document success in `.errors_fixes/errors_and_fixes.md` (if any fixes were applied)
   - Stop execution

3. If tests fail:
   - Parse errors from test output
   - Fix all errors using Simplified Error Registry pipeline (see Fix Loop below)
   - Document all fixes in `.errors_fixes/errors_and_fixes.md`
   - Run `task test` again
   - Repeat until all tests pass OR max iterations (5) reached
   - Report final status to user

### Fix Loop (Command-Based Mode)

**Maximum 5 iterations per command:**

1. For each error found:
   - Check `.errors_fixes/errors_and_fixes.md` for recent session errors
   - Check `.errors_fixes/fix_repo.md` for consolidated fixes
   - Check `.errors_fixes/coding_tips.md` for agent process rules
   - Apply fix with highest success count
   - Document attempt in `.errors_fixes/errors_and_fixes.md`

2. Run `task test` again

3. Stop conditions:
   - All tests pass → Report success
   - Same error repeats 3 times → Stop and report to user
   - Maximum iterations (5) reached → Stop and report status
   - New errors appear → Continue fixing

---

## Lookup Strategy

**fix_repo.md** — Use when you have a **runtime or test error** to fix: look up the error type/message and apply the suggested code fix(es) in order of success count.

**coding_tips.md** — Use **before and during coding** for **process and workflow rules** (paths, commands, Docker, project-specific behavior) so you don’t cause those errors or workflow failures.

When an error occurs, check in this order:

1. **First**: Check `.errors_fixes/errors_and_fixes.md` for recent session errors
   - Look for the same or similar error in today's session
   - If found, check if a fix was already attempted

2. **Second**: Check `.errors_fixes/fix_repo.md` for consolidated **code fixes**
   - Use when you have a runtime/test error. Search by error type or tags
   - Try fixes in order of success count (highest first)
   - If first fix fails, try the next one

3. **Third**: Check `.errors_fixes/coding_tips.md` for **agent process rules**
   - Process/workflow rules: paths, commands, Docker, conventions
   - Check proactively before coding to avoid causing errors

---

## Fix Application Workflow

### Step 1: Identify Error

**Manual Mode**: Wait for the user to provide the error log. Do not guess the error.

**Command Mode**: Parse errors from `task test` output automatically.

### Step 2: Lookup Fixes

1. Check `.errors_fixes/errors_and_fixes.md` for recent attempts
2. Check `.errors_fixes/fix_repo.md` for consolidated fixes
3. Check `.errors_fixes/coding_tips.md` for process rules

### Step 3: Apply Fix

- If fix found: Apply the fix with highest success count
- If multiple fixes: Try them in order (highest success count first)
- If no fix found: Analyze error and create new fix

### Step 4: Document Result

**Manual Mode** (after user runs tests):

**If test passes:**
- Document in `.errors_fixes/errors_and_fixes.md`:
  - Error signature
  - Fix applied
  - Result: ✅ Solved
  - Success count: 1 (or increment if same fix)

**If test fails:**
- Document in `.errors_fixes/errors_and_fixes.md`:
  - Error signature
  - Fix attempted
  - Result: ❌ Failed
  - Try next fix from `fix_repo.md` (if available)

**Command Mode** (automatic):
- Document each fix attempt in `.errors_fixes/errors_and_fixes.md` immediately
- Continue fixing until all pass or limits reached
- Report final summary to user

### Step 5: Advise Test Commands

**After generating or modifying code**, always advise the user which tests to run:

- **Backend changes** → Advise: `task test:backend` or `task test` (if backend-only)
- **Frontend changes** → Advise: `task test:frontend`
- **Integration changes** → Advise: `task test:integration`
- **Mixed changes** → Advise: Run all relevant test suites

**Format**:
```
**Next Steps:**
- Run tests: `task test:backend` (for the new API endpoint)
- Run tests: `task test:frontend` (for the React component changes)
- Run tests: `task test:integration` (for the end-to-end workflow)
```

### Step 6: Session Tracking

Track attempted fixes in current session to avoid immediate retries:
- If fix failed in this session, try next fix
- Don't retry same fix in same session unless explicitly requested
- In command mode: Stop if same error repeats 3 times

---

## Process Rules

**CRITICAL**: Always check and follow rules in `.errors_fixes/coding_tips.md` before writing code or making changes.

**Proactive Prevention**:
- Before writing code: Check `.errors_fixes/coding_tips.md` for relevant process rules
- Before using file paths: Review path handling rules
- Before running commands: Check command format rules
- Before Docker work: Review Docker networking rules

**Common Rules** (check `coding_tips.md` for current list):
- Use `pathlib.Path` for file paths (cross-platform)
- Use correct command formats (check project's taskipy config)
- Follow string formatting best practices
- Use Docker service names in containers

**Note**: See "Ensuring Agent References `coding_tips.md`" section above for options on how to ensure the agent proactively references this file.

---

## Validation

### Manual Mode (Default)
Do not run tests yourself. Ask the user to run `task test` after applying fixes.

### Command Mode (When User Runs test-and-fix)
You may run `task test` automatically when user triggers the command. Follow the Fix Loop workflow with safety limits (max 5 iterations, stop if same error repeats 3 times).
```

---

## Portability & Setup

### Self-Contained System

The `.errors_fixes/` folder is **self-contained and portable**. To set up the system in a new project:

1. **Copy the folder**: Copy `.errors_fixes/` from an existing project to the new project root
2. **Global rules/commands**: The `.cursor/rules/global/errors.mdc` and `.cursor/commands/global/test-and-fix.mdc` files are automatically available in all repositories (no copying needed)
3. **Update `.gitignore`**: Add `.errors_fixes/` to `.gitignore`

### Setup Steps

```bash
# 1. Copy .errors_fixes folder from template project
cp -r /path/to/template/.errors_fixes /path/to/new/project/

# 2. Add to .gitignore
echo ".errors_fixes/" >> /path/to/new/project/.gitignore

# Note: Global rules and commands are automatically available
# No need to copy .cursor/rules/global/errors.mdc or .cursor/commands/global/test-and-fix.mdc
# They are shared across all repositories via the global Cursor setup
```

### Folder Contents

The `.errors_fixes/` folder should contain:

```
.errors_fixes/
├── errors_and_fixes.md    # Session log (created/cleared by agent and consolidation app)
├── fix_repo.md            # Consolidated fixes (created/updated by consolidation app)
├── coding_tips.md         # Agent process rules (created/updated by consolidation app)
└── README.md              # Optional: Quick reference (can be included in template)
```

### Initial State

When copying to a new project, the folder should have:

- **`errors_and_fixes.md`**: Empty or with header only
- **`fix_repo.md`**: Empty or with header only (will be populated by consolidation app)
- **`coding_tips.md`**: Empty or with header only (will be populated by consolidation app)
- **`README.md`**: Optional documentation

### Consolidation App Discovery

The consolidation app discovers projects via `discover_projects(root_path, extra_projects)` — see **Consolidation App Design, Discovery module** for the implementation. **rglob:** only projects with `.errors_fixes/errors_and_fixes.md`. **extra_projects** (optional config): paths outside `projects_root`; auto-bootstrap only for those when `errors_and_fixes.md` is missing.

### Including a New Project in the Read/Write Pipeline

For a new project to participate in the pipeline, two conditions must be met:

1. **Under the scan root**: The project directory must live under `projects_root` (the path the consolidation app scans, e.g. `PROJECTS_ROOT` / `consolidation.projects_root`). In Docker, that is the host folder mounted at `/projects` (or the configured root).
2. **Discovery marker exists**: `discover_projects()` uses `rglob('.errors_fixes/errors_and_fixes.md')` — that file must exist or the project is not discovered. The writer creates `fix_repo.md` and `coding_tips.md` as needed; it does **not** create `errors_and_fixes.md`, so that file must be bootstrapped.

**Ways to onboard a new project:**

| Method | When to use |
|--------|-------------|
| **A. Manual copy** | One-off; you have a template project with `.errors_fixes/` already set up. |
| **B. Bootstrap script** | Reproducible; you run a small Python script per new project. |
| **C. Config project list + auto-bootstrap** | Projects live outside `projects_root`, or you want to explicitly register new projects without moving them. |
| **D. Symlink-based central output** | *(For discussion)* Single consolidated output in the error-registry repo; each project symlinks to it. See below. |

#### A. Manual copy (current)

```bash
# 1. Ensure new project is under projects_root (or add its parent to the consolidation mount)
# 2. Copy from a template that already has .errors_fixes/
cp -r /path/to/template/.errors_fixes /path/to/new/project/

# 3. Add to .gitignore
echo ".errors_fixes/" >> /path/to/new/project/.gitignore
```

On the next consolidation run, the app discovers the project, reads `errors_and_fixes.md` (empty is fine), and writes `fix_repo.md` and `coding_tips.md` (creating them if missing).

#### B. Bootstrap script

Run `scripts/bootstrap_errors_fixes.py /path/to/new/project`. The script is a **Phase 1 deliverable**; it creates `.errors_fixes/`, `errors_and_fixes.md` with header, stubs for `fix_repo.md` and `coding_tips.md`, and optionally updates `.gitignore` (see .gitignore note in File Structure). Ensure the new project is under `projects_root`; the next consolidation run will discover and process it.

#### C. Config project list + auto-bootstrap in discovery (optional)

For projects outside `projects_root` or for explicit registration, set `consolidation.projects` in optional YAML (or equivalent). Pass it as `extra_projects` to `discover_projects(root_path, extra_projects=...)`. Discovery calls `bootstrap(project_root, update_gitignore=False)` when `errors_and_fixes.md` is missing for an extra path. To include a new project: add its path to `consolidation.projects`; on the next run it is bootstrapped if needed, then read and written as usual.

#### D. Symlink-based central output (for discussion)

An alternative architecture to discuss: **read** `errors_and_fixes.md` from each project as today, but **write** `fix_repo.md` and `coding_tips.md` only inside the error-registry (consolidation) repo; each project then has a **symlink** from `.errors_fixes/fix_repo.md` and `.errors_fixes/coding_tips.md` to those central files.

**Flow:**
- **Read**: Consolidation app discovers projects via `rglob('.errors_fixes/errors_and_fixes.md')` and reads each `errors_and_fixes.md` (unchanged).
- **Write**: It writes a single `fix_repo.md` and a single `coding_tips.md` in the error-registry repo (e.g. `consolidation_app/output/fix_repo.md`, `consolidation_app/output/coding_tips.md`, or a dedicated `ger_output/` directory).
- **Per project**: `.errors_fixes/fix_repo.md` and `.errors_fixes/coding_tips.md` are symlinks pointing at those central files. The bootstrap (or installer) would create the symlinks instead of empty files.

**Pros (to discuss):**
- One source of truth for consolidated fixes and coding tips; no per-project copies to keep in sync.
- Updates are instant for all projects (same file).
- Version control of `fix_repo.md` and `coding_tips.md` lives in one repo.

**Cons / open questions (to discuss):**
- Symlink support: Windows (e.g. `mklink` / developer mode), macOS/Linux, and network/shared drives can behave differently; need a cross-platform strategy or fallback (e.g. copy if symlink fails).
- Git and symlinks: some setups don’t commit or resolve symlinks the same way; `.errors_fixes/` is git-ignored in the current design, so this may be less of an issue if the symlink is only local.
- Paths: the symlink target must be a path that all projects can resolve (absolute, or relative if project locations relative to the central output are stable). A config like `central_output_dir` would be required.
- Bootstrap/onboarding: for a new project, the bootstrap script (or manual steps) must create the symlinks to the central output; the central output path needs to be configured or discoverable.

**Suggested next step:** Decide whether to support this as an optional mode (e.g. `consolidation.output_mode: "per_project" | "central_symlink"`) or to keep the current per-project write as the only mode for now, and document the symlink idea as a future option once the above points are resolved.

**v1:** Per-project write only; `central_symlink` deferred.

---

## Implementation Plan

### Phase 1: Core File Formats and Template (Week 1)

**Tasks:**
- [ ] Define markdown formats for all three files
- [ ] Create template `.errors_fixes/` folder structure
- [ ] Implement **bootstrap script** (`scripts/bootstrap_errors_fixes.py`): create `.errors_fixes/`, `errors_and_fixes.md` with header, optional stubs for `fix_repo.md` and `coding_tips.md`, update `.gitignore`
- [ ] Write parser for `errors_and_fixes.md`
- [ ] Write generator for `fix_repo.md`
- [ ] Write generator for `coding_tips.md`

**Deliverables:**
- Template `.errors_fixes/` folder
- `bootstrap_errors_fixes` script
- Parser module
- Generator modules
- Unit tests

### Phase 2: Agent Integration and Test Output Verification (Week 1-2)

**Tasks:**
- [ ] Create `.cursor/rules/global/errors.mdc` template (with hybrid test execution strategy). **CRITICAL** (see Critical callout before errors.mdc): craft precise frontmatter description (do NOT use `alwaysApply: true`); trigger on pasted test errors, "There is an error in...", test failure output; add "Preventive Checks" and "Lookup order"; verify trigger scenarios.
- [ ] **Create `.cursor/rules/global/coding-tips.mdc`** (Hybrid with errors.mdc): precise description; trigger on "write code", "create file", "use file path", "run command", "Docker"; reference `.errors_fixes/coding_tips.md`.
- [ ] **Test generation and advise-test-command:** As specified in errors.mdc. Verify test generation, test command advice, and safety limits (max iterations, retry limits).
- [ ] Create `.cursor/commands/global/test-and-fix.mdc` template (optional). See test-and-fix.mdc in Test Execution or Appendix.
- [ ] **Test output capture verification:** Inspect `task test:*` and scripts; ensure capture of `=== FAILURES ===`/`=== ERRORS ===` and `=== short test summary info ===`; document required sections; update scripts if needed.
- [ ] Test agent workflow end-to-end (both modes); document agent instructions.

**Deliverables:**
- Agent rules (errors.mdc, coding-tips.mdc); optional test-and-fix.mdc
- Verification results; docs for required test output sections
- Updated test output capture scripts (if needed)

### Phase 3: Consolidation App - Core (Week 2-3)

**Tasks:**
- [ ] Discovery: `discover_projects(root_path, extra_projects)` with **auto-bootstrap for extra_projects only** (call bootstrap when `errors_and_fixes.md` missing)
- [ ] Parser module
- [ ] **Basic deduplication (exact match only)**; AI dedup in Phase 4
- [ ] Basic tagging (rule-based)
- [ ] Writer module (write to `.errors_fixes/` folder)
- [ ] Clear contents of `errors_and_fixes.md` after consolidation

**Deliverables:**
- Core consolidation app
- Unit tests
- Integration tests

### Phase 4: Consolidation App - AI Integration (Week 3-4)

**Tasks:**
- [ ] LLM client integration
- [ ] AI deduplication module
- [ ] AI tagging module
- [ ] Fix merging logic
- [ ] **Rule extraction (Agent Process Issue entries only)**

**Deliverables:**
- AI-powered consolidation
- LLM prompt engineering
- Tests with mocked LLM

### Phase 5: Docker, Config, and Scheduling (Week 4)

**Tasks:**
- [ ] Docker container setup
- [ ] **Config: ENV-first** for Docker (`PROJECTS_ROOT`, `LLM_MODEL`, `CONSOLIDATION_SCHEDULE`, `SIMILARITY_THRESHOLD` in `environment:` or `env_file:`; no config file or mount required). **YAML optional** (`CONFIG_PATH` or default path) for `projects` list and advanced overrides; ENV overrides YAML when both exist.
- [ ] Cron scheduler integration
- [ ] Logging and monitoring

**Deliverables:**
- Dockerized app
- ENV docs (required vars); optional `consolidation_config.yaml` and override docs
- Scheduled execution

### Phase 6: Testing and Refinement (Week 5)

**Tasks:**
- [ ] End-to-end testing
- [ ] Performance testing (with realistic data)
- [ ] Refine AI prompts
- [ ] Optimize consolidation logic
- [ ] Documentation
- [ ] **Portability testing:** bootstrap on new project; run consolidation; verify `fix_repo.md` and `coding_tips.md` written

**Deliverables:**
- Test suite
- Performance benchmarks
- User documentation
- Portability guide

---

## Comparison with Current GER

### Feature Comparison

| Feature | Current GER | Simplified Approach | Winner |
|--------|-------------|---------------------|--------|
| **File Format** | JSON (structured) | Markdown (readable) | Simplified (for personal use) |
| **Deduplication** | Hash-based (exact) | AI-based (semantic) | Tie (different strengths) |
| **Query Performance** | Fast (hash lookup) | Linear search | Current GER (at scale) |
| **Negative Knowledge** | ✅ Tracked | ❌ Not tracked | Current GER |
| **Agent Process Issues** | ❌ Not tracked | ✅ Built-in | Simplified |
| **Success Count Ordering** | ✅ Implemented | ✅ Implemented | Tie |
| **Tagging** | Rule-based | AI-powered | Simplified |
| **Consolidation** | On-demand (`task sync`) | Daily batch | Current GER (immediate) |
| **Complexity** | High | Medium | Simplified |
| **Maintainability** | Requires JSON knowledge | Human-readable | Simplified |
| **Portability** | Requires installer script | ✅ Single folder copy | Simplified |
| **Scale** | Enterprise-ready | Personal use | Current GER (at scale) |

### When to Use Each Approach

**Use Current GER when:**
- Large team (10+ developers)
- High error volume (> 1000 entries)
- Need immediate consolidation
- Require exact hash matching
- Need negative knowledge tracking
- Enterprise deployment

**Use Simplified Approach when:**
- Personal projects
- Small team (1-5 developers)
- Moderate error volume (< 500 entries)
- Daily consolidation acceptable
- Prefer human-readable formats
- Want agent process tracking
- Need portability (copy folder to new project)
- Simpler maintenance preferred
- You want to try symlink-based central output later (design deferred)

---

## Migration Strategy

### From Current GER to Simplified Approach

#### Option 1: Gradual Migration

1. **Phase 1**: Run both systems in parallel
   - Keep `error_registry.json` for existing fixes
   - Start using `.errors_fixes/errors_and_fixes.md` for new fixes
   - Consolidation app reads both sources

2. **Phase 2**: Export existing data
   - Convert `error_registry.json` → `.errors_fixes/fix_repo.md`
   - Use consolidation app to format and tag

3. **Phase 3**: Switch fully
   - Update agent rules
   - Archive old JSON files
   - Use only markdown system

#### Option 2: Clean Slate

1. Archive current GER system
2. Start fresh with simplified approach
3. Re-consolidate historical data if needed

### Data Export Script

```python
def export_ger_to_markdown(ger_registry_path: Path, output_path: Path):
    """
    Export current GER error_registry.json to .errors_fixes/fix_repo.md format
    """
    with open(ger_registry_path, 'r') as f:
        registry = json.load(f)
    
    entries = []
    for entry in registry:
        markdown_entry = convert_to_markdown_entry(entry)
        entries.append(markdown_entry)
    
    content = generate_fix_repo_markdown(entries)
    output_path.write_text(content, encoding='utf-8')
```

---

## Conclusion

The Simplified Error Registry approach provides a streamlined, markdown-based solution optimized for personal-scale error tracking. Key advantages:

1. **Simplicity**: Human-readable markdown files
2. **Agent Process Tracking**: Built-in documentation of workflow issues
3. **AI-Powered**: Semantic deduplication and intelligent tagging
4. **Success-Based**: Clear ordering by fix success rates
5. **Maintainable**: Easy to read, edit, and understand
6. **Portable**: Single folder can be copied to any project
7. **Self-Contained**: All files in `.errors_fixes/` folder

This approach is ideal for personal projects where the complexity of the current GER system may be overkill, while still providing powerful error tracking and agent guidance capabilities.

---

## Appendix

### A. Markdown Parser Example

```python
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from pathlib import Path

@dataclass
class ErrorEntry:
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

def parse_errors_and_fixes(file_path: Path) -> List[ErrorEntry]:
    """Parse .errors_fixes/errors_and_fixes.md content"""
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8')
    entries = []
    
    # Split by error blocks (## Error: or ### Error:)
    error_blocks = re.split(r'^###? Error:', content, flags=re.MULTILINE)
    
    for block in error_blocks[1:]:  # Skip header
        entry = parse_error_block(block)
        if entry:
            entries.append(entry)
    
    return entries

def parse_error_block(block: str) -> Optional[ErrorEntry]:
    """Parse a single error block"""
    # Extract error signature from first line
    lines = block.strip().split('\n')
    error_signature = lines[0].strip()
    
    # Extract metadata (Timestamp, File, Line, etc.)
    metadata = {}
    for line in lines:
        if line.startswith('**Timestamp:**'):
            metadata['timestamp'] = parse_timestamp(line)
        elif line.startswith('**File:**'):
            metadata['file'] = extract_value(line)
        # ... etc
    
    # Extract fix code from code blocks
    fix_code = extract_code_block(block, 'Fix Applied')
    
    # Extract result
    result_match = re.search(r'\*\*Result:\*\* (✅|❌)', block)
    result = result_match.group(1) if result_match else None
    
    return ErrorEntry(
        error_signature=error_signature,
        error_type=extract_error_type(error_signature),
        file=metadata.get('file', ''),
        line=metadata.get('line', 0),
        fix_code=fix_code,
        explanation=extract_explanation(block),
        result=result,
        success_count=metadata.get('success_count', 1),
        tags=metadata.get('tags', []),
        timestamp=metadata.get('timestamp', datetime.now()),
        is_process_issue='Agent Process Issue' in block
    )
```

### B. LLM Prompt Templates

**Deduplicator** (similarity), **Tagger** (context tags), **Rule extractor** (process rules): see Consolidation App Design for signatures; full LLM prompts were in v1 (SIMPLIFIED_ERROR_REGISTRY.md) or in the consolidation app repository. Common patterns: (1) Similarity: compare two errors, return 0–1; (2) Tags: error type, framework, domain, platform; (3) Rules: statement, why, examples, related_errors; (4) Fix explanation.

### C. Configuration

**ENV-first** for Docker and simple deployment: use `environment:` or `env_file:` in docker-compose with `PROJECTS_ROOT`, `LLM_MODEL`, `CONSOLIDATION_SCHEDULE`, `SIMILARITY_THRESHOLD`. No config file or mount required.

**YAML optional** for `projects` list (paths outside `projects_root`), standalone runs, and advanced overrides (`CONFIG_PATH` or a default path). When both ENV and YAML exist, ENV overrides YAML.

See **Consolidation App Design** and **Docker** for ENV vars and usage.

### D. Gitignore Entry

Add `.errors_fixes/` to `.gitignore`. See **File Structure & Formats** for the exact entry. The folder is git-ignored because session logs are ephemeral, consolidated files are regenerated by the app, and it keeps the repo clean.

### E. test-and-fix.mdc (Full)

Full content for `.cursor/commands/global/test-and-fix.mdc`:

```markdown
---
description: Run all tests and fix errors automatically using Simplified Error Registry
---

# Test and Fix Command

When user runs this command, execute the following workflow:

## Workflow

1. **Determine Test Command** — Backend → `task test:backend`; frontend → `task test:frontend`; integration → `task test:integration`; mixed → all relevant.
2. **Run Tests** — Execute; capture stdout and stderr.
3. **Check Results** — If pass: inform user, document in `.errors_fixes/errors_and_fixes.md`, stop. If fail: parse errors, proceed to fix loop.
4. **Fix Loop** (max 5 iterations): For each error, check lookup order (see Lookup order in Agent Rules); apply fix; document; re-run tests. Stop if all pass, same error 3×, or 5 iterations.
5. **Final Report** — Summarize fixes, list remaining errors, update `.errors_fixes/errors_and_fixes.md`.

## Safety Limits

- **Maximum Iterations**: 5
- **Same Error Retry Limit**: 3
- **Stop Conditions**: All pass; max iterations; same error 3×; user stops.

## Documentation

Document in `.errors_fixes/errors_and_fixes.md`: each error, fix, result (✅/❌), success count, test command.
```

---

**Document Version:** 2.0 (SQT-refined)  
**Last Updated:** 2025-01-15  
**Author:** System Design  
**Status:** Ready for Implementation

**Key Changes in V2 (SQT-refined):**
- ENV-first config for Docker; YAML optional. Bootstrap in Phase 1. `discover_projects(root, extra_projects)` with auto-bootstrap for extra only. Phase 2.5 merged into Phase 2. Dedup: Phase 3 exact match only; Phase 4 AI. Redundancies removed (fix_repo vs coding_tips bullets, duplicate workflows, Options 3–5, duplicate discover_projects/bootstrap). test-and-fix.mdc in Appendix E. See `SIMPLIFIED_ERROR_REGISTRY_SQT.md`.