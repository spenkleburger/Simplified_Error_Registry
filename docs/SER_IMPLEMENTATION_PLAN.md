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

### Phase 1.4: Implement Basic Generators ✅
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.1, Phase 1.3  
**Completed:** 2026-01-21

**Tasks:**
- [x] Create `src/consolidation_app/generator.py`
  - [x] Function `generate_fix_repo_markdown(entries: List[ErrorEntry]) -> str`
    - [x] Filter entries where `is_process_issue=False`
    - [x] Group by error signature (exact match for now)
    - [x] Generate header with metadata
    - [x] Generate entry sections with fixes ordered by success count
    - [x] Format code blocks, tags, metadata
  - [x] Function `generate_coding_tips_markdown(entries: List[ErrorEntry]) -> str`
    - [x] Filter entries where `is_process_issue=True`
    - [x] Group by rule category (extract from tags or issue type)
    - [x] Generate header with metadata
    - [x] Generate rule sections with examples
    - [x] Format good/bad examples
  - [x] Helper functions
    - [x] `format_code_block(code: str, language: str = "python") -> str`
    - [x] `format_tags(tags: List[str]) -> str`
    - [x] `format_timestamp(dt: datetime) -> str`
- [x] Create unit tests
  - [x] Test fix_repo generation with single entry
  - [x] Test fix_repo generation with multiple entries (same error)
  - [x] Test fix_repo generation with multiple entries (different errors)
  - [x] Test coding_tips generation with process issues
  - [x] Test empty entries (generate headers only)

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
pytest tests/test_consolidation_app_generator.py
```

**Implementation Notes:**
- `generate_fix_repo_markdown` groups entries by signature, reports aggregated metadata, and formats fix blocks with consistent code/timestamp formatting.
- `generate_coding_tips_markdown` organizes agent rules by tag-derived categories and captures rationale, examples, and related errors for each rule.
- Helper utilities enforce markdown-safe code blocks, tag lists, and ISO8601 timestamps while the new test suite guards grouping logic, ordering, and empty inputs.

---

**End of Step 1: Code Review & Security Review** ✅

At the end of Step 1, conduct comprehensive review:
- [x] Code review (architecture, best practices, maintainability) - Completed 2026-01-21
- [x] Security review (file path handling, input validation, no code injection risks) - Completed 2026-01-21
  - Tag escaping implemented (prevents markdown injection via backticks)
  - Header escaping implemented (prevents markdown injection in error signatures)
  - Logging added for debugging and troubleshooting
- [x] Performance review (parser efficiency, generator output size) - Completed 2026-01-21
  - Efficient grouping with defaultdict
  - Minimal string operations (list building, single join)
  - Acceptable for personal scale (< 500 entries)
- [x] Documentation update (README, API docs, SER_PLAN.md, PROJECT_STATUS.md) - Completed 2026-01-21
  - API_REFERENCE.md created with full module documentation
  - README.md updated with Step 1 completion
  - SER_PLAN.md updated with Step 1 status
  - PROJECT_STATUS.md updated with progress tracking
- [x] All tests passing - Completed 2026-01-21
  - Unit tests for all generator functions
  - Edge case coverage (tag escaping, header escaping, timezone handling, empty fields)
- [x] Bootstrap script works on Windows, Linux, macOS - Verified in Phase 1.2
- [x] Parser handles all edge cases - Verified in Phase 1.3
- [x] Generators produce valid markdown - Verified in Phase 1.4
  - Markdown-safe output with proper escaping
  - Handles empty inputs gracefully
  - v1 limitations documented in code comments

---

## Step 2: Agent Integration and Test Output Verification

> **Create Cursor rules for error resolution and proactive coding tips, verify test output capture, and test end-to-end agent workflow.**

**Last Updated:** 2026-01-21  
**Status:** 🟡 In Progress (3/5 phases complete)

---

### Phase 2.1: Create errors.mdc Rule ✅
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** Phase 1.1  
**Completed:** 2025-01-15

**Tasks:**
- [x] Create `.cursor/rules/global/errors.mdc`
  - [x] **CRITICAL:** Craft precise frontmatter description
    - [x] Do NOT use `alwaysApply: true`
    - [x] Description must trigger on: pasted test errors, "There is an error in...", test failure output, "fix this error"
    - [x] Test description with various user error reporting scenarios
  - [x] Add "Role" section (Responder: User runs tests, agent provides code)
  - [x] Add "Test Generation Requirements" section
    - [x] Generate tests for new/modified code
    - [x] Test file naming conventions
    - [x] Test coverage requirements (happy path, edge cases, mocked calls)
  - [x] Add "Advise Test Commands" section
    - [x] Identify code type (backend/frontend/integration)
    - [x] Advise appropriate test command (`task test:backend`, etc.)
    - [x] Format of advice
  - [x] Add "Test Execution Strategy" section
    - [x] Default: Manual (do NOT run tests automatically)
    - [x] Optional: Command-based auto-fix (when user runs test-and-fix command)
  - [x] Add "Lookup Strategy" section
    - [x] Three-step lookup order: errors_and_fixes.md → fix_repo.md → coding_tips.md
    - [x] When to use each file
  - [x] Add "Fix Application Workflow" section
    - [x] Step 1: Identify error
    - [x] Step 2: Lookup fixes (see Lookup Strategy)
    - [x] Step 3: Apply fix (highest success count first)
    - [x] Step 4: Document result
    - [x] Step 5: Advise test commands
    - [x] Step 6: Session tracking
  - [x] Add "Preventive Checks" section
    - [x] Check coding_tips.md before writing code
    - [x] Apply process rules proactively
  - [x] Add "Process Rules" section
    - [x] Reference coding_tips.md for current rules
    - [x] Common rules list
  - [x] Add "Validation" section
    - [x] Manual mode: ask user to run tests
    - [x] Command mode: run tests automatically with safety limits
- [x] Test rule triggering
  - [x] Verify triggers on pasted test errors
  - [x] Verify triggers on "There is an error in..." phrases
  - [x] Verify does NOT trigger on non-error scenarios
  - [x] Document trigger scenarios

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

### Phase 2.2: Create coding-tips.mdc Rule ✅
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 1.1  
**Completed:** 2025-01-15

**Tasks:**
- [x] Create `.cursor/rules/global/coding-tips.mdc`
  - [x] **CRITICAL:** Craft precise frontmatter description
    - [x] Do NOT use `alwaysApply: true`
    - [x] Description must trigger on: "write code", "create file", "use file path", "run command", "Docker"
    - [x] Test description with various code writing scenarios
  - [x] Add "Coding Tips Reference" section
    - [x] Check `.errors_fixes/coding_tips.md` before coding
    - [x] List of rule categories (path handling, commands, formatting, Docker)
    - [x] Proactive prevention emphasis
  - [x] Add examples of when to check
    - [x] Before writing code
    - [x] Before using file paths
    - [x] Before running commands
    - [x] Before Docker work
- [x] Test rule triggering
  - [x] Verify triggers on "write code" requests
  - [x] Verify triggers on "create file" requests
  - [x] Verify triggers on "use file path" requests
  - [x] Verify does NOT trigger on non-coding scenarios
  - [x] Document trigger scenarios

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

### Phase 2.3: Test Output Capture Verification ✅
**Priority:** Important  
**Estimated Time:** 2-3 hours  
**Dependencies:** None  
**Completed:** 2026-01-21

**Tasks:**
- [x] Inspect `task test:*` commands in `pyproject.toml`
  - [x] Identify Python scripts that copy test output
  - [x] Review `scripts/test_backend.py`, `scripts/test_frontend.py`, `scripts/test_integration.py`
- [x] Verify test output capture logic
  - [x] Ensure scripts capture `=== FAILURES ===` or `=== ERRORS ===` section
  - [x] Ensure scripts capture `=== short test summary info ===` section
  - [x] Verify scripts do NOT capture irrelevant sections (passing tests, collection info)
- [x] Test with actual failing tests
  - [x] Run `task test:backend` with failing tests
  - [x] Check clipboard contents
  - [x] Verify required sections are present (FAILURES and summary sections confirmed)
  - [x] Run `task test:frontend` with failing tests (Vitest format verified - FAIL markers captured)
  - [x] Run `task test:integration` with failing tests (pytest format verified - ERRORS and summary sections captured correctly)
- [x] Update scripts if needed
  - [x] Fix capture logic if wrong sections are copied
  - [x] Document which sections are required
  - [x] Enhanced error handling in clipboard functions (specific exception types)
  - [x] Extracted project-specific code to constants for better maintainability
  - [x] Improved documentation for template extraction
- [x] Document required test output sections
  - [x] Create documentation in `docs/` or update existing docs
  - [x] Explain why these sections are needed (agent error identification)
- [x] Code review improvements (2026-01-21)
  - [x] Added coverage.xml to .gitignore
  - [x] Expanded .gitattributes for better line ending handling
  - [x] Enhanced clipboard error handling with specific exception types
  - [x] Extracted project-specific code to VERIFICATION_TEST_FILE constant
  - [x] Improved code documentation for template extraction

**Files to Modify:**
```
scripts/
├── test_backend.py (enhanced error handling)
├── test_frontend.py (enhanced error handling)
└── test_integration.py (enhanced error handling, project-specific code extraction)
.gitignore (added coverage.xml)
.gitattributes (expanded text file type coverage)
docs/
└── TEST_OUTPUT_CAPTURE.md
```

**Files Created:**
```
docs/
└── TEST_OUTPUT_CAPTURE.md (comprehensive documentation)
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

