# Ralph Loop State Machine — CLI-Agnostic

This document describes the Ralph Loop state machine so it can be implemented by any CLI (Claude Code, Copilot CLI, Codex CLI, Gemini CLI, OpenCode CLI).

## Core Principle

**One /loop invocation = one step.** The state machine is implemented as a state file (`fix_plan.json`). Each invocation reads the current state, executes one step, updates the state, and stops.

## Automation Rules

- **NO human confirmation**: After completing a step, update `fix_plan.json` and stop immediately. Do NOT prompt the user with "Do you want to proceed?" or present confirmation options.
- **Use `--no-confirm` on sub-commands**: When invoking `task-review` (or any other interactive command) inside the loop, always pass `--no-confirm` so it does not block waiting for user input.
- **Trust the file**: The next loop invocation will read `fix_plan.json` and continue automatically.

## State File

All state lives in `docs/specs/[id]/_ralph_loop/fix_plan.json`.

### Required Fields

```json
{
  "spec_id": "001-feature",
  "spec_folder": "docs/specs/001-feature/",
  "task_range": {
    "from": "TASK-036",
    "to": "TASK-041",
    "from_num": 36,
    "to_num": 41,
    "total_in_range": 6
  },
  "state": {
    "step": "implementation",
    "current_task": "TASK-036",
    "current_task_file": "docs/specs/001-feature/tasks/TASK-036.md",
    "current_task_lang": "spring",
    "iteration": 1,
    "retry_count": 0,
    "last_updated": "2026-03-25T10:30:00",
    "error": null,
    "range_progress": {
      "done_in_range": 0,
      "total_in_range": 6
    }
  },
  "tasks": [...],
  "done": [],
  "pending": [],
  "optional": [],
  "superseded": [],
  "learnings": []
}
```

## State Machine

```
init ──────────────────────────► choose_task ────────────────────► complete
                                   │                                           ▲
                                   ▼                                           │
                           implementation                                      │
                                   │                                           │
                                   ▼                                           │
                                  review ─────── issues ───► fix ◄────────────┤
                                   │                         │                │
                              clean ▼                         ▼                │
                                 cleanup ─────────────────────────────────────┤
                                   │                                           │
                                   ▼                                           │
                                  sync ───────────────────────────────────────┤
                                   │                                           │
                                   ▼                                           │
                             update_done ─────────────────────────────────────┘
                                   │
                                   ▼
                                failed (stop)
                                 ↑
                                 └─ retry > 3
```

## Step Handlers

### init

**When**: `--action=start` or `fix_plan.json` doesn't exist.

**Actions**:
1. Read all task files from `docs/specs/[id]/tasks/TASK-*.md`
2. Extract from YAML frontmatter: `id`, `title`, `status`, `lang`, `dependencies`, `complexity`
3. Parse `--from-task` and `--to-task` to set `task_range`
4. Filter tasks by range: exclude tasks with number < `from_num` or > `to_num`
5. Initialize `state.step = "choose_task"`
6. Save `fix_plan.json`

**Output**:
```
Ralph Loop | Step: init | Range: TASK-036→TASK-041
→ Found 6 tasks in range
→ Initialized fix_plan.json
→ Next: choose_task
```

### choose_task

**When**: `state.step = "choose_task"`

**Actions**:
1. Filter `pending` tasks to only those within `task_range`
2. Filter to tasks where all dependencies are in `done` array
3. Sort by priority (lower complexity_score = higher priority)
4. If no tasks remain:
   - Set `state.step = "complete"`
   - Save and stop
5. Pick first task
6. Set `state.current_task`, `state.current_task_file`, `state.current_task_lang`
7. Set `state.step = "implementation"`
8. Set `state.retry_count = 0`
9. Save and stop

**Output**:
```
Ralph Loop | Step: choose_task | Iteration: 3
→ Selected: TASK-037 "Implement caching layer"
→ Dependencies: satisfied
→ Next: implementation
```

### implementation

**When**: `state.step = "implementation"`

**Actions**:
1. Run task-implementation:
   ```
   /specs:task-implementation --lang=LANG --task="TASK-FILE"
   ```
   Or for non-Claude CLIs, read the task file and implement manually.
2. If implementation succeeds:
   - Set `state.step = "review"`
3. If implementation fails:
   - Set `state.step = "failed"`
   - Set `state.error = "implementation failed"`
4. Save and stop

**Output**:
```
Ralph Loop | Step: implementation | Task: TASK-037
→ Running /specs:task-implementation --lang=spring --task="docs/specs/001-feature/tasks/TASK-037.md"
→ Success → Next: review
```

### review

**When**: `state.step = "review"`

