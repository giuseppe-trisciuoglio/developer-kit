---
name: clean-architecture
description: Provides implementation patterns for Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design in PHP 8.3+ with Symfony 7.x. Use when architecting enterprise PHP applications with entities/value objects/aggregates, refactoring legacy code to modern patterns, implementing domain-driven design with Symfony, or creating testable backends with clear separation of concerns.
allowed-tools: Read, Write, Bash, Edit, Glob, Grep
---

# Clean Architecture, Hexagonal Architecture & DDD for PHP/Symfony

## Overview

This skill provides guidance for implementing Clean Architecture, Hexagonal Architecture (Ports & Adapters), and Domain-Driven Design patterns in PHP 8.3+ applications using Symfony 7.x. It ensures clear separation of concerns, framework-independent business logic, and highly testable code through layered architecture with inward-only dependencies.

## When to Use

- Architecting new enterprise PHP applications with Symfony 7.x
- Refactoring legacy PHP code to modern, testable patterns
- Implementing Domain-Driven Design in PHP projects
- Creating maintainable applications with clear separation of concerns
- Building testable business logic independent of frameworks
- Designing modular PHP systems with swappable infrastructure

## Instructions

### 1. Understand the Architecture Layers

Clean Architecture follows the dependency rule: dependencies only point inward.

```
+-------------------------------------+
|  Infrastructure (Frameworks)        |  Symfony, Doctrine, External APIs
+-------------------------------------+
|  Adapter (Interface Adapters)       |  Controllers, Repositories, Presenters
+-------------------------------------+
|  Application (Use Cases)            |  Commands, Handlers, DTOs
+-------------------------------------+
|  Domain (Entities & Business Rules) |  Entities, Value Objects, Domain Events
+-------------------------------------+
```

**Hexagonal Architecture (Ports & Adapters)**:
- **Domain Core**: Business logic, framework-agnostic
- **Ports**: Interfaces (e.g., `UserRepositoryInterface`)
- **Adapters**: Concrete implementations (Doctrine, InMemory for tests)

**DDD Tactical Patterns**:
- **Entities**: Objects with identity (e.g., `User`, `Order`)
- **Value Objects**: Immutable, defined by attributes (e.g., `Email`, `Money`)
- **Aggregates**: Consistency boundaries with root entity
- **Domain Events**: Capture business occurrences
- **Repositories**: Persist/retrieve aggregates

### 2. Organize Directory Structure

Create the following directory structure to enforce layer separation:

```
src/
+-- Domain/                 # Innermost layer - no dependencies
|   +-- Entity/
|   |   +-- User.php
|   |   +-- Order.php
|   +-- ValueObject/
|   |   +-- Email.php
|   |   +-- Money.php
|   |   +-- OrderId.php
|   +-- Repository/
|   |   +-- UserRepositoryInterface.php
|   +-- Event/
|   |   +-- UserCreatedEvent.php
|   +-- Exception/
|       +-- DomainException.php
+-- Application/            # Use cases - depends on Domain
|   +-- Command/
|   |   +-- CreateUserCommand.php
|   |   +-- UpdateOrderCommand.php
|   +-- Handler/
|   |   +-- CreateUserHandler.php
|   |   +-- UpdateOrderHandler.php
|   +-- Query/
|   |   +-- GetUserQuery.php
|   +-- Dto/
|   |   +-- UserDto.php
|   +-- Service/
|       +-- NotificationServiceInterface.php
+-- Adapter/                # Interface adapters
|   +-- Http/
|   |   +-- Controller/
|   |   |   +-- UserController.php
|   |   +-- Request/
|   |       +-- CreateUserRequest.php
|   +-- Persistence/
|       +-- Doctrine/
|           +-- Repository/
|           |   +-- DoctrineUserRepository.php
|           +-- Mapping/
|               +-- User.orm.xml
+-- Infrastructure/         # Framework & external concerns
    +-- Config/
    |   +-- services.yaml
    +-- Event/
    |   +-- SymfonyEventDispatcher.php
    +-- Service/
        +-- SendgridEmailService.php
```

### 3. Implement Domain Layer

Start from the innermost layer (Domain) and work outward:

1. **Create Value Objects** with validation at construction time - they must be immutable using PHP 8.1+ `readonly`
2. **Create Entities** with domain logic and business rules - entities should encapsulate behavior, not just be data bags
3. **Define Repository Interfaces** (Ports) - keep them small and focused
4. **Define Domain Events** to decouple side effects from core business logic

### 4. Implement Application Layer

Build use cases that orchestrate domain objects:

