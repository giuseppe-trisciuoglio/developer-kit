---
description: "Synchronizes specification context (KG, tasks) with implementation reality. Detects spec-to-code drift, proposes and applies spec updates, creates missing tasks. Full sync closes the SDD triangle (Spec <-> Test <-> Code). Use after task implementation or when drift is detected."
argument-hint: "[ --spec=docs/specs/XXX-feature ] [ --kg-only ] [ --code-only ] [ --after-task=TASK-XXX ]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, AskUserQuestion, TodoWrite
model: inherit
---

# Spec Synchronization

Synchronizes specification context (Knowledge Graph, Tasks) with implementation reality and detects/applies spec-to-code drift. This is the close-the-loop step of the specification workflow.

## Overview

This command solves four problems:

1. **Inconsistent Technical Context**: Tasks lose technical context or don't reflect actual patterns used in the codebase
2. **Specs-Tasks Misalignment**: User request, specification, and tasks are not aligned
3. **Obsolete Knowledge Graph**: The knowledge-graph.json is not updated after implementations
4. **Spec-Code Drift**: The functional specification diverges from what was actually implemented, with decisions lost

It closes the SDD triangle by keeping synchronized:
- **Spec** → The functional specification (WHAT)
- **Test** → Tasks and acceptance criteria (verification)
- **Code** → The actual implementation (HOW)

### Workflow Position

```
brainstorm → spec-to-tasks → task-implementation → task-review → sync (this) → done
                                    ↑                     ↓
                                    └── optionally --kg-only after spec-to-tasks ──┘
```

## Usage

```bash
# Full sync (recommended after task-implementation or task-review)
/developer-kit-specs:specs.sync docs/specs/001-feature/

# Sync after a specific task
/developer-kit-specs:specs.sync docs/specs/001-feature/ --after-task=TASK-003

# KG-only mode (lighter, used after spec-to-tasks codebase analysis)
/developer-kit-specs:specs.sync docs/specs/001-feature/ --kg-only

# Code drift detection only
/developer-kit-specs:specs.sync docs/specs/001-feature/ --code-only

```

## Modes

| Flag | What it does | Phases executed | When to use |
|------|-------------|-----------------|-------------|
| (none) | Full sync: KG update + task enrichment + drift detection + spec update | 1-9 | Default after implementation |
| `--kg-only` | Update Knowledge Graph + task enrichment | 1, 2, 3, 4, 9 | After spec-to-tasks, when codebase was analyzed |
| `--code-only` | Spec-to-code drift detection + spec update | 1, 5, 6, 7, 8, 9 | When you suspect drift |


## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--spec` | No | Path to spec folder (e.g., `docs/specs/XXX-feature`). Auto-detected from git branch if omitted. |
| `--kg-only` | No | Update Knowledge Graph and enrich tasks only. Skip drift detection and spec updates. |
| `--code-only` | No | Detect spec-to-code drift and apply spec updates only. Skip KG and task enrichment. |
| `--after-task` | No | Sync after a specific task (e.g., `TASK-003`). Narrows extraction to task-related files. |


## Core Principles

- **Incremental updates**: Only update what has changed, don't rewrite everything
- **Bidirectional sync**: KG → Tasks and Tasks → KG alignment
- **Codebase-first**: Actual implementation is the final authority
- **Non-destructive**: Preserve manual edits and annotations in task files
- **Traceability**: All changes are logged and reported
- **Idempotent**: Running multiple times produces the same result
- **Living specification**: The spec should reflect what the system DOES, not what we planned it would do

---

## Phase 1: Discovery

**Goal**: Identify spec folder, load context, determine execution mode

**Always runs** regardless of mode.

**Actions**:

1. Create todo list with all phases:
   ```
   [ ] Phase 1: Discovery
   [ ] Phase 2: Codebase Extraction & Gap Analysis
   [ ] Phase 3: Knowledge Graph Update
   [ ] Phase 4: Task Enrichment
   [ ] Phase 5: Spec Drift Detection
   [ ] Phase 6: Spec Update Proposal & Approval
   [ ] Phase 7: Apply Updates & Task Creation
   [ ] Phase 8: Sync Verification
   [ ] Phase 9: Summary
   ```

