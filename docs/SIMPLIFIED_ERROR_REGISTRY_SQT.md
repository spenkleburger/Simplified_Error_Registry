# Simplified Error Registry: SQT Assessment and Refinements

> **Derived from:** `SIMPLIFIED_ERROR_REGISTRY.md`  
> **Purpose:** Identify redundancies, propose simplifications, and record open choices with recommendations.  
> **Status:** Assessment complete; main doc to be updated incrementally.  
> **Date:** 2025-01-15

---

## 1. Executive Summary

- **Redundancies:** The fix_repo vs coding_tips distinction, the 3-step lookup order, workflow diagrams (Manual vs Command-based), `discover_projects`, bootstrap logic, `errors.mdc` frontmatter warnings, and `.gitignore` for `.errors_fixes/` are each repeated 3–5+ times. Consolidating to one canonical place per topic with cross-references will significantly shorten the doc without losing content.
- **Simplifications:** (a) Use one Manual and one Command-based workflow diagram plus a short comparison table; drop the repeated variants. (b) Consolidation App: keep discovery and writer in full; reduce Parser, Deduplicator, Tagger, Merger, Rule extractor to “signature + in/out + LLM summary” and move detailed prompts to an appendix. (c) coding_tips reference: keep Hybrid (errors.mdc + coding-tips.mdc) as the only recommended approach; collapse Options 3–5 to one short “alternatives” sentence. (d) Onboarding: A and B in main Portability; C and D in a short “Alternatives and open design” subsection.
- **Key decisions with recommendations:** (1) **Output:** Per-project write only for v1; symlink-based central output deferred. (2) **Onboarding C:** Implement `consolidation.projects` and `discover_projects(root, extra_projects)`; auto-bootstrap only for `extra_projects`, not for rglob-discovered projects. (3) **Phase 2.5:** Merge into Phase 2 as “Agent Integration and Test Output Verification.” (4) **Phase 3 vs 4:** Phase 3 = exact-match dedup and rule-based tagging only; Phase 4 = AI dedup, AI tagging, rule extraction. (5) **Bootstrap script:** Phase 1 deliverable (implements “template” .errors_fixes/). (6) **Config:** ENV-first for Docker and simple deployment (docker-compose only, no config file); YAML optional for `projects` list, standalone runs, and advanced overrides. ENV overrides YAML when both exist.
- **Symlink:** Treated as “for discussion” only. v1 supports only per-project write. Defer `output_mode: central_symlink` until cross-platform symlink strategy and `central_output_dir` are defined.

---

## 2. Redundancies

| # | Topic | Locations in doc | Recommendation |
|---|-------|------------------|----------------|
| 1 | **fix_repo vs coding_tips** | Overview, Component Overview, comparison table, repeated bullets | Keep the comparison table and one short paragraph; remove the extra bullets that restate it. |
| 2 | **Workflow: Manual vs Command-based** | Development Session Workflow (2 diagrams), Updated Workflow Diagrams (2), Test Execution comparison | Keep one Manual and one Command-based diagram plus the comparison table; delete the duplicate diagrams. |
| 3 | **Lookup order** (errors_and_fixes → fix_repo → coding_tips) | Development Session, test-and-fix.mdc, errors.mdc Lookup Strategy, Fix Loop, Step 2: Lookup Fixes | One canonical “Lookup order” section (e.g. in errors.mdc / Agent Rules); elsewhere: “(see Lookup order).” |
| 4 | **coding_tips proactive use** | Component Overview, fix_repo vs coding_tips table, 5 options under “Ensuring Agent References coding_tips.md,” Process Rules, Lookup Strategy | Keep the Hybrid (Options 1+2) as the recommendation; collapse Options 3–5 to one “Alternatives” sentence. |
| 5 | **Test generation + advise test command** | errors.mdc (full), test-and-fix.mdc, Phase 2 verification bullets, Step 5: Advise Test Commands | Implementation Plan: “as specified in errors.mdc” and a short checklist; remove duplicated prose. |
| 6 | **discover_projects()** | Consolidation App Design, Consolidation App Discovery, Including a New Project (C) | One implementation in Consolidation App (discovery module); Portability and Including a New Project reference it, no second code block. |
| 7 | **Bootstrap script** | Full Python in Including a New Project B; logic reused in C | One canonical script (e.g. in Phase 1 as “bootstrap_errors_fixes” or in an appendix); C says “calls bootstrap().” |
| 8 | **errors.mdc frontmatter / “do NOT alwaysApply”** | Critical: Careful Crafting, Why errors.mdc Instead of AGENTS.md, Updated errors.mdc intro, Implementation Plan | One “Critical” callout near the errors.mdc template; Implementation: “(see Critical callout).” |
| 9 | **.errors_fixes/ in .gitignore** | File Structure, Setup Steps, Bootstrap, Appendix D | One canonical note (e.g. in File Structure or Portability); bootstrap and Appendix D reference it. |
| 10 | **Docker / consolidation config** | Consolidation App (Dockerfile, compose, env), Appendix C (YAML) | Main body: full Docker and a single consolidation_config example. Appendix C: “Overrides and alternate settings” or reference the main section. |

