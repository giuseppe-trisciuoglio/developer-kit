---
description: Show active and recent ralph-loop-v2 jobs for this repository
argument-hint: '[job-id] [--all]'
disable-model-invocation: true
allowed-tools: Bash(python3:*)
---

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/main.py" status $ARGUMENTS`

If the user **did not** pass a job ID:
- Render the output as a single Markdown table with columns: ID, Status, Phase, Progress, Created.
- Compact: no extra prose outside the table.

If the user **has** passed a job ID:
- Present the full command output without summarizing.
