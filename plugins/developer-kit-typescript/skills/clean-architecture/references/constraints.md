# Clean Architecture Constraints and Warnings

This file contains constraints, limitations, and common pitfalls when implementing Clean Architecture, DDD, and Hexagonal Architecture in NestJS/TypeScript applications.

## Architecture Constraints

### Dependency Rule (CRITICAL)
**Never allow inner layers to depend on outer layers.**

This is the most important constraint in Clean Architecture. Violations destroy architecture benefits.

**Enforced Rules:**
- Domain layer MUST NOT import from NestJS, TypeORM, or any framework
- Application layer CAN import from domain, but NOT from infrastructure
- Adapters CAN import from application and domain, but NOT from each other
- Infrastructure CAN import from all outer layers

**Example Violation:**
```typescript
// ❌ VIOLATION: Domain importing TypeORM
// domain/entities/order.entity.ts
import { Entity, Column } from 'typeorm'; // FORBIDDEN!

export class Order {
  // Domain entities should be plain TypeScript classes
}
```

**Correct Approach:**
```typescript
// ✅ CORRECT: Pure domain entity
// domain/entities/order.entity.ts
export class Order {
  constructor(
    private readonly id: string,
    private readonly customerId: string,
  ) {}
}

// ✅ CORRECT: Infrastructure maps to ORM
// infrastructure/database/entities/order.entity.ts
import { Entity, Column } from 'typeorm';

@Entity('orders')
export class OrderEntity {
  @Column()
  id: string;

  @Column()
  customer_id: string;
}
```

### Domain Purity
**Domain layer must have zero dependencies on frameworks.**

**Forbidden in Domain:**
- ❌ NestJS decorators (`@Injectable`, `@Inject`, etc.)
- ❌ TypeORM decorators (`@Entity`, `@Column`, etc.)
- ❌ Class-validator decorators (`@IsString`, `@IsEmail`, etc.)
- ❌ HTTP-related code (Request, Response, headers)
- ❌ Database-specific types (Connection, Repository)
- ❌ Framework interfaces (`CanActivate`, `PipeTransform`, etc.)

**Allowed in Domain:**
- ✅ Plain TypeScript classes
- ✅ Plain TypeScript interfaces
- ✅ Standard library (Date, Map, Set, etc.)
- ✅ Business logic and rules
- ✅ Value objects and entities

### Interface Location
**Repository interfaces belong in the domain layer, implementations in adapters.**

**Structure:**
```
domain/
├── repositories/
│   └── order-repository.port.ts    # Interface (port)

adapters/
└── persistence/
    └── order-repository.ts         # Implementation (adapter)
```

**Incorrect:**
```typescript
// ❌ Interface in infrastructure (wrong)
// infrastructure/repositories/order-repository.interface.ts
export interface OrderRepository {
  save(order: OrderEntity): Promise<void>; // ORM entity!
}
```

**Correct:**
```typescript
// ✅ Interface in domain
// domain/repositories/order-repository.port.ts
export interface OrderRepositoryPort {
  save(order: Order): Promise<void>; // Domain aggregate!
}

// ✅ Implementation in adapters
// adapters/persistence/order-repository.adapter.ts
export class OrderRepository implements OrderRepositoryPort {
  async save(order: Order): Promise<void> {
    // Maps to ORM entity and persists
  }
}
```

### Immutability
**Value objects must be immutable - no setters allowed.**

Once created, value objects cannot change. Any modification creates a new instance.

**Required Pattern:**
```typescript
export class Email {
  private constructor(private readonly value: string) {}

  static create(email: string): Email {
    return new Email(email.toLowerCase().trim());
  }

  getValue(): string {
    return this.value;
  }

  // NO SETTERS!
}
```

**Forbidden Pattern:**
```typescript
export class Email {
  constructor(private value: string) {}

  setValue(value: string): void {
    this.value = value; // VIOLATES immutability!
  }
}
```

