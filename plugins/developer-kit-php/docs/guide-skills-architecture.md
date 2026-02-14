# Architecture Skills Guide

Quick reference to Clean Architecture skill for PHP applications.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **clean-architecture** | Clean Architecture, Hexagonal Architecture, and DDD patterns for PHP (Laravel/Symfony) |

---

## clean-architecture

**File**: `skills/clean-architecture/SKILL.md`

Provides implementation patterns for Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design in PHP applications (Laravel, Symfony).

### When to use

- Architecting new Laravel/Symfony applications with clear separation of concerns
- Refactoring tightly coupled code into testable, layered architectures
- Implementing domain logic independent of frameworks and infrastructure
- Designing ports and adapters for swappable implementations
- Applying Domain-Driven Design tactical patterns (entities, value objects, aggregates)
- Creating testable business logic without framework context dependencies

### Key Concepts

#### Clean Architecture Layers

| Layer | Responsibility | PHP Equivalent |
|-------|---------------|----------------|
| **Domain** | Entities, value objects, domain events, repository interfaces | `Domain/` - pure PHP classes |
| **Application** | Use cases, application services, DTOs, ports | `Application/` - services, use cases |
| **Infrastructure** | Frameworks, database, external APIs | `Infrastructure/` - Eloquent/Doctrine |
| **Adapter** | Controllers, presenters, external gateways | `Interface/` - HTTP/Console |

#### Hexagonal Architecture (Ports & Adapters)

- **Domain Core**: Pure PHP business logic, no framework dependencies
- **Ports**: Interfaces defining contracts (driven and driving)
- **Adapters**: Concrete implementations (Eloquent, Doctrine, REST, CLI)

#### Domain-Driven Design Tactical Patterns

- **Entities**: Objects with identity and lifecycle (e.g., `Order`, `Customer`)
- **Value Objects**: Immutable, defined by attributes (e.g., `Money`, `Email`)
- **Aggregates**: Consistency boundary with root entity
- **Domain Events**: Capture significant business occurrences
- **Repositories**: Persistence abstraction, implemented in infrastructure

### Package Structure

```
src/Modules/Order/
├── Domain/
│   ├── Model/              # Entities, value objects
│   ├── Events/             # Domain events
│   ├── Repository/         # Repository interfaces (ports)
│   └── Exception/          # Domain exceptions
├── Application/
│   ├── UseCase/            # Use case interfaces
│   ├── Service/            # Application services
│   └── DTO/               # Request/response DTOs
├── Infrastructure/
│   ├── Persistence/        # Eloquent/Doctrine entities, repository adapters
│   └── External/          # External service adapters
└── Interface/
    └── Http/              # Laravel/Symfony controllers
```

### Best Practices

1. **Dependency Rule**: Domain has zero dependencies on frameworks (Laravel/Symfony)
2. **Immutable Value Objects**: Use PHP readonly properties and typed classes
3. **Rich Domain Models**: Place business logic in entities, not services
4. **Repository Pattern**: Domain defines interface, infrastructure implements
5. **Domain Events**: Decouple side effects from primary operations
6. **Constructor Injection**: Mandatory dependencies via constructor
7. **DTO Mapping**: Separate domain models from API contracts
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

- **PHP**: 8.2+
- **Frameworks**: Laravel 10+, Symfony 6+
- **Architecture**: Clean Architecture, Hexagonal Architecture, DDD

---

**Note**: For complete patterns and examples, see the skill file at `skills/clean-architecture/SKILL.md`
