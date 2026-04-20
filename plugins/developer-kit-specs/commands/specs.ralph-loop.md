---
name: ralph-loop
description: "Ralph Loop — spec-driven development orchestrator with foreground/background execution support. State machine: init → choose_task → implementation → review → fix → cleanup → sync → update_done."
argument-hint: '[--wait|--background] [--spec <path>] [--action start|loop|next|status] [--from-task <id>] [--to-task <id>]'
allowed-tools: Read, Glob, Grep, Bash(python3:*), Bash(git:*), AskUserQuestion
---

Run the Ralph Loop orchestrator for specification-driven development.

Raw slash-command arguments:
`$ARGUMENTS`

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

## Current Context

If `--spec` is omitted, the spec folder is auto-detected from the current git branch:

```bash
branch=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/current_branch.py")
spec_folder=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_spec_from_branch.py")
```

If no matching spec folder is found for the current branch, stop and inform the user.

## Usage examples

```bash
# Initialize
/specs:ralph-loop --action=start --spec=docs/specs/001-feature/ --from-task=TASK-001 --to-task=TASK-010

# Run one step
/specs:ralph-loop --action=loop --spec=docs/specs/001-feature/

# Advance state after executing the shown command
/specs:ralph-loop --action=next --spec=docs/specs/001-feature/

# Check status
/specs:ralph-loop --action=status --spec=docs/specs/001-feature/
```
