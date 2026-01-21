---
# YAML frontmatter for Idea Engine parsing
# 
# Format Requirements:
# - All values must be actual data (replace example values with real data)
# - health_status must be one of: "on_track", "at_risk", or "blocked" (no emoji)
# - Dates must be ISO format: YYYY-MM-DD
# - Numeric values (steps, progress, phases) must be integers
# - Idea Engine automatically parses this section for quick status display
#
# EXAMPLE VALUES - Replace with your actual project data:


---
# Project Status Template

project_name: "Idea Engine"  # Replace with your project name
current_step: 3
total_steps: 5
overall_progress: 60
phases_completed: 12
phases_total: 20
last_updated: "2025-01-15"
health_status: "on_track"
---

## Current Status

**Current Step:** Step 3 of 5  
**Progress:** 60% (12/20 phases)  
**Health:** 🟢 On Track  
**Last Updated:** 2025-01-15

---

## Step Progress Summary

- **Step 1: Foundation** - ✅ Complete (4/4 phases)
  - 1.1 Docker Setup: ✅
  - 1.2 API Foundation: ✅
  - 1.3 Authentication: ✅
  - 1.4 Frontend Foundation: ✅

- **Step 2: Idea CRUD** - ✅ Complete (4/4 phases)
  - 2.1 Idea API: ✅
  - 2.2 Dashboard: ✅
  - 2.3 Detail Page: ✅
  - 2.4 Status Management: ✅

- **Step 3: Notes & Repository** - 🟡 In Progress (2/4 phases)
  - 3.1 Notes System: ✅
  - 3.2 Notes UI: ✅
  - 3.3 Repository Linking: 🟡
  - 3.4 Project Scanning: ⬜

- **Step 4: Research Interface** - ⬜ Not Started
  - 4.1 OpenAI Integration: ⬜
  - 4.2 Research Sessions: ⬜
  - 4.3 Research UI: ⬜
  - 4.4 Cost Tracking: ⬜

- **Step 5: Mobile & Tunnel** - ⬜ Not Started
  - 5.1 Mobile Responsive UI: ⬜
  - 5.2 Cloudflare Tunnel: ⬜
  - 5.3 Mobile Testing: ⬜

**Status Legend:**
- ✅ Complete
- 🟡 In Progress
- ⬜ Not Started
- ⏸️ Blocked
- 🔄 Needs Review

**Note:** Add completion dates only when phases are completed (e.g., `✅ 2025-01-10`). Idea Engine can parse dates from milestones.

---

## Current Blockers

**Active Blockers:**
- None *(or remove this section if no blockers)*

**Recently Resolved:**
*(Leave blank if none. Add resolved blockers here with format:)*
- ✅ [Blocked item description] - Resolved: YYYY-MM-DD

---

## Recent Milestones

- 2025-01-15: Phase 3.2 Complete - Notes UI implemented
- 2025-01-14: Phase 3.1 Complete - Notes API endpoints working
- 2025-01-10: Step 2 Complete - Idea CRUD fully functional

---

## Next Steps

**Immediate Priorities:**
- Complete Phase 3.3 (Repository Linking)
- Begin Phase 3.4 (Active Project Scanning)
- Start Step 4 (Research Interface)

---

## Related Documentation

- `{PROJECT_NAME}_IMPLEMENTATION_PLAN.md` - Detailed task lists (replace "Idea_Engine" with your project name)
- `README.md` - Project overview and setup
- `docs/PORTS.md` - Port configuration (if applicable)

---

**How Idea Engine Uses This File:**

1. Parses YAML frontmatter for quick status summary
2. Reads Step Progress Summary for detailed progress
3. Monitors blockers for stalled projects
4. Tracks milestones for activity timeline
5. Auto-updates when phases complete (if configured)
6. Calculates "days since last activity" from `last_updated` field
**Note:** If YAML frontmatter is invalid or missing, Idea Engine will skip parsing this file and log an error.

**How to Update This Document:**

1. Update YAML frontmatter `last_updated` field (use ISO format: YYYY-MM-DD)
2. Update `health_status` in YAML: `"on_track"`, `"at_risk"`, or `"blocked"` (no emoji in YAML)
3. Update step progress as phases are completed
4. Add milestones when significant progress is made (Idea Engine can parse dates from these)
5. Update blockers section (move resolved items to "Recently Resolved")
6. Update next steps to reflect current priorities
7. Keep phase completion dates minimal (only add when completed)

**Template Usage:**

1. Copy this file to your project: `cp PROJECT_STATUS.md docs/PROJECT_STATUS.md`
2. **Replace YAML frontmatter** with your actual project values:
   - Replace `"Idea Engine"` with your project name
   - Set `current_step`, `total_steps`, `overall_progress`, etc. to actual values
   - Set `health_status` to `"on_track"`, `"at_risk"`, or `"blocked"`
3. **Replace markdown placeholders:**
   - Replace `Idea_Engine` references in documentation links with your project name
   - Update step and phase names to match your implementation plan
4. **Customize content:**
   - Update step progress summary with your actual steps/phases
   - Add your project's milestones and blockers
5. Idea Engine will automatically parse and monitor this file when you link your project directory

**Important:** Ensure YAML frontmatter is valid (no placeholders, proper formatting) or Idea Engine cannot parse it.
