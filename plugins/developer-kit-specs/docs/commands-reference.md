# Commands Reference

Complete reference for all SDD commands with arguments, options, and real-world examples.

---

## `/specs:brainstorm`

Transform ideas into full functional specifications through guided brainstorming.

### Syntax

```
/specs:brainstorm [idea-description]
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
/specs:brainstorm Add a multi-tenant SaaS billing system with subscription management,
usage metering, invoice generation, Stripe integration, and prorated upgrades

# API design
/specs:brainstorm Design a RESTful API for an e-commerce platform with product catalog,
shopping cart, checkout flow, and order management

# Infrastructure feature
/specs:brainstorm Add real-time WebSocket notifications for order status changes
with delivery guarantees and connection management
```

---

## `/specs:quick-spec`

Create a lightweight specification for well-understood changes.

### Syntax

```
/specs:quick-spec [description]
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
/specs:quick-spec Fix the NullPointerException in UserService.updateProfile()
when the email field is null

# Small feature
/specs:quick-spec Add pagination to the /api/v1/orders endpoint with
configurable page size and sorting

# Performance improvement
/specs:quick-spec Optimize the dashboard query that loads in 8+ seconds
by adding database indexes and caching the aggregation results
```

---

## `/specs:spec-to-tasks`

Convert a functional specification into executable task files.

### Syntax

```
/specs:spec-to-tasks [--lang=language] [spec-folder]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Recommended | Target language: `java`, `spring`, `typescript`, `nestjs`, `react`, `python`, `php`, `general` |
| `spec-folder` | Yes | Path to the specification directory |

### Process (7 Phases)

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Specification Analysis | Read and understand the spec |
| 1.5 | Architecture & Ontology | Ensure technical foundation exists |
| 2 | Requirement Extraction | Organize requirements, assign REQ-IDs |
| 2.5 | Knowledge Graph | Load or create cached codebase analysis |
| 3 | Codebase Analysis | Language-specific exploration |
| 3.5 | Update Knowledge Graph | Persist discoveries |
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
├── knowledge-graph.json                   # Codebase analysis cache
├── traceability-matrix.md                # Requirements mapping
└── tasks/
    ├── TASK-001.md
    ├── TASK-002.md
    └── ...
```

### Examples

```bash
# Spring Boot project
/specs:spec-to-tasks --lang=spring docs/specs/001-user-auth/

# NestJS project
/specs:spec-to-tasks --lang=nestjs docs/specs/002-notification-system/

# Python project
/specs:spec-to-tasks --lang=python docs/specs/003-data-pipeline/

# General / multi-language
/specs:spec-to-tasks --lang=general docs/specs/004-api-design/
```

---

## `/specs:task-manage`

Manage tasks after generation — add, split, update, list.

### Syntax

```
/specs:task-manage --action=action [options]
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
/specs:task-manage --action=list --spec="docs/specs/001-user-auth/"

# Split a complex task
/specs:task-manage --action=split --task="docs/specs/001-user-auth/tasks/TASK-003.md"
# Result: TASK-003 → TASK-003A + TASK-003B

# Add a new task
/specs:task-manage --action=add --spec="docs/specs/001-user-auth/"
# Claude will ask for task details interactively

# Mark a task as optional (won't block completion)
/specs:task-manage --action=mark-optional --task="docs/specs/001-user-auth/tasks/TASK-008.md"

# Regenerate task index after manual changes
/specs:task-manage --action=regenerate-index --spec="docs/specs/001-user-auth/"
```

---

## `/specs:task-implementation`

Implement a specific task from a task list.

### Syntax

```
/specs:task-implementation [--lang=language] --task="task-file"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Recommended | Target language/framework |
| `--task` | **Yes** | Path to task file |

### Process (12 Steps)

| Step | Name | Gate |
|------|------|------|
| T-1 | Task identification | Valid task file |
| T-2 | Git state check | Clean working tree |
| T-3 | Dependency check | All deps completed |
| T-3.5 | Knowledge Graph validation | Components exist |
| T-3.6 | Contract validation | Provides/expects compatible |
| T-3.7 | Review feedback check | For Ralph Loop iterations |
| T-4 | Implementation | — |
| T-5 | Verification | Tests pass |
| T-6 | Task completion | Status updated |
| T-6.5 | Knowledge Graph update | Context persisted |
| T-6.6 | Spec deviation check | Drift reported |

### Examples

```bash
# Spring Boot task
/specs:task-implementation --lang=spring \
  --task="docs/specs/001-user-auth/tasks/TASK-001.md"

# NestJS task
/specs:task-implementation --lang=nestjs \
  --task="docs/specs/002-notification/tasks/TASK-003.md"

# React task
/specs:task-implementation --lang=react \
  --task="docs/specs/003-dashboard/tasks/TASK-002.md"
```

---

## `/specs:task-tdd`

Generate failing tests (TDD RED phase) before implementation.

### Syntax

```
/specs:task-tdd [--lang=language] --task="task-file"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Recommended | Target language/framework |
| `--task` | **Yes** | Path to task file |

### Supported Test Frameworks

| Language | Framework | Template |
|----------|-----------|----------|
| Spring | JUnit 5 + Mockito | `spring-test-template.java` |
| Java | JUnit 5 | `java-test-template.java` |
| NestJS | Jest | `nestjs-test-template.spec.ts` |
| TypeScript | Jest / Mocha | `typescript-test-template.spec.ts` |
| React | Jest + React Testing Library | `react-test-template.test.tsx` |
| Node.js | Jest | `nodejs-test-template.test.ts` |
| Python | pytest | `python-test-template.py` |
| PHP | PHPUnit | `php-test-template.php` |