2. Parse `$ARGUMENTS` via script:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/parse_args.py" "$ARGUMENTS"
   ```
   Read the JSON output and extract:
   - `spec` → spec folder path
   - `flags` → detect `--kg-only`, `--code-only`
   - `task` → extract from `--after-task` if present

3. Determine spec folder:
   - If `--spec=` provided: use it
   - If no argument: auto-detect from git branch:
     ```bash
     branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
     spec=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
     ```
   - Validate path contains spec files (at least one markdown file matching spec patterns)

4. Resolve the functional specification file with this priority:
   1. `YYYY-MM-DD--feature-name.md`
   2. Legacy `*-specs.md`
   3. The only dated spec-like markdown file in the folder excluding task and metadata files

5. Load current state:
   - Read the resolved functional specification file
   - Read `decision-log.md` if exists → extract all DEC entries
   - Check if `knowledge-graph.json` exists
   - List all task files in `tasks/` directory
   - Read `user-request.md` if exists
   - Identify completed tasks (status: completed in frontmatter)
   - Detect language from existing tasks or source files

6. Determine execution mode:
   - If `--kg-only`: execute Phases 1, 2, 3, 4, 9
   - If `--code-only`: execute Phases 1, 5, 6, 7, 8, 9
   - If no flag: execute all phases (1-9)

---

## Phase 2: Codebase Extraction & Gap Analysis

**Goal**: Identify discrepancies between KG, tasks, and actual codebase; extract structured information from implemented code

**Runs unless**: `--code-only`

**Actions**:

### 2.1 Knowledge Graph Gap Analysis

1. **KG vs Codebase**:
   - For each component in KG: check if file actually exists
   - For each API in KG: check if endpoint exists
   - Find new files not documented in KG

2. **Tasks vs Knowledge Graph**:
   - Check if task technical context matches KG patterns
   - Identify tasks referencing non-existent components
   - Find tasks missing expected technical details

3. **Requirements Traceability**:
   - Compare `user-request.md` with task descriptions
   - Identify requirements mentioned but not in tasks
   - Find tasks without clear requirement origin

### 2.2 Codebase Extraction

1. **Identify files to extract from**:
   - If `--after-task=TASK-XXX` specified:
     - Read task file to identify implemented files
     - Extract from `provides` section or `Files to Create`
     - Validate files exist in codebase
   - If no specific task:
     - Scan codebase for files matching spec patterns
     - Use Glob to find recently modified files in relevant directories

2. **Extract symbols from files** (language-aware):
   - Java: Grep for `class|interface|enum` declarations
   - TypeScript: Grep for `class|interface|function|const` declarations
   - Python: Grep for `class|def` declarations

3. **Classify by type**:
   - Infer from directory structure: `/domain/entity/` → entity
   - Infer from annotations: `@RestController` → controller, `@Service` → service
   - Infer from naming: `*Repository` → repository, `*DTO` → dto
   - Default to generic type if unclear

4. **Build provides objects**:
   ```json
   {
     "task_id": "TASK-001",
     "file": "src/main/java/.../Search.java",
     "symbols": ["Search", "SearchStatus"],
     "type": "entity",
     "implemented_at": "2026-03-15T10:30:00Z"
   }
   ```

### 2.3 Generate Gap Report

```markdown
## Gap Analysis Report

### Missing in KG
- NewFile.java (discovered in codebase)

### Outdated in KG
- OldComponent.java (file removed from codebase)

### Tasks Needing Update
- TASK-003: References outdated pattern
- TASK-007: Missing technical context

### Orphaned Requirements
- User request mentions "X" but no task covers it

