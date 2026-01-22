# Simplified Error Registry (SER)

> **A streamlined, markdown-based approach for personal-scale error tracking and agent process documentation**

**Status:** 🟡 Design Phase  
**Last Updated:** 2026-01-22

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

### 4. Consolidation App

The consolidation app is now available! Run it manually or schedule it to run daily:

```bash
# Run consolidation for all projects under a root directory
python -m src.consolidation_app.main --root /path/to/projects

# Dry-run mode (preview changes without writing)
python -m src.consolidation_app.main --root /path/to/projects --dry-run

# Include extra projects outside the scan root
python -m src.consolidation_app.main --root /path/to/projects --extra /other/project1 /other/project2
```

**Features:**
- Discovers all projects with `.errors_fixes/errors_and_fixes.md`
- Parses session logs and existing consolidated files
- Deduplicates errors (exact match - AI semantic coming in Step 4)
- Generates tags (rule-based - AI tagging coming in Step 4)
- Writes consolidated `fix_repo.md` and `coding_tips.md`
- Clears `errors_and_fixes.md` (keeps file with header)
- Atomic writes (prevents partial file corruption)
- Path validation (prevents directory traversal attacks)
- Error isolation (one project failure doesn't stop others)

### 5. LLM Configuration (Step 4 - AI Integration)

The consolidation app supports per-task provider and model selection, allowing you to mix local and cloud providers for optimal performance, cost, and quality. Configure using a `.env` file (recommended) or environment variables.

#### Quick Setup: Create `.env` File

Create a `.env` file in the project root with your LLM configuration:

```bash
# ============================================================================
# LLM Configuration
# ============================================================================

# Default provider and model (fallback for all tasks)
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b

# Per-task providers (optional - overrides default provider for specific tasks)
# Allows mixing local (Ollama) and cloud (OpenAI/Anthropic) providers
LLM_PROVIDER_DEDUPLICATION=ollama
LLM_PROVIDER_TAGGING=openai
LLM_PROVIDER_RULE_EXTRACTION=anthropic

# Per-task models (optional - overrides default model for specific tasks)
LLM_MODEL_DEDUPLICATION=qwen2.5-coder:7b          # Semantic similarity
LLM_MODEL_TAGGING=gpt-4o-mini                     # Tag generation
LLM_MODEL_RULE_EXTRACTION=claude-3-opus-20240229  # Rule extraction

# Ollama configuration (only if using Ollama)
# OLLAMA_BASE_URL=http://localhost:11434

# API Keys (only needed for cloud providers)
# OPENAI_API_KEY=sk-your-openai-api-key-here
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

#### Configuration Examples

**Example 1: All Local (Ollama)**
```bash
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b
LLM_MODEL_DEDUPLICATION=qwen2.5-coder:7b
LLM_MODEL_TAGGING=qwen2.5-coder:7b
LLM_MODEL_RULE_EXTRACTION=qwen2.5-coder:14b
```

**Example 2: All Cloud (OpenAI)**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_MODEL_DEDUPLICATION=gpt-4o-mini
LLM_MODEL_TAGGING=gpt-4o-mini
LLM_MODEL_RULE_EXTRACTION=gpt-4
```

**Example 3: Mix Local and Cloud (Recommended for Cost Optimization)**
```bash
# Default: Use Ollama for most tasks
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b

# Use local Ollama for fast/cheap tasks
LLM_PROVIDER_DEDUPLICATION=ollama
LLM_MODEL_DEDUPLICATION=qwen2.5-coder:7b

LLM_PROVIDER_TAGGING=ollama
LLM_MODEL_TAGGING=qwen2.5-coder:7b

# Use cloud for complex reasoning
LLM_PROVIDER_RULE_EXTRACTION=openai
LLM_MODEL_RULE_EXTRACTION=gpt-4
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Example 4: Mix All Three Providers**
```bash
# Default fallback
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b

# Ollama for deduplication (fast, free)
LLM_PROVIDER_DEDUPLICATION=ollama
LLM_MODEL_DEDUPLICATION=qwen2.5-coder:7b

# OpenAI for tagging (fast, cost-effective)
LLM_PROVIDER_TAGGING=openai
LLM_MODEL_TAGGING=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic for rule extraction (best reasoning)
LLM_PROVIDER_RULE_EXTRACTION=anthropic
LLM_MODEL_RULE_EXTRACTION=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

#### Recommended Models by Task

**Local Models (Ollama):**
- **Deduplication** (`LLM_MODEL_DEDUPLICATION`): 
  - `qwen2.5-coder:7b` - Fast, good for similarity comparison
  - `deepseek-coder:7b` - Alternative fast option
  
- **Tagging** (`LLM_MODEL_TAGGING`):
  - `qwen2.5-coder:7b` - Fast, good for structured JSON output
  - `deepseek-coder:7b` - Alternative fast option
  
- **Rule Extraction** (`LLM_MODEL_RULE_EXTRACTION`):
  - `qwen2.5-coder:14b` - Better reasoning for complex rule extraction
  - `deepseek-coder:14b` - Alternative larger model

**Cloud Models:**
- **Deduplication** (`LLM_MODEL_DEDUPLICATION`):
  - OpenAI: `gpt-4o-mini` (fast, cost-effective)
  - Anthropic: `claude-3-haiku-20240307` (fast, cost-effective)
  
- **Tagging** (`LLM_MODEL_TAGGING`):
  - OpenAI: `gpt-4o-mini` (fast, good JSON output)
  - Anthropic: `claude-3-haiku-20240307` (fast, good JSON output)
  
- **Rule Extraction** (`LLM_MODEL_RULE_EXTRACTION`):
  - OpenAI: `gpt-4` or `gpt-4-turbo` (better reasoning)
  - Anthropic: `claude-3-opus-20240229` (best reasoning)

#### Setup Instructions

**For Local (Ollama):**
1. Install Ollama: https://ollama.ai
2. Start Ollama: `ollama serve`
3. Pull models: `ollama pull qwen2.5-coder:7b` and `ollama pull qwen2.5-coder:14b`
4. Create `.env` file with configuration above

**For Cloud (OpenAI/Anthropic):**
1. Get API key from provider dashboard
2. Create `.env` file with `LLM_PROVIDER` and `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
3. Configure models as shown above

#### Configuration Priority

For each task, the system uses this priority:

1. **Provider Selection:**
   - Task-specific provider (e.g., `LLM_PROVIDER_DEDUPLICATION`) if set
   - Default provider (`LLM_PROVIDER`) otherwise

2. **Model Selection:**
   - Explicit model parameter (if provided in code)
   - Task-specific model (e.g., `LLM_MODEL_DEDUPLICATION`) if set
   - Default model (`LLM_MODEL`) otherwise

This allows you to:
- Use different providers for different tasks (mix local and cloud)
- Use different models for different tasks (optimize cost/quality)
- Override defaults per task without affecting others

#### Alternative: Shell Environment Variables

If you prefer shell commands (temporary, only for current session):

```bash
export LLM_PROVIDER=ollama
export LLM_MODEL=qwen2.5-coder:14b
export LLM_PROVIDER_DEDUPLICATION=ollama
export LLM_MODEL_DEDUPLICATION=qwen2.5-coder:7b
export LLM_PROVIDER_TAGGING=openai
export LLM_MODEL_TAGGING=gpt-4o-mini
export OPENAI_API_KEY=sk-your-key-here
```

**Note:** `.env` file is automatically loaded and persists across sessions. Shell `export` commands only work for the current terminal session.

---

## Documentation

- **`docs/SER_PLAN.md`** - Complete project plan, architecture, and design decisions
- **`docs/SER_IMPLEMENTATION_PLAN.md`** - Detailed implementation plan with 6 steps and 28 phases
- **`docs/API_REFERENCE.md`** - API reference for consolidation app modules (Step 3 complete)
- **`docs/CONSOLIDATION_APP_USAGE.md`** - Usage guide for the consolidation app
- **`docs/SIMPLIFIED_ERROR_REGISTRY_V2.md`** - Complete system specification (SQT-refined)
- **`docs/PROJECT_STATUS.md`** - Current implementation status and progress tracking
- **`docs/TESTING.md`** - Testing guide, test infrastructure, and best practices
- **`docs/PHASE_4_6_REVIEW.md`** - Comprehensive code review and security review for Step 4
- **`docs/DEPENDENCY_MANAGEMENT.md`** - Dependency management guide and verification tools

---

## Project Status

**Current Step:** Step 4 of 6 (Complete) → Consolidation App - AI Integration  
**Progress:** 57% (16/28 phases)  
**Health:** 🟢 On Track

**Step 1 Completed (2026-01-21):**
- ✅ Phase 1.1: Markdown formats defined
- ✅ Phase 1.2: Bootstrap script implemented
- ✅ Phase 1.3: Parser module implemented
- ✅ Phase 1.4: Generator module implemented with security fixes

**Step 2 In Progress (2026-01-21):**
- ✅ Phase 2.1: errors.mdc rule created
- ✅ Phase 2.2: coding-tips.mdc rule created
- ✅ Phase 2.3: Test output capture verified and improved
- ✅ Phase 2.4: test-and-fix.mdc command created
- 🟡 Phase 2.5: End-to-end agent workflow testing (manual workflow complete)

**Step 3 Completed (2026-01-21):**
- ✅ Phase 3.1: Discovery module implemented
- ✅ Phase 3.2: Parser integration completed
- ✅ Phase 3.3: Basic deduplication (exact match) implemented
- ✅ Phase 3.4: Basic tagging (rule-based) implemented
- ✅ Phase 3.5: Writer module implemented
- ✅ Phase 3.6: Main consolidation workflow completed

**Step 4 Completed (2026-01-21):**
- ✅ Phase 4.1: LLM Client Integration (Ollama, OpenAI, Anthropic)
- ✅ Phase 4.2: AI Deduplication (semantic similarity)
- ✅ Phase 4.3: AI Tagging (context-aware tags)
- ✅ Phase 4.4: Fix Merging Logic (fuzzy code similarity)
- ✅ Phase 4.5: Rule Extraction (from process issues)
- ✅ Phase 4.6: Code Review & Security Review completed

**Step 3 Completed (2026-01-21):**
- ✅ Phase 3.1: Discovery module (with path validation)
- ✅ Phase 3.2: Parser integration
- ✅ Phase 3.3: Basic deduplication (exact match)
- ✅ Phase 3.4: Basic tagging (rule-based)
- ✅ Phase 3.5: Writer module (with atomic writes)
- ✅ Phase 3.6: Main consolidation workflow (CLI, error handling, dry-run)
- ✅ Security improvements: Atomic writes, path validation

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

3. **Consolidation App - Core** (6 phases) ✅ Complete 2026-01-21
   - Discovery module ✅
   - Parser integration ✅
   - Basic deduplication (exact match) ✅
   - Basic tagging (rule-based) ✅
   - Writer module ✅ (with atomic writes)
   - Main consolidation workflow ✅ (CLI, error handling, dry-run)

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

**Last Updated:** 2026-01-21  
**Status:** Implementation in progress (Step 3 complete, Step 4 next)
