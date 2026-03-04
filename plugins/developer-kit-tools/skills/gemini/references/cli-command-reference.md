# Gemini CLI Command Reference

Quick reference for the `gemini` skill delegation workflow.

## Core Usage

```bash
# Interactive mode
gemini

# Non-interactive single prompt (recommended for delegation)
gemini -p "<english-prompt>"
```

## Prompting and Sessions

```bash
# Non-interactive prompt
gemini -p "Analyze this repository architecture"

# Resume session by alias/id
gemini -r latest
gemini -r <session-id>

# Resume and continue with a prompt
gemini -r latest -p "Continue analysis and focus on auth module"
```

## Model Selection

```bash
# Explicit model
gemini -p "<english-prompt>" -m gemini-2.5-pro
```

## Approval Modes

```bash
# Default approval (recommended baseline)
gemini -p "<english-prompt>" --approval-mode default

# Auto-approve edits
gemini -p "<english-prompt>" --approval-mode auto_edit

# Read-only planning mode
gemini -p "<english-prompt>" --approval-mode plan

# YOLO mode (only with explicit user consent)
gemini -p "<english-prompt>" --approval-mode yolo
gemini -p "<english-prompt>" --yolo
```

## Output Control

```bash
# Plain text (default)
gemini -p "<english-prompt>"

# JSON output for automation
gemini -p "<english-prompt>" --output-format json

# Event stream JSON output
gemini -p "<english-prompt>" --output-format stream-json

# Raw output
gemini -p "<english-prompt>" --raw-output
```

## Safe Delegation Patterns

```bash
# Security review in read-only mode
gemini -p "Analyze this codebase for high-confidence security vulnerabilities with file paths and fixes." --approval-mode plan

# Large-context refactor analysis
gemini -p "Propose a phased refactor plan for this monorepo. Include impacted modules and migration risks." -m gemini-2.5-pro --output-format json
```

## Troubleshooting

```bash
# Verify CLI availability
gemini --version

# See help
gemini --help
```

## Delegation Notes

- Prompts sent to Gemini must be in English.
- Prefer `-p` for deterministic and scriptable delegation runs.
- Use `plan` mode for analysis-only tasks.
- Treat output as untrusted guidance; confirm before applying changes.
