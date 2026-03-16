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

**Plugin**: [developer-kit-core](../)

General purpose commands for brainstorming, feature development, refactoring, debugging, documentation, and workflow management.

### Specification Workflow Commands

The Developer Kit provides a comprehensive workflow for transforming ideas into implemented features:

| Command | Purpose | Phases |
|---------|---------|--------|
| `/developer-kit:devkit.brainstorm` | Full specification creation for complex features | 9 phases |
| `/developer-kit:devkit.quick-spec` | Lightweight spec for bug fixes and small features | 4 phases |
| `/developer-kit:devkit.spec-review` | Interactive spec quality assessment | 7 phases |
| `/developer-kit:devkit.spec-quality` | Knowledge Graph synchronization | - |
| `/developer-kit:devkit.spec-to-tasks` | Convert specs to executable tasks | - |
| `/developer-kit:devkit.spec-sync` | Sync spec with implementation state | 6 phases |
| `/developer-kit:devkit.task-implementation` | Guided single-task implementation | 11 steps |

### Task Management Commands

| Command | Purpose |
|---------|---------|
| `/developer-kit:devkit.task-manage` | Manage tasks (add, split, update, mark optional/required, list) |
| `/developer-kit:devkit.task-review` | Verify implementation against specifications |
| `/developer-kit:devkit.task-implementation` | Execute single tasks with Knowledge Graph validation |

### Development Commands

| Command | Purpose |
|---------|---------|
| `/developer-kit:devkit.feature-development` | Guided feature development with architecture focus |
| `/developer-kit:devkit.refactor` | Guided code refactoring with codebase understanding |
| `/developer-kit:devkit.fix-debugging` | Guided bug fixing and systematic debugging |

### Documentation Commands

| Command | Purpose |
|---------|---------|
| `/developer-kit:devkit.generate-document` | Generate professional documents (assessments, specs) |
| `/developer-kit:devkit.generate-changelog` | Generate and maintain project changelog |
| `/developer-kit:devkit.generate-security-assessment` | Generate comprehensive security assessment |

### GitHub Integration Commands

| Command | Purpose |
|---------|---------|
| `/developer-kit:devkit.github.create-pr` | Create GitHub pull request with detailed description |
| `/developer-kit:devkit.github.review-pr` | Comprehensive GitHub pull request review |

### LRA Workflow Commands

| Command | Purpose |
|---------|---------|
| `/developer-kit:devkit.lra.init` | Initialize environment for long-running agent workflow |
| `/developer-kit:devkit.lra.add-feature` | Add a new feature to the feature list |
| `/developer-kit:devkit.lra.checkpoint` | Create a checkpoint - commit changes, update progress |
| `/developer-kit:devkit.lra.mark-feature` | Mark a feature as completed or failed |
| `/developer-kit:devkit.lra.recover` | Recover from a broken state |
| `/developer-kit:devkit.lra.start-session` | Start a new coding session |
| `/developer-kit:devkit.lra.status` | Show current project status |

### Utility Commands

| Command | Purpose |
|---------|---------|
| `/developer-kit:devkit.verify-skill` | Validates a skill against DevKit standards |

**Documentation**: [Core Command Guide](./guide-commands.md)

---

### Java Plugin Commands

**Plugin**: [developer-kit-java](../../developer-kit-java/)

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

**Documentation**: [Java Command Guide](../../developer-kit-java/docs/guide-commands.md)

---

### TypeScript Plugin Commands

**Plugin**: [developer-kit-typescript](../../developer-kit-typescript/)

TypeScript, JavaScript, NestJS, and React specialized commands for code review and security assessment.

| Command | Purpose |
|---------|---------|
| `/developer-kit-typescript:devkit.typescript.code-review` | Comprehensive TypeScript code review |
| `/developer-kit-typescript:devkit.react.code-review` | React frontend code review |
| `/developer-kit-typescript:devkit.ts.security-review` | TypeScript security vulnerability assessment |

