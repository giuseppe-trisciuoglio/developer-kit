---
description: "Provides capability to manage tasks after generation. Use when needing to add, split, update, or modify tasks in an existing specification."
argument-hint: "--action=[add|split|mark-optional|mark-required|update|regenerate-index|list] [ --task=task-file-path ] [ --spec=spec-file-path ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
---

# Task Management

Manages tasks after task generation. Use when you need to add, split, update, or modify tasks in an existing specification.

## Overview

This command provides task management capabilities after initial task generation by `devkit.spec-to-tasks`.

**Supported Actions:**

1. `add` - Add a new task to the specification
2. `split` - Split a complex task into smaller subtasks
3. `mark-optional` - Mark a task as optional
4. `mark-required` - Mark a task as required
5. `update` - Update task details
6. `regenerate-index` - Regenerate the task index
7. `list` - List all tasks with complexity

## Usage

```bash
# Add a new task
/developer-kit:devkit.task-manage --action=add --spec=docs/specs/001-feature/ --lang=spring

# Split a complex task
/developer-kit:devkit.task-manage --action=split --task=docs/specs/001-feature/tasks/TASK-007.md

# Mark task as optional/required
/developer-kit:devkit.task-manage --action=mark-optional --task=docs/specs/001-feature/tasks/TASK-003.md
/developer-kit:devkit.task-manage --action=mark-required --task=docs/specs/001-feature/tasks/TASK-003.md

# Update task details
/developer-kit:devkit.task-manage --action=update --task=docs/specs/001-feature/tasks/TASK-005.md

# Regenerate task index
/developer-kit:devkit.task-manage --action=regenerate-index --spec=docs/specs/001-feature/

# List all tasks
/developer-kit:devkit.task-manage --action=list --spec=docs/specs/001-feature/
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--action` | Yes | The management action to perform |
| `--task` | Conditional | Path to task file (required for task-specific actions) |
| `--spec` | Conditional | Path to spec folder (required for `add`, `regenerate-index`, `list`) |
| `--lang` | No | Language/framework hint for new tasks |

---

You are managing existing task files. Follow the appropriate process based on the requested action.

## Action: Add

Adds a new task to an existing specification.

### Process

1. Parse $ARGUMENTS to extract:
   - `--spec` parameter (spec folder path)
   - `--lang` parameter (optional language hint)

2. Read the existing task index (`YYYY-MM-DD--feature-name--tasks.md`)

3. Determine the next task ID (e.g., if last is TASK-007, next is TASK-008)

4. Ask the user for:
   - Task title
   - Task description
   - Acceptance criteria
   - Dependencies (if any)
   - Estimated complexity

5. Create the new task file following the standard task format

6. Validate dependencies before saving:
   - Verify all referenced task IDs exist in the tasks directory
   - Check for circular dependencies (TASK-A depends on TASK-B which depends on TASK-A)
   - Ensure task ID format matches pattern TASK-XXX
   - Warn if dependency points to a superseded task

7. Update the task index to include the new task

8. Update the traceability matrix if requirements are affected
   - Read traceability-matrix.md and add rows for new REQ-IDs
   - Initialize Test Files and Code Files columns with "-"
   - Create matrix if it does not exist with header structure

### Task File Templates

Choose the appropriate template based on task complexity:

#### Template A: Simple (Recommended for most tasks)

Use this template for straightforward tasks with clear scope.

```yaml
---
id: "TASK-XXX"
title: "[Task Title]"
status: "pending"  # pending | in-progress | completed | superseded | optional
description: "[What this task implements]"
acceptance_criteria:
  - "[Criterion 1]"
  - "[Criterion 2]"
dependencies: []
  # - "TASK-YYY"  # if depends on other tasks
files_to_create:
  - "[file path]"
files_to_modify:
  - "[file path]"
implementation_command: "/developer-kit:devkit.task-implementation --lang=[lang] --task=\"docs/specs/[id]/tasks/TASK-XXX.md\""
---

# TASK-XXX: [Task Title]

**Description**: [Functional description]

**Complexity**: [Score]/100 - [Simple/Moderate/Complex]

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Files

**To Create**:
- `[file path]`

**To Modify**:
- `[file path]`

**Implementation Command**:
/developer-kit:devkit.task-implementation --lang=[lang] --task="docs/specs/[id]/tasks/TASK-XXX.md"
```

#### Template B: Full (For complex tasks requiring detailed tracking)

Use this template for complex tasks that need business context, data contracts, observability, and complexity tracking.

