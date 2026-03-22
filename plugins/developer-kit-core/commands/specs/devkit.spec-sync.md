---
description: "Synchronizes functional specification with current implementation state. Detects deviations between spec and code, proposes specification updates based on decision-log and completed tasks. Closes the SDD triangle (Spec <-> Test <-> Code)."
argument-hint: "[ spec-folder ] [--after-task=TASK-XXX]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, TodoWrite
model: inherit
---

# Spec Sync

Synchronizes the functional specification with the current implementation state, detecting and proposing updates based on the decision-log and completed tasks.

## Overview

This command closes the SDD triangle by keeping synchronized:
- **Spec** → The functional specification (WHAT)
- **Test** → Tasks and acceptance criteria (verification)
- **Code** → The actual implementation (HOW)

### Problem It Solves

The current workflow is unidirectional: Spec → Tasks → Code. Decisions made during implementation don't flow back to the specification, leading to:
- Specifications that are inaccurate relative to the implemented code
- Decisions lost with the conversation
- No explicit traceability: Requirement → Task → Test → Code

### Workflow Position

```
Idea → Spec → Tasks → Implementation → Spec Sync (this)
           ↑                              ↓
           └──────────────────────────────┘
               Update spec with decisions
```

## Usage

```bash
# Sync spec after implementation drift detected
/developer-kit:devkit.spec-sync docs/specs/001-hotel-search-aggregation/

# Sync after specific task completed
/developer-kit:devkit.spec-sync docs/specs/001-hotel-search-aggregation/ --after-task=TASK-001

# Sync for current spec folder (auto-detected)
/developer-kit:devkit.spec-sync
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `spec-folder` | No | Path to spec folder (default: detect from CWD) |
| `--after-task` | No | Specific task ID that just completed |

---

## Phase 1: Discovery

**Goal**: Identify spec folder and load context

**Actions**:

1. Create todo list with all phases
2. Parse arguments:
   - Extract `spec-folder` path
   - Extract `--after-task` if provided
3. Determine spec folder:
   - If argument provided: use it
   - If no argument: detect from current working directory
   - Resolve the specification file with this priority:
     1. `YYYY-MM-DD--feature-name.md`
     2. legacy `*-specs.md`
     3. the only dated spec-like markdown file in the folder excluding task and metadata files
4. Load current context:
   - Read the resolved functional specification file
   - Read `decision-log.md` if exists
   - List all task files in `tasks/` directory
   - Identify completed tasks (status: completed)

---

## Phase 2: Deviation Detection

**Goal**: Detect deviations between spec and implementation

**Actions**:

1. **Compare acceptance criteria**:
   - Read acceptance criteria from the spec
   - For each completed task, read its acceptance criteria
   - Identify criteria that were:
     - Added (not in original spec)
     - Modified (changed from original spec)
     - Dropped (removed during implementation)

2. **Analyze decision-log.md**:
   - Read all DEC entries
   - Identify decisions that caused spec changes
   - Categorize deviations by decision reference

3. **Generate deviation report**:
   ```markdown
   ## Deviation Analysis

   ### Scope Expansions
   - Added pagination to search results (DEC-003)
   - Added filtering by rating

   ### Requirement Refinements
   - Changed "instant search" to "search with caching"

   ### Scope Reductions
   - Dropped "search by proximity" feature
   ```

---

## Phase 3: Spec Update Proposal

**Goal**: Generate diff-style proposal for spec update

**Actions**:

1. **Generate diff-style proposal** showing:
   - **Additions**: New content to add to spec (marked with +)
   - **Modifications**: Content to change (marked with ~)
   - **Deletions**: Content to remove (marked with -)

2. **Categorize changes**:
   - **Scope expansion**: Features added beyond original spec
   - **Requirement refinement**: Clarifications or corrections
   - **Scope reduction**: Features dropped or deferred

3. **Present proposal to user via AskUserQuestion**:
   ```
   Summary:
   - X scope expansions
   - Y requirement refinements
   - Z scope reductions

   Options:
   - "Approve all updates" - Apply all changes to spec
   - "Review selectively" - Review each change individually
   - "Skip for now" - Don't update spec
   ```

4. **If user chooses "Review selectively"**:
   - Present each change category one by one
   - Ask for approval on each

---

## Phase 4: Apply Updates

**Goal**: Apply approved updates to the specification

**Actions**:

1. **Backup original spec**:
   - Create a backup next to the resolved spec file using `[resolved-spec-file].backup`

2. **Apply approved changes**:
   - For scope expansions: Add new sections/content
   - For refinements: Update existing content
   - For scope reductions: Remove or mark as deferred content

3. **Add Revision History section** at end of spec:
   ```markdown
   ## Revision History

   | Date | Change | Reason | Decision Ref |
   |------|--------|--------|--------------|
   | YYYY-MM-DD | Added pagination to search results | Implementation revealed need | DEC-003 |
   | YYYY-MM-DD | Clarified search caching behavior | Technical refinement | DEC-005 |
   ```

4. **Update spec metadata**:
   - Update "Last Modified" date
   - Increment version number if tracking versions

---

## Phase 5: Sync Verification

**Goal**: Verify that tasks still map to updated requirements

**Actions**:

1. **Re-validate task list**:
   - Check if all tasks still map to updated spec
   - Identify tasks that need updates
   - Flag tasks with obsolete references

2. **Report validation results**:
   ```markdown
   ## Sync Verification

   ### Tasks Still Valid
   - TASK-001: User registration ✅
   - TASK-002: Login functionality ✅

   ### Tasks Needing Update
   - TASK-003: References removed "proximity search" ❌
   ```

3. **If tasks need updates**:
   - Ask via AskUserQuestion:
     - "Update affected tasks now?" / "Review manually later"

---

## Phase 6: Summary

**Goal**: Document sync outcome

**Actions**:

1. Mark all todos complete
2. Summarize:
   - **Spec Updated**: Yes/No (changes applied)
   - **Deviations Detected**: N total (X added, Y modified, Z dropped)
   - **Decisions Referenced**: N DEC entries analyzed
   - **Revision History**: Added to spec
   - **Backup Created**: Path to backup file
   - **Next Step**: Continue with remaining tasks or re-run spec-to-tasks

---

## Integration with Workflow

This command integrates with the SDD workflow:

```
/developer-kit:devkit.brainstorm
    ↓
