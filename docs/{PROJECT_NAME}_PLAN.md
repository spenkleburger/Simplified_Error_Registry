## {PROJECT_NAME} – Working Plan

> **Template Document** - Copy this file to your project and customize with your actual project details. Replace all placeholders marked with `{...}` throughout the document.

### 1. Vision & Success Criteria
- {Primary goal statement - what are you building and why}
- {Key priorities - what matters most for this project}
- {Core requirements - must-have features or capabilities}
- {Success metrics - how will you know it's working}

### 2. Guiding Principles
- **{Principle 1 Name}:** {Description of principle and how it guides decisions}
- **{Principle 2 Name}:** {Description of principle and how it guides decisions}
- **{Principle 3 Name}:** {Description of principle and how it guides decisions}
- **{Principle 4 Name}:** {Description of principle and how it guides decisions}
- **{Principle 5 Name}:** {Description of principle and how it guides decisions}

### 3. {Domain-Specific Section Title}

{Add project-specific sections here. Examples:}
- {Channel Inventory & Automation Strategy}
- {Status Workflow & UI States}
- {User Roles & Permissions}
- {Integration Requirements}
- {Business Logic Rules}

{Use tables, lists, or detailed descriptions as needed}

### 4. Pipeline Phases (Aligned to UI Screens)

1. **{Screen/Phase 1 Name}**
   - {Description of what user sees and can do}
   - {Key features or actions available}
   - {Data displayed or collected}

2. **{Screen/Phase 2 Name}**
   - {Description of what user sees and can do}
   - {Key features or actions available}
   - {Data displayed or collected}

3. **{Screen/Phase 3 Name}**
   - {Description of what user sees and can do}
   - {Key features or actions available}
   - {Data displayed or collected}

{Continue as needed for all major UI screens or workflow phases}

### 5. Operating Modes (UI + Background Behavior)

- **{Mode 1 Name}:** {Description of when/how this mode is used, what it enables}
- **{Mode 2 Name}:** {Description of when/how this mode is used, what it enables}
- **{Mode 3 Name}:** {Description of when/how this mode is used, what it enables}

{Examples: Automated vs Manual, Active Development vs Background Monitoring, Online vs Offline}

### 6. Tech Stack Recommendation (Front-to-Back)

- **Frontend:** {Framework/library choices}
  - {UI components needed}
  - {State management approach}
  - {Design system or styling approach}
- **Backend:** {Framework/API approach}
  - {API endpoints structure}
  - {Authentication strategy}
  - {Background job processing}
- **Storage:** {Database and file storage choices}
  - {Primary database (PostgreSQL/SQLite/etc.)}
  - {File storage (local/S3/R2)}
  - {Caching strategy (Redis/etc.)}
- **Integrations:** {External services or APIs}
  - {Third-party services needed}
  - {API clients or adapters}
- **Infrastructure:** {Deployment and hosting}
  - {Docker/Docker Compose setup}
  - {Hosting options}
  - {Monitoring and logging}

### 7. Data Model (UI-facing Contracts)

{Use YAML or mermaid diagrams to define your data model}

```yaml
{entity_name}:
  {field_name}: {type}  # {description}
  {field_name}: {type}  # {description}
  {field_name}: {type}  # {description}
```

{Or use mermaid ERD:}

```mermaid
erDiagram
    {ENTITY1} ||--o{ {ENTITY2} : {relationship}
    {ENTITY1} {
        {field} {type}
        {field} {type}
    }
```

{Include all major entities and their relationships}

### 8. Workflow Walkthrough (Dashboard-first)

1. {Step 1: User action and system response}
2. {Step 2: User action and system response}
3. {Step 3: User action and system response}
4. {Step 4: User action and system response}
5. {Step 5: User action and system response}

{Walk through a typical user journey from start to finish}

### 9. File & Project Management

- **{File Structure/Organization}:** {How files are organized}
  - {Directory structure}
  - {Naming conventions}
  - {Version control approach}
- **{Data Storage Strategy}:** {Where and how data is stored}
  - {Database vs file system decisions}
  - {Backup strategy}
  - {Sync strategy if multi-device}

### 10. {Specialized Section 1}

{Add project-specific sections as needed. Examples:}
- {Automation Strategy}
- {Research Workflow}
- {Analytics & Optimization}
- {Internationalization (i18n)}
- {Security Considerations}
- {Cost Tracking}
- {Repository Monitoring}

{Provide detailed information relevant to your project}

### 11. {Specialized Section 2}

{Continue adding specialized sections as needed}

### 12. Scalability, Dockerization & SaaS Potential

#### Dockerization Strategy
**{Yes/No/Recommendation} - Dockerize from the start.**

{Benefits and rationale}

**Recommended Docker Architecture:**
```yaml
services:
  {service1}:  # {description}
  {service2}:  # {description}
  {service3}:  # {description}
```

#### SaaS Repackaging Potential
**{Assessment: Highly viable / Moderate / Not recommended}**

{Analysis of SaaS potential and required modifications}

**Required Modifications for SaaS:**
1. **{Modification 1}:** {Description}
2. **{Modification 2}:** {Description}
3. **{Modification 3}:** {Description}

#### Hosting Options & Cost Estimates

**Option 1: {Hosting Provider}**
- **Pros:** {Advantages}
- **Cons:** {Disadvantages}
- **Cost estimate:**
  - **Single user:** ${X}-${Y}/mo
  - **SaaS (10-50 tenants):** ${X}-${Y}/mo
  - **SaaS (100+ tenants):** ${X}-${Y}/mo

{Repeat for other hosting options}

**Total Cost Summary:**
- {Breakdown of costs}
- {Revenue potential analysis}
- {Profitability assessment}

### 13. Authentication Strategy

**{Single-user / Multi-user / Enterprise} Authentication:**

{Describe authentication approach}
- {Authentication method}
- {User management}
- {Session handling}
- {Security considerations}

**Future SaaS Extension:**
- {How authentication scales}
- {Additional features needed}

### 14. Database Choice: {PostgreSQL / SQLite / Other}

**{Database} Recommendation:**

{Why this database was chosen}
- {Advantages}
- {Trade-offs considered}
- {Migration considerations if applicable}

### 15. {Additional Technical Decisions}

{Add sections for other important technical decisions:}
- {Storage Strategy}
- {API Design}
- {Error Handling}
- {Logging & Monitoring}
- {Testing Strategy}

### 16. Phase 1 MVP: Minimum Viable Product Definition

**Goal:** {What the MVP achieves}

**Phase 1 MVP Features:**

**Core Features (Must Have):**
1. **{Feature 1}:**
   - {Description}
   - {Key capabilities}
2. **{Feature 2}:**
   - {Description}
   - {Key capabilities}
3. **{Feature 3}:**
   - {Description}
   - {Key capabilities}

**Deferred to Phase 2:**
- {Feature deferred}
- {Feature deferred}
- {Feature deferred}

**Deferred to Phase 3:**
- {Feature deferred}
- {Feature deferred}

**Technical Stack (MVP):**
- {Frontend:} {Technology}
- {Backend:} {Technology}
- {Database:} {Technology}
- {Infrastructure:} {Technology}

**Success Criteria:**
- {Criterion 1}
- {Criterion 2}
- {Criterion 3}

### 17. Implementation Plan Structure

**Development Approach: {Feature-by-Feature / Module-by-Module / Other}**

{Describe development approach}

**Implementation Structure: {Large Steps with Phases / Sprints / Other}**

**Step Structure:**
Each major step contains smaller phases. At the end of each phase, all code is tested. At the end of each step, comprehensive code review and security review are conducted.

**Example Step Breakdown:**

**Step 1: {Step Name}**
- Phase 1.1: {Phase description}
- Phase 1.2: {Phase description}
- Phase 1.3: {Phase description}
- **End of Step 1:** Code review, security review, testing complete

{Continue for all steps}

**Testing at End of Each Phase:**
- {Testing approach}
- {Test types}
- {Quality gates}

**Code & Security Review at End of Each Step:**
- {Review process}
- {Review criteria}
- {Documentation requirements}

### 18. Immediate Next Steps / Questions

1. {Question or decision needed}
2. {Question or decision needed}
3. {Question or decision needed}
4. {Question or decision needed}
5. {Question or decision needed}

{List open questions, decisions needed, or immediate action items}

### 19. Key Decisions Summary & Discussion

**Decisions Made:**
1. ✅ **{Decision 1}:** {What was decided and why}
2. ✅ **{Decision 2}:** {What was decided and why}
3. ✅ **{Decision 3}:** {What was decided and why}

**Recommendations & Rationale:**

**{Decision Topic}:**
- **Chose {Option}** because {rationale}
- {Trade-offs considered}
- {Alternatives evaluated}

{Continue for major decisions}

**Next Steps:**
- {Action item 1}
- {Action item 2}
- {Action item 3}

**Open Questions (if any):**
- {Open question 1}
- {Open question 2}

---

**Template Usage:**

1. Copy this file: `cp {PROJECT_NAME}_PLAN.md MyProject_PLAN.md`
2. Replace all `{PROJECT_NAME}` with your actual project name
3. Replace all `{...}` placeholders with your project-specific content
4. Customize sections based on your project needs
5. Add or remove sections as appropriate
6. Reference examples:
   - `C:\Projects\Marketing_Automation\docs\MARKETING_AUTOMATION_PLAN.md`
   - `C:\Projects\Idea_Engine\docs\IDEA_ENGINE_PLAN.md`

**Note:** This template provides a comprehensive structure. Not all sections may be relevant to every project. Customize as needed.