---

## 3. Simplifications

- **Workflow diagrams:** Before: 4+ boxes (Manual x2, Command-based x2) with near-identical content. After: one “Development workflow” with two branches—Manual (default) and Command-based (optional)—and one comparison table. Remove “Updated Workflow Diagrams” as a separate duplicate.
- **Lookup order:** Before: repeated in 5+ places. After: One “Lookup order” subsection under Agent Rules / errors.mdc: “1) errors_and_fixes.md, 2) fix_repo.md, 3) coding_tips.md.” Other sections: “Check in lookup order (see above).”
- **coding_tips reference (5 options):** Before: Options 1–5 each with pros/cons and implementation. After: “Recommended: Hybrid (Options 1+2): Preventive Checks in errors.mdc + separate coding-tips.mdc.” One short paragraph: “Alternatives: add to rules.mdc, User Rules, or workflow docs only—not recommended for reliability.”
- **Test Execution Strategy:** Before: ~200 lines (Approach 1–3, hybrid, full test-and-fix.mdc, two diagrams, table). After: (a) “Excluded: fully automatic execution” in 2–3 bullets. (b) Manual (default) and Command-based (optional) in 1–2 short paragraphs + safety limits (5 iterations, 3 same-error retries). (c) “Full test-and-fix.mdc: see Appendix or .cursor/commands/global/test-and-fix.mdc.” (d) Keep the comparison table.
- **Consolidation App modules:** Before: 7 modules with long code and prompts. After: Discovery and Writer in full (they define I/O and onboarding). Parser, Deduplicator, Tagger, Merger, Rule extractor: 3–5 lines each (signature, in/out, LLM role). Move full LLM prompts to Appendix B.
- **File format examples:** Before: long markdown samples for errors_and_fixes, fix_repo, coding_tips (plus a second fix_repo-style example). After: One compact example per format in the main body (minimal required fields); move full samples to an appendix if needed for a parser spec.
- **Portability / Onboarding:** Before: A, B, C, D (symlink) all at the same level with full code. After: “Setup” = A (manual copy) and B (bootstrap script) in the main Portability section. “Alternatives and open design” = C (config project list + auto-bootstrap for extra_projects only) and D (symlink-based central output, for discussion only). C and D: short prose and one code or config snippet each; no second full bootstrap or discover_projects block.
- **Appendix vs main:** Before: Appendix C repeats consolidation YAML; Appendix A repeats parsing approach. After: Appendix A: “Parser: regex-based (see Consolidation App); for complex nesting consider a markdown parser later.” Appendix C: “Configuration overrides and ENV” or “See Consolidation App and Docker for primary config.” Appendix D: “.gitignore: see File Structure / Portability.”

---

## 4. Open Choices and Recommendations

| # | Choice / question | Recommendation | Rationale |
|---|-------------------|----------------|-----------|
| 1 | **Output: per-project vs central symlink** | Per-project only for v1; symlink deferred. | Symlink needs cross-platform strategy and `central_output_dir`; keep “D. Symlink-based central output” as design-in-discussion. |
| 2 | **Config project list (C) and auto-bootstrap** | Implement `consolidation.projects` and `discover_projects(root, extra_projects)`. Auto-bootstrap (create errors_and_fixes.md) only when the path is in `extra_projects`. | rglob-discovered projects must already have .errors_fixes/; only explicitly listed projects get auto-bootstrap to avoid creating dirs elsewhere. |
| 3 | **coding_tips reference** | Hybrid (errors.mdc + coding-tips.mdc) as the only recommended approach. | Options 3–5 remain as one-sentence alternatives; reduces branching and maintenance. |
| 4 | **test-and-fix command** | Remain optional. | Doc already states primary is errors.mdc; no need to decide now if it becomes standard later. |
| 5 | **Phase 2.5** | Merge into Phase 2 as “Agent Integration and Test Output Verification.” | Avoids a half-phase; test output capture is part of agent/test integration. |
| 6 | **Dedup: AI vs exact match** | Phase 3: exact match only. Phase 4: AI dedup and tagging. | State explicitly: “Phase 3 dedup = exact match; AI in Phase 4.” |
| 7 | **Parser** | Regex for v1. | Simpler, no extra deps; note “consider markdown parser if nested structures grow.” |
| 8 | **Config: env vs YAML** | ENV-first for Docker and simple deployment (docker-compose only, no config mount); YAML optional for `projects` list, standalone runs, and advanced overrides. ENV overrides YAML when both exist. | One “Configuration” subsection: ENV vars (PROJECTS_ROOT, LLM_MODEL, CONSOLIDATION_SCHEDULE, etc.); optional YAML (CONFIG_PATH or default path) for projects and overrides. |
| 9 | **Bootstrap script placement** | Phase 1 deliverable; implements “template” .errors_fixes/. | Enables onboarding before the consolidation app exists; C’s auto-bootstrap reuses it. |
| 10 | **output_mode for symlink** | Do not add in v1. | Add `output_mode` (values: per_project, central_symlink) only when symlink design is finalized. |

