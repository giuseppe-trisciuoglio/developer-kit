---
description: "Maintains specification context quality (Knowledge Graph, Tasks, Codebase) by synchronizing technical context after implementations. Syncs KG, tasks, and codebase. Automatically integrated into spec-to-tasks and task-implementation workflows."
argument-hint: "[ spec-folder ] [--update-kg-only] [--task=TASK-XXX] [--dry-run]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, TodoWrite
model: inherit
---

# Specs Quality - Context Improvement

Maintains the quality and consistency of specification context by synchronizing Knowledge Graph, Tasks, and Codebase.

## Overview

This command solves three main problems in the specification workflow:

1. **Inconsistent Technical Context**: Tasks lose technical context or don't reflect actual patterns used in the codebase
2. **Specs-Tasks Misalignment**: User request, specification, and tasks are not aligned
3. **Obsolete Knowledge Graph**: The knowledge-graph.json is not updated after implementations

### Workflow Position

```
Idea → Specs → Tasks → Implementation → Specs Quality Update (this)
                ↑         ↓              ↓
                └─────────────────────────────────────┘
                    Continuously sync context
```

## Usage

```bash
# Basic usage - update context for a spec folder
/developer-kit:devkit.spec-quality docs/specs/001-hotel-search-aggregation/

# Update KG only (used by spec-to-tasks after codebase analysis)
/developer-kit:devkit.spec-quality docs/specs/001-hotel-search-aggregation/ --update-kg-only

# Update after task completion (used by task-implementation)
/developer-kit:devkit.spec-quality docs/specs/001-hotel-search-aggregation/ --task=TASK-001

# Dry run - show what would be changed without making changes
/developer-kit:devkit.spec-quality docs/specs/001-hotel-search-aggregation/ --dry-run
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `spec-folder` | No | Path to spec folder (default: current working directory) |
| `--update-kg-only` | No | Only update Knowledge Graph, skip task enrichment |
| `--task` | No | Update context after specific task completion |
| `--dry-run` | No | Show planned changes without executing them |

## Core Principles

- **Incremental updates**: Only update what has changed, don't rewrite everything
- **Bidirectional sync**: Both KG → Tasks and Tasks → KG alignment
- **Traceability**: All changes are logged and reported
- **Non-destructive**: Preserve manual edits and annotations
- **Codebase-first**: Actual implementation is source of truth

---

## Phase 1: Discovery

**Goal**: Identify spec folder and gather current context state

**Actions**:

1. Create todo list with all phases
2. Parse arguments:
   - Extract `spec-folder` path
   - Detect flags: `--update-kg-only`, `--task=TASK-XXX`, `--dry-run`
3. Determine spec folder:
   - If argument provided: use it
   - If no argument: detect from current working directory
   - Validate path contains spec files
4. Read current state:
   - Check if `knowledge-graph.json` exists
   - List all task files in `tasks/` directory
   - Read `user-request.md` if exists
5. Detect language from existing tasks or files

---

## Phase 2: Gap Analysis

**Goal**: Identify discrepancies between KG, tasks, and actual codebase

**Actions**:

1. **Knowledge Graph vs Codebase**:
   - For each component in KG: check if file actually exists
   - For each API in KG: check if endpoint exists
   - Find new files not documented in KG

2. **Tasks vs Knowledge Graph**:
   - Check if task technical context matches KG patterns
   - Identify tasks referencing non-existent components
   - Find tasks missing expected technical details

3. **Requirements Traceability**:
   - Compare user-request.md with task descriptions
   - Identify requirements mentioned but not in tasks
   - Find tasks without clear requirement origin

4. **Generate gap report**:
   ```markdown
   ## Gap Analysis Report

   ### Missing in KG
   - NewFile.java (discovered in codebase)

   ### Outdated in KG
   - OldComponent.java (file removed)

   ### Tasks Needing Update
   - TASK-003: References outdated pattern
   - TASK-007: Missing technical context

   ### Orphaned Requirements
   - User request mentions "X" but no task covers it
   ```

---

## Phase 3: Extraction

**Goal**: Extract structured information from implemented code

**Actions**:

1. **If --task=TASK-XXX specified**:
   - Read task file to identify implemented files
   - Extract from `provides` section or `Files to Create`
   - Validate files exist in codebase

2. **If no specific task**:
   - Scan codebase for files matching spec patterns
   - Use Glob to find recently modified files

3. **Extract symbols from files**:
   - For each file, use appropriate extraction method based on language
   - Java: Grep for `class|interface|enum` declarations
   - TypeScript: Grep for `class|interface|function|const` declarations
   - Python: Grep for `class|def` declarations

4. **Classify by type**:
   - Infer from directory structure: `/domain/entity/` → entity
   - Infer from annotations: `@RestController` → controller
   - Default to generic type if unclear

5. **Build provides objects**:
   ```json
   {
     "task_id": "TASK-001",
     "file": "src/main/java/.../Search.java",
     "symbols": ["Search", "SearchStatus"],
     "type": "entity",
     "implemented_at": "2026-03-15T10:30:00Z"
   }
   ```

---

## Phase 4: Knowledge Graph Update

**Goal**: Update knowledge-graph.json with new findings

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
   - Add new provides from Phase 3
   - Check for duplicates by task_id + file
   - Update `implemented_at` for existing entries
   - Mark entries as verified

3. **Update components** (if new discovered):
   - Add to appropriate category (controllers, services, etc.)
   - Preserve existing entries

4. **Update APIs** (if new endpoints discovered):
   - Scan for REST annotations
   - Add to internal/external as appropriate

5. **Update metadata**:
   - Set `updated_at` to current ISO timestamp
   - Add entry to `analysis_sources`: `{"agent": "spec-quality", "timestamp": "..."}`

6. **Write updated KG**:
   - If `--dry-run`: Show diff instead of writing
   - Otherwise: Write to `docs/specs/[ID]/knowledge-graph.json`

---

## Phase 5: Task Enrichment

**Goal**: Update task files with improved technical context

**Skip if**: `--update-kg-only` flag is set

**Actions**:

1. **Identify tasks needing update** (from Phase 2 gap analysis)

2. **For each task file**:
   - Read current content
   - Parse YAML frontmatter
   - Identify "Technical Context" section

3. **Enrich technical context** with KG data:
   - Add relevant patterns from KG
   - Reference existing components to integrate with
   - Document APIs to use/extend
   - Note conventions to follow

4. **Update provides section** (if task was implemented):
   - Add or update `provides:` array in frontmatter
   - Include file paths, symbols, types

5. **Preserve manual content**:
   - Don't overwrite custom notes
   - Preserve acceptance criteria
   - Keep manual edits to descriptions

6. **Write updated task file**:
   - If `--dry-run`: Show proposed changes
   - Otherwise: Write back to task file


## Phase 5.5: Spec Document Drift Detection

**Goal**: Detect drift between specification and implemented reality

**Actions**:

1. **Resolve and read the spec file** (`YYYY-MM-DD--feature-name.md` preferred, legacy `*-specs.md` supported):
   - Extract all acceptance criteria from the spec
   - List all user stories and requirements

2. **Read decision-log.md** if exists:
   - Extract all DEC entries with implementation deviations
   - Identify scope changes, additions, removals

3. **Read completed tasks**:
   - Scan tasks/ directory for completed tasks (status: completed)
   - Extract acceptance criteria from each completed task
   - Identify what was actually implemented

4. **Compare and identify drift**:
   - Criteria in spec but NOT implemented → Unmet requirements
   - Features implemented but NOT in spec → Scope expansion
   - Modified implementations → Requirement refinement
   - Documented deviations in decision-log → Explained drift

5. **Generate drift report**:
   - If drift detected:
     - Add to report: "Spec Drift Detected: N criteria diverged from implementation. Consider running `/devkit.spec-sync [spec-folder]` to update specification."
     - List specific drift items with references to DEC entries
   - If no drift:
     - Log: "Spec and implementation are aligned, no drift detected"
---

## Phase 6: Report Generation

**Goal**: Generate summary of all changes made

**Actions**:

1. **Generate change summary**:
   ```markdown
   ## Specs Quality Update Summary

   **Spec**: docs/specs/[ID]/
   **Timestamp**: [ISO timestamp]
   **Mode**: [full|kg-only|task=TASK-XXX|dry-run]

   ### Knowledge Graph Updates
   - Added 3 new provides entries
   - Updated 2 existing entries
   - Verified 15 components

   ### Task Updates
   - Enriched TASK-001 technical context
   - Enriched TASK-003 technical context
   - Added provides to TASK-007

   ### Gap Analysis Results
   - All requirements covered
   - Technical context synchronized

   ### Files Modified
   - knowledge-graph.json
   - tasks/TASK-001.md
   - tasks/TASK-003.md
   ```

2. **If dry-run mode**: Include detailed diff preview

3. **Present report to user**

---

## Integration Points

### In spec-to-tasks Command

Add to `spec-to-tasks` Phase 3.5 (after Codebase Analysis):

```markdown
## Phase 3.5: Update Knowledge Graph

