---
name: clean-architecture
description: Provides implementation patterns for Clean Architecture, Domain-Driven Design (DDD), and Hexagonal Architecture (Ports & Adapters) in NestJS/TypeScript applications. Use when structuring complex backend systems, designing domain layers with entities/value objects/aggregates, implementing ports and adapters, creating use cases, or refactoring from anemic models to rich domain models with dependency inversion.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
category: backend
tags: [clean-architecture, hexagonal-architecture, ddd, domain-driven-design, nestjs, typescript, ports-adapters]
version: 2.2.0
---

# Clean Architecture, DDD & Hexagonal Architecture for NestJS

## Overview

Comprehensive guidance for implementing Clean Architecture, DDD, and Hexagonal Architecture in NestJS/TypeScript. Covers architectural layers, tactical patterns, and practical implementation.

## When to Use

- Architecting complex NestJS applications with long-term maintainability
- Refactoring from tightly-coupled MVC to layered architecture
- Implementing rich domain models with business logic encapsulation
- Designing testable systems with swappable infrastructure
- Creating microservices with clear bounded contexts

## Instructions

1. **Understand Layers**: Domain (inner) -> Application (use cases) -> Adapters -> Infrastructure (outer)
2. **Implement Domain Layer**: Create pure entities, value objects, aggregates with no external deps
3. **Define Ports**: Repository interfaces in domain layer
4. **Create Use Cases**: Application layer orchestrates business logic
5. **Implement Adapters**: Controllers (HTTP) and repositories (persistence)
6. **Configure DI**: Wire dependencies in NestJS modules with Symbol tokens
7. **Follow Dependency Rule**: Dependencies only point inward

## Examples

### Project Structure

```
src/
+-- domain/           # Inner layer - no external deps
|   +-- entities/     # Domain entities with business logic
|   +-- value-objects/ # Immutable value objects
|   +-- aggregates/   # Aggregate roots
|   +-- repositories/ # Repository interfaces (ports)
+-- application/      # Use cases - orchestration
|   +-- use-cases/    # Individual use cases
|   +-- dto/          # Application DTOs
+-- adapters/         # Interface adapters
|   +-- http/         # Controllers, presenters
|   +-- persistence/  # Repository implementations
+-- infrastructure/   # External concerns
    +-- database/     # ORM config, migrations
```

### Value Object

```typescript
export class Email {
  private constructor(private readonly value: string) {}
  static create(email: string): Email {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error('Invalid email');
    return new Email(email.toLowerCase().trim());
  }
  getValue(): string { return this.value; }
  equals(other: Email): boolean { return this.value === other.value; }
}
```

### Use Case

```typescript
@Injectable()
export class CreateOrderUseCase {
  constructor(@Inject(ORDER_REPOSITORY) private readonly orderRepo: OrderRepositoryPort) {}

  async execute(input: CreateOrderInput): Promise<CreateOrderOutput> {
    const order = new Order(crypto.randomUUID(), input.customerId);
    for (const item of input.items) {
      order.addItem(new OrderItem(item.productId, item.quantity, Money.create(item.unitPrice, item.currency)));
    }
    order.confirm();
    await this.orderRepo.save(order);
    const total = order.getTotal();
    return { orderId: order.getId(), total: total.getAmount(), currency: total.getCurrency() };
  }
}
```

## Constraints and Warnings

- **Dependency Rule**: Never allow inner layers to depend on outer layers
- **Domain Purity**: Domain layer must have zero framework dependencies
- **Immutability**: Value objects must be immutable - no setters
- **Over-Engineering**: Clean Architecture for simple CRUD is unnecessary overhead
- **Mapping Overhead**: Repository adapters require mapping between domain and ORM entities

## Best Practices

1. Dependencies only point inward - domain knows nothing about NestJS or TypeORM
2. Put business logic in entities, not services (avoid anemic domain models)
3. Value objects use private constructors with static factory methods
4. One repository per aggregate
5. Domain layer tests are pure unit tests - no NestJS testing module needed
6. Keep transactions in the application layer
7. Use Symbol() for DI tokens

## References

Consult these files for detailed patterns:

- **[references/nestjs-implementation.md](references/nestjs-implementation.md)** - NestJS integration, module configuration, controller adapters, repository implementations
- **[references/typescript-clean-architecture.md](references/typescript-clean-architecture.md)** - TypeScript-specific patterns, entities, aggregates, domain events