### Phase 2.4: Create Optional test-and-fix.mdc Command ✅
**Priority:** Nice to Have  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 2.1  
**Completed:** 2025-01-15

**Tasks:**
- [x] Create `.cursor/commands/global/test-and-fix.mdc`
  - [x] Add frontmatter description
  - [x] Add "Workflow" section
    - [x] Step 1: Determine test command
    - [x] Step 2: Run tests
    - [x] Step 3: Check results
    - [x] Step 4: Fix loop (max 5 iterations)
    - [x] Step 5: Final report
  - [x] Add "Safety Limits" section
    - [x] Maximum iterations: 5
    - [x] Same error retry limit: 3
    - [x] Stop conditions
  - [x] Add "Documentation" section
    - [x] Document in errors_and_fixes.md
    - [x] What to document (error, fix, result, success count, test command)
- [x] Note: This is optional/backup - primary workflow uses errors.mdc rule

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

### Phase 2.5: End-to-End Agent Workflow Testing 🟡
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 2.1, Phase 2.2, Phase 2.3  
**Completed:** 2026-01-21 (Manual workflow complete, remaining tests optional)

**Tasks:**
- [x] Test manual workflow ✅ **COMPLETED**
  - [x] Agent writes code → generates tests → advises test command ✅ Verified
  - [x] User runs test command → provides error output ✅ Completed 2026-01-21
  - [x] Agent checks lookup order → applies fix → documents ✅ Verified
  - [x] User runs test again → tests pass ✅ Verified 2026-01-21
  - [x] Agent documents success ✅ Completed
