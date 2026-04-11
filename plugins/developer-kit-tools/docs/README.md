# Tools Plugin Documentation

Complete documentation for the Developer Kit Tools Plugin.

## Contents

- **[CLI Delegation Guide](./guide-cli-delegation.md)** - Delegation patterns for gemini, copilot-cli, codex, and qwen-coder
- **[MCP Integration Guide](./guide-mcp-integration.md)** - Setup and usage for NotebookLM and SonarQube MCP

## Overview

The Tools Plugin provides external tool integration through two mechanisms:

| Integration Type | Skills | Description |
|-----------------|--------|-------------|
| **CLI Delegation** | `gemini`, `copilot-cli`, `codex`, `qwen-coder` | Delegate tasks to external AI CLI tools |
| **MCP Integration** | `notebooklm`, `sonarqube-mcp` | Connect to MCP servers for specialized capabilities |

## Use Cases

### CLI Delegation Tasks

- **Large codebase analysis**: Use `gemini` with gemini-3-pro for 1M token context windows
- **Multi-model comparison**: Use `copilot-cli` to compare Claude, GPT, and Gemini on the same task
- **Advanced code generation**: Use `codex` with gpt-5.3-codex for architectural design and complex refactoring
- **Deep reasoning**: Use `qwen-coder` with QwQ model for chain-of-thought analysis
- **Quick iterations**: Use `gemini-3-flash` or `qwen2.5-coder` for fast, cost-effective results

### MCP Integration Tasks

- **RAG knowledge queries**: Use `notebooklm` to query project documentation in NotebookLM
- **Research notebooks**: Create and manage notebooks with mixed sources (URLs, files, YouTube, Drive)
- **Artifact generation**: Generate audio podcasts, video explainers, and reports from notebooks
- **Quality gate verification**: Check if a project passes SonarQube/SonarCloud quality gates
- **Pre-push analysis**: Use `analyze_code_snippet` for shift-left security and quality checks
- **Issue discovery**: Search and triage issues by severity across projects

## Integration

This plugin integrates with:

- **developer-kit-core**: Required dependency
- **developer-kit-java**: For Java/Spring Boot code analysis with SonarQube
- **developer-kit-typescript**: For TypeScript/React code analysis with SonarQube
- **developer-kit-python**: For Python code analysis with SonarQube
- **developer-kit-devops**: For container scanning and CI/CD quality gates

## See Also

- [Gemini Skill](./skills/gemini/SKILL.md) - Detailed Gemini CLI reference
- [Copilot CLI Skill](./skills/copilot-cli/SKILL.md) - Detailed Copilot CLI reference
- [Codex Skill](./skills/codex/SKILL.md) - Detailed Codex CLI reference
- [Qwen Coder Skill](./skills/qwen-coder/SKILL.md) - Detailed Qwen Coder reference
- [NotebookLM Skill](./skills/notebooklm/SKILL.md) - Detailed NotebookLM reference
- [SonarQube MCP Skill](./skills/sonarqube-mcp/SKILL.md) - Detailed SonarQube MCP reference
- [Core Plugin Documentation](../../developer-kit-core/docs/) - Installation and core features