### New Provides Extracted
- TASK-001: Search.java (entity) — 2 symbols
- TASK-003: SearchService.java (service) — 3 symbols
```

---

## Phase 3: Knowledge Graph Update

**Goal**: Update knowledge-graph.json with new findings from Phase 2

**Runs unless**: `--code-only`

**Actions**:

1. **Load existing KG** (or create new structure):
   ```json
   {
     "metadata": {
       "spec_id": "...",
       "feature_name": "...",
       "created_at": "...",
       "updated_at": "2026-03-15T...",
       "version": "1.0",
       "analysis_sources": [...]
     },
     "codebase_context": {...},
     "patterns": {...},
     "components": {...},
     "provides": [...],
     "apis": {...},
     "integration_points": [...]
   }
   ```

2. **Update provides array**:
   - Add new provides from Phase 2.2
   - Check for duplicates by `task_id + file` combination
   - Update `implemented_at` for existing entries
   - Mark entries as verified

3. **Update components** (if newly discovered):
   - Add to appropriate category (controllers, services, entities, repositories, etc.)
   - Preserve existing entries unchanged

4. **Update APIs** (if new endpoints discovered):
   - Scan for REST annotations (`@GetMapping`, `@PostMapping`, etc.)
   - Add to `internal` or `external` as appropriate

5. **Update metadata**:
   - Set `updated_at` to current ISO timestamp
   - Add entry to `analysis_sources`: `{"agent": "spec-sync", "timestamp": "...", "mode": "full|kg-only"}`

6. **Write updated KG** to `docs/specs/[ID]/knowledge-graph.json`

---

## Phase 4: Task Enrichment

**Goal**: Update task files with improved technical context from KG

**Runs unless**: `--code-only`

**Actions**:

1. **Identify tasks needing update** from Phase 2.3 gap report

2. **For each task file**:
   - Read current content
   - Parse YAML frontmatter
   - Identify "Technical Context" section

3. **Enrich technical context** with KG data:
   - Add relevant patterns from KG
   - Reference existing components to integrate with
   - Document APIs to use or extend
   - Note conventions to follow

4. **Update provides section** (if task was implemented):
   - Add or update `provides:` array in frontmatter
   - Include file paths, symbols, types

5. **Preserve manual content**:
   - Don't overwrite custom notes or annotations
   - Preserve acceptance criteria
   - Keep manual edits to descriptions

6. **Write updated task file** back to disk

---

## Phase 5: Spec Drift Detection

**Goal**: Detect deviations between the functional specification and the actual implementation

**Runs unless**: `--kg-only`

**Actions**:

1. **Extract spec claims**:
   - Read the resolved specification file
   - Extract all acceptance criteria
   - List all user stories, functional requirements, and non-functional requirements

2. **Extract implementation reality**:
   - Read all completed tasks (status: completed)
   - Extract acceptance criteria from each completed task
   - Identify what was actually implemented vs what was planned

3. **Analyze decision-log.md** (if exists):
   - Read all DEC entries
   - Identify decisions that caused spec changes
   - Categorize each decision reference

4. **Compare and classify deviations**:

   - **Acceptance criteria comparison**:
     - Criteria in spec but NOT implemented → Unmet requirement
     - Criteria implemented but NOT in spec → Scope expansion
     - Criteria modified during implementation → Requirement refinement

   - **Decision-log cross-reference**:
     - DEC entries not reflected in spec → Undocumented deviation
     - Scope changes documented but not applied → Pending update

5. **Generate deviation report**:
   ```markdown
   ## Deviation Analysis

   ### Scope Expansions (added beyond original spec)
   - Added pagination to search results (DEC-003)
   - Added filtering by rating

   ### Requirement Refinements (changed from original spec)
   - Changed "instant search" to "search with caching" (DEC-005)

   ### Scope Reductions (removed during implementation)
   - Dropped "search by proximity" feature (DEC-007)

   ### Unmet Requirements (in spec but not implemented)
   - Export results as CSV — no task covers this
   ```

---

## Phase 6: Spec Update Proposal & Approval

**Goal**: Present proposed spec updates to the user and get approval

**Runs unless**: `--kg-only`
**Skipped if**: No deviations detected in Phase 5 (log "Spec and implementation are aligned, no drift detected" and skip to Phase 8)

**Actions**:

1. **Generate diff-style proposal** showing:
   - **Additions** (+): New content to add to spec
   - **Modifications** (~): Content to change
   - **Deletions** (-): Content to remove or mark as deferred

2. **Categorize changes by impact**:
   - **Scope expansion**: Features added beyond original spec
   - **Requirement refinement**: Clarifications or corrections
   - **Scope reduction**: Features dropped or deferred

3. **Present proposal to user via AskUserQuestion**:
   ```
   Deviation Summary:
   - N scope expansions
   - N requirement refinements
   - N scope reductions
   - N unmet requirements

   Options:
   - "Approve all" — Apply all spec changes AND create missing tasks
   - "Spec only" — Apply spec changes, skip task creation
   - "Review each" — Review each change individually
   - "Skip" — Don't update spec or create tasks
   ```

4. **If user chooses "Approve all"**:
   - Proceed to Phase 7 (apply all spec updates + create missing tasks)

5. **If user chooses "Spec only"**:
   - Proceed to Phase 7 (apply spec updates only, skip task creation)

6. **If user chooses "Review each"**:
   - Present each deviation category one by one
   - For each: show original vs proposed change, ask approve/reject
   - Track which changes need task creation
   - Proceed to Phase 7 with approved subset

7. **If user chooses "Skip"**:
   - Log pending deviations for future reference
   - Skip to Phase 9 (Summary)

---

## Phase 7: Apply Updates & Task Creation

**Goal**: Apply approved spec updates and optionally create missing tasks

**Runs unless**: `--kg-only` or user chose "Skip" in Phase 6

### 7.1 Backup Original Spec

1. Create backup next to the resolved spec file:
   ```bash
   cp [resolved-spec-file] [resolved-spec-file].backup
   ```

### 7.2 Apply Spec Changes

2. For each approved change:
   - **Scope expansions**: Add new sections/content to spec
   - **Requirement refinements**: Update existing content
   - **Scope reductions**: Remove content or mark as deferred with reason

3. **Add Revision History section** at end of spec (append to existing if present):
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

### 7.3 Automatic Task Creation

**Runs only if**: User chose "Approve all" in Phase 6 (or approved individual tasks in "Review each" mode)

5. **Analyze deviations for task creation**:
   - For each **scope expansion**: Create task for new feature/component
   - For each **requirement refinement**: Create task if it requires implementation changes
   - For each **scope reduction**: Mark related tasks as superseded (no new task)
   - Skip refinements that don't require new implementation (e.g., documentation clarifications)

6. **Generate task proposals**:
   ```markdown
   ## Task Creation Proposals

   | Deviation | Suggested Task Title | Priority |
   |-----------|---------------------|----------|
   | Scope Expansion: Pagination | Implement pagination for search results | High |
   | Scope Expansion: Rating filter | Add rating filter to search | Medium |
   ```

7. **If user chose "Approve all"**: Create all proposed tasks automatically
   **If user chose "Review each"**: Create only individually approved tasks

8. **For each task to create**, follow this pattern:
   - Generate task title from deviation
   - Generate task description from deviation context
   - Generate acceptance criteria from deviation details
   - Determine dependencies from related existing tasks
   - Read task index to get next task ID
   - Create task file using standard template:
     ```markdown
     ---
     id: TASK-XXX
     title: "[Title]"
     status: pending
     priority: high|medium|low
     dependencies: [TASK-YYY]
     provides:
       - file: ""
         symbols: []
         type: ""
     ---

     # [Title]

     ## Description
     [From deviation context]

     ## Acceptance Criteria
     - [ ] [From deviation details]

     ## Technical Context
     [From KG relevant patterns]
     ```
   - Add to task index
   - Show created task with implementation command

9. **For scope reductions**: Find tasks that implement dropped features and update their status to "superseded" with reason

---

## Phase 8: Sync Verification

**Goal**: Verify that all tasks still map correctly to the updated specification

**Runs unless**: `--kg-only`

**Actions**:

1. **Re-validate task list**:
   - Check if all tasks still map to updated spec sections
   - Identify tasks with obsolete references
   - Flag tasks whose acceptance criteria conflict with updated spec

2. **Generate verification report**:
   ```markdown
   ## Sync Verification

   ### Tasks Still Valid
   - TASK-001: User registration
   - TASK-002: Login functionality

   ### Tasks Needing Update
   - TASK-003: References removed "proximity search" — needs revision

   ### Superseded Tasks
   - TASK-005: Marked as superseded (scope reduction)
   ```

3. **If tasks need updates**:
   - Ask via AskUserQuestion:
     - "Update affected tasks now?" — apply automatic fixes
     - "Review manually later" — log for future reference

---

## Phase 9: Summary

**Goal**: Generate comprehensive summary of all changes

**Always runs**.

**Actions**:

1. Mark all todos complete

2. Generate summary report:
   ```markdown
   ## Spec Sync Summary

   **Spec**: docs/specs/[ID]/
   **Timestamp**: [ISO timestamp]
   **Mode**: full | kg-only | code-only

   ### Knowledge Graph Updates (if applicable)
   - Added N new provides entries
   - Updated N existing entries
   - Verified N components
   - Marked N entries as stale

   ### Task Enrichment (if applicable)
   - Enriched TASK-XXX technical context
   - Updated TASK-YYY provides section

   ### Drift Detection (if applicable)
   - N scope expansions
   - N requirement refinements
   - N scope reductions
   - N unmet requirements

   ### Spec Updates (if applicable)
   - Spec updated: Yes/No
   - Revision history entries added: N
   - Backup created: [path]

   ### Tasks Created (if applicable)
   - TASK-XXX: [title] (new)
   - TASK-YYY: [title] (new)

   ### Sync Verification (if applicable)
   - All tasks valid: Yes/No
   - Tasks needing manual review: N

   ### Files Modified
   - knowledge-graph.json
   - tasks/TASK-001.md
   - YYYY-MM-DD--feature-name.md
   - YYYY-MM-DD--feature-name.md.backup (new)
   ```

---

## Integration Points

### In spec-to-tasks (after codebase analysis)

```markdown
## Phase 3.5: Update Knowledge Graph