- [ ] Test command-based workflow (optional - if test-and-fix.mdc created)
  - [ ] User runs test-and-fix command (requires command execution)
  - [ ] Agent runs tests automatically (ready for testing)
  - [ ] Agent fixes all errors (ready for testing)
  - [ ] Agent documents all fixes (ready for testing)
  - [ ] Agent reports final status (ready for testing)
- [x] Test proactive coding_tips.md usage ✅ **COMPLETED**
  - [x] Request agent to write code ✅ Verified
  - [x] Verify agent checks coding_tips.md before coding ✅ Verified (file checked, empty as expected)
  - [x] Verify agent applies process rules ✅ Verified (best practices applied)
- [x] Test error scenarios (test data created and verified)
  - [x] Error in errors_and_fixes.md (recent session) ✅ Test data created and verified in manual workflow
  - [x] Error in fix_repo.md (consolidated fix) ✅ Test data created (ready for testing)
  - [x] No fix found (agent creates new fix) ✅ Verified in manual workflow (agent created new fix entry)
  - [x] Multiple fixes (agent tries highest success count first) ✅ Test data created (ready for testing)
- [x] Document test results ✅ **COMPLETED**
  - [x] Create test scenarios document ✅ Created `docs/agent_workflow_tests.md`
  - [x] Document any issues found ✅ Documented in test file
  - [x] Update agent rules if needed ✅ No issues found requiring updates

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

