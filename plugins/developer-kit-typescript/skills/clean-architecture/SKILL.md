---
name: clean-architecture
description: Provides implementation patterns for Clean Architecture, Domain-Driven Design (DDD), and Hexagonal Architecture (Ports & Adapters) in NestJS/TypeScript applications. Use when structuring complex backend systems, designing domain layers with entities/value objects/aggregates, implementing ports and adapters, creating use cases, or refactoring from anemic models to rich domain models with dependency inversion.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Clean Architecture, DDD & Hexagonal Architecture for NestJS

## Overview

Comprehensive guidance for implementing Clean Architecture, DDD, and Hexagonal Architecture in NestJS/TypeScript. Use this skill when you need clear layer boundaries, rich domain models, and swappable adapters.

## When to Use

- Architecting complex NestJS applications with long-term maintainability
- Refactoring from tightly-coupled MVC to layered architecture
- Implementing rich domain models with business logic encapsulation
- Designing testable systems with swappable infrastructure
- Creating microservices with clear bounded contexts
- Introducing domain events and explicit aggregate boundaries
- Enforcing dependency inversion with ports/adapters

Trigger phrases:
- "clean architecture", "hexagonal architecture", "ports and adapters"
- "domain entities/value objects/aggregates"
- "separate business logic from NestJS/ORM"
- "refactor anemic domain model"

## Instructions

1. **Define Layer Boundaries**: Domain (inner) -> Application -> Adapters -> Infrastructure (outer), and enforce inward-only dependencies.
2. **Design the Domain**: Model entities, value objects, and aggregates with invariants in constructors/methods.
3. **Create Domain Ports**: Put repository interfaces in `domain/repositories`; keep them technology-agnostic.
4. **Implement Use Cases**: Orchestrate business rules in application services with explicit input/output DTOs.
5. **Implement Adapters**: Build HTTP controllers and persistence adapters that translate data across boundaries.
6. **Configure NestJS DI**: Bind ports to adapters in modules using `Symbol` tokens.
7. **Map at the Edges**: Avoid leaking ORM entities into domain objects; keep mappers in adapters.
8. **Validate in Two Places**: DTO validation at boundaries; invariant validation inside domain model methods.
9. **Test by Layer**: Pure unit tests for domain/application; integration tests for adapters and infrastructure.
10. **Use References for Depth**: Load `references/` files when implementing concrete module/database patterns.

## Examples

### Project Structure

```
src/
+-- domain/           # Inner layer - no external deps
|   +-- entities/     # Domain entities with business logic
|   +-- value-objects/ # Immutable value objects
|   +-- aggregates/   # Aggregate roots
|   +-- events/       # Domain events
|   +-- repositories/ # Repository interfaces (ports)
+-- application/      # Use cases - orchestration
|   +-- use-cases/    # Individual use cases
|   +-- dto/          # Application DTOs
+-- adapters/         # Interface adapters
|   +-- http/         # Controllers, presenters
|   +-- persistence/  # Repository implementations
+-- infrastructure/   # External concerns
    +-- database/     # ORM config, migrations
    +-- messaging/    # Brokers, queues, event bus clients
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

### Repository Port

```typescript
export interface OrderRepositoryPort {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

export const ORDER_REPOSITORY = Symbol('ORDER_REPOSITORY');
```

### Use Case with Input/Output

```typescript
export interface CreateOrderInput {
  customerId: string;
  items: Array<{ productId: string; quantity: number; unitPrice: number; currency: string }>;
}

export interface CreateOrderOutput {
  orderId: string;
  total: number;
  currency: string;
}

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

```json
// Input
{
  "customerId": "cust-123",
  "items": [
    { "productId": "p-1", "quantity": 2, "unitPrice": 10, "currency": "EUR" }
  ]
}
```

```json
// Output
{
  "orderId": "ord-9fd2...",
  "total": 20,
  "currency": "EUR"
}
```

### Adapter + Module Wiring

```typescript
@Injectable()
export class TypeOrmOrderRepository implements OrderRepositoryPort {
  constructor(@InjectRepository(OrderEntity) private readonly repo: Repository<OrderEntity>) {}

  async findById(id: string): Promise<Order | null> {
    const row = await this.repo.findOne({ where: { id }, relations: ['items'] });
    return row ? toDomain(row) : null;
  }

  async save(order: Order): Promise<void> {
    await this.repo.save(toEntity(order));
  }
}

@Module({
  providers: [
    CreateOrderUseCase,
    { provide: ORDER_REPOSITORY, useClass: TypeOrmOrderRepository },
  ],
})
export class OrdersModule {}
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
