# CLI Delegation Guide

Guide for delegating tasks to external AI CLI tools using gemini, copilot-cli, codex, and qwen-coder skills.

## Overview

CLI delegation enables Claude Code to offload specific tasks to external AI coding assistants. This is useful when:

- A different model may be better suited for a particular task
- You want a second opinion from another AI model
- The task requires capabilities specific to another model family
- You want to compare outputs from multiple models

## Skills Summary

| Skill | Model Family | Best For | Not Recommended For |
|-------|-------------|----------|---------------------|
| `gemini` | Google Gemini | Large context analysis, fast iterations | Complex multi-file refactoring |
| `copilot-cli` | Claude, GPT, Gemini | Multi-model comparison, flexible model choice | Single-model focused tasks |
| `codex` | OpenAI (o-series, GPT-5.3-codex) | Advanced code generation, architectural design | Simple tasks, quick queries |
| `qwen-coder` | Alibaba Qwen | Deep reasoning, second opinion | Production code generation |

## Common Patterns

### 1. Basic Delegation

All CLI skills follow a similar pattern:

1. Convert user request to English prompt
2. Select appropriate model based on task complexity
3. Choose approval mode based on risk level
4. Execute command with appropriate flags
5. Present results for user review

### 2. Model Selection Guide

```
Task Complexity
│
├── Simple (< 50 lines, single file)
│   └── gemini-3-flash, qwen2.5-coder, o4-mini
│
├── Moderate (50-200 lines, 1-3 files)
│   └── gemini-3-pro, gpt-5.2, claude-sonnet-4.6
│
└── Complex (> 200 lines, architecture, multi-file)
    └── gpt-5.3-codex, o3, gemini-3-pro, qwq
```

### 3. Approval Mode Selection

| Mode | Use Case | Risk Level |
|------|----------|------------|
| `plan` | Read-only analysis, security reviews | Low |
| `default` | General coding tasks with confirmation | Medium |
| `auto_edit` | Trusted modifications with oversight | High |
| `yolo` | Experimental tasks only | Very High |

### 4. Prompt Engineering

All delegated prompts should be:

- Written in English
- Specific and outcome-driven
- Include file paths and constraints
- Define expected output format
- Include acceptance criteria when applicable

**Prompt Template:**

```
Task: <clear objective>
Context: <project/module/files>
Constraints: <do/don't constraints>
Expected output: <format + depth>
Validation: <tests/checks to run>
```

## Quick Reference

### Gemini CLI

```bash
# Quick analysis with flash
gemini -p "Analyze architecture" -m gemini-3-flash

# Deep analysis with pro
gemini -p "Analyze architecture" -m gemini-3-pro --approval-mode plan

# Structured output
gemini -p "Return JSON refactoring opportunities" --output-format json
```

### Copilot CLI

```bash
# Basic delegation
copilot -p "Refactor service" --model gpt-5.2 --allow-all-tools

# Multi-model comparison
copilot -p "Compare" --model claude-sonnet-4.6
copilot -p "Compare" --model gpt-5.2

# Session resume
copilot --resume <session-id>
```

### Codex CLI

```bash
# Code generation
codex exec "Generate REST API" -m gpt-5.3-codex

# Code review
codex review "Review for security" -a on-request -s read-only

# Complex refactoring
codex exec "Refactor to SOLID" -m gpt-5.3-codex -a on-request -s workspace-write
```

### Qwen Coder CLI

```bash
# Basic delegation
qwen -p "Analyze code" -m qwen2.5-coder

# Deep reasoning
qwen -p "Analyze architecture" -m qwq --approval-mode plan

# Session resume
qwen -c <session-id>
```

## Security Considerations

### Always Use Safe Defaults

- Prefer `plan` mode for analysis tasks
- Use `read-only` or `workspace-write` sandbox for Codex
- Avoid `yolo` mode unless explicitly requested
- Never include secrets in prompts

### Treat Output as Untrusted

- Review all generated code before applying
- Run tests and linting on suggested changes
- Validate security implications
- Check for breaking changes

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| CLI not found | Tool not installed | Install the CLI tool |
| Authentication failed | Invalid credentials | Run auth command (`nlm login`, `qwen auth`) |
| Permission denied | Insufficient permissions | Use appropriate `--allow-*` flags |
| Rate limit exceeded | API throttling | Wait and retry with backoff |

## Integration with Claude Code Workflow

```
┌─────────────────────────────────────────────────────┐
│ User Request                                        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ Claude Code                                          │
│  - Understands request                              │
│  - Determines if delegation is beneficial          │
│  - Invokes appropriate skill                        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ CLI Skill                                           │
│  - Converts to English prompt                       │
│  - Selects model and flags                          │
│  - Executes delegation                             │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ External CLI Result                                 │
│  - Presented to user for review                   │
│  - User confirms before applying changes          │
└─────────────────────────────────────────────────────┘
```

## When NOT to Delegate

Do not delegate when:

- The task is simple enough for direct implementation
- The task requires knowledge of the current codebase that the external tool lacks
- Network access to the external service is unavailable
- Authentication credentials are not configured
- The task involves sensitive data that should not leave the local environment