```yaml
---
id: "TASK-XXX"
title: "[Task Title]"
status: "pending"  # pending | in-progress | completed | superseded | optional
description: "[What this task implements]"
acceptance_criteria:
  - "[Criterion 1]"
  - "[Criterion 2]"
dependencies: []
  # - "TASK-YYY"  # if depends on other tasks
files_to_create:
  - "[file path]"
files_to_modify:
  - "[file path]"
implementation_command: "/developer-kit:devkit.task-implementation --lang=[lang] --task=\"docs/specs/[id]/tasks/TASK-XXX.md\""
business_goals:
  - "[Business goal this task serves]"
data_contracts:
  input:
    - "[Input data contract]"
  output:
    - "[Output data contract]"
external_dependencies:
  - "[External system/dependency]"
observability:
  logging:
    - "[Log point 1]"
    - "[Log point 2]"
  metrics:
    - "[Metric 1]"
    - "[Metric 2]"
  security:
    - "[Security consideration 1]"
    - "[Security consideration 2]"
complexity:
  score: 0
  files: 0
  acceptance_criteria: 0
  independent_components: 0
  design_decisions: 0
  integration_points: 0
  external_dependencies: 0
parent_task: null
supersedes: []
notes:
  - "[Note]"
context_hash: "[SHA-256 hash for change detection]"
---

# TASK-XXX: [Task Title]

**Description**: [Functional description]

**Complexity**: [Score]/100 - [Simple/Moderate/Complex]

## Context Linkage

**Business Goal**: [Goal ID] - [Goal description]

**Data Contract**:
- Input: [Input contract reference]
- Output: [Output contract reference]

**External Dependencies**: [List or "None"]

## Implementation Notes

- [Technical constraint or guidance]
- [Integration point]

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Files

**To Create**:
- `[file path]`

**To Modify**:
- `[file path]`

## Observability

**Logging**:
- [Log point]

**Metrics**:
- [Metric]

**Security**:
- [Security consideration]

**Implementation Command**:
/developer-kit:devkit.task-implementation --lang=[lang] --task="docs/specs/[id]/tasks/TASK-XXX.md"
```

### Context Hash Generation

The `context_hash` field is used for change detection. Generate SHA-256 hash of: task title + description + acceptance_criteria + files_to_create + files_to_modify.

Regenerate whenever these fields change to detect task drift.

---

## Action: Split

Splits a complex task into smaller, more manageable subtasks.

### Process

1. Read the task file to be split

2. Analyze the task complexity:
   - If complexity < 50, suggest keeping as single task
   - If complexity >= 50, proceed with split

3. Propose a split strategy to the user:
   - How many subtasks (typically 2-4)
   - What each subtask covers
   - Dependencies between subtasks

4. Get user confirmation on the split strategy

5. Create subtask files:
   - Generate new task IDs (e.g., TASK-008, TASK-009)
   - Each subtask inherits relevant context from parent
   - Update dependencies to reflect split
   - Calculate complexity for each subtask:
     - Count files, acceptance criteria, components, design decisions, integration points, external dependencies
     - Apply complexity formula
     - Ensure each subtask has complexity < parent task complexity

6. Mark original task as superseded:
   - Update status to "superseded"
   - Add `supersedes` reference to new subtasks

7. Update task index with new structure

8. Update traceability matrix
   - For each new subtask, add rows to traceability-matrix.md
   - Update parent task rows to reflect new subtask structure
   - Update coverage summary with new task count

### Context Chain Inheritance

When splitting tasks, child tasks inherit context from parent:

```yaml
# Parent task context (preserved)
business_goals:
  - "[Inherited from parent]"

data_contracts:
  # Inherited but can be refined
  input:
    - "[Subset relevant to child]"
  output:
    - "[Subset relevant to child]"

external_dependencies:
  # Assign only pertinent dependencies to each child
  - "[Relevant dependency]"

observability:
  # Inherited framework, refined specifics
  logging:
    - "[Relevant log points]"
  metrics:
    - "[Relevant metrics]"
  security:
    - "[Relevant security considerations]"

parent_task: "TASK-XXX"  # Reference to parent
supersedes: []  # Child tasks don't supersede
```

---

## Action: Mark Optional/Required

Toggles the optional status of a task.

### Process

1. Read the task file

2. Update the task frontmatter:
   - For `mark-optional`: Set `optional: true`
   - For `mark-required`: Set `optional: false`

3. Update the task index to reflect the change

4. Update the traceability matrix

---

## Action: Update

Updates task details.

### Process

1. Read the current task file