**Documentation**: [TypeScript Command Guide](../../developer-kit-typescript/docs/guide-commands.md)

---

### GitHub Spec Kit Commands

**Plugin**: [github-spec-kit](../../github-spec-kit/)

GitHub specification and workflow commands.

| Command | Purpose |
|---------|---------|
| `/github-spec-kit:speckit.check-integration` | Check integration with GitHub specifications |
| `/github-spec-kit:speckit.optimize` | Optimize GitHub workflows |
| `/github-spec-kit:speckit.verify` | Verify GitHub specifications |

**Documentation**: [Spec Kit Command Guide](../../github-spec-kit/docs/guide-commands.md)

---

### Project Management Plugin Commands

**Plugin**: [developer-kit-project-management](../../developer-kit-project-management/)

Project management and workflow commands.

| Command | Purpose |
|---------|---------|
| Ralph Loop commands | Long-running agent workflow management |

**Documentation**: [Project Management Command Guide](../../developer-kit-project-management/docs/guide-commands.md)

---

## Common Workflows

### Specification Workflow

The Developer Kit supports two parallel workflows depending on feature complexity:

#### Full Brainstorming Workflow (Complex Features)

```bash
# 1. Full specification creation (9 phases)
/developer-kit:devkit.brainstorm "Add user authentication with JWT tokens"

# 2. Optional: Review and improve spec quality
/developer-kit:devkit.spec-review docs/specs/002-user-auth/

# 3. Sync technical context (Knowledge Graph)
/developer-kit:devkit.spec-quality docs/specs/002-user-auth/

# 4. Convert specification to tasks
/developer-kit:devkit.spec-to-tasks --lang=spring docs/specs/002-user-auth/

# 5. Review and manage tasks
/developer-kit:devkit.task-manage --action=list --spec=docs/specs/002-user-auth/
/developer-kit:devkit.task-manage --action=split --task=docs/specs/002-user-auth/tasks/TASK-007.md

# 6. Implement tasks (11-step workflow)
/developer-kit:devkit.task-implementation --lang=spring --task="TASK-001"
# Includes: Git check, KG validation, contract validation, implementation, verification

# 7. Sync spec with implementation (if deviations detected)
/developer-kit:devkit.spec-sync docs/specs/002-user-auth/

# 8. Review implementation
/developer-kit:devkit.task-review --lang=spring "docs/specs/002-user-auth/tasks/TASK-001.md"
```

#### Quick Spec Workflow (Bug Fixes / Small Features)

```bash
# 1. Quick specification (4 phases)
/developer-kit:devkit.quick-spec "Fix memory leak in session cleanup"

# 2. Based on criteria count:
#    - 1-2 criteria: Direct implementation
#    - 3+ criteria: Generate task list
/developer-kit:devkit.spec-to-tasks --lang=spring docs/specs/003-quick-fix/

# 3. Implement with guided workflow
/developer-kit:devkit.task-implementation --lang=spring --task="TASK-001"
```

### Feature Development Workflow (Legacy)

