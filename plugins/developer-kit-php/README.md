# Developer Kit PHP

PHP and WordPress development capabilities for Claude Code.

## Overview

The `developer-kit-php` plugin provides comprehensive PHP development support, including specialized agents for code review, refactoring, security, software architecture, and WordPress development. It also includes skills for Clean Architecture patterns and AWS Lambda deployment.

## Quick Reference

| Component | Count | Purpose |
|-----------|-------|---------|
| Agents | 5 | Specialized PHP development experts |
| Skills | 3 | WordPress Sage, Clean Architecture, AWS Lambda |
| Rules | 4 | PHP coding standards (PSR-12, error handling, naming) |

## Agents

| Agent | Purpose |
|-------|---------|
| `php-code-review-expert` | PHP code quality review with PSR standards compliance |
| `php-refactor-expert` | PHP code refactoring with clean code principles and PHP 8.3+ best practices |
| `php-security-expert` | Security auditing, OWASP vulnerabilities, and DevSecOps for Laravel/Symfony |
| `php-software-architect-expert` | Clean Architecture, DDD, hexagonal architecture, and software design |
| `wordpress-development-expert` | WordPress themes, plugins, Gutenberg, hooks/filters, REST API |

**Model**: All agents use `sonnet` for optimal performance.

## Skills

| Skill | When to Use |
|-------|-------------|
| `wordpress-sage-theme` | Creating/modifying WordPress themes with Sage (roots/sage), Blade templates, Vite/Bud build tools, ACF integration |
| `clean-architecture` | Architecting enterprise PHP applications with entities/value objects, refactoring legacy code, implementing DDD with Symfony |
| `aws-lambda-php-integration` | Deploying PHP/Symfony to AWS Lambda with Bref, configuring API Gateway, implementing serverless patterns |

## Coding Rules

Automatic PHP coding standards enforcement via 4 rules:

| Rule | Scope | Purpose |
|------|-------|---------|
| `error-handling` | `**/*.php` | Exception hierarchy, global exception handling, error response format |
| `language-best-practices` | `**/*.php` | Strict typing, PHP 8.1+ features, dependency injection |
| `naming-conventions` | `**/*.php` | PSR-12 naming for classes, methods, properties, namespaces |
| `project-structure` | `**/*.php` | PSR-4 compliant directory layout, layer responsibilities |

## LSP Support

The plugin configures PHP Language Server support:

- **Intelephense** (`intelephense`) - Fast, lightweight PHP IDE support
- **PHP Language Server** (`php-language-server`) - Alternative full-featured server

Install the binary separately, then Claude Code will automatically use it for PHP files.

## Dependencies

- `developer-kit` (required core plugin)

## Documentation

- [Plugin Docs](docs/README.md) - Main documentation index
- [Agent Guide](docs/guide-agents.md) - Detailed agent usage and selection guide
- [Architecture Skills Guide](docs/guide-skills-architecture.md) - Clean Architecture and DDD patterns

## Version

**2.8.0**
