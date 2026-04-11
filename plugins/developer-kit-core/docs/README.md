# Developer Kit Core Documentation

Guides for using the Developer Kit Core plugin, the foundational component required by all other Developer Kit plugins.

---

## Quick Start

1. **Install**: See [Installation Guide](./installation.md)
2. **Agents**: Explore available agents in [Agent Guide](./guide-agents.md)
3. **Commands**: Try core commands in [Command Guide](./guide-commands.md)
4. **LRA Workflow**: Learn the Long-Running Agent workflow in [LRA Workflow Guide](./guide-lra-workflow.md)

---

## Available Documentation

### Getting Started

- **[Installation Guide](./installation.md)** — Installation instructions for Claude Code, GitHub Copilot CLI, OpenCode CLI, and Codex CLI

### Core Guides

- **[Agent Guide](./guide-agents.md)** — All 7 general-purpose agents (code exploration, review, refactoring, architecture, debugging, documentation, pattern learning)
- **[Command Guide](./guide-commands.md)** — All 16 commands organized by category (workflows, documentation, GitHub, LRA)
- **[LRA Workflow Guide](./guide-lra-workflow.md)** — Long-running agent session management with checkpoints and recovery

---

## Plugin Components

### Agents (7)

| Agent | Purpose |
|-------|---------|
| `general-code-explorer` | Deep codebase analysis and architecture mapping |
| `general-code-reviewer` | Code review with confidence-based filtering |
| `general-refactor-expert` | Code refactoring with clean code principles |
| `general-software-architect` | Feature architecture design and implementation planning |
| `general-debugger` | Root cause analysis and targeted debugging |
| `document-generator-expert` | Professional document generation |
| `learn-analyst` | Project pattern extraction for conventions |

### Commands (16)

| Category | Commands |
|----------|----------|
| **Core Workflows** | `devkit.feature-development`, `devkit.refactor`, `devkit.fix-debugging`, `devkit.verify-skill` |
| **Documentation** | `devkit.generate-document`, `devkit.generate-changelog`, `devkit.generate-security-assessment` |
| **GitHub Integration** | `devkit.github.create-pr`, `devkit.github.review-pr` |
| **LRA Workflow** | `devkit.lra.init`, `devkit.lra.add-feature`, `devkit.lra.checkpoint`, `devkit.lra.mark-feature`, `devkit.lra.recover`, `devkit.lra.start-session`, `devkit.lra.status` |

### Skills (6)

| Skill | Purpose |
|-------|---------|
| `adr-drafting` | Architecture Decision Record creation |
| `memory-md-management` | CLAUDE.md file management and optimization |
| `docs-updater` | Automated documentation updates from git changes |
| `drawio-logical-diagrams` | draw.io diagram creation |
| `github-issue-workflow` | GitHub issue resolution workflow |
| `learn` | Project pattern learning and rule generation |

### Hooks (1)

| Hook | Purpose |
|------|---------|
| `prevent-destructive-commands` | Security hook blocking destructive Bash commands |

---

## Plugin Structure

```
developer-kit-core/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── agents/                   # 7 general-purpose agents
├── commands/                # 16 commands
│   ├── documentation/        # 3 documentation commands
│   └── lra/                  # 7 LRA commands
├── skills/                   # 6 skills
│   └── [skill-name]/
│       ├── SKILL.md
│       └── references/        # Supporting documentation
├── hooks/                    # Security hooks
│   ├── hooks.json
│   └── prevent-destructive-commands.py
└── docs/                     # This documentation
```

---

## See Also

### Other Developer Kit Plugins

- **[developer-kit-java](../developer-kit-java/)** — Java/Spring Boot/LangChain4J/AWS Lambda
- **[developer-kit-typescript](../developer-kit-typescript/)** — TypeScript/NestJS/React/Next.js
- **[developer-kit-python](../developer-kit-python/)** — Python development
- **[developer-kit-php](../developer-kit-php/)** — PHP/WordPress
- **[developer-kit-aws](../developer-kit-aws/)** — AWS/CloudFormation
- **[developer-kit-ai](../developer-kit-ai/)** — Prompt engineering/RAG
- **[developer-kit-devops](../developer-kit-devops/)** — Docker/GitHub Actions
- **[developer-kit-specs](../developer-kit-specs/)** — Specifications-driven development
