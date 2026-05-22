---
description: "Provides capability to verify that implemented tasks meet specifications and pass code review. Use when needing to validate a completed task from devkit.task-implementation against its specification."
argument-hint: "[ --lang=java|spring|typescript|nestjs|react|python|general ] [ --task=\"docs/specs/XXX-feature/tasks/TASK-XXX.md\" ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Task Review

Verifies that implemented tasks meet specifications and pass code quality standards. This is the bridge between implementation and verification.

## Overview

This command reviews a completed task to ensure:
1. **Task Implementation**: The task was implemented according to its specifications
2. **Spec Compliance**: The implementation aligns with the functional specification
3. **Code Quality**: The code passes code review standards
4. **Acceptance Criteria**: All acceptance criteria are met
5. **Definition of Done**: The documented completion conditions are fully satisfied

**Input**: `docs/specs/[id]/tasks/TASK-XXX.md` (from devkit.spec-to-tasks)
**Output**: Review report with pass/fail status and findings

### Workflow Position

```
Idea → Functional Specification → Tasks → Implementation → Review → Code Cleanup → Done
              (brainstorm)           (spec-to-tasks)       (task-implementation)  (task-review)   (code-cleanup)
```

## Usage

```bash
# Review a specific task
/developer-kit-specs:specs.task-review docs/specs/001-user-auth/tasks/TASK-001.md

# With language specification for code review
/developer-kit-specs:specs.task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | No | Target language/framework for code review |
| `--task` | No | Task file path |
| `--spec` | No | Path to spec folder |

## Examples

### Basic Usage

```bash
/developer-kit-specs:specs.task-review docs/specs/001-user-auth/tasks/TASK-001.md
```

### With Language Specification

```bash
/developer-kit-specs:specs.task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
```

### Using Spec Detection

```bash
/developer-kit-specs:specs.task-review --task=TASK-001
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
   - `flags` → detect `--no-confirm`
2. If `spec` is null, auto-detect from git branch:
   ```bash
   branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
   spec=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
   ```
3. Validate required parameters. If missing, ask user via AskUserQuestion.

## Core Principles

- **Thorough verification**: Check every acceptance criterion and every DoD item
- **Spec alignment**: Ensure implementation matches functional requirements
- **Code quality**: Verify code passes review standards
- **Evidence-based**: Base findings on actual code, not assumptions
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates

---

## Phase 1: Task Analysis

**Goal**: Read and understand the task and its specifications

**Actions**:

1. (Argument parsing completed in Phase 0)
2. Read the task file (`docs/specs/[id]/tasks/TASK-XXX.md`)
3. Extract:
   - Task ID and title
   - Description
   - Acceptance criteria
   - Definition of Ready (DoR) and Definition of Done (DoD) sections
   - Dependencies
   - Reference to specification file
   - `imp-requirements` and `ac-mapping` from frontmatter — which spec ACs this task claims to implement
   - If either section is missing, stop the review and require the task document to be updated before continuing
