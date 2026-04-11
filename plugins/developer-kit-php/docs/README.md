# Developer Kit PHP Plugin Documentation

Comprehensive documentation for the PHP and WordPress development plugin.

---

## Plugin Overview

The Developer Kit PHP Plugin provides:

- **5 Specialized Agents** for PHP code review, refactoring, security auditing, software architecture, and WordPress development
- **3 Skills** for WordPress Sage theme development, Clean Architecture patterns, and AWS Lambda PHP integration
- **4 Coding Rules** for automatic PSR-12 compliance and PHP best practices enforcement
- **LSP Configuration** for PHP IntelliSense with Intelephense

---

## Documentation Index

### Getting Started
- [Agent Guide](guide-agents.md) - How to use and select the right PHP agent
- [Architecture Skills Guide](guide-skills-architecture.md) - Clean Architecture, DDD, and AWS Lambda patterns

### Skills Reference
| Skill | File | Use Case |
|-------|------|----------|
| WordPress Sage Theme | `../skills/wordpress/wordpress-sage-theme/SKILL.md` | WordPress themes with Sage, Blade, ACF |
| Clean Architecture | `../skills/clean-architecture/SKILL.md` | Enterprise PHP with DDD patterns |
| AWS Lambda PHP Integration | `../skills/aws-lambda-php-integration/SKILL.md` | Serverless PHP on AWS Lambda |

---

## Plugin Structure

```
developer-kit-php/
├── agents/
│   ├── php-code-review-expert.md
│   ├── php-refactor-expert.md
│   ├── php-security-expert.md
│   ├── php-software-architect-expert.md
│   └── wordpress-development-expert.md
├── skills/
│   ├── wordpress/
│   │   └── wordpress-sage-theme/
│   │       ├── SKILL.md
│   │       └── references/
│   ├── clean-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   └── aws-lambda-php-integration/
│       ├── SKILL.md
│       └── references/
├── rules/
│   ├── error-handling.md
│   ├── language-best-practices.md
│   ├── naming-conventions.md
│   └── project-structure.md
└── docs/
    ├── README.md
    ├── guide-agents.md
    └── guide-skills-architecture.md
```

---

## Quick Start

### 1. Choose the Right Agent

| Task | Agent |
|------|-------|
| Review PHP code before commits | `php-code-review-expert` |
| Refactor legacy PHP code | `php-refactor-expert` |
| Security audit PHP application | `php-security-expert` |
| Design PHP application architecture | `php-software-architect-expert` |
| WordPress theme or plugin development | `wordpress-development-expert` |

### 2. Use Skills for Specific Patterns

- **WordPress Sage Theme**: `/developer-kit-php:wordpress-sage-theme` for Sage-based WordPress development
- **Clean Architecture**: `/developer-kit-php:clean-architecture` for DDD and enterprise patterns
- **AWS Lambda PHP**: `/developer-kit-php:aws-lambda-php-integration` for serverless deployment

### 3. Coding Rules Apply Automatically

PHP files automatically get PSR-12 enforcement, naming conventions, and error handling guidelines based on the `globs` patterns in the rules directory.

---

## Key Features

### PHP Code Quality
- PSR standards (PSR-4, PSR-12) compliance
- Modern PHP 8.3+ features (readonly, enums, named arguments, match)
- Anti-pattern detection and remediation

### PHP Security
- OWASP Top 10 vulnerability detection
- Dependency vulnerability scanning (CVEs)
- Authentication and authorization review
- DevSecOps integration for Laravel/Symfony

### PHP Architecture
- Clean Architecture and Hexagonal Architecture patterns
- Domain-Driven Design tactical patterns (entities, value objects, aggregates)
- Scalability assessment and architectural decisions

### WordPress Development
- Sage (roots/sage) theme framework
- Blade templates with WordPress functions
- ACF Pro integration
- Vite and Bud build tools
- Gutenberg block development

### AWS Lambda Integration
- Bref framework for Symfony integration
- Raw PHP handlers with PSR-15
- API Gateway configuration
- Cold start optimization
- Serverless Framework and SAM deployment

---

## Technology Support

| Category | Technologies |
|----------|-------------|
| **PHP Version** | 8.1, 8.2, 8.3 |
| **Frameworks** | Laravel 10+, Symfony 6+, WordPress 6+ |
| **WordPress** | Sage 10+, ACF Pro, Gutenberg |
| **AWS** | Lambda, API Gateway, SQS, SNS, DynamoDB, S3 |
| **Architecture** | Clean Architecture, Hexagonal, DDD |
| **Standards** | PSR-4, PSR-12, PSR-15 |

---

## See Also

- [Core Plugin Documentation](../../developer-kit-core/docs/) - Core guides and installation
- [Python Plugin Documentation](../../developer-kit-python/docs/) - Python development guides
- [TypeScript Plugin Documentation](../../developer-kit-typescript/docs/) - TypeScript and React guides
- [DevOps Plugin Documentation](../../developer-kit-devops/docs/) - Docker and CI/CD guides
