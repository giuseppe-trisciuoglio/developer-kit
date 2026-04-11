# Architecture Skills Guide

Reference guide for Python architecture skills covering Clean Architecture and AWS Lambda integration patterns.

## Skills Overview

| Skill | Purpose | Trigger Phrases |
|-------|---------|-----------------|
| `clean-architecture` | Clean Architecture, Hexagonal, DDD patterns | "clean architecture", "DDD patterns", "hexagonal architecture" |
| `aws-lambda-python-integration` | AWS Lambda deployment and optimization | "deploy lambda", "aws lambda python", "chalice lambda" |

---

## clean-architecture

**File**: `skills/clean-architecture/SKILL.md`

Implements Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design patterns for Python applications with FastAPI or Flask.

### When to Use

- Architecting new Python applications with clear separation of concerns
- Refactoring tightly coupled code into testable, layered architectures
- Implementing domain logic independent of frameworks and infrastructure
- Designing ports and adapters for swappable implementations
- Applying Domain-Driven Design tactical patterns (entities, value objects, aggregates)
- Creating testable business logic without framework context dependencies

### Layer Structure

```
+-------------------+     <- Outer layer (depends on inner)
|  Infrastructure   |     Frameworks, databases, external APIs
+-------------------+
|     Adapters      |     Controllers, presenters, gateways
+-------------------+
|   Application     |     Use cases, application services, DTOs
+-------------------+
|      Domain       |     <- Inner layer (no dependencies)
+-------------------+     Entities, value objects, domain events
```

### Package Structure

```
src/modules/order/
├── domain/
│   ├── model/              # Entities, value objects
│   ├── events/             # Domain events
│   ├── repository/         # Repository interfaces (ports)
│   └── exceptions/         # Domain exceptions
├── application/
│   ├── use_cases/          # Use case implementations
│   ├── services/           # Application services
│   └── dto/                # Request/response DTOs
├── infrastructure/
│   ├── persistence/        # SQLAlchemy/Django entities, repo adapters
│   └── external/           # External service adapters
└── api/
    └── rest/               # FastAPI/Flask controllers
```

### Key Patterns

| Pattern | Description |
|---------|-------------|
| **Entities** | Objects with identity and lifecycle (e.g., `Order`, `Customer`) |
| **Value Objects** | Immutable, defined by attributes (e.g., `Money`, `Email`) |
| **Aggregates** | Consistency boundary with root entity |
| **Domain Events** | Capture significant business occurrences |
| **Repositories** | Persistence abstraction, implemented in infrastructure |
| **Ports** | Abstract base classes defining contracts |
| **Adapters** | Concrete implementations (SQLAlchemy, FastAPI, REST) |

### Best Practices

1. **Dependency Rule**: Domain has zero dependencies on frameworks (FastAPI, Django, etc.)
2. **Immutable Value Objects**: Use `@dataclass(frozen=True)` with validation in `__post_init__`
3. **Rich Domain Models**: Place business logic in entities, not services
4. **Repository Pattern**: Domain defines interface, infrastructure implements
5. **Domain Events**: Decouple side effects from primary operations
6. **Constructor Injection**: Mandatory dependencies via `__init__`
7. **DTO Mapping**: Separate domain models from API contracts (Pydantic models)
8. **Transaction Boundaries**: Place transactions in application services

### Common Pitfalls to Avoid

- **Anemic Domain Model**: Entities with only getters/setters, logic in services
- **Framework Leakage**: Framework-specific code in domain layer
- **Circular Dependencies**: Between domain aggregates - use IDs instead
- **Missing Domain Events**: Direct service calls instead of events
- **Repository Misplacement**: Defining repository interfaces in infrastructure
- **DTO Bypass**: Exposing domain entities directly in API

### References

- `skills/clean-architecture/references/python-clean-architecture.md` - Python-specific patterns
- `skills/clean-architecture/references/fastapi-implementation.md` - Complete FastAPI example

---

## aws-lambda-python-integration

**File**: `skills/aws-lambda-python-integration/SKILL.md`

Provides AWS Lambda integration patterns for Python with cold start optimization. Supports AWS Chalice (full-featured) and Raw Python (minimal overhead) approaches.

### When to Use

- Deploying Python functions to AWS Lambda
- Choosing between AWS Chalice and raw Python approaches
- Optimizing cold start performance (< 100ms target)
- Configuring API Gateway or ALB integration
- Setting up deployment pipelines for Python Lambda

### Approach Comparison

| Approach | Cold Start | Best For | Complexity |
|----------|------------|----------|------------|
| AWS Chalice | < 200ms | REST APIs, rapid development, built-in routing | Low |
| Raw Python | < 100ms | Simple handlers, maximum control, minimal dependencies | Low |

### Project Structure

#### AWS Chalice Structure
```
my-chalice-app/
├── app.py                    # Main application with routes
├── requirements.txt          # Dependencies
├── .chalice/
│   ├── config.json          # Chalice configuration
│   └── deploy/              # Deployment artifacts
├── chalicelib/              # Additional modules
│   ├── __init__.py
│   └── services.py
└── tests/
    └── test_app.py
```

#### Raw Python Structure
```
my-lambda-function/
├── lambda_function.py       # Handler entry point
├── requirements.txt         # Dependencies
├── template.yaml            # SAM/CloudFormation template
└── src/                     # Additional modules
    ├── __init__.py
    ├── handlers.py
    └── utils.py
```

### Cold Start Optimization

Key strategies for < 100ms cold starts:

1. **Initialize at module level** - Persists across warm invocations
2. **Use lazy loading** - Defer heavy imports until needed
3. **Cache boto3 clients** - Reuse connections between invocations

```python
_dynamodb = None

def get_table():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource('dynamodb').Table('my-table')
    return _dynamodb
```

### Deployment Options

| Tool | Use Case |
|------|----------|
| **AWS Chalice** | Rapid deployment, built-in API Gateway |
| **Serverless Framework** | Multi-cloud, plugin ecosystem |
| **AWS SAM** | CloudFormation integration, local testing |

### Lambda Limits

- **Deployment package**: 250MB unzipped (50MB zipped)
- **Memory**: 128MB to 10GB
- **Timeout**: 15 minutes maximum
- **Concurrent executions**: 1000 default

### References

- `skills/aws-lambda-python-integration/references/chalice-lambda.md` - Chalice patterns
- `skills/aws-lambda-python-integration/references/raw-python-lambda.md` - Minimal handlers
- `skills/aws-lambda-python-integration/references/serverless-deployment.md` - CI/CD pipelines
- `skills/aws-lambda-python-integration/references/testing-lambda.md` - Testing patterns

---

## Technology Stack

| Component | Version |
|-----------|---------|
| **Python** | 3.11+ (recommended), 3.8+ (minimum) |
| **Web Frameworks** | FastAPI, Flask, Django |
| **Architecture** | Clean Architecture, Hexagonal, DDD |
| **AWS** | Lambda, API Gateway, Chalice, boto3 |

---

**Note**: For complete patterns and examples, see the skill files at `skills/clean-architecture/SKILL.md` and `skills/aws-lambda-python-integration/SKILL.md`