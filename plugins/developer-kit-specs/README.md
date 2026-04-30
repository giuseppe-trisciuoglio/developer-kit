# Developer Kit Specs

Specifications-driven development workflow for transforming ideas into functional specifications and executable tasks.

## Overview

This plugin provides a complete workflow for transforming ideas into implemented code:

- **Constitution**: Define the architectural DNA of the project — non-negotiable principles, approved stack, AI guardrails, and security constraints
- **Brainstorming**: Transform ideas into pure functional specifications (WHAT, not HOW)
- **Task Generation**: Convert functional specifications into executable tasks
- **Task Management**: Add, split, update, and manage tasks
- **TDD Workflow**: Test-Driven Development with RED/GREEN phases
- **Implementation**: Execute specific tasks with language-specific agents
- **Review**: Verify implemented tasks meet specifications
- **Code Cleanup**: Final cleanup after review approval
- **Drift Guard**: Real-time monitoring of spec-to-implementation drift
- **Ralph Loop**: Step-by-step automation for long-running implementations
- **KPI Evaluation**: Objective quality metrics using pre-calculated data

## Quick Start

```bash
# 0. Define project constitution (once per project)
/developer-kit-specs:constitution create

# 1. Create a functional specification
/developer-kit-specs:specs.brainstorm "Add user authentication with JWT tokens"

# 2. Convert specification to tasks
/developer-kit-specs:specs.spec-to-tasks --lang=spring docs/specs/001-user-auth/

# 3. Implement a task
/developer-kit-specs:specs.task-implementation --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md"

# 4. Review implementation
/developer-kit-specs:specs.task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# 5. Clean up code
/developer-kit-specs:specs-code-cleanup --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# 6. Sync specification with implementation
/developer-kit-specs:specs.spec-sync-with-code docs/specs/001-user-auth/
```

## Workflow

```
Constitution → Idea → Functional Specification → Tasks → TDD / Implementation → Review → Cleanup → Done
(constitution)  (brainstorm)  (spec-to-tasks)  (task-tdd)  (task-review)   (code-cleanup)
```

## Specification Structure

Each specification lives in `docs/specs/[ID-feature]/`:

```
docs/specs/001-user-auth/
├── 2026-04-09--user-auth.md           # Main functional specification
├── user-request.md                    # Original user input
├── brainstorming-notes.md             # Brainstorming session context
├── decision-log.md                    # Decision audit trail
├── data-model.md                      # Generated from spec-to-tasks
├── contracts/                         # Generated interface artifacts
│   ├── auth-api.openapi.yaml
│   └── README.md
├── traceability-matrix.md             # Requirements-to-task mapping
├── knowledge-graph.json               # Optional cached codebase analysis
└── tasks/
    ├── TASK-001.md                    # Individual task
    ├── TASK-001--kpi.json            # KPI analysis (auto-generated)
    ├── TASK-001--review.md           # Review report
    └── TASK-002.md
```

## Commands

### Constitution

| Command | Description |
|---------|-------------|
| `/developer-kit-specs:constitution create` | Create `docs/specs/architecture.md` and/or `docs/specs/ontology.md` as project setup |
| `/developer-kit-specs:constitution update --section=...` | Update a specific section of the constitution |
| `/developer-kit-specs:constitution check --target=...` | Validate a spec/task/file against the constitution |
| `/developer-kit-specs:constitution show` | Display the current constitution |

### Specification Creation

| Command | Description |
|---------|-------------|
| `/developer-kit-specs:specs.brainstorm [idea]` | Full specification creation for complex features |
| `/developer-kit-specs:specs.quick-spec [idea]` | Lightweight spec for bug fixes and small features |
| `/developer-kit-specs:specs.spec-quality-check [folder]` | Review specification content quality |

### Task Generation and Management

| Command | Description |
|---------|-------------|
| `/developer-kit-specs:specs.spec-to-tasks [--lang=...] [folder]` | Convert specification to executable tasks |
| `/developer-kit-specs:specs.task-manage --action=list` | List all tasks in a specification |
| `/developer-kit-specs:specs.task-manage --action=add` | Add a new task |
| `/developer-kit-specs:specs.task-manage --action=split` | Split an existing task |
| `/developer-kit-specs:specs.task-manage --action=update` | Update task metadata |

### Task Implementation

| Command | Description |
|---------|-------------|
| `/developer-kit-specs:specs.task-implementation [--lang=...] [task-file]` | Implement a specific task |
| `/developer-kit-specs:specs.task-tdd [--lang=...] [task-file]` | TDD RED phase - generate failing tests first |
| `/developer-kit-specs:specs.task-review [--lang=...] [task-file]` | Verify implemented task meets specification |
| `/developer-kit-specs:specs-code-cleanup [--lang=...] [task-file]` | Clean up code after review approval |

### Synchronization

