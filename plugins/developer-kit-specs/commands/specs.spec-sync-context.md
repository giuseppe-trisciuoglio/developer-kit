---
description: "Synchronizes specification context (WHAT: syncs Knowledge Graph JSON, Task files, and Codebase state) after implementations. Maintains technical context alignment. Use WHEN: after spec-to-tasks or task-implementation workflows complete."
argument-hint: "[ --spec=\"docs/specs/XXX-feature\" ] [--update-kg-only] [ --task=\"docs/specs/XXX-feature/tasks/TASK-XXX.md\" ] [--dry-run]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, TodoWrite
model: inherit
---

# Spec Sync Context - Technical Context Synchronization

Synchronizes the specification context (Knowledge Graph, Tasks, Codebase) to maintain technical consistency after implementations.

## Overview

This command solves three main problems in the specification workflow:

1. **Inconsistent Technical Context**: Tasks lose technical context or don't reflect actual patterns used in the codebase
2. **Specs-Tasks Misalignment**: User request, specification, and tasks are not aligned
3. **Obsolete Knowledge Graph**: The knowledge-graph.json is not updated after implementations

### Workflow Position

```
Idea → Specs → Tasks → Implementation → Spec Sync Context (this)
                ↑         ↓              ↓
                └─────────────────────────────────────┘
                    Continuously sync context
```

## Usage

```bash
# Basic usage - update context for a spec folder
/developer-kit-specs:specs.spec-sync-context docs/specs/001-hotel-search-aggregation/

# Update KG only (used by spec-to-tasks after codebase analysis)
/developer-kit-specs:specs.spec-sync-context docs/specs/001-hotel-search-aggregation/ --update-kg-only

# Update after task completion (used by task-implementation)
/developer-kit-specs:specs.spec-sync-context docs/specs/001-hotel-search-aggregation/ --task=TASK-001

# Dry run - show what would be changed without making changes
/developer-kit-specs:specs.spec-sync-context docs/specs/001-hotel-search-aggregation/ --dry-run
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `spec-folder` | No | Path to spec folder (default: current working directory) |
| `--update-kg-only` | No | Only update Knowledge Graph, skip task enrichment |
| `--task` | No | Update context after specific task completion |
| `--dry-run` | No | Show planned changes without executing them |

## Current Context

If `--spec` is omitted, the spec folder is auto-detected from the current git branch:

```bash
branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
spec_folder=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
```

If no matching spec folder is found for the current branch, stop and inform the user.

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
   - [list of modified files]
   ```

2. **Log results**:
   - Output summary to console
   - Append to `docs/specs/[ID]/decision-log.md` if it exists
