---
description: "Provides capability to verify that implemented tasks meet specifications and pass code review. Use when needing to validate a completed task from devkit.task-implementation against its specification."
argument-hint: "[ --lang=java|spring|typescript|nestjs|react|python|general ] [ task-file-path ]"
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

**Input**: `docs/specs/[id]/tasks/TASK-XXX.md` (from devkit.spec-to-tasks)
**Output**: Review report with pass/fail status and findings

### Workflow Position

```
Idea → Functional Specification → Tasks → Implementation → Review
              (devkit.brainstorm)   (this)   (devkit.task-implementation)  (this)
```

## Usage

```bash
# Review a specific task
/developer-kit:devkit.task-review docs/specs/001-user-auth/tasks/TASK-001.md

# With language specification for code review
/developer-kit:devkit.task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
/developer-kit:devkit.task-review --lang=typescript docs/specs/001-user-auth/tasks/TASK-001.md
/developer-kit:devkit.task-review --lang=nestjs docs/specs/001-user-auth/tasks/TASK-001.md
/developer-kit:devkit.task-review --lang=react docs/specs/001-user-auth/tasks/TASK-001.md
/developer-kit:devkit.task-review --lang=python docs/specs/001-user-auth/tasks/TASK-001.md
/developer-kit:devkit.task-review --lang=general docs/specs/001-user-auth/tasks/TASK-001.md
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | No | Target language/framework: `java`, `spring`, `typescript`, `nestjs`, `react`, `python`, `general` |
| `task-file-path` | Yes | Path to the task file (e.g., `docs/specs/001-user-auth/tasks/TASK-001.md`) |

## Current Context

The command will automatically gather context information when needed:
- Current git branch and status
- Recent commits and changes
- Available when the repository has history

---

You are reviewing an implemented task to verify it meets specifications and passes code review. Follow a systematic approach: analyze the task, verify implementation, check spec compliance, and perform code review.

## Core Principles

- **Thorough verification**: Check every acceptance criterion
- **Spec alignment**: Ensure implementation matches functional requirements
- **Code quality**: Verify code passes review standards
- **Evidence-based**: Base findings on actual code, not assumptions
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates

---

## Phase 1: Task Analysis

**Goal**: Read and understand the task and its specifications

**Input**: $ARGUMENTS (task file path)

**Actions**:

1. Create todo list with all phases
2. Parse $ARGUMENTS to extract:
   - `--lang` parameter (language/framework for code review)
   - `task-file-path` (path to task file)
3. Read the task file (`docs/specs/[id]/tasks/TASK-XXX.md`)
4. Extract:
   - Task ID and title
   - Description
   - Acceptance criteria
   - Dependencies
   - Reference to specification file
5. Read the functional specification file (from task's spec reference)
6. Verify both files exist and are valid
7. If files not found, ask user for correct path via AskUserQuestion

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
   - Check for `decision-log.md` in the spec folder (extract from task frontmatter `spec:` field)
   - If file exists, read any DEC entries related to this task (TASK-XXX)
   - Use decision context to understand WHY deviations were made
   - Reference specific decision IDs when explaining deviations in findings

---

## Phase 3: Acceptance Criteria Validation

**Goal**: Verify all acceptance criteria are met

**Actions**:

1. List all acceptance criteria from the task file
2. For each criterion:
   - Identify code/tests that validate this criterion
   - Check if tests exist and pass
   - Verify the criterion is actually met
3. Mark each criterion as:
   - ✅ Met (with evidence)
   - ❌ Not met (with explanation)
   - ⚠️ Partially met (with details)

4. **Update traceability-matrix.md**:
   - Read `docs/specs/[id]/traceability-matrix.md` (extract from task frontmatter `spec:` field)
   - For this task (TASK-XXX), update the matrix:
     - Fill in "Test Files" column with test file names created for this task
     - Fill in "Code Files" column with source files created for this task
     - Update "Status" to "Implemented" for REQ-IDs covered by this task
   - Save updated matrix back to `docs/specs/[id]/traceability-matrix.md`

---

## Phase 4: Specification Compliance Check

**Goal**: Ensure implementation aligns with functional specification

**Actions**:

1. Review the functional specification (already loaded in Phase 1) to verify compliance
2. Compare implementation against:
   - User stories and use cases
   - Business rules
   - Integration requirements
   - Data requirements
3. Identify any gaps or misalignments
4. Check if implementation introduces any out-of-scope changes

---

## Phase 5: Code Review

**Goal**: Verify code passes quality standards

**Actions**:

1. Based on `--lang` parameter, select appropriate code review agent:

| Language | Code Review Agent |
|----------|------------------|
| `java` | `developer-kit-java:spring-boot-code-review-expert` |
| `spring` | `developer-kit-java:spring-boot-code-review-expert` |
| `typescript` | `developer-kit:general-code-reviewer` |
| `nestjs` | `developer-kit-typescript:nestjs-code-review-expert` |
| `react` | `developer-kit:general-code-reviewer` |
| `python` | `developer-kit-python:python-code-review-expert` |
| `php` | `developer-kit-php:php-code-review-expert` |
| `general` | `developer-kit:general-code-reviewer` |

2. Launch code review agent to analyze implemented code
3. Collect review findings
4. Categorize issues by severity:
   - Critical (must fix)
   - Major (should fix)
   - Minor (recommended fix)
   - Info (suggestions)

---

## Phase 6: Review Report Generation

**Goal**: Create comprehensive review report

**Actions**:

1. Compile all findings into a review report
2. Generate the report in markdown format:

```markdown
# Task Review Report: TASK-XXX

