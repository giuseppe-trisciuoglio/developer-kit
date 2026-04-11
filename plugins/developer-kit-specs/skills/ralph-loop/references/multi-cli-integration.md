# Multi-CLI Ralph Loop Integration

This document explains how to run the Ralph Loop across all supported CLI environments using the **Python orchestrator script**.

## Architecture

The Ralph Loop uses a Python script (`ralph_loop.py`) as the central orchestrator:

1. **Script manages state**: Reads/writes `fix_plan.json`
2. **Script generates commands**: Shows the correct command for your CLI
3. **You execute commands**: Run the shown command in your CLI
4. **Script updates state**: Run the script again to advance

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ralph_loop.py  │────▶│  fix_plan.json  │────▶│  Your CLI       │
│  (orchestrator) │     │  (state file)   │     │  (Claude/Codex/ │
│                 │     │                 │     │  Copilot/Kimi)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                                               │
         │                                               ▼
         └──────────────────────────────────────────────┘
                    (you run script again)
```

## Supported CLIs

| CLI | Agent Code | Command Prefix | Example |
|-----|------------|----------------|---------|
| Claude Code | `claude` | `/` | `/specs:task-implementation` |
| Codex CLI | `codex` | (none) | `task-implementation` |
| Copilot CLI | `copilot` | (none) | `task-implementation` |
| Kimi CLI | `kimi` | `/` | `/specs:task-implementation` |

## Basic Usage (All CLIs)

### 1. Initialize

```bash
# Use python3 on macOS, python on Windows/Linux
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-feature/ \
  --from-task=TASK-036 \
  --to-task=TASK-041 \
  --agent=claude
```

### 2. Run Loop

```bash
python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

Output shows the command to execute:
```
🔄 Ralph Loop | Iteration 0 | Step: implementation
→ Implementation: TASK-036

Execute:
  /specs:task-implementation --task=TASK-036

After execution, update state:
  python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

### 3. Execute Shown Command

In your CLI, run the shown command:
```bash
/specs:task-implementation --task=TASK-036
```

### 4. Continue Loop

Run the loop command again:
```bash
python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

## CLI-Specific Examples

### Claude Code

```bash
# Initialize
python3 ralph_loop.py --action=start \
  --spec=docs/specs/001-feature/ \
  --from-task=TASK-036 --to-task=TASK-041 \
  --agent=claude

# With /loop for automation
/loop 5m python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

Commands will be formatted as: `/specs:task-implementation --task=TASK-036`

### Codex CLI

```bash
# Initialize
python3 ralph_loop.py --action=start \
  --spec=docs/specs/001-feature/ \
  --from-task=TASK-036 --to-task=TASK-041 \
  --agent=codex

# Loop
python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

Commands will be formatted as: `task-implementation --task=TASK-036`

### Copilot CLI

```bash
# Initialize
python3 ralph_loop.py --action=start \
  --spec=docs/specs/001-feature/ \
  --agent=copilot

# Loop
python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

### Kimi CLI

```bash
# Initialize
python3 ralph_loop.py --action=start \
  --spec=docs/specs/001-feature/ \
  --agent=kimi

# Loop
python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

Commands will be formatted as: `/specs:task-implementation --task=TASK-036`

## Multi-Agent Support

### Default Agent

Set default agent for all tasks:
```bash
python3 ralph_loop.py --action=start --spec=... --agent=codex
```

### Per-Task Agent

Override per task in task file frontmatter:
```yaml
---
id: TASK-036
title: Refactor service
agent: codex
---
```

## Automation Scripts

### Bash Loop

