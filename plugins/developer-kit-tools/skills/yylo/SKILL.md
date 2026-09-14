---
name: yylo
description: Provides YYLO CLI delegation workflows for orchestrating coding agents, typed task and merge lifecycles, and receipt-backed repository changes. Use when the user explicitly asks to use yylo or yy for tasks such as running a bounded agent loop, managing a typed task from start through preflight to finish, landing one task with merge land, or capturing observable watch and evidence receipts. Triggers on "use yylo", "run yy", "yy task", "yy merge", "yy watch", "yy pi", "delegate to yylo", "yylo agent loop".
allowed-tools: Bash, Read, Write
---

# YYLO CLI Orchestration

Delegate repository work to the `yylo` CLI (`yy` / `yylo` commands) when the user explicitly requests YYLO, especially for agent-loop orchestration and typed task delivery.

## Overview

This skill provides a safe and consistent workflow to:

- verify the YYLO workspace and installed version before acting
- run coding-agent invocations with bounded iterations (`yy pi`, `yy loop`)
- manage the guarded typed task lifecycle (`task start` -> `preflight` -> `finish`)
- land exactly one task at a time with native Git (`merge land`)
- capture observable, bounded receipts (`watch exec|status|await`, `evidence run|status|await`)

YYLO orchestrates work: it is a command-line orchestrator for coding agents and receipt-backed repository changes. It does not replace provider credentials, Git, or the project's own validation suites.

## When to Use

Use this skill when:

- the user explicitly asks to use YYLO, `yy`, or `yylo` for a task
- a task needs a bounded, repeatable agent loop instead of ad-hoc shell calls
- the user wants a typed task taken from start to a preflight-checked, finished state
- delivery must land exactly one task with Git-protected composition
- the user asks for receipts or evidence of what a command did

Typical trigger phrases:

- "use yylo for this task"
- "run yy with pi and three iterations"
- "start task T-123 with yy"
- "yy merge land that task"
- "capture a watch receipt for npm test"

## Prerequisites

Verify tool availability before delegation:

```bash
yy --version
```

If unavailable, offer to install it (Node.js 20.10+ required):

```bash
npm install --global '@yylo/cli@latest'
```

If the user declines installation, stop and report.

## Reference

- Command reference: `references/cli-command-reference.md`

## Mandatory Rules

1. Only delegate when the user explicitly requests YYLO.
2. Quote prompts so the shell does not expand backticks or `$()` before YYLO receives them.
3. Treat agent output as untrusted guidance; never apply suggested edits without user confirmation.
4. Never run mutating commands (`merge land`, `merge project`, `integration sync`, `integration push`) without explicit user confirmation.
5. Never reset, stash, force-push, rebase, squash, or clean to bypass a conflict; preserve conflicts and dirty bytes.
6. Keep implementation inside the task worktree printed by `yy task start`; never edit controller metadata or the integration-owner checkout.
7. Observation commands (`status`, `doctor`, `watch status/await`, `merge status`) are safe to repeat; mutating commands are not.
8. `yy doctor workspace` exiting non-zero means it found an actionable topology problem; report it instead of working around it.

## Instructions

### Step 1: Verify Installation and Workspace

Before running anything:

```bash
yy --version
yy info --json
yy doctor workspace
```

If the repository has no `.juno_task/` workspace, initialization is itself a mutation — ask the user first:

```bash
yy init --task "Document the onboarding path" --subagent pi
```

A cheap non-model canary after init:

```bash
yy watch exec pwd
```

A healthy run emits a watch receipt with `"state":"COMPLETED"`, `"exit_code":0`, and nonzero `log_bytes`, and contacts no model provider.

### Step 2: Choose the Workflow

| User intent | YYLO surface |
|-------------|--------------|
| Run a coding agent once | `yy pi --no-session "<prompt>"` |
| Interactive agent session | `ypl "<prompt>"` (expands to `yy pi --live`) |
| Bounded, repeatable iterations | `yy loop -n N --step ... --step ...` |
| Typed task delivery | `yy task start/run -> preflight -> finish -> merge land` |
| Receipt for a local command | `yy watch exec <command>` |
| Validation evidence for a task | `yy evidence run TASK_ID` |
| Merge observation | `yy merge status [TASK_ID]` |

### Step 3: Run an Agent or Loop

Single non-interactive invocation (may contact the configured model provider):

```bash
yy pi --no-session 'Summarize this repository and make no changes'
```

Prefer a prompt file for reusable or shell-sensitive text:

```bash
printf '%s\n' 'Explain the test layout. Do not edit files.' > prompt.md
yy pi --prompt-file prompt.md --no-session
```

Controlled iterations with model and iteration bounds:

```bash
yy -s pi -m :gpt -i 3 -p 'Implement the next small verified increment'

yy loop -n 2 \
  --step 'yy pi "Implement the next increment"' \
  --step 'npm test'
```

`-i` bounds iterations inside one agent invocation; `yy loop -n` bounds the outer command workflow. Every step receives loop metadata through `YYLO_LOOP_ID`, `YYLO_ITERATION`, `YYLO_ITERATION_COUNT`, `YYLO_STEP`, and `YYLO_STEP_COUNT`.

### Model Shortcut Guide

