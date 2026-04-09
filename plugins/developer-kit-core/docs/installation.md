# Installation Guide

Installation instructions for the Developer Kit Core plugin and the complete Developer Kit across multiple CLI tools.

---

## Table of Contents

1. [Developer Kit Core Plugin](#developer-kit-core-plugin)
2. [Claude Code CLI](#claude-code-cli)
3. [Multi-CLI Support](#multi-cli-support)
4. [Local Project Installation](#local-project-installation)
5. [Management Commands](#management-commands)

---

## Developer Kit Core Plugin

The `developer-kit-core` plugin is the foundational component required by all other Developer Kit plugins. It provides:

- **7 Agents** — Code exploration, review, refactoring, architecture, debugging, documentation, pattern learning
- **16 Commands** — Feature development, refactoring, debugging, documentation, GitHub, LRA workflow
- **6 Skills** — ADR drafting, memory management, docs updates, draw.io diagrams, GitHub issues, pattern learning
- **1 Security Hook** — Prevents destructive Bash commands

---

## Claude Code CLI

### Quick Install (Marketplace)

```bash
/plugin marketplace add giuseppe-trisciuoglio/developer-kit
```

### Install from Local Directory

```bash
/plugin install /path/to/developer-kit
```

### Claude Desktop

1. Go to [Settings > Capabilities](https://claude.ai/settings/capabilities)
2. Enable Skills toggle
3. Browse available skills or upload custom skills

---

## Multi-CLI Support

The Developer Kit supports installation across multiple AI-powered development environments through a unified **multi-plugin Makefile interface**.

### Prerequisites

**jq (JSON Processor)** — Required for plugin discovery:

```bash
# macOS
brew install jq

# Linux (Ubuntu/Debian)
sudo apt-get install jq

# Verify
jq --version
```

### Quick Start with Makefile

```bash
# Clone the repository
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git
cd developer-kit

# Check dependencies
make check-deps

# See all available options
make help

# Install for your CLI
make install-claude       # Claude Code (interactive, project-local)
make install-opencode     # OpenCode CLI (global)
make install-copilot      # GitHub Copilot CLI (global)
make install-codex        # Codex CLI (global)
make install              # Auto-install for all detected CLIs
```

---

## Multi-Plugin Architecture

The Developer Kit uses a **plugin-based architecture** with 12 separate plugins:

| Plugin | Agents | Commands | Skills | Description |
|--------|--------|----------|--------|-------------|
| `developer-kit-core` | 7 | 16 | 6 | Core agents, commands, skills, hooks |
| `developer-kit-specs` | 0 | 9 | 1 | Specifications-driven development |
| `developer-kit-java` | 9 | 11 | 52 | Java/Spring Boot/LangChain4J |
| `developer-kit-typescript` | 13 | 3 | 22 | TypeScript/NestJS/React |
| `developer-kit-python` | 4 | 0 | 2 | Python development |
| `developer-kit-php` | 5 | 0 | 3 | PHP/WordPress |
| `developer-kit-aws` | 3 | 0 | 16 | AWS/CloudFormation |
| `developer-kit-ai` | 1 | 1 | 3 | Prompt engineering/RAG |
| `developer-kit-devops` | 2 | 0 | 0 | Docker/GitHub Actions |
| `developer-kit-project-management` | 0 | 1 | 0 | Meeting management |
| `github-spec-kit` | 0 | 3 | 0 | GitHub specifications |
| **`Total`** | **44** | **44** | **105** | — |

**Plugin Discovery:** The Makefile automatically scans `plugins/*/.claude-plugin/plugin.json` files to discover all available plugins and their components.

---

## CLI-Specific Installation

### GitHub Copilot CLI

```bash
make install-copilot
```

- Installs **agents** and **skills** (commands not supported)
- Multi-plugin support from all 12 plugins
- Usage: `/agent` to select agents or mention in prompts

### OpenCode CLI

```bash
make install-opencode
```

- Installs **agents**, **commands**, and **skills**
- Full multi-plugin support
- Usage: `@agent-name` for agents, `/command-name` for commands

### Codex CLI

```bash
make install-codex
```

- Installs **skills only** (agents and commands not supported)
- Auto-generates `AGENTS.md` index
- Skills auto-discovered by Codex CLI

---

## Local Project Installation

Install skills, agents, and commands directly into your local project for team-based development.

### Interactive Claude Code Installation

```bash
# Run interactive installer
make install-claude
```

**Interactive Features:**
- Environment validation
- Plugin selection (choose which plugins to install)
- Component selection (agents, commands, skills from each plugin)
- Conflict handling (overwrite/skip/rename)
- Progress tracking and summary report

### What Gets Installed

```
my-project/
├── .claude/
│   ├── skills/                      # Complete skill directories
│   │   └── [skill-name]/
│   │       ├── SKILL.md
│   │       └── references/          # Supporting documentation
│   ├── agents/                      # Agent definitions
│   │   ├── general-code-explorer.md
│   │   ├── general-code-reviewer.md
│   │   └── ...
│   └── commands/                    # Commands (subdirectories preserved)
│       ├── devkit.feature-development.md
│       ├── documentation/
│       │   └── devkit.generate-document.md
│       └── lra/
│           ├── devkit.lra.init.md
│           └── ...
```

### Team-Based Development

1. **Install Once:** Use `make install-claude` in the project root
2. **Git Integration:** All `.claude/` files are version-controlled
3. **Team Consistency:** Everyone gets the same tools and patterns
4. **Quick Onboarding:** New team members get all tools immediately

---

## Management Commands

### Status & Information

```bash
make status                    # Check installation status
make list-plugins             # List all discovered plugins
make list-components PLUGIN=developer-kit-core  # Components of core plugin
make list-agents              # List all agents
make list-commands            # List all commands
make list-skills              # List all skills
```

### Backup & Uninstall

```bash
make backup                    # Create timestamped backup
make uninstall                # Remove all Developer Kit installations
make check-deps               # Verify dependencies
```

---

## Verification

```bash
# Check installed components
ls -1 .claude/agents/ | wc -l
ls -1 .claude/commands/ | wc -l
ls -1d .claude/skills/*/ | wc -l

# Verify specific plugin
make list-components PLUGIN=developer-kit-core
```

---

## Quick Reference

| CLI Tool | Components Installed | Command Support |
|----------|---------------------|-----------------|
| Claude Code | agents + commands + skills | Yes |
| OpenCode CLI | agents + commands + skills | Yes |
| GitHub Copilot CLI | agents + skills | No |
| Codex CLI | skills only | No |