[Creates: docs/specs/[id]/YYYY-MM-DD--feature-name.md]
    ↓
/developer-kit:devkit.spec-to-tasks --lang=[language] docs/specs/[id]/
    ↓
[Creates: docs/specs/[id]/tasks/TASK-XXX.md]
    ↓
/developer-kit:devkit.task-implementation --lang=[language] --task="docs/specs/[id]/tasks/TASK-XXX.md"
    ↓
[Implements task, may deviate from spec]
    ↓
T-6.6: Spec Deviation Check detects deviation
    ↓
/developer-kit:devkit.spec-sync docs/specs/[id]/  ← This command
    ↓
[Spec updated with deviations from decision-log.md]
```

### Automatic Triggers

The spec-sync command can be automatically invoked:

1. **From task-implementation T-6.6**: When spec deviation is detected
2. **From spec-quality**: When drift is detected during quality check
3. **From task-review**: When review reveals spec-level issues

### Manual Triggers

Run spec-sync manually when:
- After completing several tasks to bring spec up to date
- Before starting a new feature phase
- When decision-log.md has many entries not reflected in spec

---

## Examples

### Example 1: Sync After Implementation Drift

```bash
# Task T-003 added pagination not in original spec
/developer-kit:devkit.spec-sync docs/specs/001-hotel-search/ --after-task=TASK-003
```

Output:
```
Analyzing spec: docs/specs/001-hotel-search/
Reading decision-log.md... Found 3 decisions
Analyzing completed tasks... TASK-001 ✅, TASK-002 ✅, TASK-003 ✅

Deviations Detected:
- Scope Expansion: Pagination added (DEC-003)
- Requirement Refinement: Search timeout set to 5s (DEC-004)

Proposed Updates:
+ Add "Pagination" section to Functional Requirements
+ Update "Search Performance" with timeout clarification

Options:
- "Approve all updates" (recommended)
- "Review selectively"
- "Skip for now"
```

### Example 2: Full Spec Sync

```bash
# Sync entire spec after multiple tasks completed
/developer-kit:devkit.spec-sync docs/specs/001-user-auth/
```

### Example 3: Auto-Detect Spec Folder

```bash
# Run from within spec directory
cd docs/specs/001-hotel-search-aggregation/
/developer-kit:devkit.spec-sync
```

---

## Todo Management

Maintain todo list:

```
[ ] Phase 1: Discovery
[ ] Phase 2: Deviation Detection
[ ] Phase 3: Spec Update Proposal
[ ] Phase 4: Apply Updates
[ ] Phase 5: Sync Verification
[ ] Phase 6: Summary
```

---

## Best Practices

### When to Run Spec Sync

- ✅ After task completion when deviation detected
- ✅ Before starting new implementation phase
- ✅ When decision-log.md has significant entries
- ✅ Before releasing feature documentation

### Spec Sync vs Spec Review

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `spec-review` | Quality check for vague terms, completeness | Before generating tasks |
| `spec-sync` | Update spec to match implemented reality | After implementation changes |

### Revision History Best Practices

- **Always reference decision IDs**: Links decisions to spec changes
- **Use ISO dates**: YYYY-MM-DD format for consistency
- **Categorize changes**: Helps understand type of evolution
- **Keep backup**: Original spec preserved in `.backup` file

---

## Notes

- This command maintains the "living specification" principle
- Decision-log.md is the single source of truth for WHY changes were made
- The spec should always reflect what the system DOES, not what we thought it would do
- Regular spec-syncs prevent spec-documentation drift over time