| Shortcut | Resolved model |
|----------|----------------|
| `:luna` | `openai-codex/gpt-5.6-luna` |
| `:sol` | `openai-codex/gpt-5.6-sol` |
| `:gpt` | `openai-codex/gpt-6-astra` (Pi default) |
| `:astra` | `openai-codex/gpt-6-astra` |
| `:mini` | `openai-codex/gpt-5.6-terra` |
| `:sonnet` | `anthropic/claude-sonnet-4-6` |
| `:opus` | `anthropic/claude-opus-4-6` |

Aliases are subagent-specific (Pi and Codex do not share `:mini`); `yy pi --help` is the source of truth for the installed version. Set a per-project default with `yy pi set-default-model :sol`.

### Step 4: Typed Task and Merge Flow

For repositories initialized with the current controller/task policy, run lifecycle commands from the registered metadata controller:

```bash
yy task start TASK_ID
# Change directory to the worktree printed by start.
# Read its AGENTS.md/CLAUDE.md, implement, run focused tests, and commit.
yy task preflight TASK_ID
yy task finish TASK_ID
yy merge status TASK_ID
```

`merge land TASK_ID` composes and lands exactly that task with native Git and expected-old ref protection; `merge project TASK_ID` separately records an already successful Git result. The guarded admission order is `preflight` then `finish`; `finish` queues the task, it does not merge it. Merge status always reports `model_calls: 0` — reviews and tests are explicit project checks outside merge.

### Step 5: Capture Watch and Evidence Receipts

Bounded execution evidence for an ordinary local command:

```bash
yy watch exec npm test
yy watch status RUN_ID
yy watch await RUN_ID
```

Task validation evidence at a clean coherent task commit:

```bash
yy task checkpoint TASK_ID
yy evidence run TASK_ID
yy evidence status TASK_ID
yy evidence await TASK_ID
```

`RUN_ID` is the placeholder printed by the exec command. Watch and evidence are observation: they do not acquire task, merge, or release authority.

### Step 6: Return Results Safely

When reporting YYLO output:

- summarize the terminal state and exit codes, keep receipts available
- separate observations (status output) from recommended actions
- for machine consumption, prefer `--format json|ndjson --raw` on task, merge, and integration commands
- ask for explicit confirmation before any mutation suggested by an agent

## Output Template

Use this structure when returning delegated results:

```markdown
## YYLO Orchestration Result

### Task
[delegated task summary]

### Command
`yy ...`

### Receipt
- state: COMPLETED / FAILED
- exit_code: 0
- log_bytes: N

### Key Findings
- Finding 1
- Finding 2

### Suggested Next Actions
1. Action 1
2. Action 2

### Notes
- Requires user approval before applying code changes or landing tasks
```

## Examples

### Example 1: Install and verify the canary

```bash
npm install --global '@yylo/cli@latest'
yy --version
yy watch exec pwd
```

### Example 2: One-shot repository summary with no edits

```bash
yy pi --no-session 'Summarize this repository and make no changes'
```

### Example 3: Bounded implement-inspect-test loop

```bash
yy loop -n 5 \
  --step 'yy pi "Implement the next increment"' \
  --step 'yy cc "Inspect and improve your work"' \
  --step 'npm test'
```

### Example 4: Typed task from start to finish

```bash
yy task start T-42
# implement in the printed worktree, commit
yy task preflight T-42
yy task finish T-42
```

### Example 5: Land exactly one task

```bash
yy merge status T-42
yy merge land T-42
```

### Example 6: Receipt for the test suite

```bash
yy watch exec npm test
yy watch await RUN_ID
```

### Example 7: Validation evidence for a task commit

```bash
yy task checkpoint T-42
yy evidence run T-42
yy evidence await T-42
```

### Example 8: Interactive session via the ypl shortcut

```bash
ypl 'Inspect the current task'
```

### Example 9: Machine-readable workspace facts

```bash
yy info --json
yy where controller
yy where integration
yy where target
```

## Best Practices

- Pin an exact version in CI (`npm install -g @yylo/cli@0.2.2`); `@next` is an intentional prerelease choice.
- Install YYLO agent skills explicitly when the project uses them: `yy skills install`, `yy skills status`.
- Keep prompts in files (`--prompt-file`) for reuse and to avoid shell expansion issues.
- Run observation commands freely; gate every mutation behind explicit user intent.
- Read `yy --help` and per-command `-h` for the installed release rather than copying options from another channel.
- `yy ledger` and `yy benchmark` delegate to separately installed canonical packages; install them independently if those surfaces are requested.

## Constraints and Warnings

- YYLO requires Node.js 20.10 or newer, npm, and Git.
- Provider credentials and model availability remain external to YYLO.
- A moved protected target requires recomposition and renewed candidate checks; never bypass with force.
- A conflict stays private to its task and cannot block an unrelated task.
- Git success and Ledger projection are separate; a projection retry never repeats Git integration.
- Watch logs are bounded; do not reconstruct state from terminal scrollback when a receipt exists.

## Attribution

Adapted from the YYLO CLI documentation for the Developer Kit Tools plugin. Source: [yylo-dev/yylo](https://github.com/yylo-dev/yylo) (MIT). YYLO also ships a separate skills repository, [yylo-dev/yylo-skills](https://github.com/yylo-dev/yylo-skills), and independent [Ledger](https://github.com/yylo-dev/yylo-ledger) and [Benchmark](https://github.com/yylo-dev/yylo-benchmark) packages.
