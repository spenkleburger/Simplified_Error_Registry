# Simplified Error Registry (SER)

> **A streamlined, markdown-based approach for personal-scale error tracking and agent process documentation**

**Status:** 🟡 Design Phase  
**Last Updated:** 2025-01-15

---

## Overview

The Simplified Error Registry (SER) replaces complex JSON-based error tracking systems with a simple, human-readable markdown-based approach optimized for personal projects. The system tracks runtime/test errors and agent process issues, consolidates them daily using AI, and provides actionable fixes and coding tips.

### Key Features

- **Human-Readable Markdown:** Easy to read, edit, and understand (no JSON complexity)
- **AI-Powered Consolidation:** Semantic deduplication and intelligent tagging using LLM
- **Success-Based Ordering:** Fixes ordered by success count (most successful tried first)
- **Agent Process Tracking:** Built-in documentation of agent workflow issues
- **Self-Contained:** Single `.errors_fixes/` folder can be copied to any project
- **Portable:** Bootstrap script enables quick onboarding (< 1 minute)

### System Architecture

The system uses three main files in each project's `.errors_fixes/` folder:

1. **`errors_and_fixes.md`** - Session log (ephemeral, cleared after consolidation)
2. **`fix_repo.md`** - Consolidated fixes (read-only during dev, updated by consolidation app)
3. **`coding_tips.md`** - Agent process rules (read-only during dev, updated by consolidation app)

A daily consolidation app processes session logs, deduplicates errors, generates tags, and produces consolidated files. Agent integration is provided via Cursor rules for proactive error prevention and reactive error resolution.

---

## Quick Start

### 1. Bootstrap a New Project

```bash
# Run bootstrap script to create .errors_fixes/ folder structure
python scripts/bootstrap_errors_fixes.py /path/to/your/project
```

This creates:
- `.errors_fixes/errors_and_fixes.md` (with header)
- `.errors_fixes/fix_repo.md` (with header)
- `.errors_fixes/coding_tips.md` (with header)
- Updates `.gitignore` to exclude `.errors_fixes/`

### 2. Agent Integration

The system includes Cursor rules that are automatically available in all projects:

- **`.cursor/rules/global/errors.mdc`** - Error resolution protocol (triggers on error scenarios)
- **`.cursor/rules/global/coding-tips.mdc`** - Proactive process rules (triggers on code writing)

These rules enable the agent to:
- Check `.errors_fixes/` files for fixes before attempting solutions
- Document errors and fixes in `errors_and_fixes.md`
- Apply process rules proactively to prevent common mistakes

### 3. Development Workflow

1. **Agent writes code** → Generates tests → Advises test command
2. **User runs tests** → Provides error output if tests fail
3. **Agent looks up fixes** → Checks `errors_and_fixes.md` → `fix_repo.md` → `coding_tips.md`
4. **Agent applies fix** → Documents in `errors_and_fixes.md`
5. **Daily at 2 AM:** Consolidation app processes all session logs → Updates consolidated files

### 4. Consolidation App (Coming Soon)

The consolidation app will:
- Discover all projects with `.errors_fixes/errors_and_fixes.md`
- Parse session logs
- Deduplicate errors (exact match in Phase 3, AI semantic in Phase 4)
- Generate tags (rule-based in Phase 3, AI in Phase 4)
- Write consolidated `fix_repo.md` and `coding_tips.md`
- Clear `errors_and_fixes.md` (keep file)

---

## Documentation

- **`docs/SER_PLAN.md`** - Complete project plan, architecture, and design decisions
- **`docs/SER_IMPLEMENTATION_PLAN.md`** - Detailed implementation plan with 6 steps and 28 phases
- **`docs/SIMPLIFIED_ERROR_REGISTRY_V2.md`** - Complete system specification (SQT-refined)
- **`docs/PROJECT_STATUS.md`** - Current implementation status and progress tracking

---

## Project Status

**Current Step:** Step 1 of 6 (Core File Formats and Bootstrap)  
**Progress:** 0% (0/28 phases)  
**Health:** 🟢 On Track

See `docs/PROJECT_STATUS.md` for detailed progress tracking.

---

## Implementation Plan

The project is organized into 6 major steps:

1. **Core File Formats and Bootstrap** (4 phases)
   - Define markdown formats
   - Implement bootstrap script
   - Implement parser module
   - Implement basic generators

2. **Agent Integration and Test Output Verification** (5 phases)
   - Create errors.mdc rule
   - Create coding-tips.mdc rule
   - Verify test output capture
   - Create optional test-and-fix command
   - End-to-end agent workflow testing

3. **Consolidation App - Core** (6 phases)
   - Discovery module
   - Parser integration
   - Basic deduplication (exact match)
   - Basic tagging (rule-based)
   - Writer module
   - Main consolidation workflow

4. **Consolidation App - AI Integration** (5 phases)
   - LLM client integration
   - AI deduplication
   - AI tagging
   - Fix merging logic
   - Rule extraction

5. **Docker, Config, and Scheduling** (4 phases)
   - Docker container setup
   - ENV-first configuration
   - Cron scheduler integration
   - Logging and monitoring

6. **Testing and Refinement** (4 phases)
   - End-to-end testing
   - Performance testing
   - Portability testing
   - Documentation

See `docs/SER_IMPLEMENTATION_PLAN.md` for complete details.

---

## Key Design Decisions

- **Markdown over JSON:** Human-readable, sufficient for personal scale (< 500 entries)
- **Three-file system:** Clear separation (session log, fixes, rules)
- **ENV-first configuration:** Simpler Docker deployment, YAML optional
- **Per-project write (v1):** Symlink-based central output deferred to future
- **Daily consolidation:** Batch processing reduces overhead, acceptable latency
- **Hybrid agent rules:** errors.mdc + coding-tips.mdc for comprehensive coverage

---

## Tech Stack

- **Language:** Python 3.11+
- **LLM Integration:** Ollama (local, default) or cloud API (OpenAI, Anthropic)
- **Containerization:** Docker + Docker Compose
- **Scheduling:** Cron or Python scheduler
- **Configuration:** ENV-first (Docker), optional YAML
- **Storage:** File system (markdown files, no database)

---

## Contributing

This is a personal project, but contributions and feedback are welcome. See `docs/SER_PLAN.md` for architecture details and `docs/SER_IMPLEMENTATION_PLAN.md` for implementation details.

---

## License

*(To be determined)*

---

## Related Projects

This project is part of a larger effort to simplify developer tooling. It replaces the complex Global Error Registry (GER) system with a streamlined approach optimized for personal-scale projects.

---

**Last Updated:** 2025-01-15  
**Status:** Design Phase - Implementation starting
