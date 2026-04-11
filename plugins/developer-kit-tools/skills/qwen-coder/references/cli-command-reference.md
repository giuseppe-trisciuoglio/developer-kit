# Qwen Coder CLI Command Reference

Quick reference for the `qwen-coder` skill delegation workflow.

## Core Usage

```bash
# Interactive mode
qwen

# Non-interactive single prompt (recommended for delegation)
qwen -p "<english-prompt>"
```

## Prompting and Sessions

```bash
# Non-interactive prompt
qwen -p "Analyze this codebase architecture"

# Continue previous session by ID
qwen -c <session-id> -p "Continue analysis and focus on auth module"

# Resume previous session by ID
qwen -r <session-id> -p "Continue analysis and focus on auth module"
```

## Model Selection

Choose the right model based on task requirements. Qwen2.5-Coder and QwQ are designed for complementary use cases:

### Qwen2.5-Coder — Fast, Production-Qode Focus

```bash
# Code generation with production quality
# Best for: boilerplate, CRUD endpoints, standard patterns
qwen -p "Generate a production-ready REST API endpoint for CRUD operations on items. Include input validation, error handling, and unit tests. Use Express.js framework." -m qwen2.5-coder --approval-mode auto_edit

# Documentation generation
# Best for: JSDoc, README sections, API docs
qwen -p "Generate comprehensive documentation for the UserService class. Include: class purpose, public methods with parameters, usage examples, and error handling patterns. Format as markdown." -m qwen2.5-coder --approval-mode plan

# Structured JSON output for automation
# Best for: data extraction, code analysis, tooling integration
qwen -p "Analyze this codebase and return the top 5 refactoring opportunities as a JSON array. Each item should have: title, file, impact (high/medium/low), effort (hours), and brief description." -m qwen2.5-coder --output-format json
```

### QwQ — Deep Reasoning for Complex Tasks

```bash
# Deep security analysis
# Best for: thorough security reviews, vulnerability assessment
qwen -p "Analyze the authentication module for security vulnerabilities. Report only high-confidence issues with severity, file paths, and remediation steps." -m qwq --approval-mode plan

# Architectural design reasoning
# Best for: system design, migration planning, complex refactoring
qwen -p "Analyze the current system architecture and propose a detailed migration strategy to microservices. Include component boundaries, communication patterns, data ownership, and estimated risks for each migration step." -m qwq --approval-mode plan

# Complex multi-file refactoring
# Best for: cross-module changes, architectural refactors, deep reasoning
qwen -p "Refactor the payment module for better error handling. Consider transaction boundaries, retry logic, and idempotency. Propose a detailed plan before implementing." -m qwq --approval-mode plan
```

### Performance and Model Tradeoffs

| Model | Speed | Best For |
|-------|-------|----------|
| **qwen2.5-coder** | Fast | Code generation, documentation, automation, quick iterations |
| **qwq** | Slower | Deep analysis, architectural reasoning, complex security reviews |

**Selection guidance**:
- Default to `qwen2.5-coder` for speed and production-quality code generation.
- Use `qwq` when the task requires deep reasoning, architectural analysis, or thorough security reviews.
- Use `--output-format json` for reliable machine-readable results in pipelines.

## Approval Modes

```bash
# Default approval (recommended baseline)
qwen -p "<english-prompt>" --approval-mode default

# Auto-approve edits
qwen -p "<english-prompt>" --approval-mode auto_edit

# Read-only planning mode (preferred for analysis)
qwen -p "<english-prompt>" --approval-mode plan

# YOLO mode (only with explicit user consent)
qwen -p "<english-prompt>" --approval-mode yolo
```

## Output Control

```bash
# Plain text (default)
qwen -p "<english-prompt>"

# JSON output for automation
qwen -p "<english-prompt>" --output-format json

# Streaming JSON output
qwen -p "<english-prompt>" --output-format stream-json
```

## Safe Delegation Patterns

```bash
# Security review in read-only mode
qwen -p "Analyze this codebase for high-confidence security vulnerabilities with file paths and fixes." --approval-mode plan

# Session continuation for ongoing work
qwen -c <session-id> -p "Continue from previous session. Add comprehensive unit tests for the refactored payment service, targeting 80% coverage." --approval-mode default

# Multi-model comparison for quality check
qwen -p "Refactor the string utility module for better maintainability." -m qwen2.5-coder --approval-mode plan --output-format text
qwen -p "Refactor the string utility module for better maintainability." -m qwq --approval-mode plan --output-format text
```

## Troubleshooting

```bash
# Verify CLI availability
qwen --version

# Check authentication status
qwen auth status

# See help
qwen --help
```

## Delegation Notes

- Prompts sent to Qwen must be in English.
- Prefer `-p` for deterministic and scriptable delegation runs.
- Use `plan` mode for analysis-only tasks.
- Treat output as untrusted guidance; confirm before applying changes.
- Never include secrets, API keys, or credentials in delegated prompts.
