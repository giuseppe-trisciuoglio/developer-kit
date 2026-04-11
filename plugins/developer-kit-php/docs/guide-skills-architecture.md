# Architecture Skills Guide

Quick reference for PHP architecture skills covering Clean Architecture/DDD patterns and AWS Lambda serverless integration.

---

## Skills Overview

| Skill | Purpose | Frameworks |
|-------|---------|------------|
| `clean-architecture` | Clean Architecture, Hexagonal Architecture, DDD patterns | Laravel, Symfony |
| `aws-lambda-php-integration` | Serverless PHP deployment with AWS Lambda | Symfony (Bref), Raw PHP |

---

## clean-architecture

**File**: `skills/clean-architecture/SKILL.md`

Provides implementation patterns for Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design in PHP 8.3+ with Symfony 7.x.

### When to Use

- Architecting new Laravel/Symfony applications with clear separation of concerns
- Refactoring tightly coupled code into testable, layered architectures
- Implementing domain logic independent of frameworks and infrastructure
- Designing ports and adapters for swappable implementations
- Applying Domain-Driven Design tactical patterns (entities, value objects, aggregates)
- Creating testable business logic without framework context dependencies

### Architecture Layers

| Layer | Responsibility | PHP Equivalent |
|-------|---------------|----------------|
| **Domain** | Entities, value objects, domain events, repository interfaces | `Domain/` - pure PHP classes |
| **Application** | Use cases, application services, DTOs, ports | `Application/` - services, use cases |
| **Infrastructure** | Frameworks, database, external APIs | `Infrastructure/` - Doctrine/Eloquent |
| **Interface** | Controllers, presenters, external gateways | `Interface/` - HTTP/Console |

### Package Structure

```
src/
└── Modules/
    └── Order/
        ├── Domain/
        │   ├── Model/          # Entities, value objects
        │   ├── Events/         # Domain events
        │   ├── Repository/     # Repository interfaces (ports)
        │   └── Exception/      # Domain exceptions
        ├── Application/
        │   ├── UseCase/        # Use case classes
        │   ├── Service/        # Application services
        │   └── DTO/           # Request/response DTOs
        ├── Infrastructure/
        │   ├── Persistence/   # Repository adapters
        │   └── External/      # External service adapters
        └── Interface/
            └── Http/
                └── Controller/
```

### Key Patterns

- **Value Objects**: Immutable objects defined by attributes (e.g., `Money`, `Email`, `UUID`)
- **Entities**: Objects with identity and lifecycle (e.g., `Order`, `Customer`)
- **Aggregates**: Consistency boundary with root entity controlling access
- **Domain Events**: Capture significant business occurrences for decoupled side effects
- **Repositories**: Persistence abstraction - domain defines interface, infrastructure implements

### Best Practices

1. **Dependency Rule**: Domain has zero dependencies on frameworks (Laravel/Symfony)
2. **Immutable Value Objects**: Use PHP `readonly` properties and typed classes
3. **Rich Domain Models**: Place business logic in entities, not services
4. **Repository Pattern**: Domain defines interface, infrastructure implements
5. **Domain Events**: Decouple side effects from primary operations
6. **Constructor Injection**: Mandatory dependencies via constructor
7. **DTO Mapping**: Separate domain models from API contracts
8. **Transaction Boundaries**: Place transactions in application services

---

## aws-lambda-php-integration

**File**: `skills/aws-lambda-php-integration/SKILL.md`

Provides AWS Lambda integration patterns for PHP with Symfony using the Bref framework.

### When to Use

- Deploying PHP/Symfony applications to AWS Lambda
- Configuring API Gateway integration for PHP
- Implementing serverless PHP applications
- Optimizing Lambda cold start performance
- Setting up SQS/SNS event triggers

### Trigger Keywords

- "create lambda php", "deploy symfony lambda"
- "bref lambda aws", "php lambda cold start"
- "aws lambda php performance"
- "symfony serverless", "php serverless framework"

### Deployment Options

#### Bref (Symfony)

Best for Symfony applications requiring full framework features.

```
Bref + Symfony = Full Symfony on Lambda
```

- Symfony HTTP Kernel integration
- Warm container optimization
- Doctrine ORM support
- Messenger component support

#### Raw PHP Handlers

Best for lightweight functions with minimal dependencies.

```
Raw PHP + PSR-15 = Minimal Lambda function
```

- Minimal cold start (~10-50ms)
- PSR-15 request/response handlers
- AWS SDK integration (DynamoDB, S3)
- Lazy service loading

### Architecture Patterns

```
┌─────────────────────────────────────────────────────────────┐
│ AWS Lambda                                                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌────────────────────────────────────┐ │
│  │ API Gateway  │──▶│ PHP Runtime (Bref)                 │ │
│  │ HTTP/REST    │   │  ┌────────────────────────────────┐ │ │
│  └──────────────┘   │  │ Symfony / Raw PHP Handler     │ │ │
│                     │  └────────────────────────────────┘ │ │
│  ┌──────────────┐   │                                     │ │
│  │ SQS / SNS    │──▶│ Event Handler                      │ │
│  │ Async Events │   │                                     │ │
│  └──────────────┘   └────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Cold Start Optimization

| Strategy | Impact | Complexity |
|----------|--------|------------|
| Disable unnecessary services | Medium | Low |
| Lazy service loading | High | Medium |
| Smaller container size | Medium | Low |
| Provisioned concurrency | N/A | Low (cost) |
| SnapStart (Java) | N/A | N/A (Java only) |

### Deployment Tools

- **Serverless Framework**: `serverless.yml` configuration
- **AWS SAM**: CloudFormation-based deployment
- **CI/CD**: GitHub Actions, GitLab CI pipelines
- **Custom Domains**: Route 53 + ACM certificates

---

## See Also

- [Clean Architecture Skill](../skills/clean-architecture/SKILL.md) - Complete patterns reference
- [AWS Lambda Skill References](../skills/aws-lambda-php-integration/references/) - Detailed deployment guides
- [WordPress Sage Theme Skill](../skills/wordpress/wordpress-sage-theme/SKILL.md) - WordPress development
