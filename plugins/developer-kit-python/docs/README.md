# Developer Kit Python Plugin

Welcome to the Developer Kit Python Plugin documentation. This plugin provides comprehensive tools for Python development with focus on code quality, architecture patterns, and AWS Lambda integration.

## Available Documentation

| Guide | Description |
|-------|-------------|
| [Agent Guide](./guide-agents.md) | Specialized agents for code review, refactoring, security, and architecture |
| [Skills Guide](./guide-skills-architecture.md) | Clean Architecture and AWS Lambda integration patterns |
| [Rules Reference](./guide-rules.md) | Python coding rules for error handling, naming, structure, and best practices |

## Plugin Overview

The Python plugin provides:

- **4 Agents**: Python code review, refactoring, security, and architecture experts
- **2 Skills**: Clean Architecture and AWS Lambda integration patterns
- **4 Rules**: Automatic Python best practices (error handling, naming, structure, language)
- **LSP Support**: pyright-langserver and pylsp configuration

## Quick Start

1. **Code review**: Claude automatically invokes `python-code-review-expert`
2. **Refactoring**: Use `python-refactor-expert`
3. **Security audit**: Use `python-security-expert`
4. **Architecture design**: Use `python-software-architect-expert`
5. **Clean Architecture**: Invoke `/clean-architecture` skill
6. **AWS Lambda**: Invoke `/aws-lambda-python-integration` skill

## Plugin Structure

```
developer-kit-python/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── agents/                   # 4 specialized agents
│   ├── python-code-review-expert.md
│   ├── python-refactor-expert.md
│   ├── python-security-expert.md
│   └── python-software-architect-expert.md
├── skills/                   # 2 skills
│   ├── clean-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   └── aws-lambda-python-integration/
│       ├── SKILL.md
│       └── references/
├── rules/                    # 4 coding rules
│   ├── error-handling.md
│   ├── language-best-practices.md
│   ├── naming-conventions.md
│   └── project-structure.md
├── .lsp.json                 # LSP server configuration
└── docs/                     # This documentation
```

## Key Features

### Python Code Quality
- PEP 8 and PEP 484 compliance checking
- Python idioms and patterns validation
- Code complexity assessment
- Type hints enforcement (3.11+ generics)

### Python Refactoring
- Clean code principles application
- Design pattern implementation (Strategy, Repository, Factory)
- Legacy code migration
- Python 3.8+ features utilization

### Python Security
- OWASP Top 10 vulnerability detection
- Dependency CVE scanning
- Authentication/authorization review
- Secure coding practices validation

### Python Architecture
- Clean Architecture implementation
- Hexagonal Architecture (Ports & Adapters)
- Domain-Driven Design tactical patterns
- Dependency injection patterns

### AWS Lambda Integration
- AWS Chalice framework patterns
- Raw Python minimal handlers (< 100ms cold start)
- SAM and Serverless Framework deployment
- Cold start optimization techniques

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Python** | 3.11+ (recommended), 3.8+ (minimum) |
| **Web Frameworks** | FastAPI, Flask, Django |
| **AWS** | Lambda, API Gateway, Chalice, boto3 |
| **ORM** | SQLAlchemy (async), Django ORM |
| **Validation** | Pydantic v2 |
| **Testing** | pytest, pytest-asyncio, moto |
| **LSP** | pyright-langserver, pylsp |

## See Also

- [Core Plugin Documentation](../../developer-kit-core/docs/) - Shared patterns and installation
- [TypeScript Plugin Documentation](../../developer-kit-typescript/docs/) - NestJS, React, Next.js
- [Java Plugin Documentation](../../developer-kit-java/docs/) - Spring Boot, AWS SDK
- [AI Plugin Documentation](../../developer-kit-ai/docs/) - RAG, chunking, prompt engineering