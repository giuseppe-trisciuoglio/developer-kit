# Python Plugin Agents Guide

This guide provides comprehensive documentation for all Python specialized agents available in the Developer Kit Python Plugin.

---

## Overview

The Python Plugin provides specialized agents for Python development, including code review, refactoring, security assessment, and architecture design. These agents have deep expertise in Python best practices, PEP standards, and Python frameworks.

### Available Agents

- **Python Code Review**: 1 agent for Python code quality review
- **Python Refactoring**: 1 agent for Python code refactoring
- **Python Security**: 1 agent for Python security assessment
- **Python Architecture**: 1 agent for Python software architecture

---

## Python Development Agents

### `python-code-review-expert`

**File**: `agents/python-code-review-expert.md`

**Purpose**: Python code quality and best practices review with PEP standards compliance.

**When to use:**
- Reviewing Python code before commits
- Ensuring PEP 8 compliance
- Identifying Python anti-patterns
- Validating Python idioms and patterns
- Reviewing Python framework usage

**Key Capabilities:**
- PEP 8 style guide compliance
- Python idioms and patterns review
- Framework-specific best practices
- Code complexity assessment
- Python 3.8+ features utilization

---

### `python-refactor-expert`

**File**: `agents/python-refactor-expert.md`

**Purpose**: Python code refactoring with clean code principles, PEP standards, and Python best practices.

**When to use:**
- Refactoring Python code
- Applying clean code principles
- Implementing Python design patterns
- Reducing code complexity
- Migrating legacy Python code

**Key Capabilities:**
- PEP standards compliance
- Clean code principles for Python
- Design pattern implementation
- Code complexity reduction
- Python 3.8+ features utilization

---

### `python-security-expert`

**File**: `agents/python-security-expert.md`

**Purpose**: Python security vulnerability assessment covering OWASP, CVEs, and secure coding practices.

**When to use:**
- Security auditing Python applications
- Identifying OWASP vulnerabilities
- Reviewing authentication implementation
- Checking for dependency vulnerabilities
- Validating cryptographic practices

**Key Capabilities:**
- OWASP vulnerability detection
- Authentication and authorization review
- Dependency vulnerability scanning (CVEs)
- Cryptographic practice validation
- Secure coding practices for Python

---

### `python-software-architect-expert`

**File**: `agents/python-software-architect-expert.md`

**Purpose**: Python architecture design specialist focusing on patterns, scalability, and architectural decisions.

**When to use:**
- Designing Python application architecture
- Reviewing Python package structure
- Planning refactoring efforts
- Assessing scalability
- Validating architectural decisions

**Key Capabilities:**
- Python architecture patterns
- Package structure review
- Design pattern assessment
- Scalability evaluation
- Architectural decision validation

---

## Agent Usage Guidelines

### When to Use Python Plugin Agents

Python Plugin agents are most effective for:
- **Code Quality**: Reviewing and refactoring Python code
- **Security**: Auditing Python applications for vulnerabilities
- **Architecture**: Designing and reviewing Python application architecture
- **Best Practices**: Ensuring PEP standards compliance

### How to Invoke Agents

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the python-code-review-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

### Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Review Python code | `python-code-review-expert` |
| Refactor Python code | `python-refactor-expert` |
| Security audit | `python-security-expert` |
| Architecture review | `python-software-architect-expert` |

---

## See Also

- [Core Agent Guide](../developer-kit-core/docs/guide-agents.md) - All agents across plugins
- [TypeScript Plugin Documentation](../developer-kit-typescript/docs/) - TypeScript, NestJS, and React guides
