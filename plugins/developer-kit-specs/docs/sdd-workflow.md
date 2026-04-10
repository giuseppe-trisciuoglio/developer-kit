# Specification-Driven Development — Complete Workflow

This document covers the full SDD lifecycle from idea to production-ready code.

## The SDD Triangle

SDD enforces a three-way alignment between specification, tests, and implementation:

```
          Specification
         /              \
        /                \
    Tests  ←─────────  Code
```

Every change should update all three vertices. The sync commands keep them aligned.

## Lifecycle Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 1: SPECIFICATION                                             │
│  brainstorm → spec-quality-check → spec-to-tasks                   │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 2: IMPLEMENTATION (per task, repeat for each)                │
│  task-tdd (RED) → task-implementation (GREEN) → task-review        │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 3: FINALIZATION                                              │
│  code-cleanup → spec-sync-with-code → spec-sync-context            │
├─────────────────────────────────────────────────────────────────────┤
│  AUTOMATION (optional)                                              │
│  ralph-loop: automates Phase 2-3 across all tasks                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Specification

### 1.1 Choose Your Entry Point

| Scenario | Command | Output |
|----------|---------|--------|
| New complex feature | `/specs:brainstorm "idea"` | Full 9-phase specification |
| Bug fix or small change | `/specs:quick-spec "fix"` | Minimal 4-phase specification |

**When to use `brainstorm` vs `quick-spec`:**

- **brainstorm**: 5+ files involved, unclear requirements, multiple stakeholders, needs architectural decisions
- **quick-spec**: 1-3 files, clear solution, well-understood context, ≤4 acceptance criteria

#### Example: Complex Feature (brainstorm)

```
/specs:brainstorm Add a hotel search engine with multi-provider aggregation,
real-time availability, price comparison, and guest review scoring
```

Claude goes through these phases:

**Phase 1 — Context Discovery:**
Claude reads your project structure, identifies existing patterns, and checks for related code:
```
Exploring project structure...
Found: Spring Boot 3.2, Spring WebFlux, MongoDB, Redis
Existing: /src/main/java/com/example/search/ (search infrastructure)
Missing: No hotel-specific models or services detected
```

**Phase 1.5 — Complexity Assessment:**
Claude estimates task count. If >15 tasks, recommends splitting:
```
Estimated tasks: 22 — exceeds 15-task limit.
Recommendation: Split into 3 specifications:
  001-hotel-search-data-model  (6 tasks)
  002-hotel-search-aggregation (8 tasks)
  003-hotel-search-api         (5 tasks)
```

**Phase 2 — Idea Refinement:**
Claude asks targeted questions (max 3):
```
Question 1 of 3:
"Should the search support real-time availability via provider APIs,
 or is cached/periodic data sufficient?"
  a) Real-time via provider APIs (recommended for accuracy)
  b) Cached with periodic refresh (better performance)
  c) Hybrid: real-time for availability, cached for pricing
```

**Phase 3 — Functional Approach Exploration:**
Claude presents 2-3 approaches without prescribing technology:
```
Approach A: Direct Provider Integration
  - Each hotel provider has a dedicated adapter
  - Sequential queries to each provider
  - Simple error handling (fail-fast)

Approach B: Aggregation Pipeline (recommended)
  - Unified provider interface
  - Parallel queries with reactive composition
  - Graceful degradation (partial results allowed)
```

**Phase 5 — Specification Generation:**
Output specification is technology-agnostic — describes WHAT, not HOW:

```markdown
## Hotel Search Engine — Functional Specification

### Search Request
The system shall accept search requests containing:
- Destination (city, coordinates, or landmark)
- Check-in and check-out dates
- Number of guests and rooms
- Optional filters: price range, star rating, amenities

### Search Response
The system shall return results containing:
- Hotel name, images, star rating
- Available room types with pricing
- Guest review score (1-10) with review count
- Provider source and booking URL
```

#### Example: Simple Fix (quick-spec)

```
/specs:quick-spec Fix the N+1 query issue when loading user orders with items
```

Claude skips idea refinement and approach exploration, going straight to:
```
Phase 1 — Quick Context:
  Found: UserRepository, OrderService, OrderRepository
  Issue: OrderService.findAll() triggers lazy loading per order

Phase 2 — Problem + Solution Checkpoint:
  Problem: N+1 query on Order.findAll() → lazy loads items for each order
  Solution: Use JOIN FETCH in repository query

Phase 3 — Generate Minimal Spec:
  docs/specs/004-fix-n1-orders/2026-04-10--fix-n1-orders.md
  Acceptance criteria: 3 (within limit of 4)
```

### 1.2 Quality Check the Specification

After generating a specification, validate it:

```
/specs:spec-quality-check docs/specs/001-hotel-search/
```

