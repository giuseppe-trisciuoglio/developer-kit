# Specification-Driven Development — Complete Workflow

This document covers the full SDD lifecycle from idea to production-ready code.

## The SDD Loop

SDD enforces alignment between specification and implementation:

```
          Specification
         /              \
        /                \
       └────────────────── Code
```

Every change should update both vertices. The sync commands keep them aligned.

## Lifecycle Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 0: CONSTITUTION (first time only)                            │
│  constitution create → defines architectural DNA of the project     │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 1: SPECIFICATION                                             │
│  brainstorm → spec-check → spec-to-tasks                   │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 2: IMPLEMENTATION (per task, repeat for each)                │
│  task-implementation → task-review                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 3: FINALIZATION                                              │
│  sync (full) → Knowledge Graph update + Drift detection            │
├─────────────────────────────────────────────────────────────────────┤
│  AUTOMATION (optional)                                              │
│  ralph-loop: automates Phase 2-3 across all tasks                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Constitution (First-Time Setup)

Before writing any specification, establish the **architectural DNA** of your project:

```
/developer-kit-specs:constitution create
```

This creates `docs/specs/architecture.md` (and optionally `docs/specs/ontology.md`) — documents that define:
- Approved technology stack and forbidden libraries
- Architectural rules (e.g., constructor injection, no field injection)
- API standards and authentication approach
- Security constraints with CWE mappings
- AI guardrails that govern all subsequent code generation

**You only run `create` once per project.** After that, use `update` to evolve them and `check` to validate specs/tasks against them.

```
# Validate a spec against the constitution
/developer-kit-specs:constitution check --target=docs/specs/001-user-auth/2026-04-10--user-auth.md

# Update a section
/developer-kit-specs:constitution update --file=architecture --section=security
```

The constitution feeds into every subsequent phase — brainstorm, spec-to-tasks, task-implementation, and task-review all respect its guardrails.

---

## Phase 1: Specification

### 1.1 Choose Your Entry Point

| Scenario | Command | Output |
|----------|---------|--------|
| New complex feature | `/developer-kit-specs:specs.brainstorm "idea"` | Full 9-phase specification |
| Bug fix | `/developer-kit-specs:specs.change-spec --type=bugfix` | Bug fix specification |
| Modify existing feature | `/developer-kit-specs:specs.change-spec --type=delta` | Delta specification |
| Document bug fix | `/developer-kit-specs:specs.change-spec --type=bugfix` | Bug fix specification |
| Document technical approach | `/developer-kit-specs:specs.technical-plan --spec=...` | Technical plan |

**When to use each command:**

- **brainstorm**: Standard entry point for all new features, regardless of scope
- **change-spec delta**: Adding new feature to existing system, modifying existing behavior
- **change-spec bugfix**: Bug fix requiring root cause analysis and regression prevention
- **technical-plan**: After brainstorm, document HOW the feature will be built (stack, decisions, phases)

#### Example: Complex Feature (brainstorm)

```
/developer-kit-specs:specs.brainstorm Add a hotel search engine with multi-provider aggregation,
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

#### Example: Bug Fix

```
/developer-kit-specs:specs.change-spec --type=bugfix --spec=docs/specs/001-feature/ \
  --title="Fix N+1 query issue"
```

Claude gathers bug information and performs root cause analysis:
```
Phase 1 — Bug Discovery:
  Found: UserRepository, OrderService, OrderRepository
  Issue: OrderService.findAll() triggers lazy loading per order

Phase 2 — Root Cause Analysis:
  Root Cause: Missing JOIN FETCH causes N+1 queries
  Location: OrderRepository.java:45
  Solution: Add @Query with JOIN FETCH

Phase 3 — Bug Fix Document Generated:
  docs/specs/001-feature/changes/2026-04-10--bugfix--n1-orders.md
