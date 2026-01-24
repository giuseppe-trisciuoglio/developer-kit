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

The Developer Kit supports installation across multiple AI-powered development environments through a unified Makefile interface.

### Quick Start with Makefile

```bash
# Clone the repository
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git
cd developer-kit-claude-code

# See all available options
make help

# Install for your specific CLI tool
make install-copilot      # For GitHub Copilot CLI
make install-opencode     # For OpenCode CLI
make install-codex        # For Codex CLI
make install              # Auto-install for all detected CLIs
```

### Supported CLI Tools

#### GitHub Copilot CLI

```bash
make install-copilot

# Installation creates:
# ~/.copilot/agents/          # Specialized agents for code review, testing, etc.
```

**Features:**
- **Specialized Agents**: Code review, architecture, security, testing, debugging experts
- **Usage**: `/agent` to select agents or mention in prompts
- **Integration**: Works with Copilot's native agent system

#### OpenCode CLI

```bash
make install-opencode

# Installation creates:
# ~/.config/opencode/agent/     # Development agents
# ~/.config/opencode/command/  # Custom slash commands
```

**Features:**
- **Development Agents**: Full suite of specialized agents
- **Custom Commands**: From code generation to debugging and security reviews
- **Usage**: `@agent-name` for agents, `/command-name` for commands
- **Discovery**: Tab completion and command discovery

#### Codex CLI

```bash
make install-codex

# Installation creates:
# ~/.codex/instructions.md    # Agent context and usage guide
# ~/.codex/prompts/           # Custom prompt commands
```

**Features:**
- **Custom Prompts**: Specialized commands for development workflows
- **Agents Documentation**: Complete agent descriptions and usage
- **Usage**: `/prompts:<name>` to invoke custom commands

---

## Local Project Installation

Install skills, agents, and commands directly into your local project for team-based development.

### Interactive Claude Code Installation

```bash
# Clone the repository
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git
cd developer-kit-claude-code

# Run interactive installer for Claude Code
make install-claude
```

**Interactive Features:**
- ✅ **Environment Validation**: Confirms Claude Code usage
- 🎯 **Category Selection**: Choose specific skill categories
- 🔧 **Custom Selection**: Pick specific agents and commands
- 🛡️ **Conflict Handling**: Decide how to handle existing files
- 📊 **Progress Tracking**: Real-time installation progress
- 📋 **Summary Report**: Complete installation summary

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
│   ├── skills/                      # Auto-discovered skills
│   │   ├── langchain4j-ai-services-patterns/
│   │   ├── spring-boot-actuator/
│   │   └── ... (selected skills)
│   ├── agents/                      # @agent-name access
│   │   ├── java-documentation-specialist.md
│   │   ├── java-security-expert.md
│   │   └── ... (selected agents)
│   └── commands/                    # /command-name access
│       ├── devkit.java.code-review.md
│       ├── devkit.java.write-unit-tests.md
│       └── ... (selected commands)
```

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

```bash
# Check installation status
make status

# Create backup before installing
make backup

# Remove all Developer Kit installations
make uninstall

# List available components
make list-agents      # Show all agents
make list-commands    # Show all commands
make list-skills      # Show all skills by category
```

### Installation Safety

- **Automatic Backups**: Creates timestamped backups before installation
- **Conflict Resolution**: Preserves existing configurations
- **Rollback Support**: Easy uninstall to restore previous state
- **Version Tracking**: Tracks what's installed from this kit