---

## 5. Refined Implementation Outline

### Phase 1: Core File Formats and Template (Week 1)

- **Tasks:** Define markdown formats for errors_and_fixes, fix_repo, coding_tips; create template .errors_fixes/ (or equivalent); implement **bootstrap script** (create .errors_fixes/, errors_and_fixes.md with header, optional stubs for fix_repo and coding_tips, .gitignore); parser for errors_and_fixes; generators for fix_repo and coding_tips.
- **Deliverables:** Template .errors_fixes/; bootstrap_errors_fixes script; parser and generator modules; unit tests.

### Phase 2: Agent Integration and Test Output Verification (Week 1–2)

- **Tasks:** Create errors.mdc (with Lookup order, Preventive Checks, test generation, advise-test-command, Fix Loop, safety limits) and coding-tips.mdc; create optional test-and-fix.mdc; **merge Phase 2.5:** inspect task test:* and scripts, verify test output capture (FAILURES/ERRORS, short test summary), document required sections; verification for test generation, test command advice, test output capture, safety limits.
- **Deliverables:** errors.mdc, coding-tips.mdc, optional test-and-fix.mdc; verification results; docs for test output sections. (Phase 2.5 content is folded in; no separate Phase 2.5.)

### Phase 3: Consolidation App – Core (Week 2–3)

- **Tasks:** Discovery: `discover_projects(root_path, extra_projects)` with **auto-bootstrap for extra_projects only** (call bootstrap when errors_and_fixes.md missing); parser; **basic deduplication (exact match only)**; **basic tagging (rule-based)**; writer (per-project); clear errors_and_fixes.md after consolidation.
- **Deliverables:** Core consolidation app; discovery + writer behavior as in main doc; unit and integration tests.

### Phase 4: Consolidation App – AI (Week 3–4)

- **Tasks:** LLM client; AI deduplication; AI tagging; fix merging; **rule extraction (Agent Process Issue entries only)**.
- **Deliverables:** AI-powered dedup and tagging; rule extractor; tests with mocked LLM.

### Phase 5: Docker, Config, and Scheduling (Week 4)

- **Tasks:** Dockerfile and docker-compose; **config: ENV-first** (PROJECTS_ROOT, LLM_MODEL, CONSOLIDATION_SCHEDULE, SIMILARITY_THRESHOLD in `environment:` or `env_file:`; no config mount required); **YAML optional** (CONFIG_PATH or default path) for `projects` list and advanced overrides; ENV overrides YAML when both exist; cron/scheduler; logging.
- **Deliverables:** Dockerized app; ENV docs (required vars); optional consolidation_config.yaml and override docs; scheduled run.

### Phase 6: Testing and Refinement (Week 5)

- **Tasks:** End-to-end and portability testing; **portability: bootstrap on new project, run consolidation, verify fix_repo and coding_tips written**; performance and docs.
- **Deliverables:** Test suite; portability guide; user docs.

---

## 6. Suggested Edits to the Main Doc

Apply these incrementally to `SIMPLIFIED_ERROR_REGISTRY.md`:

1. **Overview / Component Overview:** Keep the fix_repo vs coding_tips **table** and **one** short paragraph; remove the duplicate bullets that restate the table.
2. **Workflow:** Replace the multiple Manual/Command-based boxes with **one** “Development workflow” with two branches and **one** comparison table; delete the “Updated Workflow Diagrams” duplicates.
3. **Agent Rules:** Introduce a single **“Lookup order”** subsection; in Fix Loop, test-and-fix, and “Step 2: Lookup Fixes,” replace the 3-step list with “(see Lookup order).”
4. **“Ensuring Agent References coding_tips.md”:** Keep **Recommended: Hybrid (Options 1+2)** and the implementation checklist; replace Options 3–5 with: “Alternatives: add to rules.mdc, User Rules, or docs-only—not recommended for reliability.”
5. **Test Execution Strategy:** Shorten Approach 2 to “Excluded: fully automatic” (2–3 bullets). Condense Approach 1 and 3; keep comparison table. Move **full** test-and-fix.mdc to an appendix or linked file; in main body: when to use, safety limits, and “see test-and-fix.mdc.”
6. **Consolidation App Design:** Keep **Discovery** and **Writer** (and clear_errors_and_fixes) in full. Replace Parser, Deduplicator, Tagger, Merger, Rule extractor with a short “signature + in/out + LLM role” each; move full prompts to **Appendix B**.
7. **Consolidation App Discovery / Including a New Project:** Use **one** `discover_projects` implementation (with `extra_projects` and auto-bootstrap for `extra_projects` only). In “Including a New Project,” **A** and **B** stay; **C** references `discover_projects(..., extra_projects=config.consolidation.projects)` and “calls bootstrap when errors_and_fixes.md missing for an extra path”; **D** remains “for discussion” and states “v1: per-project only; central_symlink deferred.”
8. **Bootstrap:** One canonical **bootstrap_errors_fixes** script (e.g. in Phase 1 or an appendix). In B: “Run bootstrap_errors_fixes.” In C: “discovery calls bootstrap when in extra_projects and errors_and_fixes.md missing.”
9. **errors.mdc and “do NOT alwaysApply”:** One **Critical** callout immediately before the errors.mdc template; in Implementation Plan and “Why errors.mdc,” reference “(see Critical callout).”
10. **.gitignore:** One note in File Structure or Portability; in Setup Steps, bootstrap, and Appendix D: “(see .gitignore note).”
11. **Implementation Plan:** (a) **Phase 1:** Add “Bootstrap script” to tasks and deliverables. (b) **Phase 2:** Merge Phase 2.5 into Phase 2; reduce duplicate “test generation / advise test command” to a reference to errors.mdc. (c) **Phase 3:** Add “discover_projects(root, extra_projects)” and “auto-bootstrap for extra_projects only”; state “Dedup: exact match only.” (d) **Phase 4:** State “AI dedup and tagging”; add “Rule extraction (Agent Process Issue only)” if missing. (e) **Phase 5:** Add “Config: ENV-first for Docker (no config mount); YAML optional (projects, advanced). ENV overrides YAML.” (f) **Phase 6:** In portability testing, add “bootstrap on new project; run consolidation; verify fix_repo and coding_tips.”
12. **Appendix C:** Change to “ENV-first; optional YAML for projects list and overrides. See Consolidation App and Docker for ENV vars and usage.” Avoid duplicating a full YAML schema in the appendix.
13. **Comparison / When to Use:** In “Use Simplified when,” add: “you want to try symlink-based central output later (design deferred).”

---

## 7. What Stays, What Moves, What Gets Cut

| Topic | Action |
|-------|--------|
| fix_repo vs coding_tips **table** | **Keep** (one place). |
| fix_repo vs coding_tips **repeated bullets** | **Cut.** |
| Workflow: **one** Manual + **one** Command-based diagram | **Keep.** |
| **Extra** Manual/Command-based diagrams | **Cut.** |
| **Lookup order** (single subsection) | **Keep** (canonical). |
| Lookup order **repeated in 5+ places** | **Cut**; replace with “(see Lookup order).” |
| **Hybrid (errors.mdc + coding-tips.mdc)** | **Keep** as sole recommendation. |
| **Options 3–5** for coding_tips | **Cut** to one “Alternatives” sentence. |
| **Test Execution:** Manual vs Command-based + table | **Keep** (shortened). |
| **Approach 2** (Automatic) | **Keep** as 2–3 bullets (“Excluded”). |
| **Full test-and-fix.mdc** in main body | **Move** to appendix or linked file. |
| **Discovery** and **Writer** | **Keep** in full. |
| **Parser, Deduplicator, Tagger, Merger, Rule extractor** (long) | **Shorten** to signature + in/out + LLM role; **move** full prompts to Appendix B. |
| **discover_projects** (multiple code blocks) | **Keep one** (with extra_projects and auto-bootstrap for extra only). |
| **Bootstrap** (full script in B and logic in C) | **Keep one** script; C references it. |
| **errors.mdc frontmatter / “do NOT alwaysApply”** (4 places) | **Keep one** Critical callout; **cut** the rest or reference it. |
| **.gitignore** (4 places) | **Keep one** canonical note; **cut** or reference elsewhere. |
| **Docker + consolidation_config** in main | **Keep.** Appendix C: **reduce** to overrides or reference. |
| **Onboarding A and B** | **Keep** in main Portability. |
| **Onboarding C and D** | **Keep** in “Alternatives and open design”; **shorten**; D remains “for discussion.” |
| **Phase 2.5** | **Merge** into Phase 2. |
| **Bootstrap in Phase 1** | **Add.** |
| **extra_projects + auto-bootstrap (extra only)** | **Add** in discovery/Portability and Phase 3. |
| **Symlink / output_mode** | **No** implementation in v1; **keep** “D. Symlink-based central output” as design-in-discussion. |

---

*End of SQT assessment.*
