# Architecture Skills Guide

Quick reference to Clean Architecture skill for TypeScript/Node.js applications.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **clean-architecture** | Clean Architecture, Hexagonal Architecture, and DDD patterns for TypeScript/Node.js |

---

## clean-architecture

**File**: `skills/clean-architecture/SKILL.md`

Provides implementation patterns for Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design in TypeScript/Node.js applications.

### When to use

- Architecting new NestJS or TypeScript applications with clear separation of concerns
- Refactoring tightly coupled code into testable, layered architectures
- Implementing domain logic independent of frameworks and infrastructure
- Designing ports and adapters for swappable implementations
- Applying Domain-Driven Design tactical patterns (entities, value objects, aggregates)
- Creating testable business logic without framework context dependencies

### Key Concepts

#### Clean Architecture Layers

| Layer | Responsibility | TypeScript Equivalent |
|-------|---------------|----------------------|
| **Domain** | Entities, value objects, domain events, repository interfaces | `domain/` - pure TypeScript |
| **Application** | Use cases, application services, DTOs, ports | `application/` - services, use cases |
| **Infrastructure** | Frameworks, database, external APIs | `infrastructure/` - TypeORM, Prisma adapters |
| **Adapter** | Controllers, presenters, external gateways | `adapter/` - NestJS controllers |

#### Hexagonal Architecture (Ports & Adapters)

- **Domain Core**: Pure TypeScript business logic, no framework dependencies
- **Ports**: Interfaces defining contracts (driven and driving)
- **Adapters**: Concrete implementations (TypeORM, Prisma, REST, GraphQL)

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
│   ├── ports/             # Use case interfaces
│   ├── services/          # Application services
│   └── dto/              # Request/response DTOs
├── infrastructure/
│   ├── persistence/        # TypeORM/Prisma entities, repository adapters
│   └── external/          # External service adapters
└── presentation/
    └── http/              # NestJS controllers
```

### Best Practices

1. **Dependency Rule**: Domain has zero dependencies on frameworks (NestJS, TypeORM, etc.)
2. **Immutable Value Objects**: Use TypeScript readonly properties and classes
3. **Rich Domain Models**: Place business logic in entities, not services
4. **Repository Pattern**: Domain defines interface, infrastructure implements
5. **Domain Events**: Decouple side effects from primary operations
6. **Constructor Injection**: Mandatory dependencies via constructor
7. **DTO Mapping**: Separate domain models from API contracts
8. **Transaction Boundaries**: Place transactions in application services

### Common Pitfalls to Avoid

- **Anemic Domain Model**: Entities with only getters/setters, logic in services
- **Framework Leakage**: Decorators from NestJS/TypeORM in domain layer
- **Circular Dependencies**: Between domain aggregates - use IDs instead
- **Missing Domain Events**: Direct service calls instead of events
- **Repository Misplacement**: Defining repository interfaces in infrastructure
- **DTO Bypass**: Exposing domain entities directly in API

---

## Technology Stack

- **TypeScript**: 5.x+
- **Node.js**: 18+
- **Frameworks**: NestJS, Express, Fastify
- **Architecture**: Clean Architecture, Hexagonal Architecture, DDD

---

**Note**: For complete patterns and examples, see the skill file at `skills/clean-architecture/SKILL.md`
