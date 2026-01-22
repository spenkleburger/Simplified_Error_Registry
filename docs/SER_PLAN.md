## SER – Working Plan

> **Simplified Error Registry** - A streamlined, markdown-based approach for personal-scale error tracking and agent process documentation

### 1. Vision & Success Criteria
- **Primary Goal:** Build a simplified, markdown-based error registry system that replaces complex JSON-based systems for personal-scale projects. The system tracks runtime/test errors and agent process issues, consolidates them daily using AI, and provides actionable fixes and coding tips.
- **Key Priorities:** 
  1. Simplicity and human-readability (markdown over JSON)
  2. Agent process tracking (separate from code errors)
  3. AI-powered consolidation (semantic deduplication and tagging)
  4. Portability (self-contained `.errors_fixes/` folder)
  5. Success-based ordering (fixes ordered by success count)
- **Core Requirements:**
  - Three-file system: `errors_and_fixes.md` (session log), `fix_repo.md` (consolidated fixes), `coding_tips.md` (agent rules)
  - Daily consolidation app (batch processing at 2 AM)
  - Agent integration via `.cursor/rules/global/errors.mdc` and `coding-tips.mdc`
  - Bootstrap script for easy project onboarding
  - Docker containerization for consolidation app
- **Success Metrics:**
  - Can bootstrap new project in < 1 minute
  - Consolidation processes 5-20 projects in < 5 minutes
  - Agent successfully references fixes from registry
  - System handles < 500 consolidated entries efficiently

### 2. Guiding Principles
- **Simplicity First:** Human-readable markdown files instead of structured JSON. Sufficient for personal scale (< 500 entries).
- **Agent-Centric Design:** Built-in documentation of agent workflow issues, separate from code errors. Proactive prevention through `coding_tips.md`.
- **AI-Powered Intelligence:** Semantic similarity matching handles error variations better than exact hash matching. LLM generates context tags and extracts process rules.
- **Success-Based Learning:** Fixes ordered by success count (most successful tried first). No negative knowledge tracking - simpler model.
- **Portability & Self-Containment:** Single `.errors_fixes/` folder can be copied to any project. All files in one location, git-ignored for cleanliness.

### 3. System Architecture

**High-Level Flow:**
1. **Development Session:** Agent fixes errors → Documents in `.errors_fixes/errors_and_fixes.md`
2. **Daily Consolidation (2 AM):** Consolidation app reads all session logs, deduplicates, tags, merges fixes, extracts rules, writes consolidated files
3. **Next Session:** Agent checks recent session log → consolidated fixes → coding tips

**Component Separation:**
- **fix_repo.md:** Solutions to runtime/test errors (reactive use)
- **coding_tips.md:** Agent process/workflow rules (proactive use)
- Clear distinction: `### Error:` → fix_repo, `### Agent Process Issue:` → coding_tips

### 4. Pipeline Phases (Consolidation Workflow)

1. **Discovery Phase**
   - Scan for `.errors_fixes/errors_and_fixes.md` in all projects
   - Support `extra_projects` list for projects outside scan root
   - Auto-bootstrap missing `errors_and_fixes.md` for extra_projects only

2. **Parsing Phase**
   - Parse `errors_and_fixes.md` files
   - Separate `### Error:` entries from `### Agent Process Issue:` entries
   - Extract metadata (timestamp, file, line, error type, fix code, etc.)

3. **Deduplication Phase**
   - Phase 3: Exact match deduplication
   - Phase 4: AI semantic similarity matching (threshold: 0.85)
   - Merge similar errors, increment success counts

4. **Tagging Phase**
   - Phase 3: Rule-based tagging
   - Phase 4: AI-generated context tags (error type, framework, domain, platform)

5. **Fix Merging Phase**
   - Group fixes by similarity
   - Increment success count for same fixes
   - Add as variants for different fixes
   - Sort by success count (highest first)

6. **Rule Extraction Phase**
   - Extract process rules from `### Agent Process Issue:` entries only
   - Generate structured rules with examples (✅ good, ❌ bad)
   - Link to related errors

7. **Writing Phase**
   - Write `fix_repo.md` to each project
   - Write `coding_tips.md` to each project
   - Clear contents of `errors_and_fixes.md` (keep file)

### 5. Operating Modes

- **Manual Test Execution (Default):** Agent writes code → User runs tests → User provides errors → Agent fixes. User control, lower token usage.
- **Command-Based Auto-Fix (Optional):** User triggers `.cursor/command test-and-fix` → Agent runs tests → Agent fixes all errors → Repeats until pass or max iterations (5). Comprehensive error fixing.

