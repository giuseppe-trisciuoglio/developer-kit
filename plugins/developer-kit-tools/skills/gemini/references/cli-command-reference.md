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

Choose the right model based on task requirements. Gemini 3 Flash and Pro are designed for complementary use cases:

### Gemini 3 Flash — Speed-Focused Tasks

```bash
# Fast security scan on a large codebase (speed + cost-effective)
# Best for: quick triage, iterative analysis, budget-sensitive tasks
gemini -p "Analyze this repository for security vulnerabilities. Report only high-confidence issues with file paths, severity, and patch recommendations." -m gemini-3-flash --approval-mode plan

# Structured JSON output for automation pipelines (fast + predictable)
# Best for: data extraction, automated tooling, script integration
gemini -p "Return a JSON list of top 10 refactoring opportunities with fields: title, file, impact, effort." -m gemini-3-flash --output-format json

# Quick boilerplate generation (fast iteration)
# Best for: prototyping, scaffolding, rapid feedback
gemini -p "Generate a minimal Express.js REST endpoint for POST /items with input validation and a unit test. Keep the implementation concise and ready to paste." -m gemini-3-flash

# Cost-effective CSV/file analysis (low-cost summary)
# Best for: data triage, initial exploration, lightweight analysis
gemini -p "Summarize this CSV file's key statistics: row count, missing-value counts, and top 5 columns by variance. Provide a 6-line bullet summary suitable for quick triage." -m gemini-3-flash --output-format json --approval-mode plan

# Fast microcopy prototyping (quick iterations)
# Best for: UX copy, onboarding text, A/B test variants
gemini -p "Provide 3 short alternative microcopy options (<=20 words each) for an onboarding tooltip that explains account recovery. Include a one-line A/B test metric proposal for each option." -m gemini-3-flash
```

### Gemini 3 Pro — Power-Focused Tasks

```bash
# Architectural design analysis (complex reasoning + quality)
# Best for: system design, migration planning, high-stakes decisions
gemini -p "Analyze the current system architecture and propose a detailed migration strategy to a microservices architecture. Include component boundaries, communication patterns, data ownership, and estimated risks for each migration step." -m gemini-3-pro --approval-mode plan

# Comprehensive security audit (deep analysis + thoroughness)
# Best for: critical systems, compliance reviews, detailed assessments
gemini -p "Perform a thorough security audit of the authentication and authorization layer. Identify potential vulnerabilities, rate-limiting gaps, token handling weaknesses, and injection vectors. Provide severity ratings and specific remediation steps for each finding." -m gemini-3-pro --approval-mode plan

# Production-quality code generation (quality + robustness)
# Best for: production systems, critical modules, high-reliability code
gemini -p "Generate a production-ready TypeScript module for paginated API responses. Include input validation, error handling, retry logic with exponential backoff, and comprehensive unit tests with mocks. Follow best practices for error types, logging, and type safety." -m gemini-3-pro --approval-mode auto_edit

# Large-context refactor analysis (broad context + reasoning)
# Best for: monorepos, cross-module refactors, legacy system analysis
gemini -p "Propose a phased refactor plan for this monorepo. Include impacted modules, migration risks, and rollback procedures for each phase." -m gemini-3-pro --output-format json
```

### Performance and Cost Tradeoffs

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **gemini-3-flash** | Fast | Low | Iterations, prototyping, quick analysis, automation |
| **gemini-3-pro** | Slower | Higher | Complex reasoning, production-quality output, deep analysis |

**Selection guidance**:
- Start with `gemini-3-flash` for fast feedback and iterate to `gemini-3-pro` when depth or quality is needed.
- Use `gemini-3-pro` when output correctness is critical (security audits, production code, architectural decisions).
- Use `gemini-3-flash` with `--output-format json` for reliable machine-readable results in pipelines.

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
gemini -p "Propose a phased refactor plan for this monorepo. Include impacted modules and migration risks." -m gemini-3-pro --output-format json
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
