# Complete Guide to Developer Kit Commands

This guide documents all commands available in the Developer Kit, organized by plugin and category with brief descriptions, usage, and practical examples. See individual plugin documentation for complete details.

---

## Table of Contents

1. [Overview](#overview)
2. [Command Usage Guidelines](#command-usage-guidelines)
3. [Plugin-Specific Command Documentation](#plugin-specific-command-documentation)
4. [Common Workflows](#common-workflows)

---

## Overview

Commands are reusable workflows that automate common development tasks. Each command is a specialized prompt that guides Claude through specific procedures for code generation, review, testing, and more.

### Key Benefits

- **Consistency**: Standardized approaches to common tasks
- **Efficiency**: Reduce repetitive typing with pre-built workflows
- **Best Practices**: Commands embody proven patterns and approaches
- **Reusability**: Share commands across team and projects
- **Discoverability**: Easy to find and use available commands

### Command Locations

- **Project commands**: `.claude/commands/` (team-shared via git, highest priority)
- **User commands**: `~/.claude/commands/` (personal, available across projects)
- **Plugin commands**: Bundled with installed plugins

---

## Command Usage Guidelines

### How to Invoke Commands

Commands are invoked using the slash syntax in Claude Code:

```bash
/command-name [arguments]
```

### Command Patterns

Most commands follow these patterns:
- **Prefix**: `devkit.` for core commands, `devkit.{plugin}.` for plugin-specific
- **Arguments**: Optional positional or named arguments
- **Help**: Use `/help {command-name}` to see command documentation

### Best Practices

1. **Read command docs first**: Each command has detailed documentation
2. **Provide clear context**: Give commands the information they need
3. **Review output**: Commands generate suggestions you should review
4. **Iterate**: Use command output as starting point, refine as needed

---

## Plugin-Specific Command Documentation

The Developer Kit is organized into specialized plugins, each containing domain-specific commands:

### Core Plugin Commands

**Plugin**: [developer-kit-core](../developer-kit-core/)

General purpose commands for brainstorming, feature development, refactoring, debugging, documentation, and workflow management.

| Command | Purpose |
|---------|---------|
| `/developer-kit:devkit.brainstorm` | Guided brainstorming to transform ideas into designs |
| `/developer-kit:devkit.refactor` | Guided code refactoring with codebase understanding |
| `/developer-kit:devkit.feature-development` | Guided feature development with architecture focus |
| `/developer-kit:devkit.fix-debugging` | Guided bug fixing and systematic debugging |
| `/developer-kit:devkit.generate-document` | Generate professional documents (assessments, specs) |
| `/developer-kit:devkit.generate-changelog` | Generate and maintain project changelog |
| `/developer-kit:devkit.github.create-pr` | Create GitHub pull request with detailed description |
| `/developer-kit:devkit.github.review-pr` | Comprehensive GitHub pull request review |
| `/developer-kit:devkit.lra.init` | Initialize environment for long-running agent workflow |
| `/developer-kit:devkit.lra.add-feature` | Add a new feature to the feature list |
| `/developer-kit:devkit.lra.checkpoint` | Create a checkpoint - commit changes, update progress |
| `/developer-kit:devkit.lra.mark-feature` | Mark a feature as completed or failed |
| `/developer-kit:devkit.lra.recover` | Recover from a broken state |
| `/developer-kit:devkit.lra.start-session` | Start a new coding session |
| `/developer-kit:devkit.lra.status` | Show current project status |
| `/developer-kit:devkit.verify-skill` | Validates a skill against DevKit standards |
| `/developer-kit:devkit.generate-security-assessment` | Generate comprehensive security assessment document |

**Documentation**: [Core Command Guide](./commands.md)

---

### Java Plugin Commands

**Plugin**: [developer-kit-java](../developer-kit-java/)

Java and Spring Boot specialized commands for code review, testing, CRUD generation, documentation, and more.

| Command | Purpose |
|---------|---------|
| `/developer-kit-java:devkit.java.code-review` | Comprehensive Java/Spring Boot code review |
| `/developer-kit-java:devkit.java.architect-review` | High-level Java architecture review |
| `/developer-kit-java:devkit.java.security-review` | Security-focused audit for Spring Boot apps |
| `/developer-kit-java:devkit.java.write-unit-tests` | Generate JUnit 5 unit tests with Mockito |
| `/developer-kit-java:devkit.java.write-integration-tests` | Generate Spring Boot integration tests |
| `/developer-kit-java:devkit.java.generate-crud` | Generate complete CRUD implementation |
| `/developer-kit-java:devkit.java.generate-docs` | Generate API documentation and architecture guides |
| `/developer-kit-java:devkit.java.refactor-class` | Intelligent refactoring with Clean Architecture |
| `/developer-kit-java:devkit.java.dependency-audit` | Comprehensive dependency audit |
| `/developer-kit-java:devkit.java.upgrade-dependencies` | Upgrade dependencies with compatibility checks |
| `/developer-kit-java:devkit.java.generate-refactoring-tasks` | Generate refactoring task list |

**Documentation**: [Java Command Guide](../developer-kit-java/docs/guide-commands.md)

---

### TypeScript Plugin Commands

**Plugin**: [developer-kit-typescript](../developer-kit-typescript/)

TypeScript, JavaScript, NestJS, and React specialized commands for code review and security assessment.

| Command | Purpose |
|---------|---------|
| `/developer-kit-typescript:devkit.typescript.code-review` | Comprehensive TypeScript code review |
| `/developer-kit-typescript:devkit.react.code-review` | React frontend code review |
| `/developer-kit-typescript:devkit.ts.security-review` | TypeScript security vulnerability assessment |

**Documentation**: [TypeScript Command Guide](../developer-kit-typescript/docs/guide-commands.md)

---

### GitHub Spec Kit Commands

**Plugin**: [github-spec-kit](../github-spec-kit/)

GitHub specification and workflow commands.

| Command | Purpose |
|---------|---------|
| `/github-spec-kit:speckit.check-integration` | Check integration with GitHub specifications |
| `/github-spec-kit:speckit.optimize` | Optimize GitHub workflows |
| `/github-spec-kit:speckit.verify` | Verify GitHub specifications |

**Documentation**: [Spec Kit Command Guide](../github-spec-kit/docs/guide-commands.md)

---

### Project Management Plugin Commands

**Plugin**: [developer-kit-project-management](../developer-kit-project-management/)

Project management and workflow commands.

| Command | Purpose |
|---------|---------|
| Ralph Loop commands | Long-running agent workflow management |

**Documentation**: [Project Management Command Guide](../developer-kit-project-management/docs/guide-commands.md)

---

## Common Workflows

### Feature Development Workflow

```bash
# 1. Brainstorm the feature
/developer-kit:devkit.brainstorm "Add user authentication"

# 2. Develop the feature with architecture guidance
/developer-kit:devkit.feature-development --lang=spring "Implement JWT authentication"

# 3. Review the implementation
/developer-kit-java:devkit.java.code-review full src/main/java/auth/

# 4. Generate tests
/developer-kit-java:devkit.java.write-unit-tests src/main/java/auth/
```

### Code Review Workflow

```bash
# 1. Run comprehensive review
/developer-kit-java:devkit.java.code-review full

# 2. Address critical issues

# 3. Run security-specific review
/developer-kit-java:devkit.java.security-review

# 4. Create PR with review summary
/developer-kit:devkit.github.create-pr
```

### Refactoring Workflow

```bash
# 1. Generate refactoring tasks
/developer-kit-java:devkit.java.generate-refactoring-tasks

# 2. Review tasks and prioritize

# 3. Refactor specific classes
/developer-kit-java:devkit.java.refactor-class src/main/java/service/legacy.java comprehensive

# 4. Review refactored code
/developer-kit-java:devkit.java.code-review architecture
```

### Documentation Workflow

```bash
# 1. Generate project documentation
/developer-kit-java:devkit.java.generate-docs

# 2. Generate specific document types
/developer-kit:devkit.generate-document --type=assessment "Security Assessment"

# 3. Update changelog
/developer-kit:devkit.generate-changelog
```

### Long-Running Agent Workflow

```bash
# 1. Initialize LRA environment
/developer-kit:devkit.lra.init

# 2. Add features to implement
/developer-kit:devkit.lra.add-feature "Implement user management"

# 3. Start coding session
/developer-kit:devkit.lra.start-session

# 4. Create checkpoint after progress
/developer-kit:devkit.lra.checkpoint

# 5. Mark feature as complete
/developer-kit:devkit.lra.mark-feature user-management complete

# 6. Check status
/developer-kit:devkit.lra.status
```

---

## Command Selection Guide

| Task | Recommended Command | Plugin |
|------|---------------------|--------|
| Brainstorm ideas | `/developer-kit:devkit.brainstorm` | Core |
| Develop new feature | `/developer-kit:devkit.feature-development` | Core |
| Debug issues | `/developer-kit:devkit.fix-debugging` | Core |
| Refactor code | `/developer-kit:devkit.refactor` | Core |
| Review Java code | `/developer-kit-java:devkit.java.code-review` | Java |
| Review TypeScript code | `/developer-kit-typescript:devkit.typescript.code-review` | TypeScript |
| Review React code | `/developer-kit-typescript:devkit.react.code-review` | TypeScript |
| Write Java tests | `/developer-kit-java:devkit.java.write-unit-tests` | Java |
| Generate CRUD | `/developer-kit-java:devkit.java.generate-crud` | Java |
| Security review | `/developer-kit-java:devkit.java.security-review` or `/developer-kit-typescript:devkit.ts.security-review` | Language-specific |
| Dependency audit | `/developer-kit-java:devkit.java.dependency-audit` | Java |
| Generate docs | `/developer-kit-java:devkit.java.generate-docs` or `/developer-kit:devkit.generate-document` | Core/Language |
| Create PR | `/developer-kit:devkit.github.create-pr` | Core |
| Review PR | `/developer-kit:devkit.github.review-pr` | Core |
| Generate changelog | `/developer-kit:devkit.generate-changelog` | Core |
| LRA workflow | `/developer-kit:devkit.lra.*` | Core |

---

## See Also

- [Complete Agents Guide](./guide-agents.md) - All available agents
- [LRA Workflow Guide](./guide-lra-workflow.md) - Long-running agent workflow
- [Installation Guide](./installation.md) - Installation instructions