After codebase analysis completes, automatically update KG:

/developer-kit-specs:specs.sync [spec-folder] --kg-only

This persists agent discoveries into knowledge-graph.json for future reuse.
```

### In task-implementation (after task completion)

```markdown
## T-6.5: Update Spec Context

After task completion and verification, update spec context:

/developer-kit-specs:specs.sync [spec-folder] --after-task=[TASK-ID]

This updates:
- Knowledge Graph with new provides entries
- Task file with implementation details
- Technical context for dependent tasks
```

### In task-implementation (when deviation detected)

```markdown
## T-6.6: Spec Deviation Check

When spec deviation is detected during implementation:

/developer-kit-specs:specs.sync [spec-folder] --code-only --after-task=[TASK-ID]

This detects and proposes spec updates without touching the KG.
```

### Manual Triggers

Run spec-sync manually when:
- After completing several tasks to sync all context
- Before starting a new feature phase to verify context is current
- When `decision-log.md` has many entries not reflected in spec
- After significant refactoring
- After a normal chat session that used `docs/specs/[id]/` as implementation context and clarified, narrowed, or expanded what should be built
- When context seems stale or inconsistent

### KG Freshness Indicators

- **< 7 days**: Fresh, use cached analysis
- **7-30 days**: Getting stale, consider refresh
- **> 30 days**: Old, recommend full refresh

---

## Error Handling

### Spec Folder Not Found
- **Behavior**: Error and ask for correct path
- **Message**: "Spec folder not found at [path]. Please provide a valid path with --spec="

### Knowledge Graph Corrupted
- **Behavior**: Backup corrupted file, create new structure
- **Message**: "KG corrupted, backed up to knowledge-graph.json.corrupt, creating new."

### Task File Not Found (with --after-task)
- **Behavior**: Warning, continue with KG update only
- **Message**: "Task [TASK-XXX] not found. Continuing with full scan."

### No Deviations Detected
- **Behavior**: Log alignment, skip Phase 6-7, go to Phase 8
- **Message**: "Spec and implementation are aligned. No drift detected."

### File Write Failure
- **Behavior**: Log error, continue with remaining phases, report in summary
- **Message**: "Failed to write [file]: [error]"

### No Spec File Found
- **Behavior**: Error and stop
- **Message**: "No specification file found in [folder]. Expected YYYY-MM-DD--*.md or *-specs.md."

---

## Examples

### Example 1: Full Sync After Implementation

```bash
/developer-kit-specs:specs.sync docs/specs/001-hotel-search/
```

Output:
```
Spec Sync — docs/specs/001-hotel-search/
Mode: full sync