## Common Pitfalls to Avoid

### 1. Leaky Abstractions
**ORM entities leaking into domain layer.**

**Symptom:**
- Domain entities contain TypeORM decorators
- Value objects have database column annotations
- Business logic mixed with persistence logic

**Solution:**
- Create separate domain entities (pure TypeScript)
- Create ORM entities in infrastructure layer
- Map between layers in repository adapters

**Example:**
```typescript
// ❌ Leaky: ORM in domain
import { Entity, Column } from 'typeorm'; // Leaks into domain!

@Entity('orders')
export class Order {
  @Column()
  id: string;
}

// ✅ Separate: Pure domain + separate ORM
// domain/entities/order.entity.ts
export class Order {
  constructor(private readonly id: string) {}
}

// infrastructure/database/entities/order.entity.ts
import { Entity, Column } from 'typeorm';

@Entity('orders')
export class OrderEntity {
  @Column()
  id: string;
}
```

### 2. Anemic Domain
**Entities with only getters/setters, logic in services.**

**Symptom:**
- Entities are data containers only
- All business logic in "service" classes
- Domain becomes passive, services become god objects

**Example of Anemic Domain:**
```typescript
// ❌ Anemic: Entity is data bag
export class Order {
  constructor(
    public items: OrderItem[],
    public status: OrderStatus,
  ) {}
  // No behavior, just data
}

// Logic leaks into service
export class OrderService {
  confirm(order: Order): void {
    if (order.items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    order.status = OrderStatus.CONFIRMED;
  }
}
```

**Example of Rich Domain:**
```typescript
// ✅ Rich: Entity contains behavior
export class Order {
  private items: OrderItem[] = [];
  private status: OrderStatus = OrderStatus.PENDING;

  confirm(): void {
    if (this.items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this.status = OrderStatus.CONFIRMED;
  }
}
```

### 3. Wrong Layer
**Framework decorators in domain entities.**

**Symptom:**
- `@Injectable()` in domain entities
- `@Inject()` in domain services
- Framework-specific interfaces in domain

**Solution:**
- Domain layer must be framework-agnostic
- Use framework decorators only in adapters/application layer
- Domain uses plain TypeScript constructors

**Example:**
```typescript
// ❌ Wrong: NestJS in domain
import { Injectable } from '@nestjs/common';

@Injectable() // Framework in domain!
export class OrderDomainService {
  constructor(
    @Inject() private readonly repo: OrderRepository // DI in domain!
  ) {}
}

// ✅ Correct: Plain domain service
export class OrderDomainService {
  constructor(private readonly repo: OrderRepository) {}
  // Plain constructor, no decorators
}
```

### 4. Missing Ports
**Direct dependency on concrete implementations instead of interfaces.**

**Symptom:**
- Use cases depend on concrete repositories
- Cannot swap implementations without modifying use cases
- Tight coupling between layers

**Solution:**
- Define ports (interfaces) in domain or application layer
- Use cases depend on ports, not implementations
- Wire implementations via dependency injection

**Example:**
```typescript
// ❌ Tight coupling: Concrete dependency
export class CreateOrderUseCase {
  constructor(
    private readonly orderRepository: TypeOrmOrderRepository // Concrete!
  ) {}
}

// ✅ Loose coupling: Port dependency
export class CreateOrderUseCase {
  constructor(
    @Inject(ORDER_REPOSITORY)
    private readonly orderRepository: OrderRepositoryPort // Interface!
  ) {}
}
```

### 5. Over-Engineering
**Clean Architecture for simple CRUD operations is unnecessary overhead.**

**When to Use Clean Architecture:**
- Complex business logic
- Long-term maintenance required
- Multiple data sources (database, API, messaging)
- Team understands DDD concepts
- Domain complexity justifies overhead

**When NOT to Use:**
- Simple CRUD operations
- Prototype or MVP
- Short-lived projects
- Team lacks DDD experience
- Low business complexity

