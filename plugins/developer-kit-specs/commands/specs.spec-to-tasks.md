---
description: "Transforms a functional specification into a structured list of executable tasks. Use after specs.brainstorm to prepare for implementation."
argument-hint: "[ --lang=java|spring|typescript|nestjs|react|python|general ] [ --spec=docs/specs/XXX-feature ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Specification to Tasks

Transforms a functional specification into a structured list of executable tasks. This is the bridge between WHAT (spec) and HOW (implementation).

## Overview

This command reads a functional specification and decomposes it into a list of atomic, implementable tasks.

**Workflow Position**:
```
Idea → Functional Specification → Tasks (this) → Implementation → Review → Done
```

## Usage

```bash
/developer-kit-specs:specs.spec-to-tasks docs/specs/001-feature/
```

## Argument Parsing

1. Run the shared argument parser:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/parse_args.py" "$ARGUMENTS"
   ```
   Read the JSON output and extract:
   - `spec` → spec folder path
   - `lang` → target language/framework
   - `flags` → detect `--kg-only`
2. If `spec` is null, auto-detect from git branch:
   ```bash
   branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
   spec=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
   ```
3. Validate required parameters. If missing, ask user via AskUserQuestion.

---

## Phase 1: Specification Analysis

**Goal**: Read and validate the functional specification

**Actions**:

1. Identify the specification file in the spec folder
2. Read the specification and validate:
   - Presence of `[IMP]`, `[SEF]`, `[EXT]` taxonomy tags
   - 60% rule: at least 60% of criteria must be `[IMP]`
   - Bounded Context Impact Statement presence
3. If taxonomy is missing, run `/developer-kit-specs:specs.spec-check [spec-folder]` first
4. Extract all `[IMP]` acceptance criteria for decomposition

---

## Phase 2: Task Decomposition

**Goal**: Create atomic tasks from implementable criteria

**Actions**:

1. Group related `[IMP]` criteria into logical tasks
2. For each task, define:
   - Title and description
   - Map to spec AC-IDs and REQ-IDs
   - Files to create/modify
   - Dependencies on other tasks
   - Complexity estimate
3. Ensure no tasks are generated for `[SEF]` or `[EXT]` criteria (these are verified in e2e/review)
4. Check for file collisions: if multiple tasks modify the same file, consider merging or sequencing them

---

## Phase 3: Task Generation

**Goal**: Create task files and index

**Actions**:

1. Create `tasks/` subdirectory in the spec folder
2. Generate a `TASK-XXX.md` file for each task using the standard template
3. Populate frontmatter with traceability metadata:
   - `imp-requirements`: [REQ-IDs]
   - `ac-mapping`: [AC-IDs]
   - `cross-boundary`: true/false
   - `external-dep-risk`: true/false
4. Generate the task index file: `[YYYY-MM-DD]--[feature-name]--tasks.md`
5. Generate the traceability matrix: `traceability-matrix.md`
6. Run `/developer-kit-specs:specs.sync [spec-folder] --kg-only` to initialize technical context

---

## Phase 4: Summary and Handoff

**Goal**: Inform the user of the generated tasks

**Actions**:

1. Display a summary of generated tasks and their complexity
2. Provide the command to start implementation: `/developer-kit-specs:specs.task-implementation --task=TASK-001`
3. Log completion of the task decomposition workflow