1. **Create Commands** as readonly DTOs representing write operations
2. **Create Queries** for read operations (CQRS pattern)
3. **Implement Handlers** that receive commands/queries and coordinate domain objects
4. **Define Service Interfaces** for external dependencies (notifications, etc.)

### 5. Implement Adapter Layer

Create interface adapters that connect Application to Infrastructure:

1. **Create Controllers** that receive HTTP requests and invoke handlers
2. **Create Request DTOs** with Symfony validation attributes
3. **Implement Repository Adapters** that bridge domain interfaces to persistence layer

### 6. Configure Infrastructure

Set up framework-specific configuration:

1. **Configure Symfony DI** to bind interfaces to implementations
2. **Create test doubles** (In-Memory repositories) for unit testing without database
3. **Configure Doctrine mappings** for persistence

### 7. Test Without Framework

Ensure Domain and Application layers are testable without Symfony, Doctrine, or database. Use In-Memory repositories for fast unit tests.

## Examples

### Example: Create a User (Input / Output)

**Input** — an HTTP request validated into a command:

```php
// POST /api/users  {"email": "alice@example.com", "name": "Alice"}
$request = new CreateUserRequest();       // validated via #[Assert] attributes
$request->email = 'alice@example.com';
$request->name = 'Alice';
```

**Output** — handler returns the created user id:

```php
($createUserHandler)($command);
return new JsonResponse(['id' => $command->id], 201);
```

All full implementations (value objects, entities, repository ports/adapters, controllers,
DI wiring, in-memory test doubles) live in **[references/examples.md](references/examples.md)**:
- Value Objects (Email) and Entities with domain logic (User)
- Repository Port (interface) and Controller + Request DTO (HTTP adapter)
- Command/Handler (Application layer) and Doctrine repository + InMemory adapter
- Symfony DI configuration binding ports to adapters

## Best Practices

1. **Dependency Rule**: Dependencies only point inward - domain knows nothing of application or infrastructure
2. **Immutability**: Value Objects MUST be immutable using `readonly` in PHP 8.1+ - never allow mutable state
3. **Rich Domain Models**: Put business logic in entities with factory methods like `create()` - avoid anemic models
4. **Interface Segregation**: Keep repository interfaces small and focused - do not create god interfaces
5. **Framework Independence**: Domain and application layers MUST be testable without Symfony or Doctrine
6. **Validation at Construction**: Validate in Value Objects at construction time - never allow invalid state
7. **Symfony Attributes**: Use PHP 8 attributes for routing (`#[Route]`), validation (`#[Assert\]`), and DI
8. **Test Doubles**: Always provide In-Memory implementations for repositories to enable fast unit tests
9. **Domain Events**: Dispatch domain events to decouple side effects - do not call external services from entities
10. **XML/YAML Mappings**: Use XML or YAML for Doctrine mappings instead of annotations in domain entities

## Constraints and Warnings

### Architecture Constraints

- **Dependency Rule**: Dependencies only point inward. Domain knows nothing of Application, Application knows nothing of Infrastructure. Violating this breaks the architecture.
- **No Anemic Domain**: Entities should encapsulate behavior, not just be data bags. Avoid getters/setters without business logic.
- **Interface Segregation**: Keep repository interfaces small and focused. Do not create god interfaces.

### PHP Implementation Constraints

- **Immutability**: Value Objects MUST be immutable using `readonly` in PHP 8.1+. Never allow mutable state in Value Objects.
- **Validation**: Validate in Value Objects at construction time. Never allow invalid state to exist.
- **Symfony Attributes**: Use PHP 8 attributes for routing, validation, and DI (`#[Route]`, `#[Assert\Email]`, `#[Autowire]`).

### Testing Constraints

- **Framework Independence**: Domain and Application layers MUST be testable without Symfony, Doctrine, or database.
- **Test Doubles**: Always provide In-Memory implementations for repository interfaces to enable fast unit tests.

### Warnings

- **Avoid Rich Domain Models in Controllers**: Controllers should only coordinate, not contain business logic.
- **Beware of Leaky Abstractions**: Infrastructure concerns (like Doctrine annotations) should not leak into Domain entities. Use XML/YAML mappings instead.
- **Command Bus Consideration**: For complex applications, use Symfony Messenger for async processing. Do not inline complex orchestrations in handlers.
- **Domain Events**: Dispatch domain events to decouple side effects from core business logic. Do not call external services directly from entities.

## References

- [PHP Clean Architecture Patterns](references/php-clean-architecture.md)
- [Symfony Implementation Guide](references/symfony-implementation.md)