Phase 2: Gap Analysis
- 2 new components discovered in codebase
- 1 task needs technical context update
- Extracted 5 symbols from 3 files

Phase 3: Knowledge Graph Updated
- Added 2 provides entries
- Updated metadata

Phase 4: Task Enrichment
- Enriched TASK-003 technical context

Phase 5: Drift Detection
- 1 scope expansion: Pagination added (DEC-003)
- 1 requirement refinement: Search timeout set to 5s (DEC-004)

Phase 6: Proposal
[AskUserQuestion] 1 scope expansion, 1 refinement
→ User approved all

Phase 7: Applied
- Spec updated with revision history (2 entries)
- Backup: 2026-03-15--hotel-search.md.backup
- Created TASK-009: Implement pagination for search results

Phase 8: Verification
- All tasks valid
```

### Example 2: KG-Only After spec-to-tasks

```bash
/developer-kit-specs:specs.sync docs/specs/001-hotel-search/ --kg-only
```

Output:
```
Spec Sync — docs/specs/001-hotel-search/
Mode: kg-only

Phase 2: Gap Analysis
- 3 new components discovered
- Extracted 8 symbols from 5 files

Phase 3: Knowledge Graph Updated
- Added 3 provides entries
- Updated 1 component entry

Phase 4: Task Enrichment
- Enriched TASK-001, TASK-002 technical context
```

### Example 3: Code-Only Drift Check

```bash
/developer-kit-specs:specs.sync docs/specs/001-hotel-search/ --code-only
```

Detects spec-to-code deviations and proposes spec updates, without touching the Knowledge Graph or task files.

---

## Todo Management

Maintain todo list throughout execution:

```
[ ] Phase 1: Discovery
[ ] Phase 2: Codebase Extraction & Gap Analysis
[ ] Phase 3: Knowledge Graph Update
[ ] Phase 4: Task Enrichment
[ ] Phase 5: Spec Drift Detection
[ ] Phase 6: Spec Update Proposal & Approval
[ ] Phase 7: Apply Updates & Task Creation
[ ] Phase 8: Sync Verification
[ ] Phase 9: Summary
```

Mark phases as skipped when not applicable to current mode.