### 6. Tech Stack Recommendation (Front-to-Back)

- **Consolidation App:**
  - **Language:** Python 3.11+
  - **LLM Integration:** Ollama (local) or cloud API (OpenAI, Anthropic)
  - **Scheduling:** Cron or Python scheduler
  - **Configuration:** ENV-first (Docker), optional YAML for projects list
- **Storage:**
  - **File System:** Markdown files in `.errors_fixes/` folder per project
  - **No Database:** Files are the source of truth
  - **Git-Ignored:** Session logs are ephemeral
- **Infrastructure:**
  - **Docker:** Containerized consolidation app
  - **Docker Compose:** App + Ollama service
  - **Volume Mounts:** Read-write access to projects directory
- **Agent Integration:**
  - **Cursor Rules:** `.cursor/rules/global/errors.mdc` and `coding-tips.mdc`
  - **Cursor Commands:** Optional `.cursor/commands/global/test-and-fix.mdc`
  - **File Format:** Markdown (human-readable, easy to parse)

### 7. Data Model (File Structure)

**Project Structure:**
```yaml
project_root/
  .errors_fixes/:
    errors_and_fixes.md:  # Session log (ephemeral, cleared after consolidation)
    fix_repo.md:          # Consolidated fixes (read-only during dev)
    coding_tips.md:       # Agent process rules (read-only during dev)
    README.md:            # Optional: Quick reference
```

**Error Entry Structure:**
```yaml
ErrorEntry:
  error_signature: str      # Error message/type
  error_type: str           # Exception class name
  file: str                 # File where error occurred
  line: int                 # Line number
  fix_code: str             # Code change that fixed it
  explanation: str          # Why the fix works
  result: str               # ✅ Solved / ❌ Failed
  success_count: int         # How many times this fix worked
  tags: List[str]           # Context tags (docker, networking, etc.)
  timestamp: datetime        # When error occurred
  is_process_issue: bool    # True if Agent Process Issue
```

**Process Rule Structure:**
```yaml
ProcessRule:
  title: str                # Rule category (Path Handling, etc.)
  rule: str                 # Rule statement
  why: str                  # Why it's needed
  examples:
    good: List[str]         # ✅ Good examples
    bad: List[str]          # ❌ Bad examples
  related_errors: List[str] # Error types that trigger this rule
```

### 8. Workflow Walkthrough (Development Session)

1. **Agent writes code** → Generates tests automatically → Advises test command (`task test:backend`, etc.)
2. **User reviews code** → Runs advised test command
3. **If tests fail:**
   - User provides error output to agent
   - Agent checks lookup order: `errors_and_fixes.md` → `fix_repo.md` → `coding_tips.md`
   - Agent applies fix (tries fixes in order of success count)
   - Agent documents in `errors_and_fixes.md`
   - User runs test command again
4. **If tests pass:**
   - Agent documents success in `errors_and_fixes.md`
5. **Continue development** → Repeat cycle
6. **Daily at 2 AM:** Consolidation app processes all session logs → Updates consolidated files

### 9. File & Project Management

- **File Structure:**
  - Self-contained `.errors_fixes/` folder in each project root
  - All files use UTF-8 encoding, LF line endings
  - Markdown format for human readability
- **Version Control:**
  - `.errors_fixes/` folder is git-ignored
  - Session logs are ephemeral (cleared after consolidation)
  - Consolidated files are regenerated by consolidation app
- **Portability:**
  - Copy `.errors_fixes/` folder to new project
  - Bootstrap script creates structure if missing
  - Global Cursor rules automatically available (no copying needed)

### 10. Agent Integration Strategy

**Rule Files:**
- **`.cursor/rules/global/errors.mdc`:** Error resolution protocol
  - Critical: Precise frontmatter description (NOT `alwaysApply: true`)
  - Triggers on: pasted test errors, "There is an error in...", test failure output
  - Includes: Test generation requirements, lookup order, fix application workflow
- **`.cursor/rules/global/coding-tips.mdc`:** Proactive process rules
  - Triggers on: "write code", "create file", "use file path", "run command", "Docker"
  - References: `.errors_fixes/coding_tips.md` for specific rules