4. Read the functional specification file (from task's spec reference)
5. Verify both files exist and are valid
6. If files not found, ask user for correct path via AskUserQuestion

---

## Phase 2: Implementation Verification

**Goal**: Verify the task was implemented according to specifications

**Actions**:

1. Identify what files/components were created for this task:
   - Check git diff to see what changed since task was started
   - Look for new files matching the task scope
   - Review implementation details

2. Verify implementation matches task description:
   - Compare implemented functionality with task description
   - Check if all described features are present
   - Identify any deviations or missing parts

3. Document findings:
   - What was implemented vs. what was specified
   - Any deviations from the original plan
   - Additional changes that were made

4. **Read decision-log.md if exists**:
   - Check for `decision-log.md` in the spec folder
   - If file exists, read any DEC entries related to this task (TASK-XXX)
   - Use decision context to understand WHY deviations were made
   - Reference specific decision IDs when explaining deviations in findings

---

## Phase 3: Acceptance Criteria and DoD Validation

**Goal**: Verify all acceptance criteria and DoD items are met

**Actions**:

1. List all acceptance criteria from the task file
2. List all DoD items from the task file
3. For each acceptance criterion and DoD item:
   - Identify code/tests/review evidence that validate it
   - Check if tests exist and pass when relevant
   - Verify the requirement is actually met
4. Mark each item as:
   - ✅ Met (with evidence)
   - ❌ Not met (with explanation)
   - ⚠️ Partially met (with details) — treated as FAILED for `review_status`

5. **Update traceability-matrix.md**:
   - Read `docs/specs/[id]/traceability-matrix.md`
   - For this task (TASK-XXX), update the matrix:
     - Fill in "Test Files" column with test file names created for this task
     - Fill in "Code Files" column with source files created for this task
     - Update "Status" to "Implemented" for REQ-IDs covered by this task
   - Save updated matrix back to `docs/specs/[id]/traceability-matrix.md`

6. **BOUNDED CONTEXT ADHERENCE CHECK **:
   - Read `docs/specs/ontology.md` for bounded context definitions
   - Determine the primary bounded context of the feature
   - For each file modified/created in the implementation:
     - Determine its bounded context from path conventions or ontology
     - If DIFFERENT from the feature's primary context:
       - Check if the task file has a "Cross-Boundary Warning" section
       - If YES and justification is valid: note in review as "acknowledged cross-boundary"
       - If YES but justification is weak: add `warning` issue
       - If NO warning section: add `blocking` issue
   - **Why this matters**: Tasks that silently cross bounded context boundaries are the #1 cause of architectural drift.

---

## Phase 4: Specification Compliance Check

**Goal**: Ensure implementation aligns with functional specification AND verify task necessity

**Actions**:

1. Review the functional specification to verify compliance
2. Compare implementation against:
   - User stories and use cases
   - Business rules
   - Integration requirements
   - Data requirements
3. Identify any gaps or misalignments
4. Check if implementation introduces any out-of-scope changes

5. **SPEC FIDELITY CHECK **:
   - Read the task's `imp-requirements` and `ac-mapping` from frontmatter
   - For each AC-ID in `ac-mapping`:
     - Verify the implementation actually satisfies the acceptance criterion
     - Check the criterion's taxonomy in the spec: `[IMP]`, `[SEF]`, or `[EXT]`
     - **If the task claims to implement `[SEF]` or `[EXT]` criteria**: 
       - Flag as "Task Over-Specification"
   - **If the task has NO `ac-mapping` or `imp-requirements`**:
     - Flag as "Legacy Task — no traceability metadata"

6. **Verify task necessity**:
   - Ask: "Is this task implementing a criterion that requires new code?"
   - If ALL the task's ACs are `[SEF]` or `[EXT]`: 
     - Flag as "Unnecessary Task — no implementation needed"
   - If the task creates entities/structs NOT mentioned in the functional spec:
     - Check `data-model.md` for `(derived)` marking
     - If NOT marked `(derived)`: Flag as "Invented Entity — not in spec"

7. **Check for spec contradictions**:
   - If the implementation does something DIFFERENT from the spec:
     - Check `decision-log.md` for a DEC entry justifying the deviation
     - If NO DEC entry: flag as critical issue

---

## Phase 5: Code Review

**Goal**: Verify code passes quality standards

**Actions**:

1. Based on `--lang` parameter, perform code review focusing on:
   - Architectural alignment
   - Coding standards and patterns
   - Security and performance
   - Error handling and edge cases
   - Maintainability and readability
2. Document specific code findings (file, line, issue, recommendation)

---

## Phase 6: Review Report Generation

**Goal**: Generate a summary of review findings and set status

**Actions**:

1. **Calculate overall status**:
   - `passed`: All ACs and DoD met, no critical code issues, no architectural drift
   - `needs_fix`: Minor issues in ACs, DoD, or code quality
   - `partial`: Some ACs met, but major functionality missing or incorrect
   - `escalate`: Critical architectural drift, spec contradiction without DEC, or impossible requirement

2. **Generate review report** (`docs/specs/[id]/reviews/TASK-XXX-review.md`):
   Read the review template using this lookup order:
   1. `${CLAUDE_PLUGIN_ROOT}/templates/task-review.md`
   2. `templates/task-review.md` inside the installed skill folder for non-Claude agents.
   Fill in the gathered findings and save to the reviews directory.

   The review template defines these sections:
   | Section | Purpose |
   |---------|----------|
   | Review Summary | High-level status table (AC, DoD, Code Quality, Spec Compliance, Architecture) |
   | Acceptance Criteria & DoD Results | Per-criterion and per-item status with evidence |
   | Code Review Findings | Table of issues with severity, file, category, recommendation |
   | Spec Compliance & Architectural Alignment | Fidelity check, cross-boundary adherence, decision log, traceability update |
   | Required Fixes | Critical / Warnings / Suggestions tables |
   | Next Steps | Action by review status |

3. **Update task status**:
   - Set `status: reviewed` in task frontmatter if `passed`
   - Set `reviewed_date: YYYY-MM-DD` if `passed`
   - For other statuses, update task status accordingly (e.g., `needs_fix`, `escalated`)

4. **Synchronization**:
   - Run `/developer-kit-specs:specs.sync [spec-folder]` to synchronize all components

5. **Inform user**:
   - Display review summary and status
   - Provide link to full review report
   - If `passed`, suggest running Phase T-7 cleanup in `task-implementation`
