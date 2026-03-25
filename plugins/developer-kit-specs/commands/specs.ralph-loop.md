---
description: "Ralph Wiggum automation loop for SDD. State machine: one invocation = one step. Use --action=start|loop|status|resume with --spec path."
argument-hint: "--action=[start|loop|status|resume] --spec=\"docs/specs/XXX-feature\" [ --from-task=\"TASK-036\" ] [ --to-task=\"TASK-041\" ]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
model: inherit
---

# Ralph Loop

**CRITICAL**: This command executes a state machine. Read the `ralph-loop` skill at `plugins/developer-kit-specs/skills/ralph-loop/SKILL.md` and follow its state machine logic exactly.

Do NOT generate shell scripts. Do NOT create prompt.md files. Do NOT interpret this as a tutorial to plan from scratch. Read and follow the skill's hardcoded logic.

## Overview

State machine for SDD task automation. One `/loop` = one step. State persisted in `fix_plan.json`. Claude Code interprets this command as executable logic — read the skill for hardcoded behavior.

## Usage

| Action | Purpose |
|--------|---------|
| `--action=start` | Initialize fix_plan.json, apply task range filter |
| `--action=loop` | Read state, execute ONE step, update fix_plan.json, stop |
| `--action=status` | Read fix_plan.json, print progress table |
| `--action=resume` | Verify state, continue with `--action=loop` |

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--action` | Yes | `start`, `loop`, `status`, or `resume` |
| `--spec` | Yes | Spec folder path (e.g. `docs/specs/001-feature/`) |
| `--from-task` | No | Start of task range (e.g. `TASK-036`) |
| `--to-task` | No | End of task range (e.g. `TASK-041`) |

## Execution Rules

1. Read `plugins/developer-kit-specs/skills/ralph-loop/SKILL.md` for state machine logic
2. Read current state from `docs/specs/[id]/_ralph_loop/fix_plan.json`
3. Execute exactly ONE step based on current state
4. Update `fix_plan.json` with next state
5. Print one-line progress and STOP

**No multi-step**: Do NOT combine implementation + review + sync in one call.
**No script generation**: Do NOT generate shell scripts or prompt files.
**One thing per loop**: Execute only the current step, save state, stop.

## Examples

```bash
# Initialize for TASK-036 → TASK-041
/developer-kit-specs:specs.ralph-loop --action=start --spec=docs/specs/001-feature/ --from-task=TASK-036 --to-task=TASK-041

# Run one step
/developer-kit-specs:specs.ralph-loop --action=loop --spec=docs/specs/001-feature/

# Check status
/developer-kit-specs:specs.ralph-loop --action=status --spec=docs/specs/001-feature/

# Resume
/developer-kit-specs:specs.ralph-loop --action=resume --spec=docs/specs/001-feature/
```