**Command File (Optional):**
- **`.cursor/commands/global/test-and-fix.mdc`:** Auto-fix workflow
  - User triggers → Agent runs tests → Fixes all errors → Documents results
  - Safety limits: 5 iterations max, 3 same-error retries

### 11. Consolidation App Architecture

**Module Structure:**
```
consolidation_app/
├── main.py              # Entry point, scheduler
├── discovery.py         # Find all projects
├── parser.py            # Parse markdown files
├── deduplicator.py      # AI-based deduplication
├── tagger.py            # AI-based tagging
├── merger.py            # Merge fixes and order by success
├── rule_extractor.py    # Extract process rules
├── writer.py            # Write consolidated files
├── config.py            # Configuration (ENV-first)
└── requirements.txt     # Dependencies
```

**Configuration:**
- **ENV-first:** `PROJECTS_ROOT`, `LLM_MODEL`, `CONSOLIDATION_SCHEDULE`, `SIMILARITY_THRESHOLD`
- **YAML optional:** `consolidation.projects` list, advanced overrides
- **ENV overrides YAML** when both exist

### 12. Scalability, Dockerization & SaaS Potential

#### Dockerization Strategy
**Yes - Dockerize from the start.**

**Benefits:**
- Consistent environment for consolidation app
- Easy scheduling with cron
- Isolated LLM service (Ollama)
- Simple deployment and updates

**Recommended Docker Architecture:**
```yaml
services:
  consolidation-app:  # Main consolidation service
    build: .
    volumes:
      - /path/to/projects:/projects:rw
    environment:
      - LLM_MODEL=ollama/qwen2.5-coder:14b
      - CONSOLIDATION_SCHEDULE="0 2 * * *"
      - PROJECTS_ROOT=/projects
    depends_on:
      - ollama
    
  ollama:  # Local LLM service
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
```

#### SaaS Repackaging Potential
**Moderate - Possible but requires significant modifications**

**Analysis:**
- Current design is personal-scale (single developer, < 500 entries)
- SaaS would require multi-tenancy, user isolation, scaling
- Consolidation app would need per-user/project isolation
- LLM costs would scale with usage

**Required Modifications for SaaS:**
1. **Multi-tenancy:** User authentication, project isolation, per-user consolidation
2. **Scaling:** Database for metadata, caching, distributed processing
3. **Billing:** Usage tracking, LLM cost allocation, subscription management
4. **Security:** User data isolation, API authentication, rate limiting

#### Hosting Options & Cost Estimates

**Option 1: Self-Hosted (Docker Compose)**
- **Pros:** Full control, no per-user costs, privacy
- **Cons:** Requires server management, LLM model hosting
- **Cost estimate:**
  - **Single user:** $20-50/mo (VPS + storage)
  - **SaaS (10-50 tenants):** $100-300/mo (larger VPS, more storage)
  - **SaaS (100+ tenants):** $500-1000/mo (dedicated server, CDN)

**Option 2: Cloud Hosting (AWS/GCP/Azure)**
- **Pros:** Scalable, managed services, global distribution
- **Cons:** Higher costs, vendor lock-in
- **Cost estimate:**
  - **Single user:** $30-80/mo (EC2 + S3)
  - **SaaS (10-50 tenants):** $200-500/mo (ECS + RDS + S3)
  - **SaaS (100+ tenants):** $1000-3000/mo (Auto-scaling, RDS, CloudFront)

**Total Cost Summary:**
- **Personal use:** $20-80/mo (self-hosted recommended)
- **SaaS potential:** $5-15/user/mo (requires 50+ users for profitability)
- **Revenue potential:** Limited (niche market, personal-scale focus)

### 13. Authentication Strategy

**Single-user / Personal Authentication:**

No authentication required for personal use. Each developer runs their own consolidation app with access to their own projects directory.

**Future SaaS Extension:**
- OAuth2/JWT for multi-user support
- Per-user project isolation
- API keys for programmatic access
- Role-based access control (admin, user, read-only)

### 14. Database Choice: File System (No Database)

**File System Recommendation:**

**Why no database:**
- Markdown files are human-readable and sufficient for personal scale
- No complex queries needed (linear search acceptable for < 500 entries)
- Simpler deployment (no database setup/maintenance)
- Files are self-contained and portable

**Trade-offs:**
- Linear search performance (acceptable for personal scale)
- No advanced querying (not needed for this use case)
- File locking considerations (handled by consolidation app)

**Migration considerations:**
- If scaling beyond personal use, consider SQLite for metadata
- Full-text search could use SQLite FTS or dedicated search engine
- Current design intentionally avoids database complexity