| Command | Description |
|---------|-------------|
| `/developer-kit-specs:specs.spec-sync-context [folder]` | Sync Knowledge Graph, tasks, and codebase |
| `/developer-kit-specs:specs.spec-sync-with-code [folder]` | Detect and fix spec-to-code drift |

### Automation

| Command | Description |
|---------|-------------|
| `/developer-kit-specs:specs.ralph-loop` | Step-by-step automation (use Python script directly) |

## Language Support

Commands support `--lang=` with values:

| Value | Framework | Code Review Agent |
|-------|-----------|-------------------|
| `java` | Java SE | `developer-kit-java:java-software-architect-review` |
| `spring` | Spring Boot | `developer-kit-java:spring-boot-code-review-expert` |
| `typescript` | Node.js | `developer-kit:general-code-reviewer` |
| `nestjs` | NestJS | `developer-kit-typescript:nestjs-code-review-expert` |
| `react` | React | `developer-kit:general-code-reviewer` |
| `python` | Django/FastAPI | `developer-kit-python:python-code-review-expert` |
| `php` | Laravel/Symfony | `developer-kit-php:php-code-review-expert` |
| `general` | Any | `developer-kit:general-code-reviewer` |

## Task Status Workflow

Tasks use a standardized status workflow with automatic date tracking:

```
pending → in_progress → implemented → reviewed → completed
              ↓
          blocked (can return to in_progress)
```

| Status | Description | Date Fields Set |
|--------|-------------|-----------------|
| `pending` | Initial state | None |
| `in_progress` | Work started | `started_date` |
| `implemented` | Coding complete | `implemented_date` |
| `reviewed` | Review passed | `reviewed_date` |
| `completed` | Cleanup done | `completed_date`, `cleanup_date` |
| `blocked` | Cannot proceed | None |
| `optional` | Not required | None |
| `superseded` | Replaced by other tasks | None |

### Auto-Status Management

Task status is automatically managed by hooks when you edit task files:

| User Action | Automatic Status Update |
|-------------|------------------------|
| Edit task file | `pending` → `in_progress` |
| Check AC boxes | Progress through implementation |
| Check all DoD boxes | `implemented` → `reviewed` |
| Add Cleanup Summary | `reviewed` → `completed` |

## Ralph Loop

The Ralph Loop applies Geoffrey Huntley's "Ralph Wiggum as a Software Engineer" technique to SDD. It solves context window explosion by executing **one step per invocation**, persisting state in `fix_plan.json`.

### State Machine

```
init → choose_task → implementation → review → fix → cleanup → sync → update_done
```

### Quick Start

```bash
# 1. Initialize
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-feature/

# 2. Run loop (execute shown command, then run loop again)
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-feature/

# 3. Check status
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=status \
  --spec=docs/specs/001-feature/
```

### Task Range Filtering

Process a specific range of tasks:

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-feature/ \
  --from-task=TASK-036 \
  --to-task=TASK-041
```

### Multi-Agent Support

Specify agent per task in task frontmatter:

```yaml
---
id: TASK-036
title: Refactor user service
agent: codex  # claude, codex, copilot, gemini, glm4, kimi, minimax
---
```

## KPI Evaluation

The Evaluator Agent provides objective quality evaluation using pre-calculated KPI data.

### How It Works

1. **Auto-generated KPIs**: A hook calculates KPIs every time a task file is modified
2. **KPI File**: Results saved to `TASK-XXX--kpi.json`
3. **Evaluation**: Evaluator Agent reads the KPI file and makes data-driven decisions

### KPI Categories

| Category | Weight | Metrics |
|----------|--------|---------|
| Spec Compliance | 30% | Acceptance criteria met, requirements coverage, scope control |
| Code Quality | 25% | Static analysis, complexity, patterns alignment |
| Test Coverage | 25% | Unit tests, test/code ratio, coverage % |
| Contract Fulfillment | 20% | Provides verified, expects satisfied |

### Threshold

- Default threshold: **7.5/10**
- Score >= threshold: **APPROVED**
- Score < threshold: **REQUEST FIXES**

### Reading KPI Files

The Evaluator Agent reads pre-generated KPI files. You can also read them directly:

```bash
cat docs/specs/001-user-auth/tasks/TASK-001--kpi.json
```

## TDD Workflow

Test-Driven Development is integrated into the task implementation workflow:

### RED Phase (Write Failing Tests)

```bash
/developer-kit-specs:specs.task-tdd --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
```

Generates failing tests based on task acceptance criteria before implementation.

### GREEN Phase (Make Tests Pass)

```bash
/developer-kit-specs:specs.task-implementation --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
```

Implements code to make the failing tests pass.

### Test Templates

Language-specific test templates are provided:

| Language | Framework | Template |
|----------|-----------|----------|
| Java | Spring Boot | `hooks/test-templates/spring-test-template.java` |
| TypeScript | Node.js | `hooks/test-templates/nodejs-test-template.test.ts` |
| NestJS | NestJS | `hooks/test-templates/nestjs-test-template.spec.ts` |
| React | React | `hooks/test-templates/react-test-template.test.tsx` |
| Python | pytest | `hooks/test-templates/python-test-template.py` |
| PHP | PHPUnit | `hooks/test-templates/php-test-template.php` |

## Knowledge Graph

The Knowledge Graph (`knowledge-graph.json`) stores discoveries from codebase analysis:

- **Reduces redundant exploration**: Reuse cached analysis across tasks
- **Validates dependencies**: Check if required components exist before implementing
- **Enables task validation**: Verify task expectations against actual codebase state

### Operations

```bash
# Read knowledge graph
/knowledge-graph read docs/specs/001-feature/

