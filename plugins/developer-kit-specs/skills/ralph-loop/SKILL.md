---
name: ralph-loop
description: "Ralph Wiggum-inspired automation loop for specification-driven development. Use when: user runs /loop command, user asks to automate task implementation, user wants to iterate through spec tasks step-by-step, or user wants to run development workflow automation with context window management. One /loop invocation = one step. State machine: init → choose_task → implementation → review → sync → update_done. Supports --from-task and --to-task for task range filtering. State persisted in fix_plan.json."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
---

# Ralph Loop — State Machine

## Overview

The Ralph Loop applies Geoffrey Huntley's "Ralph Wiggum as a Software Engineer" technique to specification-driven development. It uses a **state machine**: one `/loop` invocation = one step, state persisted in `fix_plan.json`.

**Key insight**: Implementing + reviewing + syncing in one invocation explodes the context window. Solution: each `/loop` does exactly one step, saves state to `fix_plan.json`, and stops. The next `/loop` resumes from saved state.

## When to Use

- User runs `/loop` command for recurring automation
- User asks to "automate implementation" or "run tasks in loop"
- User wants to "iterate through tasks step-by-step" or "run workflow automation"
- User needs "context window management" across multiple SDD commands
- User wants to "process task range" from TASK-N to TASK-M

## State Machine

```
fix_plan.json state machine:
┌─────────────────────────────────────────────────────────────┐
│  state: "init"                                            │
│    → --action=start: Initialize fix_plan.json              │
│    → Load tasks, apply task_range, save state             │
│                                                             │
│  state: "choose_task"                                      │
│    → Pick next pending task (within range, deps satisfied)│
│    → No tasks in range → state: "complete"               │
│    → Task found → state: "implementation"                │
│                                                             │
│  state: "implementation"                                  │
│    → Run /specs:task-implementation for current task     │
│    → On success → state: "review"                        │
│    → On failure → state: "failed"                        │
│                                                             │
│  state: "review"                                          │
│    → Run /specs:task-review for current task             │
│    → Issues found → state: "implementation" (retry ≤ 3)  │
│    → Clean → state: "sync"                               │
│                                                             │
│  state: "sync"                                            │
│    → Run /specs:spec-sync-with-code --after-task=[id]    │
│    → state: "update_done"                                │
│                                                             │
│  state: "update_done"                                     │
│    → Mark task done, re-evaluate dependencies            │
│    → state: "choose_task"                                │
│                                                             │
│  state: "complete" | "failed"                            │
│    → Print result, stop                                   │
└─────────────────────────────────────────────────────────────┘
```

## Instructions

1. Read `fix_plan.json` → get `state.step`
2. Execute exactly that step (see Step Handlers below)
3. Update `fix_plan.json` with next step
4. Print one-line progress: `Ralph Loop | Iteration N | Task TASK-NNN | Step: X | Range: TASK-N→TASK-M`
5. **STOP**

**CRITICAL**: Do NOT implement + review + sync in one invocation. One step only.

## Arguments

| Argument | Description |
|----------|-------------|
| `--action` | `start` (init), `loop` (run one step), `status`, `resume` |
| `--spec` | Spec folder path (e.g. `docs/specs/001-feature/`) |
| `--from-task` | Start of task range (e.g. `TASK-036`) |
| `--to-task` | End of task range (e.g. `TASK-041`) |

## Step Handlers

**`init`**: Create fix_plan.json with all tasks, apply range filter, set step to `choose_task`.

**`choose_task`**: Filter pending tasks by range, pick next (deps satisfied), set `current_task` and step to `implementation`. If no tasks in range → step `complete`.

**`implementation`**: Run `/specs:task-implementation --lang=[lang] --task="[file]"`. On success → step `review`. On failure → step `failed`.

**`review`**: Run `/specs:task-review --lang=[lang] "[file]"`. If issues → step `implementation` (retry, max 3). If clean → step `sync`.

**`sync`**: Run `/specs:spec-sync-with-code [spec-folder/] --after-task=[id]`. Then → step `update_done`.

**`update_done`**: Mark task done in fix_plan.json, increment iteration, set step to `choose_task`.

**`complete`** / **`failed`**: Print result and stop.

Update fix_plan.json with jq after each step:
```bash
jq '.state.step = "review" | .state.current_task = "TASK-036" | .state.last_updated = "2026-03-25T10:30:00"' \
  fix_plan.json > tmp.json && mv tmp.json fix_plan.json
```

## Examples

```bash
# Initialize for TASK-036 → TASK-041
/developer-kit-specs:specs.ralph-loop --action=start --spec=docs/specs/001-feature/ --from-task=TASK-036 --to-task=TASK-041

# Run one step
/developer-kit-specs:specs.ralph-loop --action=loop --spec=docs/specs/001-feature/

# With /loop (every 5 minutes)
/loop 5m /developer-kit-specs:specs.ralph-loop --action=loop --spec=docs/specs/001-feature/ --from-task=TASK-036 --to-task=TASK-041

# Check status
/developer-kit-specs:specs.ralph-loop --action=status --spec=docs/specs/001-feature/

# Resume
/developer-kit-specs:specs.ralph-loop --action=resume --spec=docs/specs/001-feature/
```

## Best Practices

- **One step per /loop**: Execute exactly one step, save state, stop
- **Trust the state**: Read from fix_plan.json, write to fix_plan.json
- **No context accumulation**: State lives in the file, not in context
- **Retry on review failure**: Max 3 retries before failing
- **Range filtering**: Always filter by `task_range`
- **Dependencies first**: Only pick tasks where all dependencies are done

## Constraints and Warnings

- **Context explosion**: Do NOT implement + review + sync in one invocation — context will overflow
- **Max retries**: Review failures retry implementation up to 3 times, then fail
- **Git state**: Ensure clean git state before starting; commit after each task completion
- **Test infrastructure**: Loop requires tests to pass — without tests, backpressure is ineffective

## CLI-Agnostic

See `references/state-machine.md` for complete state machine documentation.
See `references/multi-cli-integration.md` for Copilot CLI, Codex CLI, Gemini CLI, OpenCode CLI integration.