### 15. Additional Technical Decisions

**Storage Strategy:**
- Markdown files in `.errors_fixes/` folder
- UTF-8 encoding, LF line endings
- Git-ignored (ephemeral session logs, regenerated consolidated files)

**API Design:**
- No API required (file-based system)
- Consolidation app reads/writes files directly
- Agent reads files directly via Cursor rules

**Error Handling:**
- Consolidation app handles missing files gracefully
- Bootstrap creates structure if missing
- Logging for consolidation failures

**Logging & Monitoring:**
- Consolidation app logs to stdout/stderr
- Docker logs capture consolidation runs
- Optional: File-based logging for audit trail

**Testing Strategy:**
- Unit tests for parser, deduplicator, tagger, merger, rule extractor
- Integration tests for full consolidation workflow
- Mock LLM for testing without API costs
- End-to-end tests with sample projects

### 16. Phase 1 MVP: Minimum Viable Product Definition

**Goal:** Create a working consolidation app that can process session logs and generate consolidated files, with basic (exact-match) deduplication.

**Phase 1 MVP Features:**

**Core Features (Must Have):**
1. **Bootstrap Script:**
   - Creates `.errors_fixes/` folder structure
   - Creates `errors_and_fixes.md` with header
   - Creates stubs for `fix_repo.md` and `coding_tips.md`
   - Updates `.gitignore`

2. **Basic Parser:**
   - Parses `errors_and_fixes.md` markdown
   - Extracts `### Error:` and `### Agent Process Issue:` entries
   - Extracts metadata (timestamp, file, line, error type, fix code, etc.)

3. **Basic Consolidation:**
   - Exact-match deduplication (Phase 3)
   - Rule-based tagging (Phase 3)
   - Fix merging by success count
   - Write `fix_repo.md` and `coding_tips.md`
   - Clear `errors_and_fixes.md` after consolidation

4. **Agent Rules:**
   - `.cursor/rules/global/errors.mdc` with precise frontmatter
   - `.cursor/rules/global/coding-tips.mdc` with precise frontmatter
   - Test generation requirements
   - Lookup order documentation

**Deferred to Phase 2:**
- AI deduplication (semantic similarity)
- AI tagging
- Rule extraction from process issues
- Docker containerization

**Deferred to Phase 3:**
- Command-based auto-fix workflow
- Advanced error parsing
- Performance optimizations

**Technical Stack (MVP):**
- **Language:** Python 3.11+
- **Parsing:** Regex-based markdown parsing
- **Storage:** File system (markdown files)
- **Infrastructure:** Standalone script (Docker in Phase 2)

**Success Criteria:**
- Bootstrap script creates structure in < 1 second
- Parser correctly extracts all error and process issue entries
- Consolidation produces valid `fix_repo.md` and `coding_tips.md`
- Agent rules trigger correctly on error scenarios
- End-to-end workflow works: session log → consolidation → agent lookup

### 17. Implementation Plan Structure

**Development Approach: Feature-by-Feature**

Build complete features end-to-end: bootstrap → parser → basic consolidation → agent rules → AI features → Docker.

**Implementation Structure: Large Steps with Phases**

**Step Structure:**
Each major step contains smaller phases. At the end of each phase, all code is tested. At the end of each step, comprehensive code review and security review are conducted.

**Example Step Breakdown:**

**Step 1: Core File Formats and Bootstrap** ✅ Complete (2026-01-21)
- Phase 1.1: Define markdown formats and create template ✅
- Phase 1.2: Implement bootstrap script ✅
- Phase 1.3: Implement parser module ✅
- Phase 1.4: Implement basic generators ✅
- **End of Step 1:** Code review, security review, testing complete ✅
  - Security: Tag escaping, header escaping, input validation
  - Testing: Comprehensive unit tests with edge case coverage
  - Documentation: API reference created, all docs updated

**Step 2: Agent Integration**
- Phase 2.1: Create errors.mdc rule
- Phase 2.2: Create coding-tips.mdc rule
- Phase 2.3: Test output capture verification
- Phase 2.4: End-to-end agent workflow testing
- **End of Step 2:** Code review, security review, testing complete

**Step 3: Consolidation App - Core**
- Phase 3.1: Discovery module
- Phase 3.2: Parser integration
- Phase 3.3: Basic deduplication (exact match)
- Phase 3.4: Basic tagging (rule-based)
- Phase 3.5: Writer module
- **End of Step 3:** Code review, security review, testing complete

