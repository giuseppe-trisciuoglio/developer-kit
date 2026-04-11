# Ralph Loop — Multi-Agent Automation Guide

The Ralph Loop automates the SDD implementation cycle across multiple tasks using different AI agents. It applies Geoffrey Huntley's "Ralph Wiggum as a Software Engineer" technique: one step per invocation, state persisted to disk.

## Why Ralph Loop?

**The problem:** Implementing a 10-task specification in a single Claude Code session causes context window explosion. After 3-4 tasks, the agent loses track of earlier decisions and implementation details.

**The solution:** The Ralph Loop executes exactly one step per invocation and persists all state to `fix_plan.json`. Each invocation starts fresh with only the context it needs.

```
Traditional approach (single session):
  Session 1: TASK-001 → TASK-002 → TASK-003 → [context limit reached]

Ralph Loop approach:
  Invocation 1: choose_task → TASK-001
  Invocation 2: implement TASK-001
  Invocation 3: review TASK-001
  Invocation 4: cleanup TASK-001
  Invocation 5: choose_task → TASK-002
  ... (unlimited, state in fix_plan.json)
```

## State Machine

```
init → choose_task → implementation → review → fix → cleanup → sync → update_done → choose_task
                          ↑                                            │
                          └────────── (if review failed, max 3 retries) ┘
```

| State | Action | Next State |
|-------|--------|------------|
| `init` | Load spec, validate prerequisites | `choose_task` |
| `choose_task` | Pick next pending task | `implementation` |
| `implementation` | Execute task with assigned agent | `review` |
| `review` | Run task-review | `cleanup` (pass) or `fix` (fail) |
| `fix` | Apply review feedback | `implementation` (retry ≤3) |
| `cleanup` | Run code-cleanup | `sync` |
| `sync` | Update Knowledge Graph and context | `update_done` |
| `update_done` | Mark task completed, commit | `choose_task` |

## Getting Started

### Initialize

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-user-auth/
```

This creates `docs/specs/001-user-auth/_ralph_loop/fix_plan.json` with initial state.

**Options:**

```bash
# Process only a specific range of tasks
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-user-auth/ \
  --from-task=TASK-003 \
  --to-task=TASK-007

# Specify default agent
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-user-auth/ \
  --agent=codex

# Skip git commits (for testing)
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-user-auth/ \
  --no-commit
```

### Run the Loop

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-user-auth/
```

Each invocation:
1. Reads `fix_plan.json` to determine current state
2. Executes exactly one step
3. Updates `fix_plan.json` with new state
4. Prints a command for the user to execute next

**Example output:**
```
[ralph-loop] State: choose_task
[ralph-loop] Selected: TASK-003 (Implement JWT token service)
[ralph-loop] Agent: claude
[ralph-loop] Next: Execute the following command, then run loop again:

claude --print "/specs:task-implementation --lang=spring --task=docs/specs/001-user-auth/tasks/TASK-003.md"
```

After executing the shown command, run the loop again:
```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-user-auth/
```

### Check Status

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=status \
  --spec=docs/specs/001-user-auth/
```

**Example output:**
```
[ralph-loop] Status for docs/specs/001-user-auth/
[ralph-loop] Current state: review
[ralph-loop] Current task: TASK-003
[ralph-loop] Retries: 0/3
[ralph-loop] Progress: 3/8 tasks completed
[ralph-loop] Completed: TASK-001 ✓, TASK-002 ✓, TASK-003 (in review)
[ralph-loop] Remaining: TASK-004, TASK-005, TASK-006, TASK-007, TASK-008
```

## Multi-Agent Support

The Ralph Loop can dispatch different tasks to different AI agents. This is useful when:
- Some tasks need deep reasoning (use Claude)
- Some tasks are boilerplate (use Codex or Copilot)
- You want to compare agent outputs

### Per-Task Agent Assignment

Set the `agent` field in task frontmatter:

```yaml
---
id: TASK-003
title: Implement JWT token service
agent: claude       # Use Claude for complex security logic
---

---
id: TASK-004
title: Create REST DTOs
agent: codex        # Use Codex for straightforward DTO generation
---

---
id: TASK-005
title: Write unit tests
agent: copilot      # Use Copilot for test generation
---
```

### Supported Agents

| Agent | CLI | Best For |
|-------|-----|----------|
| `claude` | Claude Code | Complex logic, security, architecture |
| `codex` | Codex CLI | Code generation, boilerplate, straightforward tasks |
| `copilot` | GitHub Copilot CLI | Test generation, code completion |
| `gemini` | Gemini CLI | Large-context analysis, documentation |
| `glm4` | GLM-4 CLI | General-purpose coding |
| `kimi` | Kimi CLI | Long-context reasoning |
| `minimax` | MiniMax CLI | General-purpose coding |

### Default Agent

If no agent is specified in task frontmatter, the default is used:

```bash
# Set default agent at initialization
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-user-auth/ \
  --agent=codex
