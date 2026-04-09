# PHP Plugin Agents Guide

Comprehensive guide for all PHP specialized agents available in the Developer Kit PHP Plugin.

---

## Overview

The PHP Plugin provides 5 specialized agents for PHP development. Each agent has deep expertise in specific areas and uses the `sonnet` model for optimal performance.

### Agent Summary

| Agent | Focus Area | Tools |
|-------|------------|-------|
| `php-code-review-expert` | Code quality, PSR standards | Read, Write, Edit, Glob, Grep, Bash |
| `php-refactor-expert` | Code improvement, design patterns | Read, Write, Edit, Glob, Grep, Bash |
| `php-security-expert` | Security, OWASP, DevSecOps | Read, Write, Edit, Glob, Grep, Bash |
| `php-software-architect-expert` | Architecture, DDD, scalability | Read, Write, Edit, Glob, Grep, Bash |
| `wordpress-development-expert` | WordPress, themes, plugins | Read, Write, Edit, Glob, Grep, Bash |

---

## Agent Details

### `php-code-review-expert`

**File**: `agents/php-code-review-expert.md`

Reviews PHP code for quality, standards compliance, and best practices.

**When to use:**
- Before committing PHP code to version control
- During pull request reviews
- When identifying code quality issues
- When ensuring PSR standards compliance

**Key capabilities:**
- PSR-4 and PSR-12 compliance checking
- Modern PHP 8.x features utilization
- Anti-pattern detection
- Framework best practices (Laravel, Symfony)
- Code complexity analysis

---

### `php-refactor-expert`

**File**: `agents/php-refactor-expert.md`

Refactors PHP code using clean code principles and modern PHP patterns.

**When to use:**
- When improving existing PHP code
- When migrating legacy PHP to modern patterns
- When reducing code complexity
- When applying design patterns

**Key capabilities:**
- SOLID principles application
- Design pattern implementation
- PHP 8.3+ features migration
- Code complexity reduction
- Legacy code modernization

---

### `php-security-expert`

**File**: `agents/php-security-expert.md`

Security auditing and vulnerability assessment for PHP applications.

**When to use:**
- Before deploying PHP applications to production
- When auditing authentication and authorization
- When reviewing third-party dependencies
- When ensuring OWASP compliance

**Key capabilities:**
- OWASP Top 10 vulnerability detection
- Authentication and authorization review
- Dependency vulnerability scanning (CVEs)
- Cryptographic practice validation
- Laravel/Symfony security patterns

---

### `php-software-architect-expert`

**File**: `agents/php-software-architect-expert.md`

Software architecture design and assessment for PHP applications.

**When to use:**
- When designing new PHP applications
- When planning refactoring efforts
- When assessing application scalability
- When reviewing architectural decisions

**Key capabilities:**
- Clean Architecture design
- Domain-Driven Design patterns
- Hexagonal Architecture (Ports & Adapters)
- Package structure analysis
- Scalability assessment

---

### `wordpress-development-expert`

**File**: `agents/wordpress-development-expert.md`

WordPress development specialist for themes, plugins, and custom solutions.

**When to use:**
- When developing WordPress themes
- When creating WordPress plugins
- When working with Gutenberg blocks
- When integrating WordPress APIs

**Key capabilities:**
- WordPress theme development
- WordPress plugin development
- Gutenberg block development
- WordPress hooks and filters
- REST API integration
- Custom post types and taxonomies

---

## Agent Selection Guide

Use this table to select the right agent for your task:

| Task | Recommended Agent |
|------|-------------------|
| Review PHP code before commit | `php-code-review-expert` |
| Improve code quality | `php-refactor-expert` |
| Security vulnerability audit | `php-security-expert` |
| Design application architecture | `php-software-architect-expert` |
| Develop WordPress themes | `wordpress-development-expert` |
| Develop WordPress plugins | `wordpress-development-expert` |
| Migrate PHP 7 to PHP 8.x | `php-refactor-expert` |
| Set up authentication | `php-security-expert` |
| Implement DDD patterns | `php-software-architect-expert` |
| WordPress REST API integration | `wordpress-development-expert` |

---

## How to Invoke Agents

### Automatic Selection

Claude automatically selects the appropriate agent based on your task context. Simply describe what you need:

```
Review my PHP authentication code for security issues
```

Claude will automatically invoke `php-security-expert` for security-related tasks.

### Direct Invocation

You can explicitly request a specific agent:

```
Ask the php-code-review-expert to review the User class
```

### Via Task Tool

When creating background tasks, specify the agent:

```
Use the php-refactor-expert agent to refactor the Order service
```

---

## Integration with Skills

Agents work alongside skills for comprehensive development:

| Agent | Complementary Skills |
|-------|---------------------|
| `php-code-review-expert` | `clean-architecture`, `language-best-practices` rule |
| `php-refactor-expert` | `clean-architecture`, `aws-lambda-php-integration` |
| `php-security-expert` | PHP security rules and patterns |
| `php-software-architect-expert` | `clean-architecture` |
| `wordpress-development-expert` | `wordpress-sage-theme` |

---

## See Also

- [Architecture Skills Guide](guide-skills-architecture.md) - Clean Architecture and DDD patterns
- [WordPress Sage Theme Skill](../skills/wordpress/wordpress-sage-theme/SKILL.md) - Sage framework details
- [Core Agent Guide](../../developer-kit-core/docs/guide-agents.md) - All agents across plugins