**Step 4: Consolidation App - AI Integration**
- Phase 4.1: LLM client integration
- Phase 4.2: AI deduplication
- Phase 4.3: AI tagging
- Phase 4.4: Rule extraction
- **End of Step 4:** Code review, security review, testing complete

**Step 5: Docker, Config, and Scheduling**
- Phase 5.1: Docker container setup
- Phase 5.2: ENV-first configuration
- Phase 5.3: Cron scheduler integration
- Phase 5.4: Logging and monitoring
- **End of Step 5:** Code review, security review, testing complete

**Step 6: Testing and Refinement**
- Phase 6.1: End-to-end testing
- Phase 6.2: Performance testing
- Phase 6.3: Portability testing
- Phase 6.4: Documentation
- **End of Step 6:** Code review, security review, testing complete

**Testing at End of Each Phase:**
- Unit tests for new functionality
- Integration tests for module interactions
- Manual testing of workflows
- Verify no regressions

**Code & Security Review at End of Each Step:**
- Architecture review
- Security review (file access, LLM API keys, etc.)
- Performance review
- Documentation update

### 18. Immediate Next Steps / Questions

1. **LLM Provider Decision:** Ollama (local) vs cloud API (OpenAI/Anthropic)? Start with Ollama for privacy, add cloud option later.
2. **Project Discovery:** How to handle projects outside `PROJECTS_ROOT`? Use `extra_projects` config list with auto-bootstrap.
3. **Error Format Standardization:** Define exact markdown format for `errors_and_fixes.md` to ensure consistent parsing.
4. **Agent Rule Testing:** How to verify rules trigger correctly? Manual testing with various error scenarios.
5. **Consolidation Schedule:** 2 AM default acceptable? Make configurable via ENV.

### 19. Key Decisions Summary & Discussion

**Decisions Made:**
1. ✅ **Markdown over JSON:** Human-readable, sufficient for personal scale, easier maintenance
2. ✅ **Three-file system:** Clear separation of concerns (session log, fixes, rules)
3. ✅ **ENV-first configuration:** Simpler Docker deployment, YAML optional for advanced cases
4. ✅ **Per-project write (v1):** Symlink-based central output deferred to future
5. ✅ **Bootstrap in Phase 1:** Enables onboarding before consolidation app exists

**Recommendations & Rationale:**

**File Format:**
- **Chose Markdown** because human-readable, easy to edit, sufficient for personal scale
- **Trade-offs:** Linear search performance (acceptable for < 500 entries), no advanced querying (not needed)
- **Alternatives evaluated:** JSON (too complex), SQLite (overkill for personal scale), YAML (less readable than markdown)

**Consolidation Strategy:**
- **Chose Daily batch** because reduces overhead, acceptable latency for personal use
- **Trade-offs:** Not immediate (acceptable), requires scheduling infrastructure
- **Alternatives evaluated:** On-demand (too much overhead), real-time (too complex)

**Agent Integration:**
- **Chose Hybrid (errors.mdc + coding-tips.mdc)** because comprehensive coverage without redundancy
- **Trade-offs:** Two files to maintain (acceptable), requires careful frontmatter crafting
- **Alternatives evaluated:** Single rule (misses proactive prevention), alwaysApply (token bloat)

**Next Steps:**
- Create bootstrap script (Phase 1.2)
- Define exact markdown format (Phase 1.1)
- Implement basic parser (Phase 1.3)
- Create agent rules (Phase 2.1, 2.2)
- Test end-to-end workflow (Phase 2.4)

**Open Questions (if any):**
- Should consolidation app support multiple LLM providers simultaneously? (Start with one, add later)
- How to handle consolidation failures? (Log and continue, retry logic)
- Should there be a web UI for viewing consolidated fixes? (Not in MVP, consider later)

---

**Template Usage:**

1. This file replaces `{PROJECT_NAME}_PLAN.md` with `SER_PLAN.md`
2. All `{PROJECT_NAME}` replaced with `SER` (Simplified Error Registry)
3. All placeholders filled with SER-specific content based on `SIMPLIFIED_ERROR_REGISTRY_V2.md`
4. Sections customized based on SER architecture and requirements
5. References to V2 document for detailed specifications

**Note:** This plan provides a comprehensive structure for the Simplified Error Registry project. Implementation details are tracked in `SER_IMPLEMENTATION_PLAN.md`.