# Query patterns
/knowledge-graph query docs/specs/001-feature/ patterns

# Validate against knowledge graph
/knowledge-graph validate docs/specs/001-feature/ {
  components: ["HotelSearchService"],
  apis: ["/api/v1/search"]
}
```

### Freshness

| Age | Status | Action |
|-----|--------|--------|
| < 7 days | Fresh | Use cached analysis |
| 7-30 days | Stale | Warn user, offer regeneration |
| > 30 days | Very stale | Auto-regenerate |

## Specification Maintenance

Specifications are **deliverables**, not just background context.

### Rules

1. When work is driven by files in `docs/specs/`, treat the specification as a deliverable.
2. After `/developer-kit-specs:specs.task-implementation`, always run `/developer-kit-specs:specs.task-review`, fix every finding, then run `/developer-kit-specs:specs.spec-sync-with-code` whenever implementation changed, clarified, or constrained intended behavior.
3. During normal chat sessions, if specs were used to guide implementation, update affected spec files before concluding.
4. If no spec update is needed, state that explicitly.

### Add to CLAUDE.md

```markdown
## Specification Maintenance Rules

- When work is driven by files in `docs/specs/`, treat the specification as a deliverable.
- After `/developer-kit-specs:specs.task-implementation`, always run `/developer-kit-specs:specs.task-review`, fix every finding, then run `/developer-kit-specs:specs.spec-sync-with-code`.
- During normal chat sessions, if specs were used to guide implementation, update affected spec files before concluding.
- If no spec update is needed, state that explicitly and explain why.
```

## Drift Guard

Monitors specification-to-implementation drift to ensure alignment:

- **drift-init**: Initializes drift tracking for a specification
- **drift-monitor**: Analyzes implementation changes against functional requirements
- **drift-report**: Generates fidelity report on task completion

## Hooks

Hooks automate task management:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `task-auto-status.py` | Edit `TASK-*.md` | Auto-update status from checkboxes |
| `task-kpi-analyzer.py` | Edit `TASK-*.md` | Calculate quality KPIs |
| `task-validator.py` | Edit `TASK-*.md` | Validate frontmatter structure |
| `drift-monitor.py` | Write/Edit any file | Monitor spec drift |

## Skills

### constitution

Establishes and maintains the architectural DNA of a project through two shared documents:
- `docs/specs/architecture.md` — approved stack, architectural rules, AI guardrails, security constraints (CWE mappings)
- `docs/specs/ontology.md` — domain glossary (Ubiquitous Language), bounded contexts
- Can be used **before brainstorm** as a project setup step
- Provides `create`, `update`, `check`, and `show` operations
- Constitution Check validates specs and tasks with CRITICAL / WARNING / OK severity levels

### knowledge-graph

Persistent JSON file that stores discoveries from codebase analysis:
- Location: `docs/specs/[ID-feature]/knowledge-graph.json`
- Reduces redundant codebase exploration
- Enables task validation against actual codebase state

### ralph-loop

Guided automation loop for specification-driven development:
- Orchestrates task implementation, review, and cleanup
- Maintains state across turns for long-running tasks
- Integrates with spec-driven commands for consistent workflow

### specs-code-cleanup

Professional code cleanup after task review approval:
- Removes debug logs and temporary comments
- Optimizes imports and improves readability
- Finalizes code before task completion

## Agents

### Evaluator Agent

Objective quality evaluator using pre-calculated KPI data:

- **KPI-driven**: Reads `TASK-XXX--kpi.json` for decisions
- **Evidence-based**: Evaluates against quantitative metrics
- **Consistent**: Reduces evaluator bias through data-driven approach

## Dependencies

This plugin requires:

- `developer-kit-core` - For general agents (code-explorer, code-reviewer, refactor-expert, software-architect, debugger)

## Requirements

- Python 3.11+ (for hook scripts and Ralph Loop)
- Claude Code (for command integration)

## License

MIT

## Author

Giuseppe Trisciuoglio <giuseppe.trisciuoglio@gmail.com>