**Implementation Summary:**

✅ **Completed (2026-01-21):**
- Manual workflow fully tested and verified:
  - Agent created code and tests
  - User provided error output
  - Agent followed three-step lookup order correctly
  - Agent applied fix successfully
  - Tests passed after fix
  - Documentation updated with success
- Proactive coding_tips.md usage verified
- Error scenario test data created and verified
- Comprehensive test documentat22ion created

**Test Results:**
- ✅ Manual workflow: Complete cycle tested and verified
- ✅ Lookup order: Three-step lookup verified (errors_and_fixes.md → fix_repo.md → coding_tips.md)
- ✅ Fix application: Fix applied correctly and test passed
- ✅ Documentation: All fixes documented in errors_and_fixes.md

**Remaining Optional Tests:**
- Command-based workflow (test-and-fix.mdc): Optional automated workflow testing
- Multiple fixes scenario: Test data ready, can be tested when needed

**Status:** Phase 2.5 core objectives complete. Manual workflow fully functional and verified.

---

**End of Step 2: Code Review & Security Review**

At the end of Step 2, conduct comprehensive review:
- [x] Code review (rule descriptions, workflow logic, test coverage) - Completed 2026-01-21
  - Rule descriptions verified (errors.mdc, coding-tips.mdc trigger correctly)
  - Workflow logic verified (three-step lookup order, fix application, documentation)
  - Test scripts reviewed (error handling, project-specific code extraction, clipboard operations)
  - Code improvements implemented (enhanced error handling, better documentation)
- [x] Security review (no code injection in rules, safe file paths) - Completed 2026-01-21
  - Rule files contain only markdown descriptions (no executable code)
  - Test scripts use safe subprocess calls with static arguments
  - File paths validated (git commands, trusted local paths)
  - Clipboard operations use safe system commands (clip, pbcopy, xclip)
  - No user-controlled input passed to subprocess
- [x] Performance review (rule triggering efficiency, no token bloat) - Completed 2026-01-21
  - Rule frontmatter descriptions are precise (no alwaysApply: true)
  - Rules trigger only on relevant scenarios (error reports, code writing)
  - Test output capture filters irrelevant sections (reduces token usage)
  - Lookup order optimized (session → consolidated → rules)
- [x] Documentation update (README, SER_PLAN.md, PROJECT_STATUS.md, agent workflow docs) - Completed 2026-01-21
  - README.md updated with Step 2 progress and status
  - PROJECT_STATUS.md updated with milestones and phase completion
  - SER_IMPLEMENTATION_PLAN.md updated with Phase 2.3 improvements
  - TEST_OUTPUT_CAPTURE.md updated with error handling details
  - agent_workflow_tests.md created with comprehensive test scenarios
- [x] All tests passing - Completed 2026-01-21
  - Test output capture verified in all three test scripts
  - Error extraction logic verified (FAILURES, ERRORS, summary sections)
  - Clipboard operations tested and working
  - Project-specific code properly documented
- [x] Agent rules trigger correctly - Completed 2026-01-21
  - errors.mdc triggers on error scenarios (verified in Phase 2.5)
  - coding-tips.mdc triggers on code writing scenarios (verified in Phase 2.5)
  - Rules do not trigger on irrelevant scenarios (verified)
- [x] Test output capture works correctly - Completed 2026-01-21
  - Backend test output capture verified (pytest format)
  - Frontend test output capture verified (Vitest format)
  - Integration test output capture verified (pytest format)
  - Error sections extracted correctly (FAILURES, ERRORS, summary)
  - Clipboard copy functionality working
  - Enhanced error handling implemented
- [x] End-to-end workflows function correctly - Completed 2026-01-21
  - Manual workflow tested and verified (Phase 2.5)
  - Agent follows three-step lookup order correctly
2222222
---

## Step 3: Consolidation App - Core

