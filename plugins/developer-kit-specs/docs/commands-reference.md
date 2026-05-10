# Commands Reference

Complete reference for all SDD commands with arguments, options, and real-world examples.

---

## `/developer-kit-specs:constitution`

Establish and maintain the architectural DNA of a project through two shared documents: `docs/specs/architecture.md` (technology stack, rules, guardrails) and `docs/specs/ontology.md` (domain glossary / Ubiquitous Language). Can be used before `brainstorm` as a project setup step.

### Syntax

```
/developer-kit-specs:constitution [operation] [options]
```

### Operations

| Operation | Description |
|-----------|-------------|
| `create` | Interactively create `docs/specs/architecture.md` and/or `docs/specs/ontology.md` |
| `update` | Update a specific section of the existing constitution |
| `check` | Validate a spec, task, or file against the constitution |
| `show` | Display the current constitution |

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `--section` | For `update` | Section to update: `stack`, `architecture`, `api`, `testing`, `security`, `guardrails` |
| `--target` | For `check` | Path to the spec/task/file to validate |

### When to Use

- **`create`**: First step of any new SDD project — run before `brainstorm`
- **`update`**: When technology choices or security requirements change
- **`check`**: Before approving a spec or task plan; integrated into `task-review`
- **`show`**: Quick reference during development

### Constitution Check Report

The `check` operation produces a report with three severity levels:

| Level | Meaning |
|-------|---------|
| `CRITICAL` | Violates a non-negotiable rule — must fix before proceeding |
| `WARNING` | Deviates from a recommended practice — should fix |
| `OK` | Compliant |

### Examples

```bash
# Create constitution for a new project (interactive)
/developer-kit-specs:constitution create

# Validate a spec against the constitution
/developer-kit-specs:constitution check --target=docs/specs/001-user-auth/2026-04-10--user-auth.md

# Validate a task plan
/developer-kit-specs:constitution check --target=docs/specs/001-user-auth/tasks/TASK-003.md

# Update the security section
/developer-kit-specs:constitution update --section=security

# Show current constitution
/developer-kit-specs:constitution show
```

---

## `/specs:brainstorm`

Transform ideas into full functional specifications through guided brainstorming.

### Syntax

```
/developer-kit-specs:specs.brainstorm [idea-description]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `idea-description` | Yes | Natural language description of the feature to build |

### When to Use

- New features with complex requirements
- Features affecting 5+ files
- Requirements that need clarification
- Features requiring architectural decisions
- Any feature where the "right approach" isn't immediately clear

### Process (9 Phases)

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Context Discovery | Explore project structure, dependencies, existing patterns |
| 1.5 | Complexity Assessment | Estimate task count; split if >15 tasks |
| 2 | Idea Refinement | Ask up to 3 clarifying questions |
| 3 | Functional Approach | Present 2-3 approaches (WHAT, not HOW) |
| 4 | Codebase Exploration | Examine integration points |
| 5 | Spec Presentation | Validate sections incrementally |
| 6 | Spec Generation | Create full specification document |
| 7 | Quality Review | Verify completeness |
| 8 | Next Steps | Recommend follow-up commands |
| 9 | Summary | List outputs and file locations |

### Output

```
docs/specs/[ID-feature]/
├── YYYY-MM-DD--feature-name.md     # Main specification
├── user-request.md                  # Original request
├── brainstorming-notes.md           # Session context
└── decision-log.md                  # Decision audit trail
```

### Examples

```bash
# New feature with complex requirements
/developer-kit-specs:specs.brainstorm Add a multi-tenant SaaS billing system with subscription management,
usage metering, invoice generation, Stripe integration, and prorated upgrades

# API design
/developer-kit-specs:specs.brainstorm Design a RESTful API for an e-commerce platform with product catalog,
shopping cart, checkout flow, and order management

# Infrastructure feature
/developer-kit-specs:specs.brainstorm Add real-time WebSocket notifications for order status changes
with delivery guarantees and connection management
```

---

## `/developer-kit-specs:specs.quick-spec`

Create a lightweight specification for well-understood changes.

### Syntax

```
/developer-kit-specs:specs.quick-spec [description]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `description` | Yes | Clear description of the change |

### When to Use

- Bug fixes with known solutions
- Small features affecting 1-3 files
- Changes with clear acceptance criteria (≤4)
- Well-understood technical context

### Process (4 Phases)

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Quick Context | Check git log, identify affected files |
| 2 | Problem + Solution Checkpoint | Define and validate approach |
| 3 | Generate Minimal Spec | Create lightweight specification |
| 4 | Next Step Recommendation | Suggest implementation path |

### Output

```
docs/specs/[ID-feature]/
├── YYYY-MM-DD--feature-name.md     # Minimal specification
└── decision-log.md                  # Decision record
```

### Examples

