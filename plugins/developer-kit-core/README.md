# Developer Kit Core

Core agents, commands, skills, and hooks required by all Developer Kit plugins.

## Overview

The `developer-kit` plugin (directory: `developer-kit-core/`) provides the foundational components shared across all Developer Kit plugins. This plugin is **required** by all other plugins in the Developer Kit marketplace.

> **Backward Compatibility Note:** The plugin name in the manifest is `developer-kit` (not `developer-kit-core`) to maintain compatibility with the existing `devkit.*` command prefixes. The directory is named `developer-kit-core` for structural clarity.

---

## Components

| Component Type | Count | Description |
|----------------|-------|-------------|
| **Agents** | 7 | General-purpose AI assistants for code analysis, review, refactoring, architecture, debugging, documentation, and pattern learning |
| **Commands** | 16 | Reusable workflows for feature development, refactoring, debugging, documentation, GitHub integration, and long-running agent sessions |
| **Skills** | 6 | Specialized capabilities for ADR drafting, memory management, documentation updates, draw.io diagrams, GitHub issues, and project pattern learning |
| **Hooks** | 1 | Security hook that prevents destructive Bash commands |

---

## Agents

Agents are specialized AI assistants with dedicated contexts, custom prompts, and specific tool access. Invoke them using the `Agent` tool with `subagent_type`.

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `general-code-explorer` | Deep codebase analysis | Tracing execution paths, mapping architecture layers, understanding how features are implemented |
| `general-code-reviewer` | Code review | Reviewing code changes for quality, bugs, logic errors, security, and best practices (reports only issues with confidence >= 80%) |
| `general-refactor-expert` | Code refactoring | Improving code quality and maintainability while preserving functionality (SOLID patterns, clean code principles) |
| `general-software-architect` | Architecture design | Planning new features, designing system architecture, creating implementation blueprints |
| `general-debugger` | Debugging | Root cause analysis, tracing execution paths, identifying failure points, proposing targeted fixes |
| `document-generator-expert` | Documentation | Creating professional technical and business documents (assessments, specs, reports, process docs) |
| `learn-analyst` | Pattern extraction | Extracting development patterns and conventions from codebase analysis for the learn skill |

### Invocation Example

```python
Agent(
    subagent_type="general-code-explorer",
    prompt="Trace the user authentication flow in this codebase"
)
```

---

## Commands

Commands are reusable workflows invoked with `/developer-kit:devkit.<command-name>`. They guide Claude through specific procedures with mandatory confirmation gates.

### Core Workflows

| Command | Purpose | Arguments |
|---------|---------|-----------|
| `devkit.feature-development` | Guided feature implementation | `[--lang=...] [feature-description]` |
| `devkit.refactor` | Guided code refactoring | `[--lang=...] [--scope=...] [refactor-description]` |
| `devkit.fix-debugging` | Guided bug fixing | `[--lang=...] [issue-description]` |
| `devkit.verify-skill` | Validate skill against DevKit standards | `[skill-name]` |

### Documentation Generation

| Command | Purpose |
|---------|---------|
| `devkit.generate-document` | Generate professional documents (assessments, features, analysis, process, custom) |
| `devkit.generate-changelog` | Generate and manage changelog following Keep a Changelog standard |
| `devkit.generate-security-assessment` | Generate security assessment document after audit |

### GitHub Integration

| Command | Purpose |
|---------|---------|
| `devkit.github.create-pr` | Create GitHub pull request with branch creation and commits |
| `devkit.github.review-pr` | Comprehensive PR review with code quality, security, and best practices |

### Long-Running Agent (LRA) Workflow

| Command | Purpose |
|---------|---------|
| `devkit.lra.init` | Initialize LRA environment (feature list, progress file, init.sh) |
| `devkit.lra.add-feature` | Add a new feature to the feature list |
| `devkit.lra.checkpoint` | Create checkpoint (commit changes, update progress, leave clean state) |
| `devkit.lra.mark-feature` | Mark feature as completed (passed) or failed |
| `devkit.lra.recover` | Recover from broken state (diagnose, revert if needed) |
| `devkit.lra.start-session` | Start coding session (read progress, choose next feature, run tests) |
| `devkit.lra.status` | Show project status (features progress, recent activity, next priorities) |

### Example Usage

```bash
/developer-kit:devkit.lra.init "Chat app with user auth and AI responses"
/developer-kit:devkit.lra.start-session
/developer-kit:devkit.lra.checkpoint "Implemented user registration"
/developer-kit:devkit.github.create-pr
```

---

## Skills

Skills are specialized capabilities invoked with `/skill-name`. Each skill includes detailed reference documentation.

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `adr-drafting` | Create Architecture Decision Records | User decides on architectural change, needs to document technical rationale |
| `memory-md-management` | Manage CLAUDE.md files | User asks to check, audit, update, improve, or validate project memory files |
| `docs-updater` | Update documentation | Preparing release, maintaining documentation sync, updating changelog |
| `drawio-logical-diagrams` | Create draw.io diagrams | Creating logical flow diagrams, system architecture, BPMN, UML, data flow |
| `github-issue-workflow` | Resolve GitHub issues | User asks to resolve, implement, work on, fix, or close a GitHub issue |
| `learn` | Extract project patterns | User asks to "learn from project", "extract project rules", "analyze conventions" |

### Example Usage

```bash
/adr-drafting
/docs-updater
/learn
/drawio-logical-diagrams
/github-issue-workflow GH-123
```

---

## Hooks

### prevent-destructive-commands

A security hook that prevents execution of destructive Bash commands.

**Location:** `hooks/prevent-destructive-commands.py`

**Configuration:** `hooks/hooks.json`

**Security Features:**
- Prevents `rm`, `unlink`, `rmdir`, `shred` targeting paths outside working directory
- Blocks access to sensitive files (`.env`, SSH keys, AWS credentials, private keys)
- Prevents AWS CLI destructive operations (s3 rm, ec2 terminate-instances, etc.)
- Prevents Docker destructive operations (container rm, volume rm, etc.)
- Prevents Git destructive operations (reset --hard, clean, push --force, rebase, etc.)
- Handles wrapper commands (sudo, env, nice, etc.), shell invocations (bash -c, sh -c, etc.), and find -exec delegation

---

## Language/Framework Support

Commands support `--lang` parameter to use specialized language-specific agents:

| Language | Agents Used |
|----------|-------------|
| Java/Spring Boot | `spring-boot-backend-development-expert`, `java-software-architect-review` |
| TypeScript/NestJS | `typescript-software-architect-review`, `nestjs-backend-development-expert` |
| React | `react-frontend-development-expert`, `react-software-architect-review` |
| Python | `python-software-architect-expert`, `python-code-review-expert` |
| AWS | `aws-solution-architect-expert`, `aws-cloudformation-devops-expert` |
| General | `general-code-explorer`, `general-software-architect`, `general-code-reviewer` |

---

## Related Plugins

### developer-kit-specs

Specifications-driven development commands have been extracted to a dedicated plugin.

**Commands:** `/specs:brainstorm`, `/specs:spec-to-tasks`, `/specs:task-implementation`, `/specs:task-manage`, `/specs:task-review`

**Skills:** `knowledge-graph` — Persistent Knowledge Graph for specifications

**Installation:** For teams using specifications-driven development, install both `developer-kit-core` and `developer-kit-specs`.

---

## Dependencies

None — this is the foundational plugin upon which all other Developer Kit plugins depend.