**Alternative for Simple Cases:**
- Traditional layered architecture
- MVC pattern
- Service-oriented architecture

## Implementation Warnings

### Mapping Overhead
**Repository adapters require mapping between domain and ORM entities.**

**Challenge:**
- Every entity needs toDomain() and toEntity() methods
- Mapping code can be verbose
- Performance overhead of mapping

**Mitigation:**
- Use mapping libraries (automapper-ts, class-transformer)
- Keep aggregates small to reduce mapping complexity
- Consider performance-critical paths (may violate purity)

**Example:**
```typescript
// Manual mapping (verbose but explicit)
private toDomain(entity: OrderEntity): Order {
  const order = new Order(entity.id, entity.customerId);
  entity.items.forEach(item => {
    order.addItem(new OrderItem(
      item.productId,
      item.quantity,
      Money.create(item.price, item.currency)
    ));
  });
  return order;
}
```

### Learning Curve
**Team must understand DDD concepts before implementation.**

**Required Knowledge:**
- Entities vs Value Objects
- Aggregates and Aggregate Roots
- Bounded Contexts
- Domain Events
- Ubiquitous Language
- Tactical DDD patterns

**Training Strategy:**
1. Start with training on DDD fundamentals
2. Practice with small bounded context
3. Gradually increase complexity
4. Pair program with experienced developers
5. Review architecture decisions regularly

### Boilerplate
**More files and interfaces compared to traditional layered architecture.**

**Example Structure:**
```
Traditional:                          Clean Architecture:
orders/                                orders/
├── order.entity.ts                    domain/
├── order.service.ts                   ├── entities/
├── order.controller.ts                │   └── order.entity.ts
└── order.module.ts                    ├── aggregates/
                                       │   └── order.aggregate.ts
                                       ├── value-objects/
                                       │   └── money.vo.ts
                                       ├── repositories/
                                       │   └── order-repository.port.ts
                                       application/
                                       ├── use-cases/
                                       │   └── create-order.use-case.ts
                                       └── dto/
                                           └── create-order.dto.ts
                                       adapters/
                                       ├── http/
                                       │   └── order.controller.ts
                                       └── persistence/
                                           └── order-repository.adapter.ts
```

**Mitigation:**
- Use code generators for repetitive patterns
- Scaffold new modules with templates
- Accept boilerplate as trade-off for maintainability
- Use NestJS CLI with custom templates

### Transaction Boundaries
**Transactions must be managed at the application layer, not domain.**

**Challenge:**
- Domain layer cannot manage database connections
- Multiple repositories must participate in single transaction
- Use cases must orchestrate transaction boundaries

**Solution:**
```typescript
@Injectable()
export class CreateOrderUseCase {
  async execute(input: CreateOrderInput): Promise<void> {
    await this.transactionManager.run(async () => {
      const order = this.createOrder(input);
      await this.orderRepository.save(order);
      await this.inventoryRepository.updateStock(input.items);
      await this.notificationRepository.sendConfirmation(order);
      // All operations in single transaction
    });
  }
}
```

**Warning:**
- Long-running transactions impact performance
- Consider eventual consistency for distributed operations
- Use Sagas for long-running business processes

## Performance Considerations

### Aggregate Size
- Keep aggregates small (5-10 entities max)
- Large aggregates = slow queries
- Consider splitting by consistency boundaries

### Database Queries
- N+1 query problem common in Clean Architecture
- Use eager loading in repository implementations
- Consider query performance when designing aggregates

### Caching
- Cache at application layer
- Domain layer remains cache-agnostic
- Use CQRS for read/write optimization

## Migration Strategy

### Incremental Adoption
1. Start with new bounded contexts
2. Refactor existing code incrementally
3. Create anti-corruption layer for legacy systems
4. Gradually increase domain complexity

### Team Readiness
1. Assess team's DDD understanding
2. Provide training before implementation
3. Start with pilot project
4. Gather feedback and adjust approach
