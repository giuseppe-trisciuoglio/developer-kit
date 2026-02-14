# Architecture Skills Guide

Quick reference to Clean Architecture skill for Java Spring Boot applications.

---

## Skills Overview

| Skill | Purpose |
|-------|---------|
| **clean-architecture** | Clean Architecture, Hexagonal Architecture, and DDD patterns for Java 21+ Spring Boot 3.5+ |

---

## clean-architecture

**File**: `skills/clean-architecture/SKILL.md`

Provides implementation patterns for Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design in Java 21+ Spring Boot 3.5+ applications.

### When to use

- Architecting new Spring Boot applications with clear separation of concerns
- Refactoring tightly coupled code into testable, layered architectures
- Implementing domain logic independent of frameworks and infrastructure
- Designing ports and adapters for swappable implementations
- Applying Domain-Driven Design tactical patterns (entities, value objects, aggregates)
- Creating testable business logic without Spring context dependencies

### Key Concepts

#### Clean Architecture Layers

| Layer | Responsibility | Spring Boot Equivalent |
|-------|---------------|----------------------|
| **Domain** | Entities, value objects, domain events, repository interfaces | `domain/` - no Spring annotations |
| **Application** | Use cases, application services, DTOs, ports | `application/` - @Service, @Transactional |
| **Infrastructure** | Frameworks, database, external APIs | `infrastructure/` - @Repository, @Entity |
| **Adapter** | Controllers, presenters, external gateways | `adapter/` - @RestController |

#### Hexagonal Architecture (Ports & Adapters)

- **Domain Core**: Pure Java business logic, no framework dependencies
- **Ports**: Interfaces defining contracts (driven and driving)
- **Adapters**: Concrete implementations (JPA, REST, messaging)

#### Domain-Driven Design Tactical Patterns

- **Entities**: Objects with identity and lifecycle (e.g., `Order`, `Customer`)
- **Value Objects**: Immutable, defined by attributes (e.g., `Money`, `Email`)
- **Aggregates**: Consistency boundary with root entity
- **Domain Events**: Capture significant business occurrences
- **Repositories**: Persistence abstraction, implemented in infrastructure

### Package Structure

```
com.example.order/
├── domain/
│   ├── model/              # Entities, value objects
│   ├── event/              # Domain events
│   ├── repository/         # Repository interfaces (ports)
│   └── exception/          # Domain exceptions
├── application/
│   ├── port/in/            # Driving ports (use case interfaces)
│   ├── port/out/           # Driven ports (external service interfaces)
│   ├── service/            # Application services
│   └── dto/                # Request/response DTOs
├── infrastructure/
│   ├── persistence/        # JPA entities, repository adapters
│   └── external/           # External service adapters
└── adapter/
    └── rest/               # REST controllers
```

### Best Practices

1. **Dependency Rule**: Domain has zero dependencies on Spring or other frameworks
2. **Immutable Value Objects**: Use Java records for value objects with built-in validation
3. **Rich Domain Models**: Place business logic in entities, not services
4. **Repository Pattern**: Domain defines interface, infrastructure implements
5. **Domain Events**: Decouple side effects from primary operations
6. **Constructor Injection**: Mandatory dependencies via final fields
7. **DTO Mapping**: Separate domain models from API contracts
8. **Transaction Boundaries**: Place @Transactional in application services

### Common Pitfalls to Avoid

- **Anemic Domain Model**: Entities with only getters/setters, logic in services
- **Framework Leakage**: `@Entity`, `@Autowired` in domain layer
- **Lazy Loading Issues**: Exposing JPA entities through domain model
- **Circular Dependencies**: Between domain aggregates - use IDs instead
- **Missing Domain Events**: Direct service calls instead of events
- **Repository Misplacement**: Defining repository interfaces in infrastructure
- **DTO Bypass**: Exposing domain entities directly in API

---

## Technology Stack

- **Java**: 21+
- **Spring Boot**: 3.5+
- **Architecture**: Clean Architecture, Hexagonal Architecture, DDD

---

**Note**: For complete patterns and examples, see the skill file at `skills/clean-architecture/SKILL.md`