**Actions**:
1. Run task-review with `--no-confirm` to prevent interactive blocking:
   ```
   /specs:task-review --no-confirm --lang=LANG "TASK-FILE"
   ```
   Or for non-Claude CLIs, verify implementation manually:
   - Read acceptance criteria from task file
   - Check each criterion is met
   - Run tests
   - Run code review
2. Read the generated review report (`TASK-FILE--review.md`) to determine pass/fail
3. If review passes (all criteria met, no issues):
   - Set `state.step = "cleanup"`
4. If review fails (issues found):
   - Increment `state.retry_count`
   - If `retry_count >= 3`:
     - Set `state.step = "failed"`
     - Set `state.error = "review failed after 3 retries"`
   - Else:
     - Set `state.step = "fix"`
5. Save and stop. Do NOT ask the user for confirmation.

**Output**:
```
Ralph Loop | Step: review | Task: TASK-037 | Retry: 1/3
→ Running /specs:task-review --no-confirm --lang=spring "docs/specs/001-feature/tasks/TASK-037.md"
→ Reading review report
→ Clean → Next: cleanup
```

### fix

**When**: `state.step = "fix"`

**Actions**:
1. Read the review report for the current task:
   ```
   docs/specs/[id]/tasks/TASK-XXX--review.md
   ```
2. Fix the issues reported in the review report:
   - For Claude Code: run `/specs:task-implementation --lang=LANG --task="TASK-FILE"` (the task implementation command should read the review report and apply fixes)
   - For non-Claude CLIs: manually edit files to address each finding
3. If fixes succeed:
   - Set `state.step = "review"`
4. If fixes fail:
   - Set `state.step = "failed"`
   - Set `state.error = "fix failed"`
5. Save and stop

**Output**:
```
Ralph Loop | Step: fix | Task: TASK-037 | Retry: 1/3
→ Reading review report: docs/specs/001-feature/tasks/TASK-037--review.md
→ Fixes applied → Next: review
```

### cleanup

**When**: `state.step = "cleanup"`

**Actions**:
1. Run code-cleanup with `--no-confirm`:
   ```
   /specs:code-cleanup --no-confirm --lang=LANG --task="TASK-FILE"
   ```
   Or for non-Claude CLIs:
   - Remove debug logs and temporary comments
   - Optimize imports
   - Format code
   - Verify documentation
2. Set `state.step = "sync"`
3. Save and stop

**Output**:
```
Ralph Loop | Step: cleanup | Task: TASK-037
→ Running /specs:code-cleanup --no-confirm --lang=spring --task="docs/specs/001-feature/tasks/TASK-037.md"
→ Cleanup complete → Next: sync
```

### sync

**When**: `state.step = "sync"`

**Actions**:
1. Run spec-sync-with-code:
   ```
   /specs:spec-sync-with-code SPEC-FOLDER/ --after-task=TASK-ID
   ```
   Or for non-Claude CLIs:
   - Read decision-log.md for any deviations
   - Compare implementation to spec
   - Update spec if needed (with user approval)
2. Set `state.step = "update_done"`
3. Save and stop

**Output**:
```
Ralph Loop | Step: sync | Task: TASK-037
→ Running /specs:spec-sync-with-code docs/specs/001-feature/ --after-task=TASK-037
→ Sync complete → Next: update_done
```

### update_done

**When**: `state.step = "update_done"`

**Actions**:
1. Update the task's YAML frontmatter: `status: completed`, `completed_date: YYYY-MM-DD`
2. In `fix_plan.json`:
   - Move task from `pending` to `done`
   - Increment `state.iteration`
   - Increment `state.range_progress.done_in_range`
   - Update `state.last_updated`
   - For each remaining pending task: check if all dependencies are now in `done`, if yes set `dependencies_satisfied = true`
3. Commit git changes (if clean):
   ```
   git add -A && git commit -m "Ralph iteration N: TASK-ID [title]"
   ```
4. Set `state.step = "choose_task"`
5. Save and stop

**Output**:
```
Ralph Loop | Step: update_done | Task: TASK-037
→ Marked TASK-037 done
→ Progress: 2/6 in range (33%)
→ Iteration: 3
→ Next: choose_task
```

### complete

**When**: `state.step = "complete"`

**Actions**:
Print completion summary and stop:
```
Ralph Loop | COMPLETE
═══════════════════════════════════════════════════════
Task Range: TASK-036 → TASK-041
Tasks Completed: 6/6
Total Iterations: 18
Deviations Detected: N
Learnings Captured: N

Run --action=start with a new range to continue.
```

### failed

**When**: `state.step = "failed"`

**Actions**:
Print error and stop:
```
Ralph Loop | FAILED
═══════════════════════════════════════════════════════
Task: TASK-037
Error: review failed after 3 retries

Fix the issues manually, then resume:
/developer-kit-specs:specs.ralph-loop --action=loop --spec=docs/specs/001-feature/
```

