# Developer Kit Specs

Specifications-driven development workflow for transforming ideas into functional specifications and executable tasks.

## Overview

This plugin provides a complete workflow for transforming ideas into implemented code:

- **Constitution**: Define the architectural DNA of the project — non-negotiable principles, approved stack, AI guardrails, and security constraints
- **Brainstorming**: Transform ideas into pure functional specifications (WHAT, not HOW)
- **Task Generation**: Convert functional specifications into executable tasks
- **Task Management**: Add, split, update, and manage tasks
- **Implementation**: Execute specific tasks with language-specific agents
- **Review**: Verify implemented tasks meet specifications
- **Code Cleanup**: Final cleanup after review approval
- **Ralph Loop**: Step-by-step automation for long-running implementations

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
Constitution → Idea → Functional Specification → Tasks → Implementation → Review → Cleanup → Done
(constitution)  (brainstorm)  (spec-to-tasks)  (task-implementation)  (task-review)   (code-cleanup)
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

## Knowledge Graph

The Knowledge Graph maintains a structured view of the codebase state relative to the specification. It is stored in `knowledge-graph.json` and updated via `specs.spec-sync-context`.