> **Build core consolidation app: discovery, parser integration, basic deduplication (exact match), basic tagging (rule-based), writer module, and cleanup.**

**Last Updated:** 2026-01-21  
**Status:** ✅ Complete

---

### Phase 3.1: Discovery Module ✅
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.2  
**Completed:** 2026-01-21

**Tasks:**
- [x] Create `src/consolidation_app/discovery.py`
  - [x] Function `discover_projects(root_path: Path, extra_projects: list[str] | None = None) -> list[Path]`
    - [x] Use `rglob('.errors_fixes/errors_and_fixes.md')` to find projects
    - [x] For each found path, get project root (path.parent.parent)
    - [x] For `extra_projects` list:
      - [x] Resolve each path
      - [x] Check if `errors_and_fixes.md` exists
      - [x] If missing, call `bootstrap(project_root, update_gitignore=False)`
      - [x] Add to projects list
    - [x] Deduplicate projects (use `dict.fromkeys()`)
    - [x] Return list of project roots
  - [x] Add error handling
    - [x] Handle missing root_path
    - [x] Handle permission errors
    - [x] Handle invalid extra_projects paths
  - [x] Add logging for discovery process
- [x] Create unit tests
  - [x] Test rglob discovery
  - [x] Test extra_projects with existing errors_and_fixes.md
  - [x] Test extra_projects with missing errors_and_fixes.md (auto-bootstrap)
  - [x] Test deduplication
  - [x] Test e22
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

### Phase 3.2: Parser Integration ✅
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 1.3, Phase 3.1

**Tasks:**
- [x] Integrate parser into consolidation workflow
  - [x] Read `errors_and_fixes.md` for each discovered project
  - [x] Parse entries using parser from Phase 1.3
  - [x] Separate entries by `is_process_issue` flag
  - [x] Group entries by project for tracking
- [x] Add error handling
  - [x] Handle missing files (skip project, log warning)
  - [x] Handle parse errors (log error, continue with other projects)
  - [x] Handle empty files (return empty list)
- [x] Add logging for parsing process
  - [x] Log number of projects processed
  - [x] Log number of entries parsed per project
  - [x] Log any errors encountered

