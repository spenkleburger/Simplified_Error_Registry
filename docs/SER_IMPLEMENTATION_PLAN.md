# SER - Implementation Plan

> **Simplified Error Registry** - Status Tracking Document for implementing the complete SER system in 6 steps: Core File Formats and Bootstrap, Agent Integration, Consolidation App - Core, Consolidation App - AI Integration, Docker/Config/Scheduling, Testing and Refinement.

**Last Updated:** 2025-01-15  
**Status:** ⬜ Not Started

**Recent Updates:**
- 2025-01-15: Initial implementation plan created with all 6 steps and detailed phases
- 2025-01-15: Plan structure aligned with SER_PLAN.md and SIMPLIFIED_ERROR_REGISTRY_V2.md

---

## Overview

This document tracks the implementation of SER from initial bootstrap and file format definition through full Docker deployment and testing. Items are organized into steps with clear dependencies. Each step contains multiple phases that build complete features end-to-end.

**Legend:**
- ⬜ Not Started
- 🟡 In Progress
- ✅ Completed
- ⏸️ Blocked
- 🔄 Needs Review

---

## Step 1: Core File Formats and Bootstrap

> **Establish the foundation: define markdown formats, create template structure, implement bootstrap script, and build parser/generator modules.**

**Last Updated:** 2025-01-15  
**Status:** ⬜ Not Started

---

### Phase 1.1: Define Markdown Formats and Create Template ✅
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Dependencies:** None  
**Completed:** 2025-01-21

**Tasks:**
- [x] Define exact markdown format for `errors_and_fixes.md`
  - [x] `### Error:` entry structure (timestamp, file, line, error type, error context, fix code, explanation, result, success count, tags)
  - [x] `### Agent Process Issue:` entry structure (timestamp, issue type, issue description, rule established, examples, result)
  - [x] Header format with processing note
- [x] Define markdown format for `fix_repo.md`
  - [x] Entry structure (error signature, tags, first seen, last updated, total occurrences)
  - [x] Fix structure (fix number, success count, code before/after, why it works, when to use, projects)
  - [x] Header with metadata (last updated, total entries, consolidated from)
- [x] Define markdown format for `coding_tips.md`
  - [x] Rule structure (title, rule statement, why, examples good/bad, related errors)
  - [x] Header with metadata (last updated, total rules)
- [x] Create template `.errors_fixes/` folder structure
  - [x] `errors_and_fixes.md` with header only
  - [x] `fix_repo.md` with header only
  - [x] `coding_tips.md` with header only
  - [x] Optional `README.md` with quick reference

**Files to Create:**
```
docs/
└── templates/
    └── errors_fixes_template/
        ├── errors_and_fixes.md
        ├── fix_repo.md
        ├── coding_tips.md
        └── README.md
```

**Key Requirements:**
- Markdown formats must be parseable by regex (v1) or markdown parser (future)
- All formats use UTF-8 encoding, LF line endings
- Templates include all required fields with example values
- Formats match examples in SIMPLIFIED_ERROR_REGISTRY_V2.md

**Quick Start for Testing:**
```bash
# Create template folder
mkdir -p docs/templates/errors_fixes_template
# Verify template files exist and have correct format
```

---

### Phase 1.2: Implement Bootstrap Script ✅
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.1
**Completed:** 2026-01-21

**Tasks:**
- [x] Create `scripts/bootstrap_errors_fixes.py`
  - [x] Function to create `.errors_fixes/` directory
  - [x] Function to create `errors_and_fixes.md` with header
  - [x] Function to create `fix_repo.md` with header
  - [x] Function to create `coding_tips.md` with header
  - [x] Function to update `.gitignore` (add `.errors_fixes/` entry)
  - [x] Command-line interface (argparse)
    - [x] `project_path` argument (required)
    - [x] `--no-gitignore` flag (optional)
- [x] Add error handling
  - [x] Check if project path exists
  - [x] Handle permission errors
  - [x] Handle existing `.errors_fixes/` folder (skip or update)