```

## Real-World Scenario: Spring Boot Auth System

Here's a complete walkthrough for a 6-task specification:

```bash
# 1. Initialize with task range
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-user-auth/ \
  --from-task=TASK-001 \
  --to-task=TASK-006

# Output:
# [ralph-loop] Initialized fix_plan.json
# [ralph-loop] Tasks: TASK-001 through TASK-006
# [ralph-loop] Default agent: claude

# 2. Run loop (iteration 1: choose_task)
python3 .../ralph_loop.py --action=loop --spec=docs/specs/001-user-auth/
# → Selects TASK-001 (Create User entity)
# → Shows command: /specs:task-implementation --lang=spring --task=...TASK-001.md

# 3. Execute the shown command (manually or via script)
# ... implement TASK-001 ...

# 4. Run loop (iteration 2: review)
python3 .../ralph_loop.py --action=loop --spec=docs/specs/001-user-auth/
# → Reviews TASK-001
# → If PASSED: proceeds to cleanup
# → Shows command: /developer-kit-specs:specs-code-cleanup --lang=spring --task=...TASK-001.md

# 5. Execute cleanup
# ... cleanup TASK-001 ...

# 6. Run loop (iteration 3: sync + choose next)
python3 .../ralph_loop.py --action=loop --spec=docs/specs/001-user-auth/
# → Syncs Knowledge Graph
# → Marks TASK-001 completed
# → Commits changes
# → Selects TASK-002

# ... continue for remaining tasks ...
```

## Review Failure Handling

When a task review fails, the Ralph Loop enters the `fix` state:

```
implementation → review (FAILED) → fix → implementation (retry) → review → ...
```

- **Max retries:** 3 per task
- **On retry:** The loop provides review feedback to the next implementation attempt
- **After 3 failures:** The loop pauses and asks for manual intervention

## State File Reference

The `fix_plan.json` file stores all loop state:

```json
{
  "spec_path": "docs/specs/001-user-auth/",
  "state": "choose_task",
  "current_task": null,
  "task_range": {
    "from": "TASK-001",
    "to": "TASK-006"
  },
  "completed_tasks": ["TASK-001", "TASK-002"],
  "failed_tasks": [],
  "retries": {
    "TASK-003": 2
  },
  "default_agent": "claude",
  "no_commit": false,
  "started_at": "2026-04-10T10:00:00Z",
  "last_updated": "2026-04-10T11:30:00Z"
}
```

**Important:** Do not edit `fix_plan.json` manually. The Python script manages all state transitions.

## Fully Automated Orchestration with `agents_loop.py`

The manual Ralph Loop requires you to run `ralph_loop.py` and execute each command yourself. The `agents_loop.py` script in `scripts/` **fully automates** this cycle: it calls `ralph_loop.py` to get the next command, executes it with the chosen AI agent, advances the state, and repeats until all tasks are done.

```
Manual Ralph Loop:
  You: ralph_loop.py --action=loop  →  see command
  You: execute command manually
  You: ralph_loop.py --action=next
  ...repeat...

Automated agents_loop.py:
  Script: ralph_loop.py → get command → execute with agent → advance state → repeat
  You: sit back and monitor
```

### Basic Usage

```bash
# Fully automated with a single agent
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=claude

# Auto-select the best agent per workflow phase
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=auto

# Use a specific reviewer agent
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=claude \
  --reviewer=glm4
```

### Supported Agents

| Agent | CLI | Best For |
|-------|-----|----------|
| `claude` | Claude Code | Complex logic, security, architecture |
| `codex` | Codex CLI | Code generation, boilerplate |
| `gemini` | Gemini CLI | Large-context analysis |
| `kimi` | Kimi CLI | Long-context reasoning |
| `glm4` | GLM-4 CLI | General-purpose coding |
| `minimax` | MiniMax CLI | General-purpose coding |
| `openrouter` | OpenRouter CLI | Access to multiple models |
| `copilot` | GitHub Copilot CLI | Test generation, code review |
| `qwen` | Qwen Code | Coding tasks with Qwen models |
| `auto` | Dynamic selection | Best agent per workflow phase |

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--spec` | required | Path to specification folder |
| `--agent` | `codex` | AI agent to use (or `auto`) |
| `--delay` | `10` | Seconds between iterations |
| `--max-iterations` | `20` | Safety limit on iterations |
| `--fast` | `false` | Skip cleanup and sync steps |
| `--verbose` | `false` | Enable debug output with real-time streaming |
| `--model` | agent default | Model override (e.g. `sonnet`, `opus`, `gpt-5.4`) |
| `--kpi-check` | `true` | Enable KPI quality gates after review |
| `--kpi-threshold` | `7.5` | Quality score threshold (0-10) |
| `--max-quality-iterations` | `5` | Max fix cycles based on KPI score |
| `--reviewer` | none | Dedicated agent for review steps |
| `--agent-timeout` | `1200` | Timeout per agent execution (seconds) |
| `--dry-run` | `false` | Print commands without executing |

