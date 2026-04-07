---
description: "Initializes specification-driven development directory structure. Creates the docs/specs/ folder hierarchy. Run once per project before using other specs commands."
argument-hint: "[ --force ]"
allowed-tools: Read, Write, Bash, Grep, Glob, TodoWrite
model: inherit
---

# Specs Initialization

Initializes the specification-driven development infrastructure in the current project.

## Overview

This command prepares a project for specification-driven development by creating the `docs/specs/` directory structure.

**Note**: Task status management is now handled automatically by Claude Code hooks. No manual script installation required.

**Prerequisite**: None - this is the first command to run

**Output**: 
- Directory structure: `docs/specs/`
- Ready for specifications and tasks

## Usage

```bash
# Initialize specs in current project
/specs:init

# Force re-create (if directory exists)
/specs:init --force
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--force` | No | Overwrite existing structure if present |

## Process

### Phase 1: Check Existing Setup

1. Check if `docs/specs/` exists
2. If present and `--force` not set → confirm with user
3. If not present → create directory structure

### Phase 2: Create Directory Structure

```bash
mkdir -p docs/specs/
```

### Phase 3: Verification

1. Verify directory created successfully:
   ```bash
   ls -la docs/specs/
   ```

2. Confirm ready for specs workflow

### Phase 4: Summary

Report what was done:
- ✅ Directory structure created
- ✅ Ready for specifications

Show example next steps:
```bash
# Create your first specification
/specs:brainstorm "My Feature"

# Or if specs already exist
/specs:spec-to-tasks docs/specs/001-my-feature/
```

## Directory Structure After Init

```
docs/specs/
├── architecture.md        # Project architecture (optional, created on demand)
├── ontology.md            # Domain glossary (optional, created on demand)
└── [specification folders]  # Created by /specs:brainstorm or /specs:spec-to-tasks
    ├── 2026-03-07--feature-name.md
    ├── tasks/
    │   ├── TASK-001.md
    │   └── TASK-002.md
    └── traceability-matrix.md
```

## Notes

- This command is safe to run multiple times (idempotent with `--force`)
- Task frontmatter is auto-managed by hooks - no manual setup needed
- Simply edit task files and checkboxes to trigger automatic status updates

## Integration with Other Commands

Other specs commands will:
1. Create specifications in `docs/specs/`
2. Generate tasks with automatic frontmatter
3. Hooks auto-update task status when files are modified
4. No manual status management required

## Auto-Status Feature

Task status updates automatically when you:
- Check acceptance criteria boxes → Status becomes `implemented`
- Check DoD boxes → Status becomes `reviewed`  
- Add cleanup summary → Status becomes `completed`

The hooks handle all frontmatter updates including dates. Just focus on the work, not the metadata.
