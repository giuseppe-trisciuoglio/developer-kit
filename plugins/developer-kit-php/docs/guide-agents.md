# PHP Plugin Agents Guide

This guide provides comprehensive documentation for all PHP specialized agents available in the Developer Kit PHP Plugin.

---

## Overview

The PHP Plugin provides specialized agents for PHP development, including code review, refactoring, security assessment, and architecture design. These agents have deep expertise in PHP best practices, frameworks, and WordPress development.

### Available Agents

- **PHP Code Review**: 1 agent for PHP code quality review
- **PHP Refactoring**: 1 agent for PHP code refactoring
- **PHP Security**: 1 agent for PHP security assessment
- **PHP Architecture**: 1 agent for PHP software architecture
- **WordPress Development**: 1 agent for WordPress development

---

## PHP Development Agents

### `php-code-review-expert`

**File**: `agents/php-code-review-expert.md`

**Purpose**: PHP code quality and best practices review with PSR standards compliance.

**When to use:**
- Reviewing PHP code before commits
- Ensuring PSR standards compliance
- Identifying PHP anti-patterns
- Validating PHP framework usage
- Reviewing PHP code quality

**Key Capabilities:**
- PSR standards compliance
- PHP framework best practices
- Code quality assessment
- Anti-pattern detection
- Modern PHP features utilization

---

### `php-refactor-expert`

**File**: `agents/php-refactor-expert.md`

**Purpose**: PHP code refactoring with clean code principles, PSR standards, and PHP best practices.

**When to use:**
- Refactoring PHP code
- Applying clean code principles
- Implementing PHP design patterns
- Reducing code complexity
- Migrating legacy PHP code

**Key Capabilities:**
- PSR standards compliance
- Clean code principles for PHP
- Design pattern implementation
- Code complexity reduction
- Modern PHP features (PHP 8.x)

---

### `php-security-expert`

**File**: `agents/php-security-expert.md`

**Purpose**: PHP security vulnerability assessment covering OWASP, CVEs, and secure coding practices.

**When to use:**
- Security auditing PHP applications
- Identifying OWASP vulnerabilities
- Reviewing authentication implementation
- Checking for dependency vulnerabilities
- Validating secure coding practices

**Key Capabilities:**
- OWASP vulnerability detection
- Authentication and authorization review
- Dependency vulnerability scanning (CVEs)
- Cryptographic practice validation
- Secure coding practices for PHP

---

### `php-software-architect-expert`

**File**: `agents/php-software-architect-expert.md`

**Purpose**: PHP architecture design specialist focusing on patterns, scalability, and architectural decisions.

**When to use:**
- Designing PHP application architecture
- Reviewing PHP package structure
- Planning refactoring efforts
- Assessing scalability
- Validating architectural decisions

**Key Capabilities:**
- PHP architecture patterns
- Package structure review
- Design pattern assessment
- Scalability evaluation
- Architectural decision validation

---

### `wordpress-development-expert`

**File**: `agents/wordpress-development-expert.md`

**Purpose**: WordPress development specialist for themes, plugins, and custom WordPress solutions.

**When to use:**
- Developing WordPress themes
- Creating WordPress plugins
- Custom WordPress development
- WordPress API integration
- WordPress performance optimization

**Key Capabilities:**
- WordPress theme development
- WordPress plugin development
- WordPress hooks and filters
- Custom post types and taxonomies
- WordPress API integration
- Performance optimization

---

## Agent Usage Guidelines

### When to Use PHP Plugin Agents

PHP Plugin agents are most effective for:
- **Code Quality**: Reviewing and refactoring PHP code
- **Security**: Auditing PHP applications for vulnerabilities
- **Architecture**: Designing and reviewing PHP application architecture
- **WordPress**: Developing WordPress themes and plugins

### How to Invoke Agents

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the php-code-review-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

### Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Review PHP code | `php-code-review-expert` |
| Refactor PHP code | `php-refactor-expert` |
| Security audit | `php-security-expert` |
| Architecture review | `php-software-architect-expert` |
| WordPress development | `wordpress-development-expert` |

---

## See Also

- [WordPress Skill](../skills/wordpress-sage-theme/) - WordPress Sage theme skill
- [Core Agent Guide](../developer-kit-core/docs/guide-agents.md) - All agents across plugins
