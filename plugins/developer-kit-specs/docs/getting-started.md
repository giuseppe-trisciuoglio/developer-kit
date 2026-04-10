# Getting Started — Specification-Driven Development

This guide walks you through the core concepts of SDD and gets you productive in minutes.

## What is SDD?

Specification-Driven Development (SDD) is a workflow where you define **WHAT** you want to build before writing any code. The specification becomes a contract between your idea and the implementation, enforced through automated quality gates.

```
Idea → Specification → Tasks → Implementation → Review → Cleanup → Done
       (brainstorm)  (spec-to-tasks)             (task-review)  (code-cleanup)
```

**Why SDD?**
- **Eliminates ambiguity**: Every feature is defined functionally before coding starts
- **Traceability**: Every line of code traces back to a requirement
- **Quality gates**: Automated review ensures nothing is missed
- **Living docs**: Specifications evolve alongside the codebase

## Prerequisites

- **Claude Code** installed and configured
- **Python 3.11+** (for hook scripts and Ralph Loop automation)
- **developer-kit-core** plugin installed (provides general-purpose agents)
- A **git repository** with at least one commit

## Installation

```bash
# Install the plugin from marketplace
/plugin marketplace add giuseppe-trisciuoglio/developer-kit

# Or install from local directory
/plugin install /path/to/developer-kit/plugins/developer-kit-specs
```

Verify installation:

```
/help
# You should see /specs:brainstorm, /specs:spec-to-tasks, etc.
```

## Your First Specification

Let's build a real feature: **user authentication with JWT tokens** for a Spring Boot application.

### Step 1: Brainstorm the Idea

```
/specs:brainstorm Add user authentication with JWT tokens for a Spring Boot REST API
```

Claude will guide you through a 9-phase process:

1. **Context Discovery** — Analyzes your project structure, existing code patterns, dependencies
2. **Complexity Assessment** — Checks if the idea should be split into multiple specifications
3. **Idea Refinement** — Asks up to 3 clarifying questions (e.g., "Should refresh tokens be supported?")
4. **Functional Approach Exploration** — Presents 2-3 approaches, focusing on WHAT not HOW
5. **Contextual Codebase Exploration** — Examines existing security config, user entities, etc.
6. **Specification Presentation** — Shows the functional specification section by section
7. **Specification Generation** — Creates the full spec document
8. **Quality Review** — Verifies completeness and consistency
9. **Summary** — Lists outputs and recommended next steps

**Output files created:**
```
docs/specs/001-user-auth/
├── 2026-04-10--user-auth.md        # Main functional specification
├── user-request.md                  # Your original request
├── brainstorming-notes.md           # Session context and decisions
└── decision-log.md                  # Decision audit trail
```

The specification is technology-agnostic. It describes behaviors, not implementation details.

### Step 2: Convert to Tasks

```
/specs:spec-to-tasks --lang=spring docs/specs/001-user-auth/
```

Claude analyzes your specification and generates executable tasks:

1. **Reads the specification** and extracts functional requirements
2. **Explores your codebase** to understand existing patterns (Spring Security, User entities, etc.)
3. **Breaks requirements into tasks** — atomic, testable units with clear acceptance criteria
4. **Generates a traceability matrix** mapping requirements to tasks

**Output files created:**
```
docs/specs/001-user-auth/
├── 2026-04-10--user-auth--tasks.md    # Task index
├── knowledge-graph.json                # Cached codebase analysis
├── traceability-matrix.md             # Requirements → Tasks mapping
└── tasks/
    ├── TASK-001.md    # Create User entity and repository
    ├── TASK-002.md    # Implement JWT token service
    ├── TASK-003.md    # Create authentication endpoints
    ├── TASK-004.md    # Add Spring Security configuration
    ├── TASK-005.md    # Write e2e tests for auth flow
    └── TASK-006.md    # Code cleanup and finalization
```

Each task file contains:
- **Frontmatter**: ID, title, status, dependencies, provides/expects contracts
- **Description**: What to implement
- **Acceptance Criteria**: Checkboxes for verification
- **Definition of Done**: Quality checklist

### Step 3: Implement a Task

```
/specs:task-implementation --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md"
```

Claude follows a structured 12-step process:

1. **Validates prerequisites** — Checks git state, task dependencies, contracts
2. **Implements the code** — Writes production code following your project conventions
3. **Runs verification** — Executes tests, validates acceptance criteria
4. **Updates task status** — Automatically marks `in_progress` → `implemented`

**Hooks fire automatically:**
- `task-auto-status.py` updates the task frontmatter based on checkbox changes
- `task-kpi-analyzer.py` calculates quality KPIs and saves them to `TASK-001--kpi.json`

### Step 4: Review the Implementation

```
/specs:task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
```

The review validates 4 dimensions:

| Dimension | What It Checks |
|-----------|---------------|
| **Implementation** | Does the code match the task description? |
| **Acceptance Criteria** | Are all criteria met? |
| **Spec Compliance** | Does it align with the original specification? |
| **Code Quality** | Language-specific best practices, patterns, security |

**Output:** `TASK-001--review.md` with pass/fail status and detailed findings.

### Step 5: Clean Up and Complete

If the review passes:

```
/developer-kit-specs:specs-code-cleanup --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md"
```

This final step:
- Removes debug logs (`System.out.println`, temporary comments)
- Optimizes imports
- Runs language-specific formatters (`./mvnw spotless:apply`)
- Verifies tests still pass
- Marks the task as `completed`

### Step 6: Sync Specification with Implementation

After implementing several tasks, sync the spec with reality:

```
/specs:spec-sync-with-code docs/specs/001-user-auth/
```

This detects deviations (scope expansions, refinements, reductions) and updates the specification to match what was actually built.

## What's Next?

- **[SDD Workflow](./sdd-workflow.md)** — Complete workflow documentation with all phases
- **[Commands Reference](./commands-reference.md)** — Detailed command documentation with examples
- **[Ralph Loop Guide](./ralph-loop-guide.md)** — Automate task execution across multiple agents (manual and fully automated via `agents_loop.py`)
- **[TDD Workflow](./tdd-workflow.md)** — Test-Driven Development integration
- **[KPI Evaluation](./kpi-evaluation.md)** — Understanding quality metrics and scoring

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/specs:brainstorm "idea"` | Create a full specification |
| `/specs:quick-spec "fix"` | Create a minimal spec for small changes |
| `/specs:spec-to-tasks --lang=spring spec/` | Generate executable tasks |
| `/specs:task-implementation --lang=spring --task=TASK.md` | Implement a task |
| `/specs:task-tdd --lang=spring --task=TASK.md` | Generate failing tests first (RED) |
| `/specs:task-review --lang=spring TASK.md` | Review implementation |
| `/developer-kit-specs:specs-code-cleanup --lang=spring --task=TASK.md` | Final cleanup |
| `/specs:spec-sync-with-code spec/` | Sync spec with implementation |
| `/specs:spec-sync-context spec/` | Sync Knowledge Graph and context |
| `/specs:task-manage --action=list` | List and manage tasks |
| `agents_loop.py --spec=spec/ --agent=auto` | Fully automated multi-agent orchestration |
