# TypeScript Plugin Commands Guide

This guide documents all commands available in the Developer Kit TypeScript Plugin, organized by category with brief descriptions, usage, and practical examples.

---

## Table of Contents

1. [Overview](#overview)
2. [Code Review Commands](#code-review-commands)
3. [Security Commands](#security-commands)
4. [Command Usage Guidelines](#command-usage-guidelines)
5. [See Also](#see-also)

---

## Overview

The TypeScript Plugin provides specialized commands for TypeScript, JavaScript, NestJS, and React development, including code review and security assessment.

### Available Commands

- **Code Review**: 2 commands for TypeScript and React code review
- **Security**: 1 command for TypeScript security assessment

---

## Code Review Commands

### `/developer-kit-typescript:devkit.typescript.code-review`

**Purpose**: Comprehensive TypeScript code review for architecture, security, performance, and best practices.

**Usage:**
```bash
/developer-kit-typescript:devkit.typescript.code-review [full|security|performance|architecture|testing|best-practices] [path] [options]
```

**Common use cases:**
- Before creating a pull request
- After completing a feature
- Verifying TypeScript code quality
- Refactoring critical components

**Examples:**
```bash
# Full review of current directory
/developer-kit-typescript:devkit.typescript.code-review full

# Security-focused review
/developer-kit-typescript:devkit.typescript.code-review security src/

# Performance review of specific package
/developer-kit-typescript:devkit.typescript.code-review performance src/components
```

---

### `/developer-kit-typescript:devkit.react.code-review`

**Purpose**: React frontend code review for component design, hooks usage, performance, and best practices.

**Usage:**
```bash
/developer-kit-typescript:devkit.react.code-review [full|performance|hooks|architecture|testing|best-practices] [path] [options]
```

**Common use cases:**
- Reviewing React components
- Ensuring React best practices compliance
- Identifying performance issues
- Validating hooks usage
- Reviewing component architecture

**Examples:**
```bash
# Full review of React components
/developer-kit-typescript:devkit.react.code-review full src/components

# Performance-focused review
/developer-kit-typescript:devkit.react.code-review performance src/

# Hooks usage review
/developer-kit-typescript:devkit.react.code-review hooks src/hooks
```

---

## Security Commands

### `/developer-kit-typescript:devkit.ts.security-review`

**Purpose**: TypeScript security vulnerability assessment covering OWASP, XSS, CSRF, and dependency vulnerabilities.

**Usage:**
```bash
/developer-kit-typescript:devkit.ts.security-review [path]
```

**Common use cases:**
- Security auditing before deployment
- Identifying OWASP vulnerabilities
- Checking for XSS and CSRF issues
- Reviewing authentication implementation
- Validating secure coding practices

**Examples:**
```bash
# Full security review
/developer-kit-typescript:devkit.ts.security-review

# Security review of specific package
/developer-kit-typescript:devkit.ts.security-review src/auth/

# Security review of React components
/developer-kit-typescript:devkit.ts.security-review src/components
```

---

## Command Usage Guidelines

### How to Invoke Commands

Commands are invoked using the slash syntax in Claude Code:

```bash
/developer-kit-typescript:{command-name} [arguments]
```

### Best Practices

1. **Read command docs first**: Each command has detailed documentation
2. **Provide clear context**: Give commands the information they need
3. **Review output**: Commands generate suggestions you should review
4. **Iterate**: Use command output as starting point, refine as needed
5. **Test thoroughly**: Especially for security-related changes

---

## Common Workflows

### NestJS Development Workflow

```bash
# 1. Review NestJS implementation
/developer-kit-typescript:devkit.typescript.code-review full src/

# 2. Run security review
/developer-kit-typescript:devkit.ts.security-review src/

# 3. Address critical issues

# 4. Re-review
/developer-kit-typescript:devkit.typescript.code-review full
```

### React Development Workflow

```bash
# 1. Review React components
/developer-kit-typescript:devkit.react.code-review full src/components

# 2. Performance review
/developer-kit-typescript:devkit.react.code-review performance src/

# 3. Security review
/developer-kit-typescript:devkit.ts.security-review src/

# 4. Address issues

# 5. Re-review
/developer-kit-typescript:devkit.react.code-review best-practices
```

### TypeScript Security Workflow

```bash
# 1. Run comprehensive security review
/developer-kit-typescript:devkit.ts.security-review

# 2. Review findings

# 3. Address vulnerabilities

# 4. Re-audit
/developer-kit-typescript:devkit.ts.security-review
```

---

## Command Selection Guide

| Task | Recommended Command |
|------|---------------------|
| Review TypeScript code | `/developer-kit-typescript:devkit.typescript.code-review` |
| Review React code | `/developer-kit-typescript:devkit.react.code-review` |
| Security audit | `/developer-kit-typescript:devkit.ts.security-review` |
| Performance review (React) | `/developer-kit-typescript:devkit.react.code-review performance` |
| Architecture review | `/developer-kit-typescript:devkit.typescript.code-review architecture` |
| Best practices review | `/developer-kit-typescript:devkit.react.code-review best-practices` |

---

## See Also

- [TypeScript Agents Guide](./guide-agents.md) - TypeScript plugin agents
- [NestJS Skills Guide](./guide-skills-nestjs.md) - NestJS framework skills
- [Frontend Skills Guide](./guide-skills-frontend.md) - React, TypeScript, UI skills
- [Core Command Guide](../developer-kit-core/docs/guide-commands.md) - All commands across plugins
