# Architecture Skills Guide

Quick reference to Clean Architecture skill for Python applications.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **clean-architecture** | Clean Architecture, Hexagonal Architecture, and DDD patterns for Python |

---

## clean-architecture

**File**: `skills/clean-architecture/SKILL.md`

Provides implementation patterns for Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design in Python applications.

### When to use

- Architecting new Python applications with clear separation of concerns
- Refactoring tightly coupled code into testable, layered architectures
- Implementing domain logic independent of frameworks and infrastructure
- Designing ports and adapters for swappable implementations
- Applying Domain-Driven Design tactical patterns (entities, value objects, aggregates)
- Creating testable business logic without framework context dependencies

### Key Concepts

#### Clean Architecture Layers

| Layer | Responsibility | Python Equivalent |
|-------|---------------|------------------|
| **Domain** | Entities, value objects, domain events, repository interfaces | `domain/` - pure Python classes |
| **Application** | Use cases, application services, DTOs, ports | `application/` - services, use cases |
| **Infrastructure** | Frameworks, database, external APIs | `infrastructure/` - SQLAlchemy, Django ORM |
| **Adapter** | Controllers, presenters, external gateways | `api/` - FastAPI, Flask views |

#### Hexagonal Architecture (Ports & Adapters)

- **Domain Core**: Pure Python business logic, no framework dependencies
- **Ports**: Abstract base classes defining contracts (driven and driving)
- **Adapters**: Concrete implementations (SQLAlchemy, Django, REST, CLI)

#### Domain-Driven Design Tactical Patterns

- **Entities**: Objects with identity and lifecycle (e.g., `Order`, `Customer`)
- **Value Objects**: Immutable, defined by attributes (e.g., `Money`, `Email`)
- **Aggregates**: Consistency boundary with root entity
- **Domain Events**: Capture significant business occurrences
- **Repositories**: Persistence abstraction, implemented in infrastructure

### Package Structure

```
src/modules/order/
├── domain/
│   ├── model/              # Entities, value objects
│   ├── events/             # Domain events
│   ├── repository/         # Repository interfaces (ports)
│   └── exceptions/        # Domain exceptions
├── application/
│   ├── use_cases/         # Use case implementations
│   ├── services/          # Application services
│   └── dto/              # Request/response DTOs
├── infrastructure/
│   ├── persistence/        # SQLAlchemy/Django entities, repository adapters
│   └── external/         # External service adapters
└── api/
    └── rest/              # FastAPI/Flask controllers
```

### Best Practices

1. **Dependency Rule**: Domain has zero dependencies on frameworks (FastAPI, Django, etc.)
2. **Immutable Value Objects**: Use `@dataclass(frozen=True)` or `attrs`
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

---

## Technology Stack

- **Python**: 3.11+
- **Frameworks**: FastAPI, Django, Flask
- **Architecture**: Clean Architecture, Hexagonal Architecture, DDD

---

**Note**: For complete patterns and examples, see the skill file at `skills/clean-architecture/SKILL.md`