After codebase analysis completes, automatically update KG:

/developer-kit:devkit.spec-quality [spec-folder] --update-kg-only

This persists agent discoveries into knowledge-graph.json for future reuse.
```

### In task-implementation Command

Add to `task-implementation`, after T-6 (Task Completion):

```markdown
## T-6.5: Update Specs Quality

After task completion and verification, update spec context:

/developer-kit:devkit.spec-quality [spec-folder] --task=[TASK-ID]

This updates:
- Knowledge Graph with new provides entries
- Task file with implementation details
- Technical context for dependent tasks
```

---

## Error Handling

### Spec Folder Not Found
- **Behavior**: Error and ask for correct path
- **Message**: "Spec folder not found at [path]. Please provide valid path."

### Knowledge Graph Corrupted
- **Behavior**: Backup corrupted file, create new structure
- **Message**: "KG corrupted, backed up to [path].kg.backup, creating new."

### Task File Not Found (with --task)
- **Behavior**: Warning, continue with KG update only
- **Message**: "Task TASK-XXX not found, updating KG only."

### File Write Failure
- **Behavior**: Log error, report in summary
- **Message**: "Failed to write [file]: [error]"

---

## Best Practices

### When to Run Manually
- After completing several tasks to sync context
- Before starting new implementation to verify context
- After significant refactoring
- When context seems stale or inconsistent

### Automation Frequency
- **After each task**: Recommended for accurate tracking
- **Batch updates**: Acceptable for minor tasks
- **Before releases**: Always run to ensure context is current

### KG Freshness Indicators
- **< 7 days**: Fresh, use cached analysis
- **7-30 days**: Getting stale, consider refresh
- **> 30 days**: Old, recommend full refresh

---

## Examples

### Example 1: Full Context Update

```bash
/developer-kit:devkit.spec-quality docs/specs/001-hotel-search-aggregation/
```

Output:
```
Analyzing spec folder: docs/specs/001-hotel-search-aggregation/
Found knowledge-graph.json (3 days old)
Found 10 task files

