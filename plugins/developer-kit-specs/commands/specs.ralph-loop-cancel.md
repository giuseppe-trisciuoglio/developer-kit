---
description: "Cancel an active Ralph Loop background job (WHAT: stops a running ralph-loop-v2 job by ID). Use WHEN: a background Ralph Loop job needs to be terminated early."
argument-hint: '[job-id]'
disable-model-invocation: true
allowed-tools: Bash(python3:*)
---

## Overview

Cancels an active Ralph Loop background job in the current repository. The job is stopped and its state is preserved for potential resumption.

## Usage

```bash
/developer-kit-specs:specs.ralph-loop-cancel <job-id>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `job-id` | Yes | The ID of the background job to cancel |

## Examples

```bash
# Cancel a specific background job
/developer-kit-specs:specs.ralph-loop-cancel abc123
```

## Execution

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/main.py" cancel $ARGUMENTS`