```bash
# Bug fix
/developer-kit-specs:specs.quick-spec Fix the NullPointerException in UserService.updateProfile()
when the email field is null

# Small feature
/developer-kit-specs:specs.quick-spec Add pagination to the /api/v1/orders endpoint with
configurable page size and sorting

# Performance improvement
/developer-kit-specs:specs.quick-spec Optimize the dashboard query that loads in 8+ seconds
by adding database indexes and caching the aggregation results
```

---

## `/developer-kit-specs:specs.spec-to-tasks`

Convert a functional specification into executable task files.

### Syntax

```
/developer-kit-specs:specs.spec-to-tasks [--lang=language] [spec-folder]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Recommended | Target language: `java`, `spring`, `typescript`, `nestjs`, `react`, `python`, `php`, `general` |
| `spec-folder` | Yes | Path to the specification directory |

### Process (11 Phases)

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Specification Analysis | Read and understand the spec |
| 1.5 | Architecture & Ontology | Ensure technical foundation exists |
| 2 | Requirement Extraction | Organize requirements, assign REQ-IDs |
| 2.5 | Knowledge Graph | Load cached codebase analysis when available |
| 3 | Codebase Analysis | Language-specific exploration |
| 3.5 | Spec Artifact Generation | Always generate `data-model.md` and `contracts/*` from the specification |
| 4 | Task Decomposition | Break into atomic tasks |
| 5 | Task Generation | Create task files and index |
| 5.5 | Traceability Matrix | Map requirements to tasks |
| 6 | Review and Confirmation | Present for validation |
| 7 | Summary | List outputs |

### Task Limit

Maximum 15 implementation tasks per specification. If exceeded, the command rejects and recommends splitting.

### Output

```
docs/specs/[ID-feature]/
├── YYYY-MM-DD--feature-name--tasks.md    # Task index
├── data-model.md                         # Generated domain/data model
├── traceability-matrix.md                # Requirements mapping
├── contracts/                            # Generated interface contracts
│   ├── *.openapi.yaml
│   └── *.md
└── tasks/
    ├── TASK-001.md
    ├── TASK-002.md
    └── ...
```

If a prior `knowledge-graph.json` exists, it may be reused as input, but `spec-to-tasks` does not update agent context files as part of this workflow.

### Examples

```bash
# Spring Boot project
/developer-kit-specs:specs.spec-to-tasks --lang=spring docs/specs/001-user-auth/

# NestJS project
/developer-kit-specs:specs.spec-to-tasks --lang=nestjs docs/specs/002-notification-system/

# Python project
/developer-kit-specs:specs.spec-to-tasks --lang=python docs/specs/003-data-pipeline/

# General / multi-language
/developer-kit-specs:specs.spec-to-tasks --lang=general docs/specs/004-api-design/
```

---

## `/developer-kit-specs:specs.task-manage`

Manage tasks after generation — add, split, update, list.

### Syntax

```
/developer-kit-specs:specs.task-manage --action=action [options]
```

### Actions

| Action | Description | Required Options |
|--------|-------------|-----------------|
| `list` | Display all tasks with status and complexity | `--spec` |
| `add` | Create a new task | `--spec` |
| `split` | Split a complex task into subtasks | `--task` |
| `mark-optional` | Mark task as not required | `--task` |
| `mark-required` | Mark optional task as required | `--task` |
| `update` | Modify task details | `--task` |
| `regenerate-index` | Recreate task index from files | `--spec` |

### Options

| Option | Description |
|--------|-------------|
| `--spec="path"` | Specification directory |
| `--task="path"` | Path to specific task file |

### Task Complexity Scoring

```
COMPLEXITY = (Files × 10) + (Acceptance Criteria × 5) +
             (Independent Components × 25) + (Design Decisions × 10) +
             (Integration Points × 15) + (External Dependencies × 20)
```

Tasks with complexity ≥50 are candidates for splitting.

### Examples

```bash
# List all tasks
/developer-kit-specs:specs.task-manage --action=list --spec="docs/specs/001-user-auth/"

# Split a complex task
/developer-kit-specs:specs.task-manage --action=split --task="docs/specs/001-user-auth/tasks/TASK-003.md"
# Result: TASK-003 → TASK-003A + TASK-003B

# Add a new task
/developer-kit-specs:specs.task-manage --action=add --spec="docs/specs/001-user-auth/"
# Claude will ask for task details interactively

# Mark a task
/developer-kit-specs:specs.task-manage --action=mark-optional --task="docs/specs/001-user-auth/tasks/TASK-003.md"
```

---

## `/developer-kit-specs:specs.task-implementation`

Guided task implementation following the SDD workflow.

### Syntax

```
/developer-kit-specs:specs.task-implementation [--lang=language] --task="task-file"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Recommended | Target language/framework |
| `--task` | **Yes** | Path to the task file to implement |

### Process (10 Phases)

| Phase | Name | Description |
|-------|------|-------------|
| T-1 | Task identification | Valid task file |
| T-2 | Git state check | Clean working tree |
| T-3 | Dependency check | All deps completed |
| T-3.5 | Knowledge Graph validation | Components exist |
| T-3.6 | Contract validation | Provides/expects compatible |
| T-3.7 | Review feedback check | For Ralph Loop iterations |
| T-4 | Implementation | — |
| T-5 | Verification | Tests pass |
| T-6 | Task completion | Status updated |
| T-7 | Code Cleanup | Post-review cleanup (auto-activates) |

> **Note**: The TDD RED phase command was removed in v3.0. Test generation is now
> integrated into `specs.task-implementation`. The review phase (T-7) includes
> test verification as part of the standard workflow.

### Examples

```bash
# Spring Boot task
/developer-kit-specs:specs.task-implementation --lang=spring \
  --task="docs/specs/001-user-auth/tasks/TASK-001.md"

# NestJS task
/developer-kit-specs:specs.task-implementation --lang=nestjs \
  --task="docs/specs/002-notification/tasks/TASK-003.md"

# React task
/developer-kit-specs:specs.task-implementation --lang=react \
  --task="docs/specs/003-dashboard/tasks/TASK-002.md"
```

---

## `/developer-kit-specs:specs.task-review`

Verify that an implemented task meets specifications and passes code review.

### Syntax

```
/developer-kit-specs:specs.task-review [--lang=language] [--task="task-file"]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Recommended | Target language/framework |
| `--task` | Yes | Path to task file |

> **Note**: Code cleanup is now integrated as Phase T-7 of
> `specs.task-implementation`. It auto-activates after `specs.task-review` passes.
> See `skills/specs-code-cleanup/SKILL.md` for language-specific formatter reference.

### Review Dimensions

| Dimension | Description |
|-----------|-------------|
| **Implementation** | Matches task description |
| **Acceptance Criteria** | All criteria met |
| **DoD** | Definition of Done satisfied |
| **Compliance** | Aligns with functional spec |
| **Code Quality** | Language-specific standards |

### Examples

```bash
# Review Spring Boot task
/developer-kit-specs:specs.task-review --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md"

# Review NestJS task
/developer-kit-specs:specs.task-review --lang=nestjs --task="docs/specs/002-notification/tasks/TASK-003.md"
```

---

## `/developer-kit-specs:specs.sync`

Synchronizes specification with implementation. Replaces the old `specs.spec-sync-with-code` and `specs.spec-sync-context` commands with a unified interface.

### Syntax

```
/developer-kit-specs:specs.sync [spec-folder] [--kg-only] [--code-only] [--after-task=TASK-XXX] [--dry-run]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `spec-folder` | Yes | Specification directory (positional) |
| `--kg-only` | No | Update Knowledge Graph only |
| `--code-only` | No | Detect spec-to-code deviations only |
| `--after-task` | No | Sync after specific task completion |
| `--dry-run` | No | Preview changes without writing |

### Modes

| Flag | Behavior |
|------|----------|
| (none) | Full sync: KG + drift detection + spec update |
| `--kg-only` | Knowledge Graph update only |
| `--code-only` | Drift detection only |
| `--dry-run` | Read-only preview |

### Examples

```bash
# Full sync after implementation
/developer-kit-specs:specs.sync docs/specs/001-feature/

# KG-only after spec-to-tasks
/developer-kit-specs:specs.sync docs/specs/001-feature/ --kg-only

# Drift check
/developer-kit-specs:specs.sync docs/specs/001-feature/ --code-only

# Preview
/developer-kit-specs:specs.sync docs/specs/001-feature/ --dry-run
```

---

## `/developer-kit-specs:specs.spec-check`

Resolves `[NEEDS CLARIFICATION]` markers generated during brainstorming and performs a structured quality scan to identify underspecified areas.

### Syntax

```
/developer-kit-specs:specs.spec-check [--spec="spec-folder"]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--spec` | Yes | Specification directory |

### Quality Scan Taxonomy

The scan covers 12 areas:

1. Completeness and Clarity
2. Domain and Data Model
3. Interaction and UX Flow
4. Non-Functional Quality (performance, scalability, reliability)
5. Security and Compliance
6. Integrations and Dependencies
7. Edge Cases and Error Handling
8. Constraints and Trade-offs
9. Terminology and Consistency
10. Completion Criteria
11. Placeholders and TODOs
12. Architecture/Ontology Alignment

### Process

Claude asks up to 5 focused questions, one at a time. Marker-derived questions from brainstorming are presented first; if quota remains, a structured scan generates additional questions. Your answers are integrated directly into the specification.

### Examples

```bash
# Check specification quality and resolve markers
/developer-kit-specs:specs.spec-check --spec="docs/specs/001-user-auth/"

# Can be run multiple times (idempotent)
/developer-kit-specs:specs.spec-check --spec="docs/specs/001-user-auth/"
```
