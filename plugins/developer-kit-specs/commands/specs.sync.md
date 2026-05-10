---
description: "Synchronizes the specification with the implementation. Full sync updates Knowledge Graph, enriches tasks, and detects spec-to-code deviations. Use after task implementation or review to keep spec, tasks, and code aligned."
argument-hint: "[ --spec=docs/specs/XXX-feature ] [ --kg-only ] [ --code-only ] [ --after-task=TASK-XXX ] [ --dry-run ]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, TodoWrite
model: inherit
---

# Spec Synchronization

## Overview

Synchronizes the functional specification with implementation reality. This is the close-the-loop step of the workflow.

## Usage

```bash
# Full sync (recommended after task-implementation or task-review)
/developer-kit-specs:specs.sync docs/specs/001-feature/

# Sync after a specific task
/developer-kit-specs:specs.sync docs/specs/001-feature/ --after-task=TASK-003

# KG-only (lighter, used after spec-to-tasks codebase analysis)
/developer-kit-specs:specs.sync docs/specs/001-feature/ --kg-only

# Code drift detection only
/developer-kit-specs:specs.sync docs/specs/001-feature/ --code-only

# Preview changes
/developer-kit-specs:specs.sync docs/specs/001-feature/ --dry-run
```

## Modes

| Flag | What it does | When to use |
|------|-------------|-------------|
| (none) | Full sync: KG + task enrichment + code drift detection | Default after implementation |
| `--kg-only` | Update Knowledge Graph only | After spec-to-tasks, when codebase was analyzed |
| `--code-only` | Detect spec-to-code deviations only | When you suspect drift |
| `--dry-run` | Show what would change without writing | Review before applying |

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--spec` | No | Path to spec folder (e.g., docs/specs/XXX-feature) |
| `--kg-only` | No | Update Knowledge Graph only |
| `--code-only` | No | Detect spec-to-code deviations only |
| `--after-task` | No | Sync after a specific task (e.g., TASK-003) |
| `--dry-run` | No | Preview changes without writing |

## Examples

### Full Sync (Recommended)

```bash
/developer-kit-specs:specs.sync docs/specs/001-feature/
```

### Sync After a Specific Task

```bash
/developer-kit-specs:specs.sync docs/specs/001-feature/ --after-task=TASK-003
```

### KG-Only Mode

```bash
/developer-kit-specs:specs.sync docs/specs/001-feature/ --kg-only
```

### Code Drift Detection Only

```bash
/developer-kit-specs:specs.sync docs/specs/001-feature/ --code-only
```

### Preview Changes

```bash
/developer-kit-specs:specs.sync docs/specs/001-feature/ --dry-run
```

## Workflow Position

```
brainstorm → spec-to-tasks → task-implementation → task-review → sync (this) → done
                                                    ↑              ↓
                                              optionally --kg-only after spec-to-tasks
```

## Phase 1: Discovery

1. Parse `$ARGUMENTS` via script:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/parse_args.py" "$ARGUMENTS"
   ```
   Read the JSON output and extract:
   - `spec` → spec folder path
   - `flags` → detect `--kg-only`, `--code-only`, `--dry-run`
   - `task` → extract from `--after-task` if present
2. If `spec` is null, auto-detect from git branch:
   ```bash
   branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
   spec=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
   ```
3. Load `knowledge-graph.json` if present
4. Load task files from `tasks/` subdirectory

## Phase 2: Knowledge Graph Sync (runs unless `--code-only`)

1. Scan codebase for patterns defined in spec
2. Extract `provides`/`expects` from implemented files
3. Update `knowledge-graph.json`:
   - Add discovered components
   - Update interfaces
   - Mark stale entries
4. Enrich task files with technical context from KG
5. If `--kg-only`: stop here, generate summary report

## Phase 3: Spec-to-Code Drift Detection (runs unless `--kg-only`)

1. Read the functional specification
2. Read implemented files referenced by completed tasks
3. Compare spec claims vs code reality:
   - Acceptance criteria implemented?
   - File structure matches?
   - API signatures consistent?
4. Identify deviations (drift)
5. If drift found and not `--dry-run`:
   - Update `decision-log.md` with deviation entries
   - Propose spec updates
   - Update spec document
6. If `--code-only`: stop here, generate drift report

## Phase 4: Summary Report

Always runs. Reports:
- KG entries updated / added / stale
- Tasks enriched
- Drift items detected (if any)
- Spec updates applied (if any)
- Files modified