Claude asks up to 5 targeted questions, one at a time:

```
Question 1 of 5:
"The specification mentions 'real-time availability' but doesn't specify
a timeout. What should happen if a provider takes >5 seconds to respond?"

Your answer: "Return cached data if available, otherwise skip that provider"
→ Integrated into specification under "Error Handling" section
```

Quality scan covers 12 taxonomy areas:
- Completeness and Clarity
- Domain and Data Model
- Interaction and UX Flow
- Non-Functional Requirements (performance, scalability, security)
- Edge Cases and Error Handling
- Architecture Alignment (if architecture.md exists)

### 1.3 Generate Tasks

```
/specs:spec-to-tasks --lang=spring docs/specs/001-hotel-search/
```

This is the bridge from functional specification to executable code:

**What happens:**
1. Reads the specification and extracts requirements (assigned REQ-IDs)
2. Loads or creates a Knowledge Graph (`knowledge-graph.json`)
3. Explores your codebase with language-specific patterns
4. Updates the Knowledge Graph with discoveries
5. Decomposes requirements into atomic tasks
6. Generates a traceability matrix
7. Enforces task limit (≤15 implementation tasks)

**Task file structure:**
```markdown
---
id: TASK-003
title: Implement hotel availability aggregation
spec: docs/specs/001-hotel-search
lang: spring
status: pending
complexity: 65
dependencies: [TASK-001, TASK-002]
provides: [HotelAggregationService, AggregatedResult]
expects: [HotelProviderClient, ProviderResponse]
started_date:
implemented_date:
reviewed_date:
completed_date:
---

## Description
Implement the service that queries multiple hotel providers in parallel
and aggregates results into a unified response.

## Acceptance Criteria
- [ ] Query all configured providers in parallel
- [ ] Return results within 3 seconds total
- [ ] Gracefully handle provider timeouts
- [ ] Deduplicate results by hotel ID
- [ ] Sort by price (ascending) as default

## Definition of Done
- [ ] All acceptance criteria checked
- [ ] Unit tests written and passing
- [ ] Integration test with mock providers
- [ ] Code follows project conventions
- [ ] No TODOs or placeholder code
```

**Traceability matrix example:**
```markdown
| REQ-ID | Requirement | TASK-001 | TASK-002 | TASK-003 |
|--------|------------|----------|----------|----------|
| REQ-01 | Search by destination | ✅ | | |
| REQ-02 | Multi-provider query | | ✅ | ✅ |
| REQ-03 | Price sorting | | | ✅ |
```

### 1.4 Manage Tasks

View, split, or reorganize tasks before implementation:

```
# List all tasks with status and complexity
/specs:task-manage --action=list --spec="docs/specs/001-hotel-search/"

# Split a complex task (complexity ≥ 50)
/specs:task-manage --action=split --task="docs/specs/001-hotel-search/tasks/TASK-003.md"

# Add a new task
/specs:task-manage --action=add --spec="docs/specs/001-hotel-search/"

# Mark a task as optional
/specs:task-manage --action=mark-optional --task="docs/specs/001-hotel-search/tasks/TASK-006.md"
```

---

## Phase 2: Implementation

For each task, follow one of two approaches:

### Approach A: Direct Implementation

```
/specs:task-implementation --lang=spring --task="docs/specs/001-hotel-search/tasks/TASK-001.md"
```

### Approach B: TDD (Test-Driven Development)

```
# RED phase — generate failing tests
/specs:task-tdd --lang=spring --task="docs/specs/001-hotel-search/tasks/TASK-001.md"

# GREEN phase — implement to make tests pass
/specs:task-implementation --lang=spring --task="docs/specs/001-hotel-search/tasks/TASK-001.md"
```

### Implementation Process (12 Steps)

When you run `task-implementation`, Claude follows this structured process:

| Step | Action | Gate |
|------|--------|------|
| T-1 | Parse task file, extract parameters | Valid task file required |
| T-2 | Check git state (clean working tree) | No uncommitted changes |
| T-3 | Validate dependencies (all completed) | All deps in `completed` status |
| T-3.5 | Validate against Knowledge Graph | Required components exist |
| T-3.6 | Contract validation (provides/expects) | Contracts compatible |
| T-4 | **Implement the code** | — |
| T-5 | Run tests, verify acceptance criteria | All tests pass |
| T-6 | Update task status, write summary | — |
| T-6.5 | Update Knowledge Graph | — |
| T-6.6 | Check for spec deviations | Report any drift |

**Automatic hooks fire during implementation:**
- `task-auto-status.py` — Updates status when you edit the task file
- `task-kpi-analyzer.py` — Calculates quality KPIs
- `drift-monitor.py` — Watches for unplanned file changes

### Task Status Lifecycle

