# Installation Guide

Complete installation instructions for Developer Kit across multiple CLI tools and IDEs.

---

## Table of Contents

1. [Claude Code CLI](#claude-code-cli)
2. [Claude Desktop](#claude-desktop)
3. [Multi-CLI Support](#multi-cli-support)
4. [Local Project Installation](#local-project-installation)
5. [Management Commands](#management-commands)

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

---

## Claude Desktop

1. Go to [Settings > Capabilities](https://claude.ai/settings/capabilities)
2. Enable Skills toggle
3. Browse available skills or upload custom skills
4. Start using in conversations

---

## Multi-CLI Support

The Developer Kit supports installation across multiple AI-powered development environments through a unified **multi-plugin Makefile interface**.

### Prerequisites

**jq (JSON Processor)** - Required for plugin discovery
```bash
# macOS
brew install jq

# Linux (Ubuntu/Debian)
sudo apt-get install jq

# Verify installation
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

# Discover available plugins
make list-plugins

# Install for your specific CLI tool
make install-claude       # For Claude Code (interactive, project-local)
make install-opencode     # For OpenCode CLI (global)
make install-copilot      # For GitHub Copilot CLI (global)
make install-codex        # For Codex CLI (global)
make install              # Auto-install for all detected CLIs
```

### What's New in Multi-Plugin Architecture

The Developer Kit now uses a **plugin-based architecture** with 10 separate plugins:

- **developer-kit** - Core agents, commands, and skills (6 agents, 17 commands, 3 skills)
- **developer-kit-java** - Java/Spring Boot/LangChain4J/AWS Lambda integration (9 agents, 11 commands, 49 skills)
- **developer-kit-typescript** - TypeScript/NestJS/React/Next.js/Drizzle/Monorepo (13 agents, 3 commands, 22 skills)
- **developer-kit-python** - Python/AWS Lambda capabilities (4 agents, 2 skills)
- **developer-kit-php** - PHP/WordPress/AWS Lambda (5 agents, 3 skills)
- **developer-kit-aws** - AWS/CloudFormation (3 agents, 16 skills)
- **developer-kit-ai** - Prompt engineering/RAG/chunking (1 agent, 1 command, 3 skills)
- **developer-kit-devops** - Docker/GitHub Actions (2 agents)
- **developer-kit-project-management** - LRA workflow (1 command)
- **github-spec-kit** - GitHub specifications (3 commands)

**Total Components:** 43 agents, 36 commands, 96 skills across all plugins

| Plugin | Agents | Commands | Skills |
|--------|--------|----------|--------|
| developer-kit | 6 | 17 | 3 |
| developer-kit-java | 9 | 11 | 49 |
| developer-kit-typescript | 13 | 3 | 22 |
| developer-kit-python | 4 | 0 | 2 |
| developer-kit-php | 5 | 0 | 3 |
| developer-kit-aws | 3 | 0 | 16 |
| developer-kit-ai | 1 | 1 | 3 |
| developer-kit-devops | 2 | 0 | 0 |
| developer-kit-project-management | 0 | 1 | 0 |
| github-spec-kit | 0 | 3 | 0 |
| **Total** | **43** | **36** | **96** |

**Plugin Discovery:** The Makefile automatically scans `plugins/*/.claude-plugin/plugin.json` files to discover all available plugins and their components (agents, commands, skills).

### Supported CLI Tools

#### GitHub Copilot CLI

```bash
make install-copilot

# Installation creates:
# ~/.copilot/agents/          # All discovered agents from plugins
# ~/.copilot/skills/          # All discovered skills from plugins
```

**Features:**
- **Multi-Plugin Support**: Automatically installs agents and skills from all 10 plugins
- **Specialized Agents**: Code review, architecture, security, testing, debugging experts
- **Usage**: `/agent` to select agents or mention in prompts
- **Integration**: Works with Copilot's native agent system
- **⚠️ Important**: Commands are NOT installed (Copilot CLI does not support commands)

#### OpenCode CLI

```bash
make install-opencode

# Installation creates:
# ~/.config/opencode/agent/     # All discovered agents from plugins
# ~/.config/opencode/command/  # All discovered commands from plugins (with subdirs)
# ~/.config/opencode/skills/   # All discovered skills from plugins
```

**Features:**
- **Multi-Plugin Support**: Automatically installs agents, commands, and skills from all 10 plugins
- **Development Agents**: Full suite of specialized agents from all plugins
- **Custom Commands**: All commands with subdirectory structure preserved
- **Usage**: `@agent-name` for agents, `/command-name` for commands
- **Discovery**: Tab completion and command discovery
- **Complete Installation**: All component types (agents + commands + skills)

#### Codex CLI

```bash
make install-codex

# Installation creates:
# ~/.codex/skills/           # All discovered skills from plugins
# ~/.codex/AGENTS.md         # Auto-generated index of all skills
```

**Features:**
- **Multi-Plugin Support**: Automatically installs skills from all 10 plugins
- **Skills-Only**: Installs skills only (agents and commands not supported by Codex)
- **Auto-Generated Index**: Creates `AGENTS.md` with complete skill descriptions
- **Usage**: Skills are auto-discovered by Codex CLI
- **⚠️ Important**: Agents and commands are NOT installed (Codex CLI does not support them)

---

## Local Project Installation

Install skills, agents, and commands directly into your local project for team-based development.

### Interactive Claude Code Installation

```bash
# Clone the repository
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git
cd developer-kit

# Run interactive installer for Claude Code
make install-claude
```

**Interactive Features (Multi-Plugin):**
- ✅ **Environment Validation**: Confirms Claude Code usage
- 📦 **Plugin Selection**: Choose which plugins to install (all 10 available)
- 🎯 **Component Selection**: Automatically installs all components (agents, commands, skills) from selected plugins
- 🛡️ **Conflict Handling**: Decide how to handle existing files (overwrite/skip/rename)
- 📊 **Progress Tracking**: Real-time installation progress
- 📋 **Summary Report**: Complete installation summary with file counts

**Plugin Selection Example:**
```bash
$ make install-claude
...
Step 2: Available Plugins

  1) developer-kit
     Core agents and commands required by all Developer Kit plugins
     Components: 6 agents, 17 commands, 0 skills

  2) developer-kit-java
     Comprehensive Java development toolkit...
     Components: 9 agents, 11 commands, 47 skills

  3) developer-kit-typescript
     TypeScript/JavaScript full-stack development...
     Components: 13 agents, 3 commands, 5 skills

  ...

Select plugins to install (comma-separated numbers, or 'all'): 1,2
```

### Example Installation Flow

```bash
$ make install-claude

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      Claude Code Interactive Developer Kit Installer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ This installer is designed for Claude Code only.

Are you installing for Claude Code? (y/N): y

Step 1: Target Project
Enter the project path (absolute or relative): ~/my-spring-project

Step 2: Select Skill Categories
Available skill categories:
  1) AWS Java Skills (10 skills)
  2) AI Skills (3 skills)
  3) JUnit Test Skills (15 skills)
  4) LangChain4j Skills (8 skills)
  5) Spring Boot Skills (13 skills)
  6) Spring AI Skills (1 skill)
  7) All Skills
  8) None (skip skills)

Select categories (comma-separated, e.g., 1,4,5): 4,5

Step 3: Select Agents
  1) All Agents (14 available)
  2) Select specific agents
  3) None (skip agents)
Choose option [1-3]: 2

Available agents:
   1) java-documentation-specialist
   2) java-refactor-expert
   3) java-security-expert
   ...
Select agents (comma-separated numbers, or type 'all'): 1,3

Step 4: Select Commands
  1) All Commands (32 available)
  2) Select specific commands
  3) None (skip commands)
Choose option [1-3]: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Installation...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Installing Skills...
  Category: LangChain4j Skills
    ✓ Installed: langchain4j-ai-services-patterns
    ✓ Installed: langchain4j-mcp-server-patterns
  Category: Spring Boot Skills
    ✓ Installed: spring-boot-actuator
    ✓ Installed: spring-boot-cache
    ...

Installing Selected Agents...
  ✓ Installed: java-documentation-specialist.md
  ✓ Installed: java-security-expert.md

Installing All Commands...
  ✓ Installed: devkit.java.code-review.md
  ✓ Installed: devkit.java.write-unit-tests.md
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Installation Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target directory: /Users/you/my-spring-project/.claude/
Files installed:  52
Files skipped:    0

Next Steps:
  1. Navigate to your project: cd /Users/you/my-spring-project
  2. Start Claude Code in the project directory
  3. Your skills, agents, and commands are now available!
```

### What Gets Installed

```
my-project/
├── .claude/
│   ├── skills/                      # Complete skill directories
│   │   └── [skill-name]/
│   │       ├── SKILL.md
│   │       ├── references/          # Documentation
│   │       ├── assets/              # Scripts, templates
│   │       └── ...                  # All subdirectories preserved
│   ├── agents/                      # Flattened agent files
│   │   ├── aws-solution-architect-expert.md
│   │   ├── java-code-review-expert.md
│   │   ├── spring-boot-backend-development-expert.md
│   │   └── ... (all agents from selected plugins)
│   └── commands/                    # Commands with subdirs preserved
│       ├── devkit.java.code-review.md
│       ├── devkit.lra.init.md
│       ├── lra/
│       │   └── devkit.lra.start-session.md
│       └── ... (all commands from selected plugins)
```

**Important Notes:**
- **Skills**: Installed with **complete directory structure** (references/, assets/, scripts/, templates/)
- **Agents**: Flattened structure (all `.md` files directly in `agents/`)
- **Commands**: Subdirectory structure **preserved** (e.g., `commands/lra/file.md`)

### Team-Based Development

**For Teams Sharing Projects:**

1. **Install Once**: Use `make install-claude` in the project root
2. **Git Integration**: All `.claude/` files are version-controlled
3. **Team Consistency**: Everyone gets the same tools and patterns
4. **Custom Skills**: Create project-specific skills shared with team

**Benefits:**
- 🔄 **Consistent Tooling**: Team uses same agents, skills, commands
- 📚 **Project Context**: Skills understand your specific project structure
- 🎯 **Domain-Specific**: Tailored to your business domain and patterns
- 🚀 **Quick Onboarding**: New team members get all tools immediately

---

## Management Commands

### Status & Information

```bash
# Check installation status for all CLIs
make status

# List all discovered plugins
make list-plugins

# List components of a specific plugin
make list-components PLUGIN=developer-kit-java

# List all available agents
make list-agents

# List all available commands
make list-commands

# List all available skills
make list-skills
```

### Backup & Uninstall

```bash
# Create backup before installing
make backup
# Creates timestamped backup in ~/.devkit-backups/YYYYMMDD_HHMMSS/

# Remove all Developer Kit installations
make uninstall
# Removes only files installed by Developer Kit (preserves configs)

# Check dependencies
make check-deps
# Verifies jq is installed
```

### Manual Installation

For manual installation or custom setups, you can copy components directly:

```bash
# Set your target project
TARGET_PROJECT="/path/to/your/project"
TARGET_DIR="$TARGET_PROJECT/.claude"

# Create directory structure
mkdir -p "$TARGET_DIR"/{agents,commands,skills}

# Install developer-kit (core plugin)
PLUGIN_DIR="plugins/developer-kit"

# Copy agents (6 agents)
cp $PLUGIN_DIR/agents/*.md "$TARGET_DIR/agents/"

# Copy commands (17 commands, preserving subdirectories)
cp -r $PLUGIN_DIR/commands/* "$TARGET_DIR/commands/"

# Copy skills (if any)
cp -r $PLUGIN_DIR/skills/* "$TARGET_DIR/skills/" 2>/dev/null || true
```

**Install Multiple Plugins:**

```bash
# Install all plugins
for plugin in plugins/*/; do
    echo "Installing from: $plugin"
    cp "$plugin"agents/*.md "$TARGET_DIR/agents/" 2>/dev/null || true
    cp -r "$plugin"commands/* "$TARGET_DIR/commands/" 2>/dev/null || true
    cp -r "$plugin"skills/* "$TARGET_DIR/skills/" 2>/dev/null || true
done
```

**Verification:**

```bash
# Check installed components
ls -1 "$TARGET_DIR/agents/" | wc -l      # Should show 43+ agents
ls -1 "$TARGET_DIR/commands/" | wc -l     # Should show 37+ commands
ls -1d "$TARGET_DIR/skills/"* | wc -l     # Should show 77+ skills
```

---

### Installation Safety

- **Automatic Backups**: Creates timestamped backups before installation
- **Plugin Validation**: Skips invalid plugin.json files with warnings
- **Conflict Resolution**: Interactive prompts for existing files (overwrite/skip/rename)
- **Rollback Support**: Easy uninstall to restore previous state
- **Component Filtering**: Each CLI receives only supported components
  - **Claude Code**: agents + commands + skills (all)
  - **OpenCode**: agents + commands + skills (all)
  - **Copilot**: agents + skills (NO commands)
  - **Codex**: skills only (NO agents, NO commands)

### Command Testing

All Makefile commands have been tested and verified to work correctly:

| Command | Status | Description |
|---------|--------|-------------|
| `make help` | ✓ Working | Shows all available targets with descriptions |
| `make check-deps` | ✓ Working | Verifies jq is installed |
| `make list-plugins` | ✓ Working | Lists all 10 discovered plugins with component counts |
| `make list-components` | ✓ Working | Shows agents, commands, skills for a specific plugin |
| `make list-agents` | ✓ Working | Lists all 43+ agents across all plugins |
| `make list-commands` | ✓ Working | Lists all 36+ commands across all plugins |
| `make list-skills` | ✓ Working | Lists all 71+ skills across all plugins |
| `make status` | ✓ Working | Shows installation status for all CLI tools |
| `make backup` | ✓ Working | Creates timestamped backup in `~/.devkit-backups/` |
| `make install` | ✓ Working | Auto-installs for all detected CLIs |
| `make install-claude` | ✓ Working | Interactive installer for Claude Code |
| `make install-opencode` | ✓ Working | Installs for OpenCode CLI |
| `make install-copilot` | ✓ Working | Installs for GitHub Copilot CLI |
| `make install-codex` | ✓ Working | Installs for Codex CLI |
| `make uninstall` | ✓ Working | Removes all Developer Kit installations |
| `make clean` | ✓ Working | Removes generated files |

### Example Workflows

**Install everything for a new Java project:**
```bash
cd my-java-project
make install-claude
# Select: developer-kit, developer-kit-java
# Confirm installation
```

**Update existing installation:**
```bash
make backup              # Create backup first
make install-claude      # Re-run interactive installer
# Handle conflicts as prompted
```

**Check what's available:**
```bash
make list-plugins        # See all plugins
make list-components PLUGIN=developer-kit-java  # See plugin details
make status              # See what's installed
```