**Files to Create/Modify:**
```
src/
└── consolidation_app/
    └── consolidation.py   # process_projects, ProjectEntries
tests/
└── test_consolidation_app_consolidation.py
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

### Phase 3.3: Basic Deduplication (Exact Match) ✅
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 3.2  
**Completed:** 2026-01-21

**Tasks:**
- [x] Create `src/consolidation_app/deduplicator.py`
  - [x] Function `deduplicate_errors_exact(new_entries: List[ErrorEntry], existing_entries: List[ErrorEntry]) -> List[ErrorEntry]`
    - [x] For each new entry, check if exact match exists in existing entries
    - [x] Match criteria: error_signature (exact), error_type (exact), file (exact)
    - [x] If match found: merge into existing entry (increment success count if fix is same)
    - [x] If no match: add as new entry
    - [x] Return consolidated list
  - [x] Function `merge_entries(existing: ErrorEntry, new: ErrorEntry) -> ErrorEntry`
    - [x] Update last_seen timestamp (use newer timestamp)
    - [x] Increment total_occurrences (sum success counts)
    - [x] If fix code is same: increment success count
    - [x] If fix code is different: add as variant fix (keep both entries)
  - [x] Handle edge cases
    - [x] Empty lists
    - [x] No matches
    - [x] Multiple matches (handled via lookup dict update)
- [x] Create unit tests
  - [x] Test exact match deduplication
  - [x] Test no match (new entry)
  - [x] Test same fix (increment success count)
  - [x] Test different fix (add as variant)
  - [x] Test empty lists

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

### Phase 3.4: Basic Tagging (Rule-Based) ✅
**Priority:** Important  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 3.2  
**Completed:** 2026-01-21

**Tasks:**
- [x] Create `src/consolidation_app/tagger.py`
  - [x] Function `generate_tags_rule_based(entry: ErrorEntry) -> List[str]`
    - [x] Extract error type tag (from error_type field)
    - [x] Extract framework/library tag (from file path or error context)
      - [x] Check for common frameworks (docker, django, flask, etc.)
    - [x] Extract domain tag (from error context or file location)
      - [x] networking, file-io, database, authentication, etc.
    - [x] Extract platform tag (from error message or file path)
      - [x] windows, linux, cross-platform
    - [x] Return list of tags
  - [x] Define tag rules
    - [x] Error type mapping (FileNotFoundError → file-io, TypeError → type-conversion, etc.)
    - [x] Framework detection (check file paths, imports, error context)
    - [x] Domain detection (check file locations, error context)
    - [x] Platform detection (check error messages, file paths)
  - [x] Handle edge cases
    - [x] Unknown error types (use generic tag)
    - [x] No framework detected (skip framework tag)
- [x] Create unit tests
  - [x] Test error type tagging
  - [x] Test framework detection
  - [x] Test domain detection
  - [x] Test platform detection
  - [x] Test edge cases

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

### Phase 3.5: Writer Module ✅
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1.4, Phase 3.3, Phase 3.4  
**Completed:** 2026-01-21

**Tasks:**
- [x] Create `src/consolidation_app/writer.py`
  - [x] Function `write_fix_repo(project_path: Path, consolidated_entries: List[ErrorEntry]) -> None`
    - [x] Filter entries where `is_process_issue=False`
    - [x] Generate markdown using generator from Phase 1.4
    - [x] Write to `project_path/.errors_fixes/fix_repo.md`
    - [x] Create directory if missing
    - [x] Use UTF-8 encoding, LF line endings
  - [x] Function `write_coding_tips(project_path: Path, process_entries: List[ErrorEntry]) -> None`
    - [x] Filter entries where `is_process_issue=True`
    - [x] Generate markdown using generator from Phase 1.4
    - [x] Write to `project_path/.errors_fixes/coding_tips.md`
    - [x] Create directory if missing
    - [x] Use UTF-8 encoding, LF line endings
  - [x] Function `clear_errors_and_fixes(project_path: Path) -> None`
    - [x] Read current `errors_and_fixes.md`
    - [x] Replace contents with header only
    - [x] Keep file (don't delete)
    - [x] Use UTF-8 encoding, LF line endings
  - [x] Add error handling
    - [x] Handle permission errors
    - [x] Handle missing directories
    - [x] Handle write failures
  - [x] Add logging for write operations
- [x] Create unit tests
  - [x] Test write_fix_repo
  - [x] Test write_coding_tips
  - [x] Test clear_errors_and_fixes
  - [x] Test error handling

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

**Implementation Notes:**
- `write_fix_repo` filters non-process-issue entries, generates markdown via `generate_fix_repo_markdown`, and writes to `.errors_fixes/fix_repo.md` with UTF-8 encoding and LF line endings.
- `write_coding_tips` filters process-issue entries, generates markdown via `generate_coding_tips_markdown`, and writes to `.errors_fixes/coding_tips.md` with UTF-8 encoding and LF line endings.
- `clear_errors_and_fixes` preserves the header from bootstrap template and clears all content, keeping the file structure intact.
- All functions create directories if missing, handle permission errors and OSErrors gracefully, and include comprehensive logging.
- Unit tests cover file creation, directory creation, filtering, line endings, error handling, and edge cases (empty entries, missing files).

---

### Phase 3.6: Main Consolidation Workflow ✅
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Dependencies:** Phase 3.1, Phase 3.2, Phase 3.3, Phase 3.4, Phase 3.5  
**Completed:** 2026-01-21

**Tasks:**
- [x] Create `src/consolidation_app/main.py`
  - [x] Function `consolidate_all_projects(root_path: Path, extra_projects: list[str] | None = None) -> ConsolidationResult`
    - [x] Discover projects (Phase 3.1)
    - [x] For each project:
      - [x] Parse errors_and_fixes.md (Phase 3.2)
      - [x] Read existing fix_repo.md (if exists) and parse
      - [x] Read existing coding_tips.md (if exists) and parse
      - [x] Deduplicate errors (Phase 3.3)
      - [x] Generate tags (Phase 3.4)
      - [x] Merge fixes by success count
      - [x] Write fix_repo.md (Phase 3.5)
      - [x] Write coding_tips.md (Phase 3.5)
      - [x] Clear errors_and_fixes.md (Phase 3.5)
    - [x] Log summary statistics
  - [x] Add error handling
    - [x] Continue processing other projects if one fails
    - [x] Log errors for each project
    - [x] Return success/failure status
  - [x] Add command-line interface
    - [x] `--root` argument for projects root
    - [x] `--config` argument for config file (optional)
    - [x] `--dry-run` flag (don't write files, just log)
- [x] Create unit tests
  - [x] Test full consolidation workflow
  - [x] Test error handling (one project fails, others continue)
  - [x] Test dry-run mode
- [x] Create integration tests
  - [x] Test with multiple projects
  - [x] Test with existing fix_repo.md and coding_tips.md
  - [x] Test with empty projects

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
- [x] Code review (architecture, module organization, error handling) - Completed 2026-01-21
- [x] Security review (file path handling, input validation, no code injection) - Completed 2026-01-21
  - [x] Atomic writes implemented (temp file + rename pattern)
  - [x] Path validation for extra_projects (rejects traversal patterns)
  - [x] Input validation and error handling verified
- [ ] Performance review (processing time for 5-20 projects, memory usage) - Deferred to Step 6
- [x] Documentation update (README, SER_PLAN.md, PROJECT_STATUS.md, consolidation app docs) - Completed 2026-01-21
- [x] All tests passing - Completed 2026-01-21 (93 tests passing)
- [x] Consolidation workflow processes all projects correctly - Verified 2026-01-21
- [x] Consolidated files are valid and useful - Verified 2026-01-21
- [x] Error handling is robust - Verified 2026-01-21

**Security Improvements Implemented (2026-01-21):**
- **Atomic Writes:** All file writes use temp file + atomic rename pattern to prevent partial writes on interruption
- **Path Validation:** `extra_projects` paths are validated to reject directory traversal patterns (`../..`, `..\\..`, etc.)
- **Error Isolation:** Per-project failures don't stop processing of other projects
- **Comprehensive Logging:** All operations logged with appropriate levels (DEBUG, INFO, WARNING, ERROR)

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
- [x] Update `README.md` with new features - Completed 2026-01-21
- [x] Update `docs/SER_PLAN.md` with implementation status - Completed 2026-01-21
- [x] Update `docs/PROJECT_STATUS.md` with progress - Completed 2026-01-21
- [x] Create/update API documentation - Completed 2026-01-21 (`docs/API_REFERENCE.md`)
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

**Step 1 (Core File Formats and Bootstrap):** 4/4 completed (100%) ✅ - 1.1 ✅, 1.2 ✅, 1.3 ✅, 1.4 ✅  
**Step 2 (Agent Integration):** 4.8/5 completed (96%) - 2.1 ✅, 2.2 ✅, 2.3 ✅ (verified), 2.4 ✅, 2.5 🟡 (manual workflow complete, command-based workflow optional)  
**Step 3 (Consolidation App - Core):** 5/6 completed (83%) - 3.1 ✅, 3.2 ✅, 3.3 ✅, 3.4 ✅, 3.5 ✅, 3.6 ⬜  
**Step 4 (Consolidation App - AI):** 0/5 completed (0%) - 4.1 ⬜, 4.2 ⬜, 4.3 ⬜, 4.4 ⬜, 4.5 ⬜  
**Step 5 (Docker/Config/Scheduling):** 0/4 completed (0%) - 5.1 ⬜, 5.2 ⬜, 5.3 ⬜, 5.4 ⬜  
**Step 6 (Testing and Refinement):** 0/4 completed (0%) - 6.1 ⬜, 6.2 ⬜, 6.3 ⬜, 6.4 ⬜  
**Overall Progress:** 13/28 completed (46%)

**Blocked Items:**
- None currently

---

**Notes:**
- Update status emoji (⬜/🟡/✅) as you work through items
- Add completion dates when items are finished
- Document any blockers or issues encountered
- Update estimated times based on actual experience
- This document serves as the PROJECT_STATUS.md equivalent for tracking SER development progress
