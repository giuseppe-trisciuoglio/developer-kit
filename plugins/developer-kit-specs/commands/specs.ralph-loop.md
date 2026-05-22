---
description: "Ralph Loop orchestrator for spec-driven development (WHAT: runs the SDD state machine one step at a time). Use WHEN: automating the implement-review-fix-sync cycle for specification tasks."
argument-hint: '[--wait|--background] [--spec <path>] [--action start|loop|next|status] [--from-task <id>] [--to-task <id>]'
allowed-tools: Read, Glob, Grep, Bash(python3:*), Bash(git:*), AskUserQuestion
---

## Overview

The Ralph Loop applies the "Ralph Wiggum as a Software Engineer" technique to specification-driven development. It solves context window explosion by executing **one step per invocation**, persisting state in `fix_plan.json`.

State machine: `init → choose_task → implementation → review → [fix | escalate] → cleanup → sync → update_done → (loop)`

**States**:
- `fix`: Normal review feedback — implementation needs fixes (Ralph Loop)
- `escalate`: Design-level problem detected — requires returning to spec-to-tasks (Circuit Breaker)
- **Ralph Loop Circuit Breaker**: If the same issue persists for 3+ iterations, force `escalate` even if review says `needs_fix`

**State transitions**:
```
review_status = passed    → cleanup
review_status = needs_fix → fix (if iteration < 3) OR escalate (if iteration >= 3)
review_status = partial   → fix (if iteration < 3) OR escalate (if iteration >= 3)
review_status = escalate  → escalate (always, regardless of iteration count)
```

## Usage

```bash
# Initialize a new loop
/developer-kit-specs:specs.ralph-loop --action=start --spec=docs/specs/001-feature/ --from-task=TASK-001 --to-task=TASK-010

# Run one step (execute shown command, then run loop again)
/developer-kit-specs:specs.ralph-loop --action=loop --spec=docs/specs/001-feature/

# Advance state after executing the shown command
/developer-kit-specs:specs.ralph-loop --action=next --spec=docs/specs/001-feature/

# Check status
/developer-kit-specs:specs.ralph-loop --action=status --spec=docs/specs/001-feature/
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--action` | Yes | Action to perform: `start`, `loop`, `next`, `status` |
| `--spec` | No | Path to spec folder (auto-detected from git branch if omitted) |
| `--from-task` | No | Starting task ID (for `start` action) |
| `--to-task` | No | Ending task ID (for `start` action) |
| `--wait` | No | Run in foreground, wait for results |
| `--background` | No | Run in background without prompting |

## Current Context

If `--spec` is omitted, the spec folder is auto-detected from the current git branch:

```bash
branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
spec_folder=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
```

If no matching spec folder is found for the current branch, stop and inform the user.

## Execution mode rules

- If the raw arguments include `--wait`, run in the foreground without asking.
- If the raw arguments include `--background`, run in the background without asking.
- Otherwise, use `AskUserQuestion` exactly once with two options, putting the recommended option first and suffixing its label with `(Recommended)`:
  - `Run in background (Recommended)`
  - `Wait for results`

## Foreground flow

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/main.py $ARGUMENTS
```

Return the command stdout verbatim.

## Background flow

Launch with `Bash` in the background:

```typescript
Bash({
  command: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/main.py $ARGUMENTS`,
  description: "Ralph Loop",
  run_in_background: true
})
```

After launching, tell the user: "Ralph Loop started in the background."

## Examples

```bash
# Initialize
/developer-kit-specs:specs.ralph-loop --action=start --spec=docs/specs/001-feature/ --from-task=TASK-001 --to-task=TASK-010

# Run one step
/developer-kit-specs:specs.ralph-loop --action=loop --spec=docs/specs/001-feature/

# Advance state after executing the shown command
/developer-kit-specs:specs.ralph-loop --action=next --spec=docs/specs/001-feature/

# Check status
/developer-kit-specs:specs.ralph-loop --action=status --spec=docs/specs/001-feature/
```