```
pending → in_progress → implemented → reviewed → completed
              ↓
          blocked (can return to in_progress)
```

Status transitions happen automatically based on your actions:

| Your Action | Status Change |
|-------------|---------------|
| Start editing a task file | `pending` → `in_progress` |
| Check acceptance criteria boxes | Progress tracked |
| Check all DoD boxes | `implemented` → ready for review |
| Review passes | `reviewed` |
| Cleanup completes | `completed` |

### Language-Specific Agents

Implementation uses language-specific review agents:

| `--lang` Value | Framework | Review Agent |
|----------------|-----------|--------------|
| `spring` | Spring Boot | `developer-kit-java:spring-boot-code-review-expert` |
| `java` | Java SE | `developer-kit-java:java-software-architect-review` |
| `nestjs` | NestJS | `developer-kit-typescript:nestjs-code-review-expert` |
| `typescript` | Node.js | `developer-kit:general-code-reviewer` |
| `react` | React | `developer-kit:general-code-reviewer` |
| `python` | Django/FastAPI | `developer-kit-python:python-code-review-expert` |
| `php` | Laravel/Symfony | `developer-kit-php:php-code-review-expert` |
| `general` | Any | `developer-kit:general-code-reviewer` |

---

## Phase 3: Finalization

### 3.1 Review

```
/specs:task-review --lang=spring docs/specs/001-hotel-search/tasks/TASK-001.md
```

The review checks 4 dimensions:

1. **Implementation Verification** — Does the code match the task description?
2. **Acceptance Criteria** — Are all checkboxes ✅?
3. **Specification Compliance** — Does it align with the functional spec?
4. **Code Quality** — Language-specific review (patterns, security, conventions)

**Review outcomes:**

| Status | Condition |
|--------|-----------|
| **PASSED** | All criteria ✅, all DoD ✅, no critical code issues |
| **FAILED** | Any criterion ❌ or ⚠️, or critical code issues found |

Output: `TASK-001--review.md` with detailed findings.

**If FAILED:** Fix the issues and re-run task-implementation. The Ralph Loop automates this cycle.

### 3.2 Code Cleanup

```
/developer-kit-specs:specs-code-cleanup --lang=spring --task="docs/specs/001-hotel-search/tasks/TASK-001.md"
```

8-phase cleanup process:

1. Verify task is in `reviewed` status
2. Identify files from review report and task provides
3. Remove debug artifacts (`console.log`, `System.out.println`, temporary comments)
4. Optimize imports
5. Run formatters (`spotless:apply`, `prettier`, `black`)
6. Verify documentation headers
7. Run final tests
8. Mark task as `completed`

### 3.3 Sync Specification

After completing tasks, sync the specification with the implementation:

```
/specs:spec-sync-with-code docs/specs/001-hotel-search/
```

This detects three types of deviations:

| Deviation Type | Example |
|---------------|---------|
| **Scope Expansion** | Added refresh token support not in original spec |
| **Requirement Refinement** | Changed password policy from 8 to 12 characters |
| **Scope Reduction** | Deferred 2FA to a future specification |

The sync command:
- Compares acceptance criteria vs actual implementation
- Proposes spec updates with revision markers
- Creates new tasks for unexpected scope expansions
- Updates the revision history section

### 3.4 Sync Context

```
/specs:spec-sync-context docs/specs/001-hotel-search/
```

This keeps technical context aligned:

1. **Gap Analysis** — Identifies discrepancies between Knowledge Graph, tasks, and codebase
2. **Knowledge Graph Update** — Extracts new components, APIs, patterns from implemented code
3. **Task Enrichment** — Updates task files with improved technical context
4. **Drift Detection** — Checks if spec document reflects actual implementation

**Options:**
```bash
# Preview changes without writing
/specs:spec-sync-context --spec="docs/specs/001-hotel-search/" --dry-run

# Update only the Knowledge Graph
/specs:spec-sync-context --spec="docs/specs/001-hotel-search/" --update-kg-only

# Sync after a specific task
/specs:spec-sync-context --spec="docs/specs/001-hotel-search/" --task="TASK-003"
```

---

## Automation: Ralph Loop

For multi-task implementations, the Ralph Loop automates the entire cycle:

```
# Initialize the loop
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-hotel-search/

# Run one step (execute the shown command, then run again)
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-hotel-search/
```

Each `loop` invocation executes exactly one step from the state machine:

```
choose_task → implementation → review → fix (if needed) → cleanup → sync → update_done → choose_task
```

The Ralph Loop supports **multi-agent execution** — different AI agents can implement different tasks:

```yaml
---
id: TASK-003
title: Implement aggregation service
agent: codex  # Use Codex CLI for this task
---
```