### Auto Mode (`--agent=auto`)

When using `--agent=auto`, the script selects the best agent for each workflow phase:

| Phase | Agent | Rationale |
|-------|-------|-----------|
| `review` | `codex` | Code review specialist |
| `sync` | `gemini` | Powerful context analysis |
| `implementation` | Rotates: `claude` → `kimi` → `glm4` | Diversity of approach |
| `fix` | Rotates: `glm4` → `minimax` → `openrouter` | Alternative perspectives |
| `cleanup` | Rotates: `claude` → `kimi` → `codex` | General cleanup |
| Other steps | `glm4` | Default fallback |

### Fast Mode (`--fast`)

Skip cleanup and sync steps for rapid iteration cycles:

```bash
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=claude \
  --fast
```

- **Normal flow**: `review → cleanup → sync → update_done`
- **Fast flow**: `review → update_done`

Use fast mode when you want rapid implementation-review cycles and will sync later.

### KPI Quality Gates (`--kpi-check`)

When enabled (default), the script checks quality KPIs after each review step:

1. Reads `TASK-XXX--kpi.json` (auto-generated by hooks)
2. Compares `overall_score` against threshold (default: 7.5)
3. If **passed**: proceeds normally
4. If **failed**: forces state to `fix` for another iteration
5. After max quality iterations (default: 5): marks task as failed

This enables data-driven iteration — the script keeps fixing until quality meets the threshold.

```bash
# Custom quality threshold
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=claude \
  --kpi-threshold=8.0 \
  --max-quality-iterations=3
```

### Reviewer Override (`--reviewer`)

Use a different agent specifically for review steps, regardless of the main agent:

```bash
# Implementation with Claude, review with GLM-4
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=claude \
  --reviewer=glm4
```

This also works with `--agent=auto`, overriding the auto-selection for review phases only.

### Real-World Example

```bash
# 1. Initialize the Ralph Loop first
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-user-auth/ \
  --from-task=TASK-001 \
  --to-task=TASK-006

# 2. Run fully automated with auto mode and KPI checks
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=auto \
  --kpi-check \
  --verbose

# The script will:
# - Auto-select agents per phase
# - Execute implementation, review, cleanup, sync
# - Check quality KPIs after each review
# - Fix issues if KPIs below threshold
# - Create git checkpoints after each iteration
# - Stop when all tasks are complete or failed
```

### Monitoring and Debugging

```bash
# Enable verbose output for real-time agent streaming
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=claude \
  --verbose

# Dry run to see what would be executed
python3 scripts/agents_loop.py \
  --spec=docs/specs/001-user-auth/ \
  --agent=claude \
  --dry-run

# Logs are saved automatically to .agents_loop_logs/
```

Log files are written to `.agents_loop_logs/<spec-name>/` with timestamps, agent output, and execution metrics.

### Graceful Shutdown

Press `Ctrl+C` to stop the loop. The script:
1. Finishes the current agent execution
2. Prints a summary
3. Preserves `fix_plan.json` state
4. You can resume later by running the same command

## Best Practices

1. **Start with clean git state** — Uncommitted changes can cause conflicts
2. **One step per invocation** — Never combine implementation + review + sync (manual mode)
3. **Check status between runs** — Use `--action=status` to verify state (manual mode)
4. **Assign agents wisely** — Use Claude for complex logic, Codex for boilerplate
5. **Monitor retries** — If a task fails 3 times, investigate manually
6. **Commit between tasks** — Each task completion triggers a git commit
7. **Use task ranges** — Start with a small range to validate the workflow
8. **Use `agents_loop.py` for automation** — Fully automates the manual loop cycle
9. **Use `--verbose` for debugging** — See real-time agent output and execution metrics
10. **Leverage KPI quality gates** — Let the script iterate on quality automatically

## Troubleshooting

### "fix_plan.json not found"

Run `--action=start` to initialize:

```bash
python3 .../ralph_loop.py --action=start --spec=docs/specs/001-user-auth/
```

### "State is wrong"

Resume or reset the loop:

```bash
# Resume from current state
python3 .../ralph_loop.py --action=resume --spec=docs/specs/001-user-auth/

# Or reset and start over
rm -rf docs/specs/001-user-auth/_ralph_loop/
python3 .../ralph_loop.py --action=start --spec=docs/specs/001-user-auth/
```

### "Max retries exceeded"

The task has failed review 3 times. Options:
1. Implement the task manually
2. Split the task into smaller subtasks: `/specs:task-manage --action=split --task=...`
3. Review the task yourself and fix the issues
