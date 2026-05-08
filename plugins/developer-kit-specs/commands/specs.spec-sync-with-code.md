---
description: "Synchronizes functional specification with current implementation state. Use this command after implementing tasks or when spec drift is detected. Detects deviations between spec and code, proposes specification updates based on decision-log and completed tasks. Closes the SDD loop (Spec <-> Code)."
argument-hint: "[ --spec=\"docs/specs/XXX-feature\" ] [ --after-task=\"TASK-XXX\" ]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, TodoWrite
model: inherit
---

# Spec Sync With Code

Synchronizes the functional specification with the current implementation state, detecting and proposing updates based on the decision-log and completed tasks.

## Overview

This command closes the SDD loop by keeping synchronized:
- **Spec** → The functional specification (WHAT)
- **Code** → The actual implementation (HOW)

### Problem It Solves

The current workflow is unidirectional: Spec → Tasks → Code. Decisions made during implementation don't flow back to the specification, leading to:
- Specifications that are inaccurate relative to the implemented code
- Decisions lost with the conversation
- No explicit traceability: Requirement → Task → Code

### Workflow Position

```
Idea → Spec → Tasks → Implementation → Spec Sync With Code (this)
           ↑                              ↓
           └──────────────────────────────┘
               Update spec with decisions
```

## Usage

```bash
# Sync spec after implementation drift detected
/developer-kit-specs:specs.spec-sync-with-code docs/specs/001-hotel-search-aggregation/

# Sync after specific task completed
/developer-kit-specs:specs.spec-sync-with-code docs/specs/001-hotel-search-aggregation/ --after-task=TASK-001

# Sync for current spec folder (auto-detected)
/developer-kit-specs:specs.spec-sync-with-code
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `spec-folder` | No | Path to spec folder (default: detect from CWD) |
| `--after-task` | No | Specific task ID that just completed |

## Current Context

If `--spec` is omitted, the spec folder is auto-detected from the current git branch:

```bash
branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
spec_folder=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
```

If no matching spec folder is found for the current branch, stop and inform the user.

---

## Phase 1: Discovery

**Goal**: Identify spec folder and load context

**Actions**:

1. Create todo list with all phases
2. Parse arguments:
   - Extract `spec-folder` path (positional argument or `--spec=` parameter)
   - Extract `--after-task` if provided
3. Determine spec folder:
   - If positional argument provided: use it
   - If `--spec=` parameter provided: use it
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

   ### Architecture Deviations
   - Cross-boundary modification in TASK-005 (modified Core Engine file)
   - New cross-context dependency introduced

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
   - "Approve all updates" - Apply all changes to spec and create missing tasks
   - "Approve spec only" - Apply spec changes, skip task creation
   - "Review selectively" - Review each change individually
   - "Skip for now" - Don't update spec or create tasks
   ```

4. **If user chooses "Approve all updates" or "Approve spec only"**:
   - First apply spec updates (Phase 4)
   - If "Approve all updates": Proceed to Phase 3.5 for automatic task creation
   - If "Approve spec only": Skip task creation

5. **If user chooses "Review selectively"**:
   - Present each change category one by one
   - Ask for approval on each
   - Track which changes need task creation

---

## Phase 3.5: Automatic Task Creation (Conditional)

**Goal**: Create missing tasks for detected GAPs

**Trigger**: Only runs when user chooses "Approve all updates" in Phase 3

**Actions**:

1. **Analyze deviations for task creation**:
   - For each scope expansion: Create task for new feature/component
   - For each requirement refinement: Create task for updated requirement
   - For each scope reduction: Mark related tasks as optional or superseded
   - For each architecture deviation: Check if escalation report exists in `docs/specs/[id]/escalations/`
     - If YES: suggest returning to `/developer-kit-specs:specs.spec-to-tasks` instead of creating tasks
     - If NO: flag as requiring ADR or architecture review before proceeding
   - Skip refinements that don't require new implementation (e.g., documentation clarifications)

2. **Generate task proposals**:
   ```markdown
   ## Task Creation Proposals

   ### New Tasks to Create
   | Deviation | Suggested Task Title | Priority |
   |-----------|---------------------|----------|
   | Scope Expansion: Pagination | Implement pagination for search results | High |
   | Scope Expansion: Rating filter | Add rating filter to search | Medium |
   ```

3. **Present task creation options via AskUserQuestion**:
   ```
   GAPs Found: N deviations require new tasks

   Options:
   - "Create all tasks" - Generate tasks for all deviations (recommended)
   - "Review each" - Review and approve each task individually
   - "Skip task creation" - Only update spec, don't create tasks
   ```

4. **If user chooses "Create all tasks"**:
   - For each deviation requiring a task:
     a. Generate task title from deviation
     b. Generate task description from deviation context
     c. Generate acceptance criteria from deviation details
     d. Determine dependencies from related existing tasks
     e. Use `/developer-kit-specs:specs.task-manage` pattern to create task file:
        - Read task index to get next task ID
        - Create task file with template
        - Add to task index
   - Show created task list with implementation commands

5. **If user chooses "Review each"**:
   - Present each task proposal individually
   - Ask for approval before creating each task
   - Allow modifications to task title/description/criteria

6. **If user chooses "Skip task creation"**:
   - Log pending tasks for future creation
   - Continue with spec updates only

### Task Creation from Deviation

For each deviation type, create task as follows:

**Scope Expansion**:
- Title: "Implement [feature from deviation]"
- Description: Describe the expanded feature
- Acceptance Criteria: Derived from deviation details
- Dependencies: Related existing tasks

**Requirement Refinement**:
- Title: "Update [component] for [refinement]"
- Description: Describe the updated requirement
- Acceptance Criteria: New acceptance criteria from refinement
- Dependencies: Related existing tasks

**Scope Reduction**:
- Find tasks that implement dropped features
- Update those tasks to status "superseded" with reason
- No new task creation needed

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
   - **Verify taxonomy compliance**: Ensure no task claims to implement `[SEF]` or `[EXT]` criteria as `[IMP]`

2. **Generate final report**:
   ```markdown
   ## Spec Sync Complete
   - Specification updated: [path]
   - Revision history added
   - Decision log references maintained
   - N new tasks created (if applicable)
   ```
