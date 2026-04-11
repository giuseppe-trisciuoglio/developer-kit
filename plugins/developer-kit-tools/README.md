# Developer Kit Tools Plugin

External tools integration for CLI utilities, APIs, and third-party services.

## Overview

The `developer-kit-tools` plugin provides delegation skills for external AI coding assistants and integration with third-party services through the Model Context Protocol (MCP). It enables Claude Code to leverage specialized tools for tasks that benefit from different models, large-context analysis, or dedicated service integrations.

## Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| `gemini` | Delegate tasks to Google Gemini CLI for large-context analysis and complex reasoning | "use gemini", "delegate to gemini", "gemini 3 flash/pro" |
| `copilot-cli` | Delegate tasks to GitHub Copilot CLI with multi-model support (Claude, GPT, Gemini) | "ask copilot", "delegate to copilot", "use copilot with sonnet/gpt" |
| `codex` | Delegate tasks to OpenAI Codex CLI for advanced code generation and analysis | "use codex", "codex exec", "codex review", "gpt-5.3-codex" |
| `qwen-coder` | Delegate tasks to Qwen Coder CLI for coding assistance using Qwen2.5-Coder and QwQ models | "use qwen", "delegate to qwen", "second opinion from qwen" |
| `notebooklm` | Integrate with Google NotebookLM for RAG, research notebooks, and AI-synthesized artifacts | "notebooklm", "nlm", "query notebook", "research notebook" |
| `sonarqube-mcp` | Integrate with SonarQube/SonarCloud for quality gates, issue discovery, and code analysis | "sonarqube", "quality gate", "sonar issues", "check sonar" |

## Quick Start

### CLI Delegation Skills (gemini, copilot-cli, codex, qwen-coder)

```bash
# Verify the CLI is installed
gemini --version
copilot --version
codex --version
qwen --version

# Basic delegation pattern
gemini -p "Analyze this codebase architecture"
copilot -p "Refactor this service" --model gpt-5.2 --allow-all-tools
codex exec "Review this code for security issues"
qwen -p "Generate unit tests for this module"
```

### MCP Integration Skills (notebooklm, sonarqube-mcp)

```bash
# NotebookLM - install and authenticate
uv tool install notebooklm-mcp-cli
nlm login

# SonarQube - set environment variables
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_URL="https://sonarqube.mycompany.com"
# or for SonarCloud:
export SONARQUBE_ORG="your-org-key"
```

## Plugin Structure

```
developer-kit-tools/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── .mcp.json                 # MCP server configuration
├── scripts/
│   ├── wrap-notebooklm-mcp.sh  # NotebookLM MCP wrapper
│   └── wrap-sonarqube-mcp.sh   # SonarQube MCP wrapper
└── skills/
    ├── gemini/               # Gemini CLI delegation
    ├── copilot-cli/         # GitHub Copilot CLI delegation
    ├── codex/               # OpenAI Codex CLI delegation
    ├── qwen-coder/          # Qwen Coder CLI delegation
    ├── notebooklm/          # NotebookLM RAG integration
    └── sonarqube-mcp/       # SonarQube/SonarCloud integration
```

## When to Use Each Skill

### Choose by Task Type

| Task | Recommended Skill |
|------|-------------------|
| Large codebase analysis (>100 files) | `gemini` (gemini-3-pro with 1M token context) |
| Quick prototyping and iterations | `gemini` (gemini-3-flash) or `qwen-coder` |
| Multi-model comparison on same task | `copilot-cli` (supports Claude, GPT, Gemini) |
| Advanced code generation and architectural design | `codex` (gpt-5.3-codex) |
| Code review with specialized review command | `codex` (`codex review`) |
| Second opinion or alternative reasoning | `qwen-coder` (QwQ deep reasoning) |
| Querying RAG knowledge bases | `notebooklm` |
| Generating podcasts/reports from documentation | `notebooklm` |
| Pre-commit/pre-push code quality checks | `sonarqube-mcp` |
| Quality gate verification before merge | `sonarqube-mcp` |

### Choose by Model Preference

| Model Family | Skill |
|--------------|-------|
| Google Gemini | `gemini` (gemini-3-flash, gemini-3-pro) |
| Anthropic Claude | `copilot-cli` (claude-sonnet-4.6, claude-opus-4.6, claude-haiku-4.5) |
| OpenAI GPT | `copilot-cli` (gpt-5.2) or `codex` (gpt-5.3-codex) |
| OpenAI o-series | `codex` (o3, o4-mini) |
| Alibaba Qwen | `qwen-coder` (qwen2.5-coder, qwq) |

## MCP Servers

The plugin includes MCP server wrappers that handle dependency checking:

### NotebookLM MCP

- **Wrapper**: `scripts/wrap-notebooklm-mcp.sh`
- **Requires**: `uv` and `notebooklm-mcp-cli`
- **Authentication**: Chrome cookie extraction via `nlm login`
- **Tools**: Notebook management, source handling, studio content generation, research

### SonarQube MCP

- **Wrapper**: `scripts/wrap-sonarqube-mcp.sh`
- **Requires**: Docker and `SONARQUBE_TOKEN` / `SONARQUBE_URL` or `SONARQUBE_ORG`
- **Tools**: Quality gate status, issue search, code snippet analysis, rule documentation

## Requirements

- `developer-kit-core` (required dependency)
- For CLI delegation skills: respective CLI installed (`gemini`, `copilot`, `codex`, `qwen`)
- For NotebookLM: `uv` and `notebooklm-mcp-cli`
- For SonarQube: Docker and SonarQube/SonarCloud credentials

## Documentation

- [Gemini Skill](./skills/gemini/SKILL.md) - Gemini CLI delegation patterns
- [Copilot CLI Skill](./skills/copilot-cli/SKILL.md) - Copilot CLI delegation patterns
- [Codex Skill](./skills/codex/SKILL.md) - Codex CLI delegation patterns
- [Qwen Coder Skill](./skills/qwen-coder/SKILL.md) - Qwen Coder CLI delegation patterns
- [NotebookLM Skill](./skills/notebooklm/SKILL.md) - NotebookLM RAG integration
- [SonarQube MCP Skill](./skills/sonarqube-mcp/SKILL.md) - SonarQube/SonarCloud integration
