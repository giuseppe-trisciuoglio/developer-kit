# Python Plugin Agents Guide

Comprehensive documentation for all Python specialized agents in the Developer Kit Python Plugin.

## Overview

The Python Plugin provides 4 specialized agents for Python development. Each agent has deep expertise in Python best practices, PEP standards, and specific Python frameworks.

### Available Agents

| Agent | Purpose |
|-------|---------|
| `python-code-review-expert` | Code quality review and PEP standards compliance |
| `python-refactor-expert` | Clean code refactoring and design patterns |
| `python-security-expert` | Security vulnerability assessment (OWASP, CVEs) |
| `python-software-architect-expert` | Architecture design and scalability evaluation |

---

## python-code-review-expert

**File**: `agents/python-code-review-expert.md`

Specializes in Python code quality review with PEP standards compliance.

### When to Use

- Reviewing Python code before commits
- Ensuring PEP 8 compliance
- Identifying Python anti-patterns
- Validating Python idioms and patterns
- Reviewing Python framework usage

### Key Capabilities

- PEP 8 style guide compliance
- Python idioms and patterns review
- Framework-specific best practices (FastAPI, Flask, Django)
- Code complexity assessment
- Python 3.8+ features utilization

### Triggers

- "Review this Python code"
- "Check PEP compliance"
- "Python code quality"
- "lint python"

---

## python-refactor-expert

**File**: `agents/python-refactor-expert.md`

Specializes in Python code refactoring with clean code principles and design patterns.

### When to Use

- Refactoring Python code
- Applying clean code principles
- Implementing Python design patterns
- Reducing code complexity
- Migrating legacy Python code

### Key Capabilities

- PEP standards compliance
- Clean code principles for Python
- Design pattern implementation (Repository, Factory, Strategy)
- Code complexity reduction
- Python 3.8+ features utilization

### Triggers

- "Refactor this Python code"
- "Clean up Python code"
- "Improve Python code structure"
- "Python migration"

---

## python-security-expert

**File**: `agents/python-security-expert.md`

Specializes in Python security vulnerability assessment covering OWASP Top 10 and CVE scanning.

### When to Use

- Security auditing Python applications
- Identifying OWASP vulnerabilities
- Reviewing authentication implementation
- Checking for dependency vulnerabilities
- Validating cryptographic practices

### Key Capabilities

- OWASP vulnerability detection
- Authentication and authorization review
- Dependency vulnerability scanning (CVEs)
- Cryptographic practice validation
- Secure coding practices for Python

### Triggers

- "Security audit Python"
- "Check for vulnerabilities"
- "OWASP Python review"
- "Python security"

---

## python-software-architect-expert

**File**: `agents/python-software-architect-expert.md`

Specializes in Python architecture design focusing on patterns, scalability, and architectural decisions.

### When to Use

- Designing Python application architecture
- Reviewing Python package structure
- Planning refactoring efforts
- Assessing scalability
- Validating architectural decisions

### Key Capabilities

- Python architecture patterns (Clean, Hexagonal, Event-Driven)
- Package structure review
- Design pattern assessment
- Scalability evaluation
- Architectural decision validation

### Triggers

- "Design Python architecture"
- "Architecture review"
- "Python scalability"
- "DDD patterns"

---

## Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Review Python code before commit | `python-code-review-expert` |
| Refactor Python code | `python-refactor-expert` |
| Security audit Python application | `python-security-expert` |
| Design or review architecture | `python-software-architect-expert` |

## How to Invoke

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the python-code-review-expert to review this code")
3. **Task Tool**: When using the Task tool, specify the subagent_type parameter

## See Also

- [Core Agent Guide](../../developer-kit-core/docs/guide-agents.md) - All agents across plugins
- [TypeScript Plugin Documentation](../../developer-kit-typescript/docs/) - TypeScript, NestJS, React guides
- [Java Plugin Documentation](../../developer-kit-java/docs/) - Java and Spring Boot guides