```

### 1.2 Quality Check the Specification

After generating a specification, validate it:

```
/developer-kit-specs:specs.spec-check docs/specs/001-hotel-search/
```

Claude resolves any `[NEEDS CLARIFICATION]` markers from brainstorming, then asks up to 5 targeted questions, one at a time:

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
- `[NEEDS CLARIFICATION]` Markers (resolved first, before scan)

### 1.3 Generate Tasks

```
/developer-kit-specs:specs.spec-to-tasks --lang=spring docs/specs/001-hotel-search/
```

This is the bridge from functional specification to executable code:

**What happens:**
1. Reads the specification and extracts requirements (assigned REQ-IDs)
2. Generates `data-model.md` and `contracts/*` directly from the specification
3. Optionally reuses an existing Knowledge Graph (`knowledge-graph.json`) if present
4. Explores your codebase with language-specific patterns
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
/developer-kit-specs:specs.task-manage --action=list --spec="docs/specs/001-hotel-search/"

# Split a complex task (complexity ≥ 50)
/developer-kit-specs:specs.task-manage --action=split --task="docs/specs/001-hotel-search/tasks/TASK-003.md"

# Add a new task
/developer-kit-specs:specs.task-manage --action=add --spec="docs/specs/001-hotel-search/"

# Mark a task as optional
/developer-kit-specs:specs.task-manage --action=mark-optional --task="docs/specs/001-hotel-search/tasks/TASK-006.md"
```

### 1.5 Document Technical Plan (Optional)

After generating a specification with brainstorm, you may want to document the technical approach:

```
/developer-kit-specs:specs.technical-plan --spec=docs/specs/001-hotel-search/
```

The technical plan captures:
- **Technology Stack**: Exact versions with rationale (no ranges)
- **Architecture Decisions**: Key decisions with alternatives considered (AD-001, AD-002, ...)
- **Implementation Phases**: Step-by-step build plan with milestones
- **Performance Requirements**: Measurable targets (response time, throughput)
- **Risk Assessment**: What could go wrong and how to detect it
- **Project Structure**: Directory organization and naming conventions

### 1.6 Document Changes (Delta/Bug Fix)

For modifying existing systems, use change-spec:

```
# Delta: Adding new feature to existing system
/developer-kit-specs:specs.change-spec --type=delta --spec=docs/specs/001-hotel-search/ \
  --title="Add multi-currency support"

# Bug Fix: With root cause analysis
/developer-kit-specs:specs.change-spec --type=bugfix --spec=docs/specs/001-hotel-search/ \
  --title="Fix session timeout calculation"
```

Key features of change-spec:
- **Root Cause Analysis**: Not just symptom, but WHY the bug exists
- **Unchanged Behavior**: MANDATORY section preventing regressions
- **EARS Syntax**: Standardized requirements format

---

## Phase 2: Implementation

For each task, follow the implementation workflow:

### Implementation

```
/developer-kit-specs:specs.task-implementation --lang=spring --task="docs/specs/001-hotel-search/tasks/TASK-001.md"
```

Claude reads the task, analyzes existing code, and implements the required logic following the specification and architectural guardrails.

### Review

```
/developer-kit-specs:specs.task-review --task="docs/specs/001-hotel-search/tasks/TASK-001.md"
```

Claude verifies the implementation against acceptance criteria, checks for architectural drift, and validates contract adherence.

---

## Phase 3: Finalization

### Spec Sync

Keep your specification in sync with implementation decisions:

```
# Full sync: Knowledge Graph update + Drift detection
/developer-kit-specs:specs.sync docs/specs/001-hotel-search/

# Update technical context (KG) only
/developer-kit-specs:specs.sync docs/specs/001-hotel-search/ --kg-only
```

---

## Automation: Ralph Loop

Automate the entire implementation-review cycle across all tasks:

```
/developer-kit-specs:specs.ralph-loop --spec="docs/specs/001-hotel-search/"
```

Ralph Loop will:
1. Identify the next pending task
2. Run `task-implementation` (includes cleanup Phase T-7)
3. Run `task-review`
4. If review fails, iterate (up to 3 times) to fix issues
5. Move to the next task until the feature is complete
6. Run finalization commands automatically
