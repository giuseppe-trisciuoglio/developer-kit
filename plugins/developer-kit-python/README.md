# Developer Kit Python Plugin

Comprehensive Python development capabilities for Claude Code.

## Overview

The `developer-kit-python` plugin provides specialized Python development tools including code review, refactoring, security assessment, architectural guidance, and production-ready patterns. It supports modern Python (3.11+) with focus on clean architecture, AWS Lambda integration, and best practices.

## Components

### Agents (4)

| Agent | Purpose |
|-------|---------|
| `python-code-review-expert` | Code quality review and PEP standards compliance |
| `python-refactor-expert` | Clean code refactoring and design patterns |
| `python-security-expert` | Security vulnerability assessment (OWASP, CVEs) |
| `python-software-architect-expert` | Architecture design and scalability evaluation |

### Skills (2)

| Skill | Purpose |
|-------|---------|
| `clean-architecture` | Clean Architecture, Hexagonal Architecture, and DDD patterns |
| `aws-lambda-python-integration` | AWS Lambda deployment with Chalice and raw Python approaches |

### Rules (4)

Rules activate automatically for all `**/*.py` files:

| Rule | Purpose |
|------|---------|
| `error-handling` | Exception hierarchies, logging, and recovery patterns |
| `language-best-practices` | Modern Python (3.11+) patterns, type hints, async |
| `naming-conventions` | PEP 8 naming standards for modules, classes, functions |
| `project-structure` | Modular project organization and layer separation |

### LSP Servers

The plugin includes LSP configuration for Python IDE support:

- **pyright-langserver**: Fast, Microsoft TypeScript-based language server
- **pylsp**: Python Language Server Protocol implementation

> **Note:** LSP binaries must be installed separately. Install with: `pip install pyright` or `pip install python-lsp-server`

## Installation

This plugin requires `developer-kit-core`:

```bash
claude plugin install ./plugins/developer-kit-python --scope project
```

## Quick Start

1. **Review Python code**: Claude automatically invokes `python-code-review-expert` for code reviews
2. **Refactor Python code**: Use `python-refactor-expert` for clean code improvements
3. **Security audit**: Invoke `python-security-expert` for vulnerability assessment
4. **Design architecture**: Use `python-software-architect-expert` for architectural decisions
5. **Apply patterns**: Use `/clean-architecture` skill for layered architecture guidance
6. **Deploy to AWS**: Use `/aws-lambda-python-integration` for Lambda deployment patterns

## Documentation

| Guide | Content |
|-------|---------|
| [Agent Guide](./docs/guide-agents.md) | Detailed documentation for all 4 agents |
| [Skills Guide](./docs/guide-skills-architecture.md) | Architecture patterns for both skills |
| [Rules Reference](./docs/guide-rules.md) | Python coding rules and best practices |

## Key Features

### Code Quality
- PEP 8 and PEP 484 compliance
- Python 3.8+ idioms and patterns
- Code complexity assessment
- Type hints validation

### Refactoring
- Clean code principles
- Design pattern implementation
- Legacy code migration
- Complexity reduction

### Security
- OWASP Top 10 vulnerability detection
- CVE scanning for dependencies
- Authentication/authorization review
- Secure coding practices

### Architecture
- Clean Architecture implementation
- Hexagonal Architecture (Ports & Adapters)
- Domain-Driven Design patterns
- Dependency injection patterns

### AWS Lambda
- AWS Chalice framework integration
- Raw Python minimal handlers
- Cold start optimization (< 100ms)
- SAM and Serverless Framework deployment

## Technology Stack

- **Python**: 3.11+ (recommended), 3.8+ (minimum)
- **Web Frameworks**: FastAPI, Flask, Django
- **AWS**: Lambda, API Gateway, Chalice, boto3
- **ORM**: SQLAlchemy (async), Django ORM
- **Validation**: Pydantic
- **Testing**: pytest, pytest-asyncio, moto

## See Also

- [Core Plugin Documentation](../developer-kit-core/docs/) - Core guides and shared patterns
- [TypeScript Plugin Documentation](../developer-kit-typescript/docs/) - NestJS, React, and Next.js
- [Java Plugin Documentation](../developer-kit-java/docs/) - Spring Boot and JVM patterns
- [AI Plugin Documentation](../developer-kit-ai/docs/) - RAG and prompt engineering