Supported agents: `claude`, `codex`, `copilot`, `gemini`, `glm4`, `kimi`, `minimax`

### Fully Automated Orchestration

For hands-off execution, use `agents_loop.py` to automate the entire loop — no manual step execution needed:

```bash
# Fully automated with auto agent selection and KPI quality gates
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-hotel-search/ \
  --agent=auto \
  --kpi-check
```

This script calls `ralph_loop.py` internally, executes each command with the chosen agent, advances the state, and repeats until all tasks are complete. It supports `--fast` mode, `--reviewer` override, and automatic KPI-based quality iteration.

See the [Ralph Loop Guide](./ralph-loop-guide.md) for complete documentation of both manual and automated modes.

---

## File Structure Reference

A complete specification directory:

```
docs/specs/001-hotel-search/
├── 2026-04-10--hotel-search.md             # Main functional specification
├── 2026-04-10--hotel-search--tasks.md       # Task index
├── user-request.md                          # Original user input
├── brainstorming-notes.md                   # Brainstorming session context
├── decision-log.md                          # Decision audit trail
├── traceability-matrix.md                   # Requirements → Tasks mapping
├── knowledge-graph.json                     # Cached codebase analysis
├── tasks/
│   ├── TASK-001.md                          # Create data models
│   ├── TASK-001--kpi.json                   # Auto-generated quality KPIs
│   ├── TASK-001--review.md                  # Review report
│   ├── TASK-002.md                          # Implement provider clients
│   ├── TASK-002--kpi.json
│   ├── TASK-003.md                          # Implement aggregation
│   ├── TASK-004.md                          # REST API endpoints
│   ├── TASK-005.md                          # E2E tests
│   └── TASK-006.md                          # Cleanup and finalization
├── _ralph_loop/
│   └── fix_plan.json                        # Ralph Loop state (auto-managed)
└── _drift/
    └── tdd-handoff-TASK-001.md              # TDD handoff artifacts
```

---

## Real-World Example: Full Feature

Here's a concrete example implementing a **notification system** for a NestJS application:

```
# 1. Brainstorm
/specs:brainstorm Add a notification system with email, SMS, and push channels
   with template management and delivery tracking

# 2. Quality check
/specs:spec-quality-check docs/specs/002-notification-system/

# 3. Generate tasks
/specs:spec-to-tasks --lang=nestjs docs/specs/002-notification-system/
   → Generates 8 tasks

# 4. List tasks
/specs:task-manage --action=list --spec="docs/specs/002-notification-system/"
   TASK-001 [pending]  Create notification entity and repository    complexity: 35
   TASK-002 [pending]  Implement template engine                     complexity: 50
   TASK-003 [pending]  Build email channel adapter                   complexity: 40
   TASK-004 [pending]  Build SMS channel adapter                     complexity: 40
   TASK-005 [pending]  Build push notification adapter               complexity: 45
   TASK-006 [pending]  Create notification orchestration service     complexity: 60
   TASK-007 [pending]  Add REST API endpoints                        complexity: 35
   TASK-008 [pending]  E2E tests and cleanup                        complexity: 30

# 5. Split complex task
/specs:task-manage --action=split --task="docs/specs/002-notification-system/tasks/TASK-006.md"
   → Split into TASK-006A (orchestrator) and TASK-006B (delivery tracking)

# 6. Implement each task
/specs:task-implementation --lang=nestjs --task="docs/specs/002-notification-system/tasks/TASK-001.md"
/specs:task-review --lang=nestjs docs/specs/002-notification-system/tasks/TASK-001.md
/developer-kit-specs:specs-code-cleanup --lang=nestjs --task="docs/specs/002-notification-system/tasks/TASK-001.md"

# Repeat for TASK-002 through TASK-006B...

# 7. Final sync
/specs:spec-sync-with-code docs/specs/002-notification-system/
/specs:spec-sync-context docs/specs/002-notification-system/

# 8. Or automate everything with Ralph Loop
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/002-notification-system/
```

---

## Hooks: Automatic Quality Gates

The plugin installs hooks that run automatically during your workflow:

| Hook | Trigger | What It Does |
|------|---------|-------------|
| `task-auto-status.py` | Edit any `TASK-*.md` file | Updates status based on checkbox changes |
| `task-kpi-analyzer.py` | Edit any `TASK-*.md` file | Calculates quality KPIs to `TASK-XXX--kpi.json` |
| `drift-init.py` | User submits a prompt | Initializes drift tracking for current spec |
| `drift-monitor.py` | Write or Edit any file | Monitors for changes outside task scope |
| `drift-report.py` | Task marked completed | Generates fidelity report |
| Session Tracking | Claude finishes a response | Creates audit trail in `tracking_log.md` |

These hooks require no configuration — they activate automatically when the plugin is installed.