Gap Analysis:
- 2 new components discovered
- 1 task needs technical context update

Updating Knowledge Graph...
✓ Added 2 provides entries
✓ Updated metadata

Updating Tasks...
✓ Enriched TASK-003 technical context

Summary:
- KG updated: 3 days ago → now
- Tasks enriched: 1
- Files modified: 2
```

### Example 2: Dry Run

```bash
/developer-kit:devkit.spec-quality docs/specs/001-hotel-search-aggregation/ --dry-run
```

Shows what would change without applying changes.

### Example 3: After Task Implementation

```bash
/developer-kit:devkit.spec-quality docs/specs/001-hotel-search-aggregation/ --task=TASK-001
```

Updates KG with provides from TASK-001 and enriches related tasks.

---

## Todo Management

Maintain todo list:

```
[ ] Phase 1: Discovery
[ ] Phase 2: Gap Analysis
[ ] Phase 3: Extraction
[ ] Phase 4: Knowledge Graph Update
[ ] Phase 5: Task Enrichment (skipped if --update-kg-only)
[ ] Phase 6: Report Generation
```

---

## Notes

- This command is designed to be **idempotent**: running multiple times produces same result
- Manual edits to task files are preserved whenever possible
- The Knowledge Graph is the single source of truth for technical context
- When in doubt, the actual codebase is the final authority
