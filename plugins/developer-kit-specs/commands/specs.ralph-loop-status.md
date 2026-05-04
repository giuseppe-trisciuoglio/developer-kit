---
description: "Show active and recent Ralph Loop jobs (WHAT: displays status table or full details for a specific job). Use WHEN: checking progress of background Ralph Loop jobs."
argument-hint: '[job-id] [--all]'
disable-model-invocation: true
allowed-tools: Bash(python3:*)
---

## Overview

Displays active and recent Ralph Loop background jobs for the current repository. Without arguments, shows a summary table of all jobs. With a job ID, shows full details for a specific job.

## Usage

```bash
# Show all active/recent jobs
/developer-kit-specs:specs.ralph-loop-status

# Show full details for a specific job
/developer-kit-specs:specs.ralph-loop-status <job-id>

# Show all jobs including completed ones
/developer-kit-specs:specs.ralph-loop-status --all
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `job-id` | No | Show full details for a specific job |
| `--all` | No | Include completed jobs in the listing |

## Examples

```bash
# Check all active jobs
/developer-kit-specs:specs.ralph-loop-status

# Check a specific job's full output
/developer-kit-specs:specs.ralph-loop-status abc123

# Show all jobs including completed
/developer-kit-specs:specs.ralph-loop-status --all
```

## Execution

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/main.py" status $ARGUMENTS`

If the user **did not** pass a job ID:
- Render the output as a single Markdown table with columns: ID, Status, Phase, Progress, Created.
- Compact: no extra prose outside the table.

If the user **has** passed a job ID:
- Present the full command output without summarizing.
