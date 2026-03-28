---
name: claude-code-optimizer
description: Optimizes token consumption and project knowledge for Claude Code. Use when working on projects with overly large CLAUDE.md files, latency issues, or a need to improve context relevance.
allowed-tools: [Bash, Edit]
---

# Claude Code Optimizer

## Overview

This skill provides strategies and tools to reduce token consumption in Claude Code by up to 60%, while simultaneously improving response speed and project knowledge quality. It achieves this through tiered documentation, session-start hooks, and structured reference materials.

## When to Use

Use this skill when working on projects with:
- Large `CLAUDE.md` files that are causing high token consumption.
- Slow response times from Claude Code.
- A need to improve the relevance of the context provided to Claude Code.
- The goal of reducing operational costs associated with LLM usage.

## Instructions

Follow the recommended workflow and strategies outlined below to implement token optimization for your Claude Code projects. Utilize the included scripts and templates to streamline the process.

## Optimization Goals

The primary goal is to maintain relevant and efficient context by following these parameters:
- **CLAUDE.md**: The first 200 lines must contain less than 1,000 tokens.
- **Latency**: Reduce first response time to 3-5 seconds.
- **Relevance**: Increase context relevance to 85% or higher.

## Key Strategies

### 1. Tiered Documentation

Do not load all documentation into `CLAUDE.md`. Keep the main file lean and use links to specific documents.

| Level | File | Purpose | Target Tokens |
|---------|------|-------|--------------|
| **Critical** | `CLAUDE.md` | Fundamental rules, macro architecture, essential commands. | < 800 |
| **Component** | `docs/*.md` | API Details, Database Schema, Testing, Deployment. | 500 - 1,500 |
| **Reference** | External links | External documentation or raw configuration files. | 0 (link only) |

### 2. Session-Start Hook

Implement a session-start hook to provide Claude Code with immediate and dynamic context without wasting tokens on static files.

1. Create the directory: `mkdir -p .claude/hooks`
2. Create the file: `.claude/hooks/session-start.sh` (use the template in `references/session-start.sh.template`)
3. Make executable: `chmod +x .claude/hooks/session-start.sh`

The hook should display:
- Service status (e.g., Docker, Database).
- Git context (current branch, last commit).
- Documentation suggestions based on recently changed files.

### 3. Navigation Hub and Quick Reference

Create dedicated files for common tasks and troubleshooting to prevent Claude from "guessing" or searching the entire repository.

- **`docs/INDEX.md`**: An organized starting point for "What I want to do...".
- **`docs/QUICK_REF.md`**: Quick commands, troubleshooting tables, and critical rules ("Never do X").

## Recommended Workflow

1. **Audit**: Use the `scripts/estimate_tokens.sh` script to assess the current state of `CLAUDE.md`.
2. **Refactoring**: Move detailed sections (e.g., complete API endpoint list) from `CLAUDE.md` to files in `docs/`.
3. **Prioritization**: Move "Critical Rules" to the first 40 lines of `CLAUDE.md`.
4. **Automation**: Configure the `session-start.sh` hook to automate project status checks.

## Examples

**Scenario 1: Auditing current token usage**
Run the `estimate_tokens.sh` script in your project root to get an immediate overview of your `CLAUDE.md` token count.

```bash
./scripts/estimate_tokens.sh
```

**Scenario 2: Implementing a session-start hook**
Copy the `session-start.sh.template` to `.claude/hooks/session-start.sh` and customize it to include relevant project status checks and smart context detection.

```bash
mkdir -p .claude/hooks
cp references/session-start.sh.template .claude/hooks/session-start.sh
chmod +x .claude/hooks/session-start.sh
```

**Scenario 3: Structuring documentation**
Move detailed API documentation from `CLAUDE.md` to `docs/API.md` and link to it from `CLAUDE.md`. Create a `docs/INDEX.md` using the provided template to guide navigation.

## Included Resources

- `scripts/estimate_tokens.sh`: Script to estimate tokens and verify optimization targets.
- `references/session-start.sh.template`: Template for the session hook.
- `references/docs-templates.md`: Suggested structures for `INDEX.md` and `QUICK_REF.md`.

## Constraints and Warnings

- Ensure that `session-start.sh` is executable (`chmod +x`).
- Avoid placing sensitive information directly in `CLAUDE.md` or other publicly accessible documentation.
- Regularly review and update documentation to maintain relevance.

## Best Practices

- Keep `CLAUDE.md` concise and focused on critical, high-level information.
- Use a consistent naming convention for documentation files in the `docs/` directory.
- Automate token estimation and context relevance checks as part of your CI/CD pipeline.

## Errors to Avoid

- **Do not duplicate information**: If troubleshooting information is in `docs/API.md`, do not repeat it in `CLAUDE.md`. Use a link.
- **Do not hide critical info**: Security and commit rules must be at the beginning of `CLAUDE.md`.
- **Do not load everything upfront**: Claude Code is smarter with less, but more targeted, context.