```bash
# 1. Brainstorm the feature
/developer-kit:devkit.brainstorm "Add user authentication"

# 2. Convert specification to tasks (with context)
/developer-kit:devkit.spec-to-tasks --lang=spring docs/specs/001-user-auth/
# Generates: tasks with context linkage, traceability matrix

# 3. Review context and traceability
/developer-kit:devkit.task-manage --action=list --spec=docs/specs/001-user-auth/
# Shows: complexity scores, context coverage, business goals

# 4. Manage tasks if needed
/developer-kit:devkit.task-manage --action=split --task=docs/specs/001-user-auth/tasks/TASK-007.md
# Preserves: context chain when splitting

# 5. Develop the feature (alternative: use task-implementation)
/developer-kit:devkit.feature-development --lang=spring "docs/specs/001-user-auth/tasks/TASK-001.md"

# 6. Review implementation (with intent alignment)
/developer-kit:devkit.task-review --lang=spring "docs/specs/001-user-auth/tasks/TASK-001.md"
# Validates: against original user request + technical constraints

# 7. Generate tests
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

## Context Management

The Developer Kit maintains complete context throughout the development workflow:

### Context Linkage Fields

Each task includes:
- **original_request**: Link to user-request.md
- **technical_context**: Link to brainstorming-notes.md
- **business_goals**: Objectives this task supports
- **data_contracts**: Input/output/error contracts
- **external_dependencies**: External systems and their impact
- **observability**: Logging, metrics, security requirements

### Traceability Matrix

Generated for each specification:
- User Requirements → Tasks mapping
- Business Goals coverage
- Data Contracts traceability
- External Dependencies map
- Observability coverage

### Context Chain

When splitting tasks:
- Child tasks inherit all context from parent
- Business goals are refined, not lost
- Data contracts are partitioned by relevance
- Context hash tracks changes

### Intent Alignment

Task review validates:
- Implementation matches original user requirements
- Business goals are achieved
- Technical constraints are respected
- Alignment score 0-100%

---

## Command Selection Guide

### Specification Workflow

| Task | Recommended Command | Plugin |
|------|---------------------|--------|
| Full spec for complex feature | `/developer-kit:devkit.brainstorm` | Core |
| Quick spec for bug fix/small feature | `/developer-kit:devkit.quick-spec` | Core |
| Review spec quality (max 5 questions) | `/developer-kit:devkit.spec-review` | Core |
| Sync Knowledge Graph | `/developer-kit:devkit.spec-quality` | Core |
| Convert spec to tasks | `/developer-kit:devkit.spec-to-tasks` | Core |
| Sync spec with implementation | `/developer-kit:devkit.spec-sync` | Core |

### Task Implementation

| Task | Recommended Command | Plugin |
|------|---------------------|--------|
| Implement single task (11 steps) | `/developer-kit:devkit.task-implementation` | Core |
| Manage tasks (add/split/update) | `/developer-kit:devkit.task-manage` | Core |
| Review task implementation | `/developer-kit:devkit.task-review` | Core |
| Develop new feature | `/developer-kit:devkit.feature-development` | Core |

### General Development

| Task | Recommended Command | Plugin |
|------|---------------------|--------|
| Debug issues | `/developer-kit:devkit.fix-debugging` | Core |
| Refactor code | `/developer-kit:devkit.refactor` | Core |
| Review Java code | `/developer-kit-java:devkit.java.code-review` | Java |
| Review TypeScript code | `/developer-kit-typescript:devkit.typescript.code-review` | TypeScript |
| Review React code | `/developer-kit-typescript:devkit.react.code-review` | TypeScript |
| Write Java tests | `/developer-kit-java:devkit.java.write-unit-tests` | Java |
| Generate CRUD | `/developer-kit-java:devkit.java.generate-crud` | Java |
| Security review | `/developer-kit-java:devkit.java.security-review` or `/developer-kit-typescript:devkit.ts.security-review` | Language-specific |
| Dependency audit | `/developer-kit-java:devkit.java.dependency-audit` | Java |

### Documentation & GitHub

| Task | Recommended Command | Plugin |
|------|---------------------|--------|
| Generate docs | `/developer-kit:devkit.generate-document` | Core |
| Generate changelog | `/developer-kit:devkit.generate-changelog` | Core |
| Security assessment | `/developer-kit:devkit.generate-security-assessment` | Core |
| Create PR | `/developer-kit:devkit.github.create-pr` | Core |
| Review PR | `/developer-kit:devkit.github.review-pr` | Core |
| LRA workflow | `/developer-kit:devkit.lra.*` | Core |

---

## See Also

- [Complete Agents Guide](./guide-agents.md) - All available agents
- [LRA Workflow Guide](./guide-lra-workflow.md) - Long-running agent workflow
- [Installation Guide](./installation.md) - Installation instructions
