---
description: Cancel an active ralph-loop-v2 background job in this repository
argument-hint: '[job-id]'
disable-model-invocation: true
allowed-tools: Bash(python3:*)
---

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/main.py" cancel $ARGUMENTS`