## Shell Script Implementation (CLI-Agnostic)

Create `docs/specs/[id]/_ralph_loop/run-ralph.sh`:

```bash
#!/bin/bash
# Ralph Loop State Machine — CLI-Agnostic
# One invocation = one step

SPEC_FOLDER="$1"
FIX_PLAN="$SPEC_FOLDER/_ralph_loop/fix_plan.json"

# Read current step
STEP=$(jq -r '.state.step' "$FIX_PLAN")
TASK=$(jq -r '.state.current_task // "none"' "$FIX_PLAN")
ITERATION=$(jq -r '.state.iteration // 0' "$FIX_PLAN")

echo "Ralph Loop | Iteration: $ITERATION | Step: $STEP | Task: $TASK"

case "$STEP" in
  init)
    echo "→ Initializing... (already done)"
    jq '.state.step = "choose_task"' "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    ;;

  choose_task)
    # Pick next task within range
    # (Implementation: filter pending, check deps, pick simplest)
    NEXT=$(jq -r '.pending | .[0]' "$FIX_PLAN" 2>/dev/null)
    if [ "$NEXT" = "null" ] || [ -z "$NEXT" ]; then
      echo "→ No more tasks in range"
      jq '.state.step = "complete"' "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    else
      TASK_FILE=$(jq -r ".tasks[] | select(.id == \"$NEXT\") | .file" "$FIX_PLAN")
      TASK_LANG=$(jq -r ".tasks[] | select(.id == \"$NEXT\") | .lang" "$FIX_PLAN")
      echo "→ Selected: $NEXT"
      jq --arg t "$NEXT" --arg f "$TASK_FILE" --arg l "$TASK_LANG" \
        '.state.current_task = $t | .state.current_task_file = $f | .state.current_task_lang = $l | .state.step = "implementation" | .state.retry_count = 0' \
        "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    fi
    ;;

  implementation)
    echo "→ [IMPLEMENTATION: Run task-implementation for $TASK]"
    # In real implementation: call the actual command
    jq '.state.step = "review"' "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    ;;

  review)
    echo "→ [REVIEW: Run task-review for $TASK]"
    # In real implementation: check results, on issues go to fix, on clean go to cleanup
    jq '.state.step = "cleanup"' "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    ;;

  cleanup)
    echo "→ [CLEANUP: Run code-cleanup for $TASK]"
    # In real implementation: call the actual command
    jq '.state.step = "sync"' "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    ;;

  fix)
    echo "→ [FIX: Apply fixes for $TASK based on review report]"
    # In real implementation: call the actual command or edit files
    jq '.state.step = "review"' "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    ;;

  sync)
    echo "→ [SYNC: Run spec-sync-with-code for $TASK]"
    # In real implementation: call the actual command
    jq '.state.step = "update_done"' "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    ;;

  update_done)
    echo "→ [UPDATE_DONE: Marking $TASK as done]"
    jq --arg t "$TASK" \
      '.done += [$t] | .pending -= [$t] | .state.iteration += 1 | .state.step = "choose_task"' \
      "$FIX_PLAN" > tmp.json && mv tmp.json "$FIX_PLAN"
    ;;

  complete)
    echo "═══════════════════════════════════════════════"
    echo "Ralph Loop COMPLETE"
    echo "═══════════════════════════════════════════════"
    ;;

  failed)
    echo "═══════════════════════════════════════════════"
    echo "Ralph Loop FAILED"
    ERROR=$(jq -r '.state.error // "unknown"' "$FIX_PLAN")
    echo "Error: $ERROR"
    echo "═══════════════════════════════════════════════"
    ;;
esac

echo ""
```

## Claude Code /loop Integration

```bash
# Start and loop (Claude Code)
/loop 5m /developer-kit-specs:specs.ralph-loop --action=start --spec=docs/specs/001-feature/ --from-task=TASK-036 --to-task=TASK-041
/loop 5m /developer-kit-specs:specs.ralph-loop --action=loop --spec=docs/specs/001-feature/ --from-task=TASK-036 --to-task=TASK-041
```

Claude Code's `/loop` skill will repeatedly invoke this skill until `state.step = "complete"` or `state.step = "failed"`.

## Non-Claude CLI Shell Loop

```bash
cd docs/specs/001-feature/_ralph_loop/

# Claude Code
while :; do claude "Execute one step of Ralph Loop. Read fix_plan.json, run the current step, update state, and stop."; done

# Copilot CLI
while :; do copilot "Execute one step of Ralph Loop. Read fix_plan.json, run the current step, update state, and stop."; done

# Codex CLI
while :; do codex "Execute one step of Ralph Loop. Read fix_plan.json, run the current step, update state, and stop."; done
```
