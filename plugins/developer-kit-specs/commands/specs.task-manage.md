---
description: "Provides task creation and splitting after initial task generation. Use when needing to add a new task to a spec or divide a complex task into subtasks."
argument-hint: "--action=[add|split] [ --task=\"docs/specs/XXX-feature/tasks/TASK-XXX.md\" ] [ --spec=\"docs/specs/XXX-feature\" ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
---

# Task Management

Creates or splits tasks after initial generation by `specs.spec-to-tasks`.

## Overview

**Supported Actions:**

1. `add` — Add a new task to the specification
2. `split` — Split a complex task into smaller subtasks

**Note on other operations**: Marking optional/required, updating metadata, and regenerating indices can be done by directly editing the task file's frontmatter. The task schema is documented in `hooks/task_lifecycle.py`.

## Usage

```bash
# Add a new task
/developer-kit-specs:specs.task-manage --action=add --spec=docs/specs/001-feature/ --lang=spring

# Split a complex task
/developer-kit-specs:specs.task-manage --action=split --task=docs/specs/001-feature/tasks/TASK-007.md
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--action` | Yes | Management action: add or split |
| `--task` | Conditional | Required when action=split |
| `--spec` | Conditional | Required when action=add |
| `--lang` | No | Target language/framework |

## Examples

### Add a New Task

```bash
/developer-kit-specs:specs.task-manage --action=add --spec=docs/specs/001-feature/ --lang=spring
```

### Split an Existing Task

```bash
/developer-kit-specs:specs.task-manage --action=split --task=docs/specs/001-feature/tasks/TASK-007.md
```

## Argument Parsing

1. Run the shared argument parser:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/parse_args.py" "$ARGUMENTS"
   ```
   Read the JSON output and extract:
   - `task` → task file path (or construct from `spec` + `task_id`)
   - `spec` → spec folder path
   - `lang` → target language/framework
   - `action` → management action (add or split)
   - `flags` → boolean flags
2. If `spec` is null, auto-detect from git branch:
   ```bash
   branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
   spec=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
   ```
3. Validate required parameters. If missing, ask user via AskUserQuestion.

---

## Action: add

**Goal**: Add a new task to an existing specification.

**Actions**:

1. Read the specification folder to identify the next task ID.
2. Read the functional specification to understand the feature context.
3. Ask the user for the task title and a brief description.
4. Create a new task file in `docs/specs/[id]/tasks/TASK-XXX.md`.
5. Populate the task file using the task template with this lookup order:
   1. `${CLAUDE_PLUGIN_ROOT}/templates/task.md`
   2. `templates/task.md` inside the installed skill folder for non-Claude agents.
   - Fill in frontmatter (id, title, spec, status: pending)
   - Fill in Functional Description, Acceptance Criteria (ask user or derive from spec)
   - Include Definition of Ready, Test Instructions, Definition of Done from the template
6. Inform the user of the new task path.

---

## Action: split

**Goal**: Split a complex task into smaller, more manageable subtasks.

**Actions**:

1. Read the target task file (`--task`).
2. Analyze its acceptance criteria and complexity.
3. Propose a split into 2-3 subtasks.
4. Ask for user confirmation on the split plan.
5. For each new subtask:
   - Create a new task file with a new ID.
   - Distribute acceptance criteria from the original task.
   - Set dependencies if one subtask must follow another.
6. Mark the original task as `optional` or move it to an `archive/` folder.
7. Inform the user of the new tasks.

---

## Manual Task Editing

The following operations don't require a command — edit the task `.md` file directly:

| Operation | How |
|-----------|-----|
| Mark optional/required | Edit `status: optional` or `status: required` in frontmatter |
| Update metadata | Edit YAML frontmatter fields |
| Regenerate index | The index is auto-updated when tasks are added/split |
| List tasks | `ls docs/specs/XXX-feature/tasks/` |
