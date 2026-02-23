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

```
src/
+-- Domain/                 # Innermost layer - no dependencies
|   +-- Entity/
|   +-- ValueObject/
|   +-- Repository/         # Interfaces (Ports)
|   +-- Event/
|   +-- Exception/
+-- Application/            # Use cases - depends on Domain
|   +-- Command/
|   +-- Handler/
|   +-- Query/
|   +-- Dto/
|   +-- Service/            # Service interfaces
+-- Adapter/                # Interface adapters
|   +-- Http/
|   |   +-- Controller/
|   |   +-- Request/
|   +-- Persistence/
|       +-- Doctrine/
|           +-- Repository/
|           +-- Mapping/
+-- Infrastructure/         # Framework & external concerns
    +-- Config/
    +-- Event/
    +-- Service/
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

1. **Configure Symfony DI** to bind interfaces to implementations
2. **Create test doubles** (In-Memory repositories) for unit testing without database
3. **Configure Doctrine mappings** for persistence

### 7. Test Without Framework

Ensure Domain and Application layers are testable without Symfony, Doctrine, or database. Use In-Memory repositories for fast unit tests.

## Examples

### Value Object with Validation

```php
<?php
// src/Domain/ValueObject/Email.php

namespace App\Domain\ValueObject;

use InvalidArgumentException;

final readonly class Email
{
    public function __construct(
        private string $value
    ) {
        if (!filter_var($value, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException(
                sprintf('"%s" is not a valid email address', $value)
            );
        }
    }

    public function value(): string
    {
        return $this->value;
    }

    public function equals(self $other): bool
    {
        return $this->value === $other->value;
    }
}
```

See [examples.md](references/examples.md) for complete examples of Entity, Repository Port, Command/Handler, Controller, Doctrine Adapter, DI Configuration, and In-Memory Repository for testing.

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

- **No Anemic Domain**: Entities should encapsulate behavior, not just be data bags
- **Avoid Rich Domain Models in Controllers**: Controllers should only coordinate, not contain business logic
- **Beware of Leaky Abstractions**: Infrastructure concerns (like Doctrine annotations) should not leak into Domain entities
- **Command Bus Consideration**: For complex applications, use Symfony Messenger for async processing

## References

- [Complete Code Examples](references/examples.md)
- [PHP Clean Architecture Patterns](references/php-clean-architecture.md)
- [Symfony Implementation Guide](references/symfony-implementation.md)
