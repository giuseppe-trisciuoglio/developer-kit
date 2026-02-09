# Complete Guide to Developer Kit Agents

This guide provides comprehensive documentation for all specialized agents available in the Developer Kit, organized by development domain with descriptions, use cases, and integration patterns.

---

## Table of Contents

1. [Overview](#overview)
2. [Agent Usage Guidelines](#agent-usage-guidelines)
3. [Plugin-Specific Agent Documentation](#plugin-specific-agent-documentation)
4. [Common Workflows](#common-workflows)

---

## Overview

Agents are specialized AI assistants with dedicated context windows, custom prompts, and specific tool access. They enable efficient problem-solving by delegating task-specific work to focused experts.

### Key Benefits

- **Context Preservation**: Each agent operates independently, keeping main conversation focused
- **Specialized Expertise**: Fine-tuned with detailed instructions for specific domains
- **Reusability**: Available across projects and shareable with team
- **Flexible Permissions**: Each agent can have different tool restrictions
- **Autonomous Selection**: Claude automatically selects appropriate agent based on task

### Agent Locations

- **Project agents**: `.claude/agents/` (team-shared via git, highest priority)
- **User agents**: `~/.claude/agents/` (personal, available across projects)
- **Plugin agents**: Bundled with installed plugins

---

## Agent Usage Guidelines

### When to Use Agents

Agents are most effective for:
- **Complex, multi-step tasks** requiring specialized knowledge
- **Large codebase exploration** where focused analysis is needed
- **Code reviews** requiring domain-specific expertise
- **Architecture decisions** benefiting from specialized patterns
- **Debugging** complex issues requiring deep analysis

### How to Invoke Agents

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the java-security-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

---

## Plugin-Specific Agent Documentation

The Developer Kit is organized into specialized plugins, each containing domain-specific agents:

### Core Plugin Agents

**Plugin**: [developer-kit-core](../developer-kit-core/)

General purpose agents for code analysis, review, refactoring, architecture design, and documentation.

| Agent | Purpose |
|-------|---------|
| `general-code-explorer` | Deep codebase analysis and architecture mapping |
| `general-code-reviewer` | Code quality review with confidence-based filtering |
| `general-refactor-expert` | Code refactoring with clean code principles |
| `general-software-architect` | Feature architecture design and implementation planning |
| `general-debugger` | Root cause analysis and targeted debugging |
| `document-generator-expert` | Professional document generation for assessments and specs |

**Documentation**: [Core Agent Guide](./agents.md)

---

### Java Plugin Agents

**Plugin**: [developer-kit-java](../developer-kit-java/)

Java and Spring Boot specialized agents for backend development, code review, testing, security, and architecture.

| Agent | Purpose |
|-------|---------|
| `spring-boot-backend-development-expert` | Spring Boot backend development specialist |
| `spring-boot-code-review-expert` | Spring Boot code quality and best practices review |
| `spring-boot-unit-testing-expert` | JUnit and Spring Boot testing strategies |
| `java-refactor-expert` | Java code refactoring with clean code principles |
| `java-security-expert` | Java security vulnerability assessment |
| `java-software-architect-review` | Java architecture design review |
| `java-documentation-specialist` | Java documentation generation |
| `java-tutorial-engineer` | Java learning and tutorial creation |
| `langchain4j-ai-development-expert` | LangChain4J AI integration patterns |

**Documentation**: [Java Agent Guide](../developer-kit-java/docs/guide-agents.md)

---

### TypeScript Plugin Agents

**Plugin**: [developer-kit-typescript](../developer-kit-typescript/)

TypeScript, JavaScript, NestJS, and React specialized agents for full-stack development.

| Agent | Purpose |
|-------|---------|
| `nestjs-backend-development-expert` | NestJS backend development specialist |
| `nestjs-code-review-expert` | NestJS code quality and best practices review |
| `nestjs-database-expert` | NestJS database integration and ORM patterns |
| `nestjs-security-expert` | NestJS security implementation review |
| `nestjs-testing-expert` | NestJS testing strategies and frameworks |
| `nestjs-unit-testing-expert` | NestJS unit testing best practices |
| `react-frontend-development-expert` | React frontend development specialist |
| `react-software-architect-review` | React architecture design review |
| `typescript-refactor-expert` | TypeScript code refactoring specialist |
| `typescript-security-expert` | TypeScript security vulnerability assessment |
| `typescript-software-architect-review` | TypeScript architecture design review |
| `typescript-documentation-expert` | TypeScript documentation generation |
| `expo-react-native-development-expert` | React Native development with Expo |

**Documentation**: [TypeScript Agent Guide](../developer-kit-typescript/docs/guide-agents.md)

---

### Python Plugin Agents

**Plugin**: [developer-kit-python](../developer-kit-python/)

Python development agents for code review, refactoring, security, and architecture.

| Agent | Purpose |
|-------|---------|
| `python-code-review-expert` | Python code quality and best practices review |
| `python-refactor-expert` | Python code refactoring with PEP standards |
| `python-security-expert` | Python security vulnerability assessment |
| `python-software-architect-expert` | Python architecture design specialist |

**Documentation**: [Python Agent Guide](../developer-kit-python/docs/guide-agents.md)

---

### PHP Plugin Agents

**Plugin**: [developer-kit-php](../developer-kit-php/)

PHP development agents for code review, refactoring, security, and architecture.

| Agent | Purpose |
|-------|---------|
| `php-code-review-expert` | PHP code quality and best practices review |
| `php-refactor-expert` | PHP code refactoring specialist |
| `php-security-expert` | PHP security vulnerability assessment |
| `php-software-architect-expert` | PHP architecture design specialist |
| `wordpress-development-expert` | WordPress development specialist |

**Documentation**: [PHP Agent Guide](../developer-kit-php/docs/guide-agents.md)

---

### AWS Plugin Agents

**Plugin**: [developer-kit-aws](../developer-kit-aws/)

AWS architecture, CloudFormation, and DevOps specialized agents.

| Agent | Purpose |
|-------|---------|
| `aws-solution-architect-expert` | AWS solution architecture design |
| `aws-architecture-review-expert` | AWS architecture review against Well-Architected Framework |
| `aws-cloudformation-devops-expert` | CloudFormation IaC templates and DevOps automation |

**Documentation**: [AWS Agent Guide](../developer-kit-aws/docs/guide-agents.md)

---

### AI Plugin Agents

**Plugin**: [developer-kit-ai](../developer-kit-ai/)

AI and prompt engineering specialized agents.

| Agent | Purpose |
|-------|---------|
| `prompt-engineering-expert` | Prompt optimization and pattern design |

**Documentation**: [AI Agent Guide](../developer-kit-ai/docs/guide-agents.md)

---

### DevOps Plugin Agents

**Plugin**: [developer-kit-devops](../developer-kit-devops/)

DevOps and containerization specialized agents.

| Agent | Purpose |
|-------|---------|
| `general-docker-expert` | Docker containerization and orchestration |
| `github-actions-pipeline-expert` | GitHub Actions CI/CD pipeline development |

**Documentation**: [DevOps Agent Guide](../developer-kit-devops/docs/guide-agents.md)

---

## Common Workflows

### Code Review Workflow

1. **Select appropriate reviewer agent** based on language/framework
2. **Provide context**: files to review, specific concerns
3. **Review findings**: agent returns prioritized issues
4. **Address issues**: fix critical and high-priority items
5. **Re-review**: validate fixes

### Architecture Design Workflow

1. **Use software-architect agent** to design feature architecture
2. **Review with domain-specific architect** if needed
3. **Implement based on architecture blueprint**
4. **Validate with code-reviewer agent**

### Debugging Workflow

1. **Describe the issue** with error messages and context
2. **general-debugger agent** performs root cause analysis
3. **Proposes targeted fixes** with minimal changes
4. **Validate fixes** and re-test

---

## Agent Selection Guide

| Task | Recommended Agent | Plugin |
|------|-------------------|---------|
| Understand codebase | `general-code-explorer` | Core |
| Review code quality | `{language}-code-reviewer` | Language-specific |
| Design architecture | `{language}-software-architect` | Language-specific |
| Debug issues | `general-debugger` | Core |
| Refactor code | `{language}-refactor-expert` | Language-specific |
| Generate docs | `document-generator-expert` | Core |
| Security review | `{language}-security-expert` | Language-specific |
| Write tests | `{framework}-testing-expert` | Framework-specific |
| AWS architecture | `aws-solution-architect-expert` | AWS |
| Prompt engineering | `prompt-engineering-expert` | AI |

---

## See Also

- [Complete Commands Guide](./guide-commands.md) - All available commands
- [LRA Workflow Guide](./guide-lra-workflow.md) - Long-running agent workflow
- [Installation Guide](./installation.md) - Installation instructions