### TDD Workflow

```
RED phase: /specs:task-tdd      → Generate failing tests
GREEN phase: /specs:task-implementation → Make tests pass
```

### Examples

```bash
# Spring Boot — RED phase
/specs:task-tdd --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-002.md"
# Creates: src/test/java/.../JwtTokenServiceTest.java (all tests fail)

# Then GREEN phase
/specs:task-implementation --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-002.md"
# Creates: src/main/java/.../JwtTokenService.java (all tests pass)
```

---

## `/specs:task-review`

Verify that an implemented task meets specifications and passes code review.

### Syntax

```
/specs:task-review [--lang=language] [--task="task-file"]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Recommended | Target language/framework |
| `--task` | Yes | Path to task file |

### Review Dimensions

| Dimension | What It Checks |
|-----------|---------------|
| Implementation | Code matches task description |
| Acceptance Criteria | All criteria checkboxes ✅ |
| Spec Compliance | Alignment with functional specification |
| Code Quality | Language-specific patterns, security, conventions |

### Review Outcomes

| Status | Condition |
|--------|-----------|
| **PASSED** | All criteria ✅, all DoD ✅, no critical issues |
| **FAILED** | Any criterion ❌, or critical code issues |

### Output

`TASK-XXX--review.md` — Detailed review report with findings per dimension.

### Examples

```bash
# Spring Boot review
/specs:task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# NestJS review
/specs:task-review --lang=nestjs docs/specs/002-notification/tasks/TASK-003.md
```

---

## `/developer-kit-specs:specs-code-cleanup`

Professional code cleanup after task review approval.

### Syntax

```
/developer-kit-specs:specs-code-cleanup --lang=language --task="task-file"
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | Yes | Target language/framework |
| `--task` | Yes | Path to task file (must be in `reviewed` status) |

### Cleanup Process (8 Phases)

1. **Task verification** — Confirm reviewed status
2. **Identify files** — From review report and task provides
3. **Remove debug artifacts** — `console.log`, `System.out.println`, temporary comments
4. **Optimize imports** — Language-specific import cleanup
5. **Code readability** — Run formatters
6. **Documentation check** — Headers, API docs
7. **Final verification** — Run tests, verify no logic changes
8. **Task completion** — Update status to `completed`

### Language-Specific Formatters

| Language | Formatter Command |
|----------|-------------------|
| Spring | `./mvnw spotless:apply` |
| TypeScript | `npm run lint:fix && npm run format` |
| Python | `black .` |
| PHP | `php-cs-fixer fix` |

### Examples

```bash
/developer-kit-specs:specs-code-cleanup --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md"
/developer-kit-specs:specs-code-cleanup --lang=nestjs --task="docs/specs/002-notification/tasks/TASK-003.md"
/developer-kit-specs:specs-code-cleanup --lang=python --task="docs/specs/003-pipeline/tasks/TASK-002.md"
```

---

## `/specs:spec-sync-with-code`

Synchronize functional specification with actual implementation state.

### Syntax

```
/specs:spec-sync-with-code [--spec="spec-folder"] [--after-task="TASK-XXX"]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--spec` | Yes | Specification directory |
| `--after-task` | No | Sync after specific task completion |

### Deviation Types

| Type | Description | Example |
|------|-------------|---------|
| **Scope Expansion** | Features added beyond spec | Added refresh token support |
| **Requirement Refinement** | Clarifications or corrections | Changed password length to 12 |
| **Scope Reduction** | Features dropped or deferred | Deferred 2FA to next spec |

### Examples

```bash
# Full sync
/specs:spec-sync-with-code docs/specs/001-user-auth/

# Sync after specific task
/specs:spec-sync-with-code --spec="docs/specs/001-user-auth/" --after-task="TASK-003"
```

---

## `/specs:spec-sync-context`

Synchronize Knowledge Graph, tasks, and codebase state.

### Syntax

```
/specs:spec-sync-context [--spec="spec-folder"] [--update-kg-only] [--task="task-file"] [--dry-run]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--spec` | Yes | Specification directory |
| `--update-kg-only` | No | Only update Knowledge Graph, skip task enrichment |
| `--task` | No | Sync context for specific task |
| `--dry-run` | No | Preview changes without writing |

### Examples

```bash
# Full context sync
/specs:spec-sync-context --spec="docs/specs/001-user-auth/"

# Preview only
/specs:spec-sync-context --spec="docs/specs/001-user-auth/" --dry-run

# Update Knowledge Graph only
/specs:spec-sync-context --spec="docs/specs/001-user-auth/" --update-kg-only

# Sync after specific task
/specs:spec-sync-context --spec="docs/specs/001-user-auth/" --task="TASK-003"
```

---

## `/specs:spec-quality-check`

Interactive specification quality assessment.

### Syntax

```
/specs:spec-quality-check [--spec="spec-folder"]
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

Claude asks up to 5 focused questions, one at a time. Your answers are integrated directly into the specification.

### Examples

```bash
# Check specification quality
/specs:spec-quality-check --spec="docs/specs/001-user-auth/"

# Can be run multiple times (idempotent)
/specs:spec-quality-check --spec="docs/specs/001-user-auth/"
```