- [x] Add logging for bootstrap actions
- [x] Create unit tests
  - [x] Test folder creation
  - [x] Test file creation with correct headers
  - [x] Test `.gitignore` update (add entry, don't duplicate)
  - [x] Test error handling

**Files to Create:**
```
scripts/
└── bootstrap_errors_fixes.py
tests/
└── test_scripts_bootstrap_errors_fixes.py
```

**Key Requirements:**
- Script must be runnable standalone: `python scripts/bootstrap_errors_fixes.py /path/to/project`
- Must create all required files with correct headers
- Must handle existing folders gracefully
- Must update `.gitignore` without duplicating entries
- Must work on Windows, Linux, macOS

**Quick Start for Testing:**
```bash
# Test bootstrap on a new project
python scripts/bootstrap_errors_fixes.py /tmp/test_project
# Verify .errors_fixes/ folder and files created
# Verify .gitignore updated
```

---

### Phase 1.3: Implement Parser Module ⬜
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** Phase 1.1

**Tasks:**
- [x] Create `src/consolidation_app/parser.py`
  - [x] Define `ErrorEntry` dataclass
    - [x] error_signature, error_type, file, line, fix_code, explanation, result, success_count, tags, timestamp, is_process_issue
  - [x] Function `parse_errors_and_fixes(file_path: Path) -> List[ErrorEntry]`
    - [x] Read file with UTF-8 encoding
    - [x] Split by `### Error:` and `### Agent Process Issue:` headers
    - [x] Parse each block to extract metadata
    - [x] Extract code blocks (fix code, error context)
    - [x] Extract result (✅ Solved / ❌ Failed)
    - [x] Set `is_process_issue` flag correctly
  - [x] Helper functions
    - [x] `parse_error_block(block: str) -> Optional[ErrorEntry]`
    - [x] `parse_process_issue_block(block: str) -> Optional[ErrorEntry]`
    - [x] `extract_metadata(line: str) -> dict`
    - [x] `extract_code_block(block: str, section: str) -> str`
    - [x] `parse_timestamp(timestamp_str: str) -> datetime`
- [x] Handle edge cases
  - [x] Missing fields (use defaults)
  - [x] Malformed markdown (log warning, skip entry)
  - [x] Empty files (return empty list)
- [x] Create unit tests
  - [x] Test parsing valid error entry
  - [x] Test parsing valid process issue entry
  - [x] Test parsing multiple entries
  - [x] Test handling missing fields
  - [x] Test handling malformed markdown
  - [x] Test empty file

**Files to Create:**
```
src/
└── consolidation_app/
    ├── __init__.py
    └── parser.py
tests/
└── test_consolidation_app_parser.py
```

**Key Requirements:**
- Parser must handle all fields defined in Phase 1.1
- Must correctly identify `is_process_issue` flag
- Must be robust to missing or malformed data
- Regex-based parsing (v1), note for future markdown parser upgrade

**Quick Start for Testing:**
```bash
# Create test errors_and_fixes.md with sample entries
# Run parser
python -c "from src.consolidation_app.parser import parse_errors_and_fixes; from pathlib import Path; entries = parse_errors_and_fixes(Path('test_errors_and_fixes.md')); print(entries)"
```

---

### Phase 1.4: Implement Basic Generators ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.1, Phase 1.3

**Tasks:**
- [ ] Create `src/consolidation_app/generator.py`
  - [ ] Function `generate_fix_repo_markdown(entries: List[ErrorEntry]) -> str`
    - [ ] Filter entries where `is_process_issue=False`
    - [ ] Group by error signature (exact match for now)
    - [ ] Generate header with metadata
    - [ ] Generate entry sections with fixes ordered by success count
    - [ ] Format code blocks, tags, metadata
  - [ ] Function `generate_coding_tips_markdown(entries: List[ErrorEntry]) -> str`
    - [ ] Filter entries where `is_process_issue=True`
    - [ ] Group by rule category (extract from tags or issue type)
    - [ ] Generate header with metadata
    - [ ] Generate rule sections with examples
    - [ ] Format good/bad examples
  - [ ] Helper functions
    - [ ] `format_code_block(code: str, language: str = "python") -> str`
    - [ ] `format_tags(tags: List[str]) -> str`
    - [ ] `format_timestamp(dt: datetime) -> str`
- [ ] Create unit tests
  - [ ] Test fix_repo generation with single entry
  - [ ] Test fix_repo generation with multiple entries (same error)
  - [ ] Test fix_repo generation with multiple entries (different errors)
  - [ ] Test coding_tips generation with process issues
  - [ ] Test empty entries (generate headers only)

**Files to Create:**
```
src/
└── consolidation_app/
    └── generator.py
tests/
└── test_consolidation_app_generator.py
```

**Key Requirements:**
- Generators must produce valid markdown matching formats from Phase 1.1
- Must handle empty entry lists gracefully
- Must format code blocks, tags, timestamps correctly
- Output must be human-readable

**Quick Start for Testing:**
```bash
# Create test ErrorEntry objects
# Run generator
python -c "from src.consolidation_app.generator import generate_fix_repo_markdown; from src.consolidation_app.parser import ErrorEntry; entries = [...]; markdown = generate_fix_repo_markdown(entries); print(markdown)"
```

---

**End of Step 1: Code Review & Security Review**

At the end of Step 1, conduct comprehensive review:
- [ ] Code review (architecture, best practices, maintainability)
- [ ] Security review (file path handling, input validation, no code injection risks)
- [ ] Performance review (parser efficiency, generator output size)
- [ ] Documentation update (README, API docs, SER_PLAN.md, PROJECT_STATUS.md)
- [ ] All tests passing
- [ ] Bootstrap script works on Windows, Linux, macOS
- [ ] Parser handles all edge cases
- [ ] Generators produce valid markdown

---

## Step 2: Agent Integration and Test Output Verification

> **Create Cursor rules for error resolution and proactive coding tips, verify test output capture, and test end-to-end agent workflow.**

**Last Updated:** 2025-01-15  
**Status:** ⬜ Not Started

---

### Phase 2.1: Create errors.mdc Rule ⬜
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** Phase 1.1

**Tasks:**
- [ ] Create `.cursor/rules/global/errors.mdc`
  - [ ] **CRITICAL:** Craft precise frontmatter description
    - [ ] Do NOT use `alwaysApply: true`
    - [ ] Description must trigger on: pasted test errors, "There is an error in...", test failure output, "fix this error"
    - [ ] Test description with various user error reporting scenarios
  - [ ] Add "Role" section (Responder: User runs tests, agent provides code)
  - [ ] Add "Test Generation Requirements" section
    - [ ] Generate tests for new/modified code
    - [ ] Test file naming conventions
    - [ ] Test coverage requirements (happy path, edge cases, mocked calls)
  - [ ] Add "Advise Test Commands" section
    - [ ] Identify code type (backend/frontend/integration)
    - [ ] Advise appropriate test command (`task test:backend`, etc.)
    - [ ] Format of advice
  - [ ] Add "Test Execution Strategy" section
    - [ ] Default: Manual (do NOT run tests automatically)
    - [ ] Optional: Command-based auto-fix (when user runs test-and-fix command)
  - [ ] Add "Lookup Strategy" section
    - [ ] Three-step lookup order: errors_and_fixes.md → fix_repo.md → coding_tips.md
    - [ ] When to use each file
  - [ ] Add "Fix Application Workflow" section
    - [ ] Step 1: Identify error
    - [ ] Step 2: Lookup fixes (see Lookup Strategy)
    - [ ] Step 3: Apply fix (highest success count first)
    - [ ] Step 4: Document result
    - [ ] Step 5: Advise test commands
    - [ ] Step 6: Session tracking
  - [ ] Add "Preventive Checks" section
    - [ ] Check coding_tips.md before writing code
    - [ ] Apply process rules proactively
  - [ ] Add "Process Rules" section
    - [ ] Reference coding_tips.md for current rules
    - [ ] Common rules list
  - [ ] Add "Validation" section
    - [ ] Manual mode: ask user to run tests
    - [ ] Command mode: run tests automatically with safety limits
- [ ] Test rule triggering
  - [ ] Verify triggers on pasted test errors
  - [ ] Verify triggers on "There is an error in..." phrases
  - [ ] Verify does NOT trigger on non-error scenarios
  - [ ] Document trigger scenarios

**Files to Create:**
```
.cursor/
└── rules/
    └── global/
        └── errors.mdc
```

**Key Requirements:**
- Frontmatter description must be precise (no token bloat)
- Rule must cover all error resolution workflows
- Must reference `.errors_fixes/` file paths correctly
- Must include test generation and test command advice
- Must document lookup order clearly

**Quick Start for Testing:**
```bash
# Create test error scenario
# Paste test error output to Cursor
# Verify errors.mdc rule is triggered
# Verify agent follows lookup order
```

---

### Phase 2.2: Create coding-tips.mdc Rule ⬜
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 1.1

**Tasks:**
- [ ] Create `.cursor/rules/global/coding-tips.mdc`
  - [ ] **CRITICAL:** Craft precise frontmatter description
    - [ ] Do NOT use `alwaysApply: true`
    - [ ] Description must trigger on: "write code", "create file", "use file path", "run command", "Docker"
    - [ ] Test description with various code writing scenarios
  - [ ] Add "Coding Tips Reference" section
    - [ ] Check `.errors_fixes/coding_tips.md` before coding
    - [ ] List of rule categories (path handling, commands, formatting, Docker)
    - [ ] Proactive prevention emphasis
  - [ ] Add examples of when to check
    - [ ] Before writing code
    - [ ] Before using file paths
    - [ ] Before running commands
    - [ ] Before Docker work
- [ ] Test rule triggering
  - [ ] Verify triggers on "write code" requests
  - [ ] Verify triggers on "create file" requests
  - [ ] Verify triggers on "use file path" requests
  - [ ] Verify does NOT trigger on non-coding scenarios
  - [ ] Document trigger scenarios

**Files to Create:**
```
.cursor/
└── rules/
    └── global/
        └── coding-tips.mdc
```

**Key Requirements:**
- Frontmatter description must be precise (no token bloat)
- Rule must emphasize proactive use (before errors occur)
- Must reference `.errors_fixes/coding_tips.md` correctly
- Must complement errors.mdc (hybrid approach)

**Quick Start for Testing:**
```bash
# Request agent to write code
# Verify coding-tips.mdc rule is triggered
# Verify agent checks coding_tips.md
```

---

### Phase 2.3: Test Output Capture Verification ⬜
**Priority:** Important  
**Estimated Time:** 2-3 hours  
**Dependencies:** None

**Tasks:**
- [ ] Inspect `task test:*` commands in `pyproject.toml`
  - [ ] Identify Python scripts that copy test output
  - [ ] Review `scripts/test_backend.py`, `scripts/test_frontend.py`, `scripts/test_integration.py`
- [ ] Verify test output capture logic
  - [ ] Ensure scripts capture `=== FAILURES ===` or `=== ERRORS ===` section
  - [ ] Ensure scripts capture `=== short test summary info ===` section
  - [ ] Verify scripts do NOT capture irrelevant sections (passing tests, collection info)
- [ ] Test with actual failing tests
  - [ ] Run `task test:backend` with failing tests
  - [ ] Check clipboard contents
  - [ ] Verify required sections are present
  - [ ] Repeat for `task test:frontend` and `task test:integration`
- [ ] Update scripts if needed
  - [ ] Fix capture logic if wrong sections are copied
  - [ ] Document which sections are required
- [ ] Document required test output sections
  - [ ] Create documentation in `docs/` or update existing docs
  - [ ] Explain why these sections are needed (agent error identification)

**Files to Modify:**
```
scripts/
├── test_backend.py
├── test_frontend.py
└── test_integration.py
docs/
└── (test output capture documentation)
```

**Key Requirements:**
- Test output must include errors/failures section and summary section
- Agent must be able to parse errors from captured output
- Scripts should not capture excessive irrelevant output
- Documentation must explain required sections

**Quick Start for Testing:**
```bash
# Create intentionally failing tests
# Run task test:backend
# Check clipboard - verify FAILURES and summary sections present
# Test agent can parse errors from clipboard
```

---

### Phase 2.4: Create Optional test-and-fix.mdc Command ⬜
**Priority:** Nice to Have  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 2.1

**Tasks:**
- [ ] Create `.cursor/commands/global/test-and-fix.mdc`
  - [ ] Add frontmatter description
  - [ ] Add "Workflow" section
    - [ ] Step 1: Determine test command
    - [ ] Step 2: Run tests
    - [ ] Step 3: Check results
    - [ ] Step 4: Fix loop (max 5 iterations)
    - [ ] Step 5: Final report
  - [ ] Add "Safety Limits" section
    - [ ] Maximum iterations: 5
    - [ ] Same error retry limit: 3
    - [ ] Stop conditions
  - [ ] Add "Documentation" section
    - [ ] Document in errors_and_fixes.md
    - [ ] What to document (error, fix, result, success count, test command)
- [ ] Note: This is optional/backup - primary workflow uses errors.mdc rule

**Files to Create:**
```
.cursor/
└── commands/
    └── global/
        └── test-and-fix.mdc
```

**Key Requirements:**
- Command provides alternative auto-fix workflow
- Must include safety limits to prevent infinite loops
- Must reference lookup order from errors.mdc
- Must document all fixes comprehensively

**Quick Start for Testing:**
```bash
# Run .cursor/command test-and-fix
# Verify agent runs tests automatically
# Verify agent fixes errors and documents results
# Verify safety limits are respected
```

---

### Phase 2.5: End-to-End Agent Workflow Testing ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 2.1, Phase 2.2, Phase 2.3

**Tasks:**
- [ ] Test manual workflow
  - [ ] Agent writes code → generates tests → advises test command
  - [ ] User runs test command → provides error output
  - [ ] Agent checks lookup order → applies fix → documents
  - [ ] User runs test again → tests pass
  - [ ] Agent documents success
- [ ] Test command-based workflow (if test-and-fix.mdc created)
  - [ ] User runs test-and-fix command
  - [ ] Agent runs tests automatically
  - [ ] Agent fixes all errors
  - [ ] Agent documents all fixes
  - [ ] Agent reports final status
- [ ] Test proactive coding_tips.md usage
  - [ ] Request agent to write code
  - [ ] Verify agent checks coding_tips.md before coding
  - [ ] Verify agent applies process rules
- [ ] Test error scenarios
  - [ ] Error in errors_and_fixes.md (recent session)
  - [ ] Error in fix_repo.md (consolidated fix)
  - [ ] No fix found (agent creates new fix)
  - [ ] Multiple fixes (agent tries highest success count first)
- [ ] Document test results
  - [ ] Create test scenarios document
  - [ ] Document any issues found
  - [ ] Update agent rules if needed

**Files to Create:**
```
docs/
└── agent_workflow_tests.md
```

**Key Requirements:**
- All workflows must function correctly
- Agent must follow lookup order
- Agent must document fixes correctly
- Agent must apply process rules proactively
- Test results must be documented

**Quick Start for Testing:**
```bash
# Follow manual workflow with real error
# Verify each step works correctly
# Document results
```

---

**End of Step 2: Code Review & Security Review**

At the end of Step 2, conduct comprehensive review:
- [ ] Code review (rule descriptions, workflow logic, test coverage)
- [ ] Security review (no code injection in rules, safe file paths)
- [ ] Performance review (rule triggering efficiency, no token bloat)
- [ ] Documentation update (README, SER_PLAN.md, PROJECT_STATUS.md, agent workflow docs)
- [ ] All tests passing
- [ ] Agent rules trigger correctly
- [ ] Test output capture works correctly
- [ ] End-to-end workflows function correctly

---

## Step 3: Consolidation App - Core

> **Build core consolidation app: discovery, parser integration, basic deduplication (exact match), basic tagging (rule-based), writer module, and cleanup.**

**Last Updated:** 2025-01-15  
**Status:** ⬜ Not Started

---

### Phase 3.1: Discovery Module ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.2

**Tasks:**
- [ ] Create `src/consolidation_app/discovery.py`
  - [ ] Function `discover_projects(root_path: Path, extra_projects: list[str] | None = None) -> list[Path]`
    - [ ] Use `rglob('.errors_fixes/errors_and_fixes.md')` to find projects
    - [ ] For each found path, get project root (path.parent.parent)
    - [ ] For `extra_projects` list:
      - [ ] Resolve each path
      - [ ] Check if `errors_and_fixes.md` exists
      - [ ] If missing, call `bootstrap(project_root, update_gitignore=False)`
      - [ ] Add to projects list
    - [ ] Deduplicate projects (use `dict.fromkeys()`)
    - [ ] Return list of project roots
  - [ ] Add error handling
    - [ ] Handle missing root_path
    - [ ] Handle permission errors
    - [ ] Handle invalid extra_projects paths
  - [ ] Add logging for discovery process
- [ ] Create unit tests
  - [ ] Test rglob discovery
  - [ ] Test extra_projects with existing errors_and_fixes.md
  - [ ] Test extra_projects with missing errors_and_fixes.md (auto-bootstrap)
  - [ ] Test deduplication
  - [ ] Test error handling

**Files to Create:**
```
src/
└── consolidation_app/
    └── discovery.py
tests/
└── test_consolidation_app_discovery.py
```

**Key Requirements:**
- Must discover all projects with `.errors_fixes/errors_and_fixes.md`
- Must support extra_projects list for projects outside scan root
- Must auto-bootstrap only for extra_projects (not rglob-discovered)
- Must handle errors gracefully

**Quick Start for Testing:**
```bash
# Create test project structure
# Run discovery
python -c "from src.consolidation_app.discovery import discover_projects; from pathlib import Path; projects = discover_projects(Path('/tmp/projects')); print(projects)"
```

---

### Phase 3.2: Parser Integration ⬜
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 1.3, Phase 3.1

**Tasks:**
- [ ] Integrate parser into consolidation workflow
  - [ ] Read `errors_and_fixes.md` for each discovered project
  - [ ] Parse entries using parser from Phase 1.3
  - [ ] Separate entries by `is_process_issue` flag
  - [ ] Group entries by project for tracking
- [ ] Add error handling
  - [ ] Handle missing files (skip project, log warning)
  - [ ] Handle parse errors (log error, continue with other projects)
  - [ ] Handle empty files (return empty list)
- [ ] Add logging for parsing process
  - [ ] Log number of projects processed
  - [ ] Log number of entries parsed per project
  - [ ] Log any errors encountered

**Files to Modify:**
```
src/
└── consolidation_app/
    └── (main.py or consolidation.py)
```

**Key Requirements:**
- Must process all discovered projects
- Must handle errors gracefully (don't stop on one failure)
- Must separate error entries from process issue entries
- Must log processing statistics

**Quick Start for Testing:**
```bash
# Create test projects with errors_and_fixes.md
# Run consolidation (parser integration)
# Verify entries are parsed correctly
# Verify errors are handled gracefully
```

---

### Phase 3.3: Basic Deduplication (Exact Match) ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 3.2

**Tasks:**
- [ ] Create `src/consolidation_app/deduplicator.py`
  - [ ] Function `deduplicate_errors_exact(new_entries: List[ErrorEntry], existing_entries: List[ErrorEntry]) -> List[ErrorEntry]`
    - [ ] For each new entry, check if exact match exists in existing entries
    - [ ] Match criteria: error_signature (exact), error_type (exact), file (exact)
    - [ ] If match found: merge into existing entry (increment success count if fix is same)
    - [ ] If no match: add as new entry
    - [ ] Return consolidated list
  - [ ] Function `merge_entries(existing: ErrorEntry, new: ErrorEntry) -> ErrorEntry`
    - [ ] Update last_seen timestamp
    - [ ] Increment total_occurrences
    - [ ] If fix code is same: increment success count
    - [ ] If fix code is different: add as variant fix
  - [ ] Handle edge cases
    - [ ] Empty lists
    - [ ] No matches
    - [ ] Multiple matches (shouldn't happen with exact match, but handle)
- [ ] Create unit tests
  - [ ] Test exact match deduplication
  - [ ] Test no match (new entry)
  - [ ] Test same fix (increment success count)
  - [ ] Test different fix (add as variant)
  - [ ] Test empty lists

**Files to Create:**
```
src/
└── consolidation_app/
    └── deduplicator.py
tests/
└── test_consolidation_app_deduplicator.py
```

**Key Requirements:**
- Must use exact match only (no AI in Phase 3)
- Must correctly identify same vs different fixes
- Must increment success counts correctly
- Must handle edge cases gracefully

**Quick Start for Testing:**
```bash
# Create test entries (some duplicates, some new)
# Run deduplication
# Verify duplicates are merged, new entries added
# Verify success counts are correct
```

---

### Phase 3.4: Basic Tagging (Rule-Based) ⬜
**Priority:** Important  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 3.2

**Tasks:**
- [ ] Create `src/consolidation_app/tagger.py`
  - [ ] Function `generate_tags_rule_based(entry: ErrorEntry) -> List[str]`
    - [ ] Extract error type tag (from error_type field)
    - [ ] Extract framework/library tag (from file path or error context)
      - [ ] Check for common frameworks (docker, django, flask, etc.)
    - [ ] Extract domain tag (from error context or file location)
      - [ ] networking, file-io, database, authentication, etc.
    - [ ] Extract platform tag (from error message or file path)
      - [ ] windows, linux, cross-platform
    - [ ] Return list of tags
  - [ ] Define tag rules
    - [ ] Error type mapping (FileNotFoundError → file-io, TypeError → type-conversion, etc.)
    - [ ] Framework detection (check file paths, imports, error context)
    - [ ] Domain detection (check file locations, error context)
    - [ ] Platform detection (check error messages, file paths)
  - [ ] Handle edge cases
    - [ ] Unknown error types (use generic tag)
    - [ ] No framework detected (skip framework tag)
- [ ] Create unit tests
  - [ ] Test error type tagging
  - [ ] Test framework detection
  - [ ] Test domain detection
  - [ ] Test platform detection
  - [ ] Test edge cases

**Files to Create:**
```
src/
└── consolidation_app/
    └── tagger.py
tests/
└── test_consolidation_app_tagger.py
```

**Key Requirements:**
- Must use rule-based tagging only (no AI in Phase 3)
- Must generate 3-5 tags per entry
- Must handle unknown cases gracefully
- Tags must be consistent and useful

**Quick Start for Testing:**
```bash
# Create test entries with various error types
# Run tagging
# Verify tags are generated correctly
# Verify tags are useful for lookup
```

---

### Phase 3.5: Writer Module ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.4, Phase 3.3, Phase 3.4

**Tasks:**
- [ ] Create `src/consolidation_app/writer.py`
  - [ ] Function `write_fix_repo(project_path: Path, consolidated_entries: List[ErrorEntry]) -> None`
    - [ ] Filter entries where `is_process_issue=False`
    - [ ] Generate markdown using generator from Phase 1.4
    - [ ] Write to `project_path/.errors_fixes/fix_repo.md`
    - [ ] Create directory if missing
    - [ ] Use UTF-8 encoding, LF line endings
  - [ ] Function `write_coding_tips(project_path: Path, process_entries: List[ErrorEntry]) -> None`
    - [ ] Filter entries where `is_process_issue=True`
    - [ ] Generate markdown using generator from Phase 1.4
    - [ ] Write to `project_path/.errors_fixes/coding_tips.md`
    - [ ] Create directory if missing
    - [ ] Use UTF-8 encoding, LF line endings
  - [ ] Function `clear_errors_and_fixes(project_path: Path) -> None`
    - [ ] Read current `errors_and_fixes.md`
    - [ ] Replace contents with header only
    - [ ] Keep file (don't delete)
    - [ ] Use UTF-8 encoding, LF line endings
  - [ ] Add error handling
    - [ ] Handle permission errors
    - [ ] Handle missing directories
    - [ ] Handle write failures
  - [ ] Add logging for write operations
- [ ] Create unit tests
  - [ ] Test write_fix_repo
  - [ ] Test write_coding_tips
  - [ ] Test clear_errors_and_fixes
  - [ ] Test error handling

**Files to Create:**
```
src/
└── consolidation_app/
    └── writer.py
tests/
└── test_consolidation_app_writer.py
```

**Key Requirements:**
- Must write valid markdown matching formats from Phase 1.1
- Must create directories if missing
- Must clear errors_and_fixes.md but keep file in original format
- Must handle errors gracefully

**Quick Start for Testing:**
```bash
# Create test project
# Run writer functions
# Verify files are created with correct content
# Verify errors_and_fixes.md is cleared but kept
```

---

### Phase 3.6: Main Consolidation Workflow ⬜
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** Phase 3.1, Phase 3.2, Phase 3.3, Phase 3.4, Phase 3.5

**Tasks:**
- [ ] Create `src/consolidation_app/main.py`
  - [ ] Function `consolidate_all_projects(root_path: Path, extra_projects: list[str] | None = None) -> None`
    - [ ] Discover projects (Phase 3.1)
    - [ ] For each project:
      - [ ] Parse errors_and_fixes.md (Phase 3.2)
      - [ ] Read existing fix_repo.md (if exists) and parse
      - [ ] Read existing coding_tips.md (if exists) and parse
      - [ ] Deduplicate errors (Phase 3.3)
      - [ ] Generate tags (Phase 3.4)
      - [ ] Merge fixes by success count
      - [ ] Write fix_repo.md (Phase 3.5)
      - [ ] Write coding_tips.md (Phase 3.5)
      - [ ] Clear errors_and_fixes.md (Phase 3.5)
    - [ ] Log summary statistics
  - [ ] Add error handling
    - [ ] Continue processing other projects if one fails
    - [ ] Log errors for each project
    - [ ] Return success/failure status
  - [ ] Add command-line interface
    - [ ] `--root` argument for projects root
    - [ ] `--config` argument for config file (optional)
    - [ ] `--dry-run` flag (don't write files, just log)
- [ ] Create unit tests
  - [ ] Test full consolidation workflow
  - [ ] Test error handling (one project fails, others continue)
  - [ ] Test dry-run mode
- [ ] Create integration tests
  - [ ] Test with multiple projects
  - [ ] Test with existing fix_repo.md and coding_tips.md
  - [ ] Test with empty projects

**Files to Create:**
```
src/
└── consolidation_app/
    └── main.py
tests/
├── test_consolidation_app_main.py
└── integration/
    └── test_consolidation_workflow.py
```

**Key Requirements:**
- Must process all projects in workflow
- Must handle errors gracefully (continue on failure)
- Must produce valid consolidated files
- Must clear session logs after successful consolidation
- Must log comprehensive statistics

**Quick Start for Testing:**
```bash
# Create test projects with errors_and_fixes.md
# Run consolidation
python -m src.consolidation_app.main --root /tmp/projects
# Verify fix_repo.md and coding_tips.md are created
# Verify errors_and_fixes.md is cleared
```

---

**End of Step 3: Code Review & Security Review**

At the end of Step 3, conduct comprehensive review:
- [ ] Code review (architecture, module organization, error handling)
- [ ] Security review (file path handling, input validation, no code injection)
- [ ] Performance review (processing time for 5-20 projects, memory usage)
- [ ] Documentation update (README, SER_PLAN.md, PROJECT_STATUS.md, consolidation app docs)
- [ ] All tests passing
- [ ] Consolidation workflow processes all projects correctly
- [ ] Consolidated files are valid and useful
- [ ] Error handling is robust

---

## Step 4: Consolidation App - AI Integration

> **Add AI-powered features and select appropriate model: LLM client, semantic deduplication, AI tagging, fix merging, and rule extraction from process issues.**

**Last Updated:** 2025-01-15  
**Status:** ⬜ Not Started

---

### Phase 4.1: LLM Client Integration ⬜
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** None

**Tasks:**
- [ ] Create `src/consolidation_app/llm_client.py`
  - [ ] Support Ollama (local)
    - [ ] Function `call_ollama(prompt: str, model: str = "qwen2.5-coder:14b") -> str`
    - [ ] Handle connection errors
    - [ ] Handle timeout errors
    - [ ] Retry logic for transient failures
  - [ ] Support OpenAI API (optional)
    - [ ] Function `call_openai(prompt: str, model: str = "gpt-4") -> str`
    - [ ] Handle API errors
    - [ ] Handle rate limiting
  - [ ] Support Anthropic API (optional)
    - [ ] Function `call_anthropic(prompt: str, model: str = "claude-3-opus") -> str`
    - [ ] Handle API errors
  - [ ] Configuration
    - [ ] Read LLM provider from ENV (`LLM_PROVIDER`, `LLM_MODEL`)
    - [ ] Default to Ollama
    - [ ] Support API keys from ENV
  - [ ] Add logging for LLM calls
    - [ ] Log prompt length
    - [ ] Log response length
    - [ ] Log errors
- [ ] Create unit tests
  - [ ] Test Ollama connection (mock or real)
  - [ ] Test OpenAI API (mock)
  - [ ] Test error handling
  - [ ] Test configuration

**Files to Create:**
```
src/
└── consolidation_app/
    └── llm_client.py
tests/
└── test_consolidation_app_llm_client.py
```

**Key Requirements:**
- Must support Ollama (local, default)
- Must support cloud APIs (OpenAI, Anthropic) as optional
- Must handle errors gracefully
- Must be configurable via ENV
- Must log LLM usage for cost tracking

**Quick Start for Testing:**
```bash
# Test Ollama connection
python -c "from src.consolidation_app.llm_client import call_ollama; response = call_ollama('Hello'); print(response)"
# Test with mock for cloud APIs
```

---

### Phase 4.2: AI Deduplication ⬜
**Priority:** Critical  
**Estimated Time:** 5-6 hours  
**Dependencies:** Phase 4.1, Phase 3.3

**Tasks:**
- [ ] Create `src/consolidation_app/deduplicator_ai.py`
  - [ ] Function `deduplicate_errors_ai(new_entries: List[ErrorEntry], existing_entries: List[ErrorEntry], similarity_threshold: float = 0.85) -> List[ErrorEntry]`
    - [ ] For each new entry, use LLM to find similar existing entries
    - [ ] Calculate similarity score (0.0-1.0)
    - [ ] If score >= threshold: merge into existing entry
    - [ ] If no match: add as new entry
    - [ ] Return consolidated list
  - [ ] Function `calculate_similarity(entry1: ErrorEntry, entry2: ErrorEntry) -> float`
    - [ ] Build LLM prompt comparing two errors
    - [ ] Ask LLM to rate similarity (0.0-1.0) with reasoning
    - [ ] Parse JSON response: `{"similarity": 0.95, "reason": "..."}`
    - [ ] Return similarity score
  - [ ] LLM prompt template
    - [ ] Include error type, message, file, line, context
    - [ ] Ask for similarity score and brief reason
    - [ ] Specify JSON response format
  - [ ] Batch processing (optional optimization)
    - [ ] Process multiple comparisons in one LLM call
    - [ ] Reduce API costs
  - [ ] Add error handling
    - [ ] Handle LLM failures (fall back to exact match)
    - [ ] Handle malformed JSON responses
    - [ ] Handle timeout errors
- [ ] Create unit tests
  - [ ] Test similarity calculation (mock LLM)
  - [ ] Test deduplication with similar errors
  - [ ] Test deduplication with different errors
  - [ ] Test threshold behavior
  - [ ] Test error handling

**Files to Create:**
```
src/
└── consolidation_app/
    └── deduplicator_ai.py
tests/
└── test_consolidation_app_deduplicator_ai.py
```

**Key Requirements:**
- Must use semantic similarity (not exact match)
- Must handle LLM failures gracefully (fallback to exact match)
- Must be configurable (similarity threshold)
- Must log similarity scores for debugging
- Must be efficient (batch processing if possible)

**Quick Start for Testing:**
```bash
# Create test entries (some semantically similar, some different)
# Run AI deduplication
# Verify similar errors are merged
# Verify different errors are kept separate
```

---

### Phase 4.3: AI Tagging ⬜
**Priority:** Important  
**Estimated Time:** 4-5 hours  
**Dependencies:** Phase 4.1, Phase 3.4

**Tasks:**
- [ ] Create `src/consolidation_app/tagger_ai.py`
  - [ ] Function `generate_tags_ai(entry: ErrorEntry) -> List[str]`
    - [ ] Build LLM prompt with error details
    - [ ] Ask LLM to generate 3-5 context tags
    - [ ] Parse JSON response: `{"tags": ["tag1", "tag2", "tag3"]}`
    - [ ] Return list of tags
  - [ ] LLM prompt template
    - [ ] Include error signature, type, file, line, context
    - [ ] Ask for tags: error type, framework/library, domain, platform
    - [ ] Specify JSON response format
    - [ ] Provide examples
  - [ ] Combine with rule-based tags (optional)
    - [ ] Use AI tags as primary
    - [ ] Add rule-based tags for missing categories
  - [ ] Add error handling
    - [ ] Handle LLM failures (fall back to rule-based)
    - [ ] Handle malformed JSON responses
    - [ ] Handle timeout errors
- [ ] Create unit tests
  - [ ] Test tag generation (mock LLM)
  - [ ] Test error handling
  - [ ] Test tag quality (verify tags are useful)

**Files to Create:**
```
src/
└── consolidation_app/
    └── tagger_ai.py
tests/
└── test_consolidation_app_tagger_ai.py
```

**Key Requirements:**
- Must generate 3-5 useful context tags
- Must handle LLM failures gracefully (fallback to rule-based)
- Must produce consistent tags
- Must be efficient (batch processing if possible)

**Quick Start for Testing:**
```bash
# Create test entries
# Run AI tagging
# Verify tags are generated and useful
# Verify fallback works if LLM fails
```

---

### Phase 4.4: Fix Merging Logic ⬜
**Priority:** Important  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 3.3

**Tasks:**
- [ ] Enhance `src/consolidation_app/merger.py`
  - [ ] Function `merge_fixes(entry: ErrorEntry) -> ErrorEntry`
    - [ ] Group fixes by code similarity (fuzzy match)
    - [ ] If same fix: increment success_count
    - [ ] If different fix: add as variant with explanation
    - [ ] Sort all fixes by success_count (highest first)
  - [ ] Function `group_similar_fixes(fixes: List[Fix]) -> List[List[Fix]]`
    - [ ] Compare fix code (normalize whitespace, comments)
    - [ ] Use fuzzy string matching (Levenshtein distance or similar)
    - [ ] Group fixes with similarity > 0.9
  - [ ] Function `calculate_fix_similarity(fix1: Fix, fix2: Fix) -> float`
    - [ ] Normalize code (remove whitespace differences, comments)
    - [ ] Calculate similarity score
    - [ ] Return 0.0-1.0 score
- [ ] Create unit tests
  - [ ] Test fix grouping (same fixes)
  - [ ] Test fix grouping (different fixes)
  - [ ] Test success count incrementing
  - [ ] Test sorting by success count

**Files to Create/Modify:**
```
src/
└── consolidation_app/
    └── merger.py
tests/
└── test_consolidation_app_merger.py
```

**Key Requirements:**
- Must correctly identify same vs different fixes
- Must increment success counts correctly
- Must sort fixes by success count
- Must handle edge cases (single fix, no fixes)

**Quick Start for Testing:**
```bash
# Create test entries with multiple fixes (some same, some different)
# Run fix merging
# Verify same fixes are grouped and success counts incremented
# Verify different fixes are kept separate
# Verify sorting by success count
```

---

### Phase 4.5: Rule Extraction ⬜
**Priority:** Important  
**Estimated Time:** 5-6 hours  
**Dependencies:** Phase 4.1, Phase 3.2

**Tasks:**
- [ ] Create `src/consolidation_app/rule_extractor.py`
  - [ ] Function `extract_process_rules(entries: List[ErrorEntry]) -> List[ProcessRule]`
    - [ ] Filter entries where `is_process_issue=True` ONLY
    - [ ] Group by issue type or category
    - [ ] For each group, use LLM to extract general rules
    - [ ] Return list of ProcessRule objects
  - [ ] Function `extract_rules_from_group(group: List[ErrorEntry]) -> List[ProcessRule]`
    - [ ] Build LLM prompt with all process issues in group
    - [ ] Ask LLM to extract general rules
    - [ ] Parse JSON response with rule structure
    - [ ] Return ProcessRule objects
  - [ ] LLM prompt template
    - [ ] Include all process issues in group
    - [ ] Ask for: rule statement, why it's needed, examples (good/bad), related errors
    - [ ] Specify JSON response format
    - [ ] Provide examples
  - [ ] ProcessRule dataclass
    - [ ] title, rule, why, examples (good/bad), related_errors
  - [ ] Add error handling
    - [ ] Handle LLM failures (use basic rule extraction)
    - [ ] Handle malformed JSON responses
    - [ ] Handle empty groups
- [ ] Create unit tests
  - [ ] Test rule extraction (mock LLM)
  - [ ] Test filtering (only process issues)
  - [ ] Test grouping
  - [ ] Test error handling

**Files to Create:**
```
src/
└── consolidation_app/
    └── rule_extractor.py
tests/
└── test_consolidation_app_rule_extractor.py
```

**Key Requirements:**
- Must ONLY process entries with `is_process_issue=True`
- Must extract useful, actionable rules
- Must include examples (good/bad)
- Must link to related errors
- Must handle LLM failures gracefully

**Quick Start for Testing:**
```bash
# Create test process issue entries
# Run rule extraction
# Verify rules are extracted correctly
# Verify rules are useful and actionable
```

---

**End of Step 4: Code Review & Security Review**

At the end of Step 4, conduct comprehensive review:
- [ ] Code review (AI integration, prompt engineering, error handling)
- [ ] Security review (API key handling, no secrets in logs, input validation)
- [ ] Performance review (LLM call efficiency, batch processing, cost optimization)
- [ ] Documentation update (README, SER_PLAN.md, PROJECT_STATUS.md, LLM usage docs)
- [ ] All tests passing
- [ ] AI features work correctly (deduplication, tagging, rule extraction)
- [ ] Fallback mechanisms work (exact match, rule-based)
- [ ] LLM costs are reasonable

---

## Step 5: Docker, Config, and Scheduling

> **Containerize the consolidation app, implement ENV-first configuration, add cron scheduling, and set up logging/monitoring.**

**Last Updated:** 2025-01-15  
**Status:** ⬜ Not Started

---

### Phase 5.1: Docker Container Setup ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Step 3, Step 4

**Tasks:**
- [ ] Create `Dockerfile`
  - [ ] Base image: `python:3.11-slim`
  - [ ] Install dependencies from `requirements.txt`
  - [ ] Copy application code
  - [ ] Set working directory
  - [ ] Set default command
  - [ ] Set environment variables (defaults)
- [ ] Create `docker-compose.yml`
  - [ ] `consolidation-app` service
    - [ ] Build from Dockerfile
    - [ ] Volume mount: projects directory (read-write)
    - [ ] Environment variables (ENV-first config)
    - [ ] Depends on: ollama
  - [ ] `ollama` service
    - [ ] Image: `ollama/ollama`
    - [ ] Volume: ollama data persistence
    - [ ] Ports: 11434 (Ollama API)
  - [ ] Volumes: ollama_data
- [ ] Create `.dockerignore`
  - [ ] Exclude unnecessary files
  - [ ] Exclude test files
  - [ ] Exclude development files
- [ ] Test Docker build and run
  - [ ] Build image
  - [ ] Run container
  - [ ] Verify consolidation app works
  - [ ] Verify Ollama connection

**Files to Create:**
```
Dockerfile
docker-compose.yml
.dockerignore
```

**Key Requirements:**
- Docker image must be minimal (slim base)
- Docker Compose must include Ollama service
- Volume mounts must provide read-write access to projects
- Environment variables must be configurable
- Container must be production-ready

**Quick Start for Testing:**
```bash
# Build image
docker build -t ser-consolidation .
# Run with docker-compose
docker-compose up -d
# Verify services are running
docker-compose ps
```

---

### Phase 5.2: ENV-First Configuration ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 5.1

**Tasks:**
- [ ] Create `src/consolidation_app/config.py`
  - [ ] Read configuration from ENV variables (primary)
    - [ ] `PROJECTS_ROOT` (required)
    - [ ] `LLM_PROVIDER` (default: "ollama")
    - [ ] `LLM_MODEL` (default: "qwen2.5-coder:14b")
    - [ ] `CONSOLIDATION_SCHEDULE` (default: "0 2 * * *")
    - [ ] `SIMILARITY_THRESHOLD` (default: 0.85)
    - [ ] `LLM_API_KEY` (optional, for cloud APIs)
  - [ ] Support optional YAML config file
    - [ ] `CONFIG_PATH` ENV variable or default path
    - [ ] Read YAML if exists
    - [ ] ENV overrides YAML when both exist
    - [ ] YAML supports `consolidation.projects` list (extra_projects)
  - [ ] Configuration validation
    - [ ] Check required ENV variables
    - [ ] Validate paths exist
    - [ ] Validate schedule format
    - [ ] Validate threshold range (0.0-1.0)
  - [ ] Configuration dataclass
    - [ ] All config values in one object
    - [ ] Type-safe access
- [ ] Update `docker-compose.yml`
  - [ ] Add environment variables section
  - [ ] Add env_file support (optional)
  - [ ] Document required variables
- [ ] Create example `.env` file
  - [ ] Document all variables
  - [ ] Provide defaults
  - [ ] Add to `.gitignore`
- [ ] Create unit tests
  - [ ] Test ENV variable reading
  - [ ] Test YAML config reading
  - [ ] Test ENV overrides YAML
  - [ ] Test validation

**Files to Create:**
```
src/
└── consolidation_app/
    └── config.py
.env.example
tests/
└── test_consolidation_app_config.py
```

**Key Requirements:**
- ENV variables must be primary configuration method
- YAML must be optional (for projects list, advanced overrides)
- ENV must override YAML when both exist
- Configuration must be validated
- Must be documented clearly

**Quick Start for Testing:**
```bash
# Set ENV variables
export PROJECTS_ROOT=/tmp/projects
export LLM_MODEL=ollama/qwen2.5-coder:14b
# Test config loading
python -c "from src.consolidation_app.config import load_config; config = load_config(); print(config)"
```

---

### Phase 5.3: Cron Scheduler Integration ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 5.1, Phase 5.2

**Tasks:**
- [ ] Create `src/consolidation_app/scheduler.py`
  - [ ] Function `schedule_consolidation(schedule: str, consolidation_func: Callable) -> None`
    - [ ] Parse cron schedule string
    - [ ] Use Python scheduler (APScheduler or similar)
    - [ ] Schedule consolidation function
    - [ ] Run scheduler in background
  - [ ] Support cron format: `"0 2 * * *"` (2 AM daily)
  - [ ] Add one-time run mode (for testing)
    - [ ] `--run-once` flag
    - [ ] Run consolidation immediately, then exit
  - [ ] Add logging for scheduled runs
    - [ ] Log when consolidation starts
    - [ ] Log when consolidation completes
    - [ ] Log any errors
  - [ ] Handle scheduler errors
    - [ ] Log errors
    - [ ] Continue running (don't crash)
- [ ] Update `main.py`
  - [ ] Add scheduler integration
  - [ ] Support both scheduled and one-time modes
  - [ ] Add command-line flags
- [ ] Update Dockerfile
  - [ ] Set default command to run scheduler
  - [ ] Support override for one-time run
- [ ] Create unit tests
  - [ ] Test scheduler setup
  - [ ] Test cron parsing
  - [ ] Test one-time run mode

**Files to Create/Modify:**
```
src/
└── consolidation_app/
    └── scheduler.py
src/
└── consolidation_app/
    └── main.py (update)
```

**Key Requirements:**
- Must support cron schedule format
- Must run consolidation at scheduled times
- Must support one-time run for testing
- Must log all runs
- Must handle errors gracefully

**Quick Start for Testing:**
```bash
# Test one-time run
python -m src.consolidation_app.main --run-once
# Test scheduler (short interval for testing)
# Set CONSOLIDATION_SCHEDULE="*/5 * * * *" (every 5 minutes)
# Run and verify consolidation runs on schedule
```

---

### Phase 5.4: Logging and Monitoring ⬜
**Priority:** Important  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 5.1

**Tasks:**
- [ ] Set up logging configuration
  - [ ] Use Python `logging` module
  - [ ] Configure log levels (INFO default, DEBUG for development)
  - [ ] Format: timestamp, level, message
  - [ ] Output: stdout/stderr (for Docker logs)
  - [ ] Optional: file logging for audit trail
- [ ] Add logging throughout consolidation app
  - [ ] Discovery: log projects found
  - [ ] Parsing: log entries parsed per project
  - [ ] Deduplication: log duplicates found
  - [ ] Tagging: log tags generated
  - [ ] Writing: log files written
  - [ ] Errors: log all errors with context
- [ ] Add monitoring metrics (optional)
  - [ ] Projects processed count
  - [ ] Entries processed count
  - [ ] Consolidation duration
  - [ ] LLM API calls count (for cost tracking)
  - [ ] Errors encountered count
- [ ] Create logging configuration file
  - [ ] `config/logging.py` or similar
  - [ ] Centralized logging setup
- [ ] Update Docker Compose
  - [ ] Configure log driver (optional)
  - [ ] Set log retention
- [ ] Create unit tests
  - [ ] Test logging configuration
  - [ ] Test log output

**Files to Create/Modify:**
```
src/
└── consolidation_app/
    └── (add logging throughout)
config/
└── logging.py (or use project's existing)
```

**Key Requirements:**
- Must log all important operations
- Must log errors with context
- Must be suitable for Docker (stdout/stderr)
- Must support different log levels
- Must be useful for debugging and monitoring

**Quick Start for Testing:**
```bash
# Run consolidation with logging
python -m src.consolidation_app.main --run-once
# Verify logs are output correctly
# Check Docker logs
docker-compose logs consolidation-app
```

---

**End of Step 5: Code Review & Security Review**

At the end of Step 5, conduct comprehensive review:
- [ ] Code review (Docker setup, configuration, scheduling, logging)
- [ ] Security review (API keys in ENV not code, no secrets in logs, container security)
- [ ] Performance review (container size, startup time, resource usage)
- [ ] Documentation update (README, SER_PLAN.md, PROJECT_STATUS.md, Docker docs, deployment guide)
- [ ] All tests passing
- [ ] Docker container builds and runs correctly
- [ ] Configuration works (ENV-first, YAML optional)
- [ ] Scheduler runs consolidation on schedule
- [ ] Logging is comprehensive and useful

---

## Step 6: Testing and Refinement

> **Comprehensive testing: end-to-end workflows, performance testing, portability testing, and complete documentation.**

**Last Updated:** 2025-01-15  
**Status:** ⬜ Not Started

---

### Phase 6.1: End-to-End Testing ⬜
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** Step 5

**Tasks:**
- [ ] Create end-to-end test scenarios
  - [ ] Scenario 1: Bootstrap new project → Add errors → Run consolidation → Verify files
  - [ ] Scenario 2: Multiple projects → Run consolidation → Verify all processed
  - [ ] Scenario 3: Existing fix_repo.md → Add new errors → Run consolidation → Verify updates
  - [ ] Scenario 4: Agent workflow → Error occurs → Agent looks up fix → Applies fix → Documents
  - [ ] Scenario 5: Process issues → Run consolidation → Verify coding_tips.md generated
- [ ] Create test data
  - [ ] Sample errors_and_fixes.md files
  - [ ] Sample fix_repo.md files
  - [ ] Sample coding_tips.md files
- [ ] Create integration tests
  - [ ] Test full consolidation workflow
  - [ ] Test agent lookup workflow
  - [ ] Test error handling (missing files, malformed data)
- [ ] Run all scenarios
  - [ ] Verify each scenario works correctly
  - [ ] Document any issues found
  - [ ] Fix issues and re-test
- [ ] Create test documentation
  - [ ] Document test scenarios
  - [ ] Document test data
  - [ ] Document how to run tests

**Files to Create:**
```
tests/
└── integration/
    ├── test_e2e_consolidation.py
    ├── test_e2e_agent_workflow.py
    └── test_data/
        ├── sample_errors_and_fixes.md
        ├── sample_fix_repo.md
        └── sample_coding_tips.md
docs/
└── testing_guide.md
```

**Key Requirements:**
- Must test complete workflows end-to-end
- Must test error handling
- Must test with realistic data
- Must be repeatable
- Must be documented

**Quick Start for Testing:**
```bash
# Run end-to-end tests
pytest tests/integration/test_e2e_consolidation.py -v
# Run agent workflow tests (manual + automated)
# Verify all scenarios pass
```

---

### Phase 6.2: Performance Testing ⬜
**Priority:** Important  
**Estimated Time:** 3-4 hours  
**Dependencies:** Step 5

**Tasks:**
- [ ] Create performance test scenarios
  - [ ] Test with 5 projects (small scale)
  - [ ] Test with 20 projects (target scale)
  - [ ] Test with 100 entries per project (stress test)
  - [ ] Test with AI features enabled
  - [ ] Test with AI features disabled (exact match only)
- [ ] Measure performance metrics
  - [ ] Consolidation duration
  - [ ] Memory usage
  - [ ] LLM API call count and duration
  - [ ] File I/O operations
- [ ] Identify bottlenecks
  - [ ] Profile code execution
  - [ ] Identify slow operations
  - [ ] Document findings
- [ ] Optimize if needed
  - [ ] Batch LLM calls
  - [ ] Cache results
  - [ ] Optimize file I/O
- [ ] Create performance benchmarks
  - [ ] Document baseline performance
  - [ ] Document target performance
  - [ ] Document optimization results

**Files to Create:**
```
tests/
└── performance/
    └── test_consolidation_performance.py
docs/
└── performance_benchmarks.md
```

**Key Requirements:**
- Must test at target scale (5-20 projects)
- Must measure key metrics
- Must identify bottlenecks
- Must document benchmarks
- Must be repeatable

**Quick Start for Testing:**
```bash
# Create test projects (5-20)
# Run performance tests
pytest tests/performance/test_consolidation_performance.py -v
# Review performance metrics
# Document benchmarks
```

---

### Phase 6.3: Portability Testing ⬜
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.2, Step 3

**Tasks:**
- [ ] Test bootstrap on new project
  - [ ] Run bootstrap script on fresh project
  - [ ] Verify `.errors_fixes/` folder created
  - [ ] Verify all files created with correct headers
  - [ ] Verify `.gitignore` updated
  - [ ] Test on Windows, Linux, macOS
- [ ] Test consolidation on new project
  - [ ] Add sample errors to `errors_and_fixes.md`
  - [ ] Run consolidation
  - [ ] Verify `fix_repo.md` and `coding_tips.md` are written
  - [ ] Verify `errors_and_fixes.md` is cleared but kept
- [ ] Test copying `.errors_fixes/` folder
  - [ ] Copy folder to new project
  - [ ] Verify files are readable
  - [ ] Verify consolidation still works
- [ ] Test cross-platform compatibility
  - [ ] Test on Windows (paths, line endings)
  - [ ] Test on Linux
  - [ ] Test on macOS
- [ ] Create portability guide
  - [ ] Document bootstrap process
  - [ ] Document copying process
  - [ ] Document platform-specific considerations
  - [ ] Document troubleshooting

**Files to Create:**
```
docs/
└── portability_guide.md
```

**Key Requirements:**
- Must work on Windows, Linux, macOS
- Must handle path differences correctly
- Must handle line ending differences (LF)
- Must be documented clearly
- Must be tested on all platforms

**Quick Start for Testing:**
```bash
# Test bootstrap on new project
python scripts/bootstrap_errors_fixes.py /tmp/new_project
# Verify folder structure
# Test consolidation
# Test on different platforms
```

---

### Phase 6.4: Documentation ⬜
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** All previous steps

**Tasks:**
- [ ] Update `README.md`
  - [ ] Project overview
  - [ ] Quick start guide
  - [ ] Installation instructions
  - [ ] Usage instructions
  - [ ] Configuration guide
  - [ ] Troubleshooting
- [ ] Create user documentation
  - [ ] How to bootstrap a project
  - [ ] How to use agent rules
  - [ ] How to run consolidation
  - [ ] How to view consolidated fixes
  - [ ] How to add errors manually (if needed)
- [ ] Create developer documentation
  - [ ] Architecture overview
  - [ ] Module documentation
  - [ ] API documentation
  - [ ] Contributing guide
- [ ] Create deployment documentation
  - [ ] Docker setup
  - [ ] Configuration
  - [ ] Scheduling
  - [ ] Monitoring
- [ ] Update `SER_PLAN.md` with implementation status
- [ ] Update `PROJECT_STATUS.md` with current status
- [ ] Create changelog
  - [ ] Document all features
  - [ ] Document breaking changes
  - [ ] Document version history

**Files to Create/Modify:**
```
README.md (update)
docs/
├── user_guide.md
├── developer_guide.md
├── deployment_guide.md
└── CHANGELOG.md
docs/
└── SER_PLAN.md (update)
docs/
└── PROJECT_STATUS.md (update)
```

**Key Requirements:**
- Must be comprehensive and clear
- Must cover all use cases
- Must include examples
- Must be up-to-date with implementation
- Must be accessible to users and developers

**Quick Start for Testing:**
```bash
# Review all documentation
# Verify examples work
# Check for broken links
# Update as needed
```

---

**End of Step 6: Code Review & Security Review**

At the end of Step 6, conduct comprehensive review:
- [ ] Code review (final architecture, all modules, test coverage)
- [ ] Security review (complete security audit, no vulnerabilities)
- [ ] Performance review (meets performance targets, optimized)
- [ ] Documentation review (complete, accurate, clear)
- [ ] All tests passing (unit, integration, performance, portability)
- [ ] System is production-ready
- [ ] All documentation is complete
- [ ] Project status is updated

---

## Implementation Notes

### Dependencies Between Steps

**Step 1 Dependencies:**
- Phase 1.1 → Required for all other phases (defines formats)
- Phase 1.2 → Required for onboarding (bootstrap script)
- Phase 1.3 → Required for Step 3 (parser)
- Phase 1.4 → Required for Step 3 (generators)

**Step 2 Dependencies:**
- Requires Step 1 complete (file formats defined)
- Phase 2.1 → Required for agent error resolution
- Phase 2.2 → Required for proactive prevention
- Phase 2.3 → Required for test output capture
- Phase 2.4 → Optional (command-based workflow)
- Phase 2.5 → Requires 2.1, 2.2, 2.3

**Step 3 Dependencies:**
- Requires Step 1 complete (parser, generators)
- Phase 3.1 → Required for all other phases (discovery)
- Phase 3.2 → Requires 3.1 (discovery)
- Phase 3.3 → Requires 3.2 (parsing)
- Phase 3.4 → Requires 3.2 (parsing)
- Phase 3.5 → Requires 1.4, 3.3, 3.4 (generators, dedup, tags)
- Phase 3.6 → Requires all 3.1-3.5

**Step 4 Dependencies:**
- Requires Step 3 complete (core consolidation)
- Phase 4.1 → Required for all AI features
- Phase 4.2 → Requires 4.1, 3.3 (LLM, basic dedup)
- Phase 4.3 → Requires 4.1, 3.4 (LLM, basic tagging)
- Phase 4.4 → Requires 3.3 (basic dedup)
- Phase 4.5 → Requires 4.1, 3.2 (LLM, parsing)

**Step 5 Dependencies:**
- Requires Step 3 and Step 4 complete (full consolidation app)
- Phase 5.1 → Required for deployment
- Phase 5.2 → Requires 5.1 (Docker)
- Phase 5.3 → Requires 5.1, 5.2 (Docker, config)
- Phase 5.4 → Requires 5.1 (Docker)

**Step 6 Dependencies:**
- Requires all previous steps complete
- All phases can be done in parallel after dependencies met

### Recommended Implementation Order

1. **Step 1:** Foundation must be done first
   - 1.1 → 1.2 → 1.3 → 1.4 (sequential)
2. **Step 2:** Agent integration (can start after 1.1)
   - 2.1, 2.2 can be done in parallel
   - 2.3 can be done independently
   - 2.4 is optional
   - 2.5 requires 2.1, 2.2, 2.3
3. **Step 3:** Core consolidation (requires Step 1)
   - 3.1 → 3.2 → then 3.3, 3.4 can be parallel → 3.5 → 3.6
4. **Step 4:** AI features (requires Step 3)
   - 4.1 → then 4.2, 4.3, 4.4, 4.5 can be done in parallel
5. **Step 5:** Docker and deployment (requires Step 3, 4)
   - 5.1 → 5.2 → 5.3 → 5.4 (sequential)
6. **Step 6:** Testing and docs (requires all steps)
   - All phases can be done in parallel

### Testing Strategy

**After Each Phase:**
- [ ] Run unit tests for new functionality
- [ ] Run existing tests to ensure nothing broke
- [ ] Manual testing of new features
- [ ] Verify error handling works
- [ ] Check code quality (formatting, linting)

**After Each Step:**
- [ ] Comprehensive code review
- [ ] Security review
- [ ] Performance review (if applicable)
- [ ] Documentation update
- [ ] Integration testing
- [ ] Fix any bugs before proceeding

### Documentation Updates

**As items are completed:**
- [ ] Update `README.md` with new features
- [ ] Update `docs/SER_PLAN.md` with implementation status
- [ ] Update `docs/PROJECT_STATUS.md` with progress
- [ ] Create/update user guides
- [ ] Create/update developer guides
- [ ] Document setup and deployment process
- [ ] Update changelog

### Security Review Schedule

Security reviews are conducted at key milestones after each Step:

- ⏸️ **Step 1 (Core File Formats):** Security review before proceeding
  - Verify file path handling (no directory traversal)
  - Test input validation (no code injection)
  - Review file permissions
  - Validate bootstrap script security

- ⏸️ **Step 2 (Agent Integration):** Security review
  - Verify rule descriptions (no code injection)
  - Test file path handling in rules
  - Review test output capture (no command injection)
  - Validate agent workflow security

- ⏸️ **Step 3 (Consolidation Core):** Security review
  - Verify file access controls
  - Test input validation (markdown parsing)
  - Review error handling (no information leakage)
  - Validate writer module security

- ⏸️ **Step 4 (AI Integration):** Security review
  - Verify API key handling (no secrets in logs)
  - Test LLM prompt security (no injection)
  - Review error handling (no API key leakage)
  - Validate cost tracking

- ⏸️ **Step 5 (Docker/Config):** Security review
  - Verify container security
  - Test configuration security (no secrets in code)
  - Review scheduler security
  - Validate logging security (no secrets)

- ⏸️ **Pre-Production:** Full security audit required
  - Complete penetration testing
  - Security checklist review
  - Compliance verification
  - Infrastructure security review

**Note:** Security is a continuous concern. While foundation patterns are established, critical security features must be verified as they're implemented and before production deployment.

---

## Progress Summary

**Step 1 (Core File Formats and Bootstrap):** 2/4 completed (50%) - 1.1 ✅, 1.2 ✅, 1.3 ⬜, 1.4 ⬜  
**Step 2 (Agent Integration):** 0/5 completed (0%) - 2.1 ⬜, 2.2 ⬜, 2.3 ⬜, 2.4 ⬜, 2.5 ⬜  
**Step 3 (Consolidation App - Core):** 0/6 completed (0%) - 3.1 ⬜, 3.2 ⬜, 3.3 ⬜, 3.4 ⬜, 3.5 ⬜, 3.6 ⬜  
**Step 4 (Consolidation App - AI):** 0/5 completed (0%) - 4.1 ⬜, 4.2 ⬜, 4.3 ⬜, 4.4 ⬜, 4.5 ⬜  
**Step 5 (Docker/Config/Scheduling):** 0/4 completed (0%) - 5.1 ⬜, 5.2 ⬜, 5.3 ⬜, 5.4 ⬜  
**Step 6 (Testing and Refinement):** 0/4 completed (0%) - 6.1 ⬜, 6.2 ⬜, 6.3 ⬜, 6.4 ⬜  
**Overall Progress:** 2/28 completed (7%)

**Blocked Items:**
- None currently

---

**Notes:**
- Update status emoji (⬜/🟡/✅) as you work through items
- Add completion dates when items are finished
- Document any blockers or issues encountered
- Update estimated times based on actual experience
- This document serves as the PROJECT_STATUS.md equivalent for tracking SER development progress