**Task**: [Task Title]
**Specification**: [spec-file.md]
**Reviewed**: [date]
**Language**: [language]

## Summary

| Category | Status |
|----------|--------|
| Implementation | ✅ Complete / ⚠️ Partial / ❌ Incomplete |
| Acceptance Criteria | ✅ All Met / ⚠️ Partial / ❌ Failed |
| Spec Compliance | ✅ Compliant / ⚠️ Deviations / ❌ Non-compliant |
| Code Review | ✅ Passed / ⚠️ Issues Found / ❌ Failed |

## Implementation Verification

- **Implemented**: [description]
- **Deviations**: [list if any]

## Acceptance Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Criterion 1 | ✅/⚠️/❌ | [evidence] |
| Criterion 2 | ✅/⚠️/❌ | [evidence] |

## Specification Compliance

- **Compliant**: Yes/No
- **Deviations**: [list]


## Traceability

-- **Traceability Coverage**: N/N requirements covered (X%)
-- **REQ-IDs**: [List of REQ-IDs covered by this task]
## Code Review Findings

### Critical
- [list]

### Major
- [list]

### Minor
- [list]

### Info
- [list]

## Recommendations

- [actionable recommendations]

## Decisions Referenced

- [List any DEC-ID entries from decision-log.md that explain deviations]


3. **If decision-log.md exists, include decisions referenced**:
   - Search for DEC entries mentioning this task (TASK-XXX)
   - Summarize key decisions that affected implementation
   - Reference specific decision IDs (e.g., See DEC-003)
```

3. Save report to: `docs/specs/[id]/tasks/TASK-XXX--review.md`

---

## Phase 7: Review Confirmation

**Goal**: Present review results to user

**Actions**:

1. Present the review report to the user
2. Ask for confirmation via AskUserQuestion:
   - **Option A**: Review complete, task approved
   - **Option B**: Issues found, needs revision
   - **Option C**: Need additional verification

3. If issues found:
   - List specific issues that need fixing
   - Save findings to the review report at `docs/specs/[id]/tasks/TASK-XXX--review.md`
   - Invoke `/developer-kit:devkit.task-implementation --lang=[language] --task="docs/specs/[id]/tasks/TASK-XXX.md"`
   - Reference the review report path so implementation can read the detailed findings
   - Track unresolved items
   - **Note**: Before re-implementing, consider running `/devkit.spec-review [spec-folder]` to verify the spec is still accurate if issues suggest spec-level problems

---

## Phase 8: Summary

**Goal**: Document what was accomplished

**Actions**:

1. Mark all todos complete
2. Summarize:
    - **Task Reviewed**: Path to task file
    - **Specification**: Reference to functional spec
    - **Implementation Status**: Complete/Partial/Incomplete
    - **Acceptance Criteria**: All met / Partial / Failed
    - **Code Review Status**: Passed / Issues / Failed
    - **Review Report**: `docs/specs/[id]/tasks/TASK-XXX--review.md`
    - **Next Step**: Fix issues or proceed to next task

---

## Integration with Workflow

This command completes the verification loop:

```
/developer-kit:devkit.brainstorm
    ↓
[Creates: docs/specs/[id]/YYYY-MM-DD--feature-name.md]
    ↓
/developer-kit:devkit.spec-to-tasks --lang=[language] docs/specs/[id]/
    ↓
[Creates: docs/specs/[id]/tasks/TASK-XXX.md]
    ↓
/developer-kit:devkit.task-implementation--lang=[language] --task="docs/specs/[id]/tasks/TASK-XXX.md"
    ↓
[Implements task]
    ↓
/developer-kit:devkit.task-review --lang=[language] "docs/specs/[id]/tasks/TASK-XXX.md"
    ↓
[Verifies implementation, generates review report]
    ↓
[If issues: back to implementation]
[If approved: proceed to next task]
```

---

## Examples

### Example 1: Review User Authentication Task

```bash
# Review a completed task
/developer-kit:devkit.task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
```

### Example 2: Review Checkout Task

```bash
/developer-kit:devkit.task-review --lang=typescript docs/specs/005-checkout/tasks/TASK-003.md
```

### Example 3: Review API Integration Task

```bash
/developer-kit:devkit.task-review --lang=python docs/specs/010-payment/tasks/TASK-002.md
```

---

## Todo Management

Throughout the process, maintain a todo list like:

```
[ ] Phase 1: Task Analysis
[ ] Phase 2: Implementation Verification
[ ] Phase 3: Acceptance Criteria Validation
[ ] Phase 4: Specification Compliance Check
[ ] Phase 5: Code Review
[ ] Phase 6: Review Report Generation
[ ] Phase 7: Review Confirmation
[ ] Phase 8: Summary
```

Update the status as you progress through each phase.

---

**Note**: This command ensures quality control in the development workflow by verifying that implemented tasks meet specifications and pass code review standards before proceeding to the next task.