```bash
#!/bin/bash
# ralph-loop.sh - Run until complete

SPEC="docs/specs/001-feature"
PYTHON="python3"  # Use python3 on macOS

while true; do
  # Run one step
  OUTPUT=$($PYTHON ralph_loop.py --action=loop --spec="$SPEC" 2>&1)
  echo "$OUTPUT"

  # Check if complete or failed
  if echo "$OUTPUT" | grep -q "COMPLETE"; then
    echo "✅ All done!"
    break
  fi
  if echo "$OUTPUT" | grep -q "FAILED"; then
    echo "❌ Loop failed!"
    exit 1
  fi

  # The script shows the command to execute
  # In automation, you would need to execute it programmatically
  # For manual use, execute the shown command then continue
  echo "Execute the shown command, then press Enter to continue..."
  read
done
```

### With Claude Code /loop

```bash
# This will run the loop every 5 minutes
/loop 5m python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-feature/
```

Note: With `/loop`, you'll see the command to execute each iteration. Execute it manually, then the next `/loop` will continue.

## State File

All state lives in `fix_plan.json`:

```json
{
  "spec_id": "001-feature",
  "spec_folder": "docs/specs/001-feature/",
  "task_range": {
    "from": "TASK-036",
    "to": "TASK-041",
    "total_in_range": 6
  },
  "default_agent": "claude",
  "tasks": [...],
  "pending": ["TASK-036", "TASK-037"],
  "done": [],
  "state": {
    "step": "implementation",
    "current_task": "TASK-036",
    "current_task_file": "docs/specs/001-feature/tasks/TASK-036.md",
    "current_task_lang": "java",
    "iteration": 0,
    "retry_count": 0,
    "last_updated": "2026-04-05T10:30:00",
    "range_progress": {
      "done_in_range": 0,
      "total_in_range": 6
    }
  }
}
```

## Legacy Shell Loop (Deprecated)

For non-Claude CLIs without the Python script, you can use a shell loop with `prompt.md`:

```bash
cd docs/specs/001-feature/_ralph_loop/

# Claude Code
while :; do cat prompt.md | claude; done

# Copilot CLI
while :; do cat prompt.md | copilot; done

# Codex CLI
while :; do cat prompt.md | codex; done
```

**Note**: The Python orchestrator is the recommended approach for all CLIs.

## Command Reference

### Script Commands

| Action | Description |
|--------|-------------|
| `--action=start` | Initialize fix_plan.json from task files |
| `--action=loop` | Execute one step, show command to run |
| `--action=status` | Show current state and progress |
| `--action=resume` | Resume from current state |

### Generated Commands by Agent

| Step | Claude/Kimi | Codex/Copilot |
|------|-------------|---------------|
| Implementation | `/specs:task-implementation --task=TASK-036` | `task-implementation --task=TASK-036` |
| Review | `/specs:task-review --task=TASK-036` | `task-review --task=TASK-036` |
| Cleanup | `/developer-kit-specs:specs-code-cleanup --task=TASK-036` | `specs-code-cleanup --task=TASK-036` |
| Sync | `/specs:spec-sync-with-code --after-task=TASK-036` | `spec-sync-with-code --after-task=TASK-036` |

## Best Practices

1. **Use Python script for state management**: Don't manually edit `fix_plan.json`
2. **Execute shown commands**: The script generates the correct command for your CLI
3. **One step at a time**: Don't try to combine steps — context will explode
4. **Check status regularly**: Use `--action=status` to see progress
5. **Git commits**: The script auto-commits after each completed task

## Troubleshooting

### "fix_plan.json not found"

Run `--action=start` first.

### Wrong command format

Check `--agent` matches your CLI (`claude`, `codex`, `copilot`, or `kimi`).

### Task not found

Ensure task files are in `tasks/TASK-XXX.md` format with YAML frontmatter.

## Migration from Shell Loop

If you were using the shell loop approach:

1. **Before**: `while :; do cat prompt.md | claude; done`
2. **After**: 
   ```bash
   python3 ralph_loop.py --action=start --spec=...
   python3 ralph_loop.py --action=loop --spec=...
   # Execute shown command
   python3 ralph_loop.py --action=loop --spec=...
   ```

The Python script provides:
- Better state management
- Multi-agent support
- Command formatting per CLI
- Progress tracking
- Git integration
