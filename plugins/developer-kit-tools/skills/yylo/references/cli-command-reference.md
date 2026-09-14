# YYLO CLI Command Reference

Quick reference for the `yylo` skill delegation workflow. Commands: `yylo` and `yy` (equivalent); `ypl` is `yy pi --live`.

## Installation and Version

```bash
# Stable channel (Node.js 20.10+, npm, Git required)
npm install --global '@yylo/cli@latest'

# Prerelease channel
npm install --global '@yylo/cli@next'

# Exact pin for reproducible installs / CI
npm install -g @yylo/cli@0.2.2

# Inspect published versions
npm view '@yylo/cli' version dist-tags --json
yy --version
```

## Workspace Init and Discovery

```bash
# Initialize the .juno_task/ workspace (mutation: creates the initial workspace commit)
yy init --task "Document the onboarding path" --subagent pi

# Read-only discovery
yy info --json
yy doctor workspace
yy --help

# Workspace routing (read-only)
yy where controller
yy where integration
yy where target
yy where task TASK_ID
```

`doctor workspace` is intentionally nonzero when it finds an actionable topology problem; it never fetches or changes the workspace.

## Agent Runs

```bash
# Non-interactive single invocation (may contact the model provider)
yy pi --no-session 'Summarize this repository and make no changes'

# Prompt from file (safer for shell-sensitive text)
yy pi --prompt-file prompt.md --no-session

# Interactive session shortcut
ypl 'Inspect the current task'   # expands to: yy pi --live

# Controlled iterations
yy -s pi -m :gpt -i 3 -p 'Implement the next small verified increment'
```

## Model Shortcuts

Pi subagent shortcuts (aliases are subagent-specific):

| Shortcut | Resolved model |
|----------|----------------|
| `:luna` | `openai-codex/gpt-5.6-luna` |
| `:sol` | `openai-codex/gpt-5.6-sol` |
| `:gpt` | `openai-codex/gpt-6-astra` (Pi default) |
| `:astra` | `openai-codex/gpt-6-astra` |
| `:mini` | `openai-codex/gpt-5.6-terra` |
| `:sonnet` | `anthropic/claude-sonnet-4-6` |
| `:opus` | `anthropic/claude-opus-4-6` |

```bash
# Per-project default model
yy pi set-default-model :sol
```

Project shortcuts live in `.juno_task/config.json` under `modelShortcuts`.

## Loop and Managed Workflows

```bash
# Outer command workflow with bounded iterations
yy loop -n 2 \
  --step 'yy pi "Implement the next increment"' \
  --step 'npm test'

# Reusable workflow contract saved as flow.yaml
yylo loop --workflow flow.yaml
```

Example `flow.yaml`:

```yaml
iterations: 5
continuity: iteration
on_error: continue
steps:
  - run: yy pi "Implement the next increment"
  - run: yy cc "Inspect and improve your work"
  - run: npm test
```

Steps receive `YYLO_LOOP_ID`, `YYLO_ITERATION`, `YYLO_ITERATION_COUNT`, `YYLO_STEP`, and `YYLO_STEP_COUNT`.

Workflow Runner (managed scripts installed by `yy init`):

```bash
./.juno_task/scripts/workflow_runner.sh \
  --init-example agent-chain .juno_task/workflows/agent-chain.yaml
./.juno_task/scripts/workflow_runner.sh lint \
  --workflow .juno_task/workflows/agent-chain.yaml
./.juno_task/scripts/workflow_runner.sh \
  --workflow .juno_task/workflows/agent-chain.yaml --dry-run \
  --print-output none --no-print-step-stdout

# Diagnose an interrupted producer before any mutation
./.juno_task/scripts/workflow_runner.sh recover-attempt RUN_DIRECTORY --dry-run
./.juno_task/scripts/workflow_runner.sh doctor RUN_DIRECTORY
```

## Watch (Observable Local Commands)

```bash
yy watch exec npm test
yy watch status RUN_ID
yy watch await RUN_ID
```

`RUN_ID` is printed by the exec command. Status is observation only; no task, merge, or release authority.

## Task Validation Evidence

```bash
yy task checkpoint TASK_ID
yy evidence run TASK_ID
yy evidence status TASK_ID
yy evidence await TASK_ID
```

Plans and retains exact-input validation evidence at a clean coherent task commit; does not finish or merge the task.

## Typed Task Lifecycle

Run lifecycle commands from the registered metadata controller.

```bash
# Managed path
yy task run TASK_ID

# Manual implementation path
yy task start TASK_ID     # freezes target SHA, creates branch/worktree, hydrates deps
# implement + focused tests in the printed worktree, then commit
yy task preflight TASK_ID # read-only closure-defect check
yy task finish TASK_ID    # requires clean committed tip; queues, does not merge

# Observation (safe to repeat)
yy task status TASK_ID
yy task doctor TASK_ID
```

The guarded admission order is `preflight` then `finish`.

## Merge (Protected Delivery)

```bash
yy merge status          # all independently landable active tasks
yy merge status TASK_ID
yy merge land TASK_ID    # composes + lands exactly one task, native Git
yy merge project TASK_ID # records an already successful Git result
```

Merge launches no models, chooses no reviewers, schedules no suites. A moved target requires recomposition and renewed candidate checks.

## Integration Owner

```bash
yy integration status    # observation
yy integration sync      # mutation: guarded refresh, refuses dirty/diverged state
yy integration push      # separate remote authority — never inferred from sync
```

## Agent Skills Management

```bash
yy skills install
yy skills install --version 2.0.0
yy skills update --force
yy skills status
```

Skills content is versioned independently in yylo-dev/yylo-skills and is not bundled with the CLI.

## Ledger and Benchmark Delegates

```bash
python3 -m pip install 'yylo-ledger==0.3.1'
npm install --global '@yylo/benchmark@0.1.1-rc.2'

yy ledger --help        # delegates to yylo-ledger
yy benchmark --help     # delegates to yylo-benchmark
```

Delegation preserves arguments, stdin/stdout/stderr, cwd, exit status, and signals.

## Machine Output and Completion

```bash
# Strict stdout-only data channel
yy task status TASK_ID --format json --raw
yy merge status --format ndjson --raw
yy capabilities

# Shell completion
yy completion install
yy completion status
yy help
```

## Safety Invariants

1. `task start` freezes the protected target SHA and completes dependency hydration before reporting `WORKING`.
2. Product edits and focused tests happen only in the task worktree.
3. `finish` requires a clean committed tip and queues it; it does not merge.
4. `merge land` selects one immutable task source and composes in a private detached candidate with Git expected-old ref protection.
5. A conflict remains private to its task; preserve conflicts and dirty bytes — never reset, stash, force, rebase, squash, or clean to bypass them.
6. Git success and Ledger projection are separate; a projection retry never repeats Git integration.

## Sources

- Live README of [yylo-dev/yylo](https://github.com/yylo-dev/yylo) (MIT)
- npm: `@yylo/cli` — [package page](https://www.npmjs.com/package/%40yylo%2Fcli)