2. Present current values and ask what to update:
   - Title
   - Description
   - Acceptance criteria
   - Dependencies
   - Files to create/modify
   - Complexity assessment
   - Context fields (business goals, data contracts, etc.)

3. Apply the requested changes

4. Recalculate complexity if relevant fields changed

5. Update context_hash if task structure changed

6. Update task index

7. Update traceability matrix if requirements mapping changed

---

## Action: Regenerate Index

Recreates the task index file from existing task files.

### Process

1. Scan `docs/specs/[id]/tasks/` directory for all `TASK-XXX.md` files

2. Read each task file and extract:
   - Task ID
   - Title
   - Status
   - Complexity score
   - Optional flag
   - Dependencies

3. Sort tasks by ID

4. Generate new task index:
   - Summary statistics
   - Task table
   - Complexity distribution
   - Dependency graph

5. Write updated index file

---

## Action: List

Displays all tasks with their status and complexity.

### Process

1. Read the task index

2. Display formatted list:

```
Task List for [Feature Name]
============================

Simple Tasks (≤30):
  ✅ TASK-001: [Title] ([Status])
  ✅ TASK-002: [Title] ([Status])

Moderate Tasks (31-50):
  ⚠️  TASK-003: [Title] ([Status])

Complex Tasks (>50):
  ❌ TASK-004: [Title] ([Status]) - Consider splitting

Optional Tasks:
  ○ TASK-005: [Title] (optional)

Total: X tasks | Y simple | Z moderate | W complex
```

3. Show dependency warnings if any

---

## Complexity Recalculation

When task details change, recalculate complexity:

```
COMPLEXITY SCORE =
  (Files × 10) +
  (Acceptance Criteria × 5) +
  (Independent Components × 25) +
  (Design Decisions × 10) +
  (Integration Points × 15) +
  (External Dependencies × 20)

Thresholds:
- 0-30: Simple
- 31-50: Moderate
- 51+: Complex (must split)
```

Update both the score and complexity level in the task frontmatter.

---

## Index Update Template

When updating the task index, use this format:

```markdown
# Task List: [Feature Name]

**Specification**: [Spec file path]
**Last Updated**: [Date]

## Summary

- **Total Tasks**: [N]
- **Simple (≤30)**: [N]
- **Moderate (31-50)**: [N]
- **Complex (>50)**: [N]
- **Optional Tasks**: [N]

## Tasks

| ID | Title | Status | Complexity | Optional | Dependencies |
|----|-------|--------|------------|----------|--------------|
| TASK-001 | [Title] | [Status] | [Score]/[Level] | [Yes/No] | [Deps] |

## Complexity Distribution

```
Simple:    [████░░░░░░] X tasks
Moderate:  [██░░░░░░░░] Y tasks
Complex:   [█░░░░░░░░░] Z tasks (requires splitting)
```

## Implementation Commands

```bash
# Task 1
/developer-kit:devkit.task-implementation --lang=[lang] --task="docs/specs/[id]/tasks/TASK-001.md"

# Task 2
/developer-kit:devkit.task-implementation --lang=[lang] --task="docs/specs/[id]/tasks/TASK-002.md"
```

## Next Actions

- [ ] Address complex tasks (split recommended)
- [ ] Complete simple tasks first
- [ ] Resolve dependency chains

---

## Examples

### Example 1: Add a new task

```bash
# Add a new task to a specification
/developer-kit:devkit.task-manage --action=add --spec=docs/specs/001-user-auth/ --lang=spring
```

### Example 2: Split a complex task

```bash
# Split a complex task into subtasks
/developer-kit:devkit.task-manage --action=split --task=docs/specs/001-user-auth/tasks/TASK-007.md
```

### Example 3: Mark task as optional

```bash
# Mark a task as optional
/developer-kit:devkit.task-manage --action=mark-optional --task=docs/specs/001-user-auth/tasks/TASK-003.md
```

### Example 4: Regenerate task index

```bash
# Regenerate the task index file
/developer-kit:devkit.task-manage --action=regenerate-index --spec=docs/specs/001-user-auth/
```

### Example 5: List all tasks

```bash
# List all tasks with complexity
/developer-kit:devkit.task-manage --action=list --spec=docs/specs/001-user-auth/
```

---

## Todo Management

For each action, maintain a todo list:

```
[ ] Parse arguments and validate
[ ] Read existing context (task/spec)
[ ] Perform requested action
[ ] Update affected files
[ ] Regenerate index if needed
[ ] Update traceability matrix
[ ] Confirm changes to user
```
