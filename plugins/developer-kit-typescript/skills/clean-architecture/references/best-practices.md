# Clean Architecture Best Practices

This file contains comprehensive best practices for implementing Clean Architecture, DDD, and Hexagonal Architecture in NestJS/TypeScript applications.

## Core Principles

### 1. Dependency Rule
**Dependencies only point inward** - domain knows nothing about NestJS, TypeORM, or HTTP.

- Inner layers must not import from outer layers
- Use dependency inversion to define interfaces in inner layers
- Outer layers implement interfaces defined by inner layers
- This enables framework swapping without affecting business logic

**Example:**
```typescript
// ✅ Correct: Domain defines interface
// domain/repositories/order.repository.ts
export interface OrderRepositoryPort {
  save(order: Order): Promise<void>;
}

// adapters/persistence/order.repository.ts
export class OrderRepository implements OrderRepositoryPort {
  // Implementation with TypeORM
}

// ❌ Wrong: Domain imports from infrastructure
// domain/entities/order.entity.ts
import { Repository } from 'typeorm'; // Violates dependency rule!
```

### 2. Rich Domain Models
**Put business logic in entities, not services** - avoid anemic domain models.

Anemic domain models have entities with only getters/setters, with all logic in services. This violates object-oriented design principles.

**Example:**
```typescript
// ❌ Anemic: Logic in service
class Order {
  getTotal(): number { return this.total; }
  setTotal(total: number) { this.total = total; }
}

class OrderService {
  calculateTotal(order: Order): void {
    const total = order.items.reduce((sum, item) => sum + item.price, 0);
    order.setTotal(total); // Logic outside entity
  }
}

// ✅ Rich: Logic in entity
class Order {
  getTotal(): number {
    return this.items.reduce((sum, item) => sum + item.getSubtotal(), 0);
  }

  addItem(item: OrderItem): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Cannot modify confirmed order');
    }
    this.items.push(item);
  }
}
```

### 3. Immutability
**Value objects must be immutable** - use private constructors with static factory methods.

Immutable objects prevent unintended state changes and make code more predictable.

**Example:**
```typescript
// ✅ Immutable value object
export class Email {
  private constructor(private readonly value: string) {}

  static create(email: string): Email {
    if (!this.isValid(email)) {
      throw new Error('Invalid email format');
    }
    return new Email(email.toLowerCase().trim());
  }

  getValue(): string {
    return this.value;
  }

  // No setters!
}

// ❌ Mutable value object (anti-pattern)
export class Email {
  constructor(public value: string) {}

  setValue(value: string): void { // Setter allows mutation
    this.value = value;
  }
}
```

### 4. Interface Segregation
**Keep repository interfaces small and focused** - one repository per aggregate.

Large repository interfaces violate Interface Segregation Principle (ISP) and make testing harder.

**Example:**
```typescript
// ✅ Focused: One repository per aggregate
export interface OrderRepositoryPort {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

export interface CustomerRepositoryPort {
  findById(id: string): Promise<Customer | null>;
  save(customer: Customer): Promise<void>;
}

// ❌ Bloated: God repository
export interface RepositoryPort {
  findById(entity: string, id: string): Promise<any>;
  save(entity: any): Promise<void>;
  // Handles all entities - violates ISP
}
```

### 5. Constructor Injection
**Use NestJS DI in outer layers only** - domain entities use plain constructors.

Domain layer should have no knowledge of NestJS decorators or DI system.

**Example:**
```typescript
// ✅ Domain: Plain constructor
export class Order {
  constructor(
    private readonly id: string,
    private readonly customerId: string,
  ) {}
}

// ✅ Application: NestJS DI
@Injectable()
export class CreateOrderUseCase {
  constructor(
    @Inject(ORDER_REPOSITORY)
    private readonly orderRepository: OrderRepositoryPort,
  ) {}
}

// ❌ Wrong: NestJS in domain
export class Order {
  constructor(
    @Inject() private readonly id: string, // NestJS in domain!
  ) {}
}
```

### 6. Validation at Boundaries
**Validate DTOs at API boundary and enforce invariants in domain entities.**

Two-layer validation approach:
1. **Boundary**: Input validation with class-validator
2. **Domain**: Business rule enforcement in entities

**Example:**
```typescript
// ✅ Boundary validation (DTO)
class CreateOrderDto {
  @IsString()
  @MinLength(1)
  customerId: string;

  @IsArray()
  @ValidateNested({ each: true })
  items: OrderItemDto[];
}

// ✅ Domain invariants (Entity)
class Order {
  confirm(): void {
    if (this.items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this.status = OrderStatus.CONFIRMED;
  }
}
```

### 7. Pure Domain Tests
**Domain layer tests require no NestJS testing module** - fast pure unit tests.

Domain tests should be pure TypeScript unit tests without NestJS infrastructure.

**Example:**
```typescript
// ✅ Pure domain test
describe('Order', () => {
  it('should calculate total correctly', () => {
    const order = new Order('1', 'customer-1');
    order.addItem(new OrderItem('product-1', 2, Money.create(10, 'USD')));

    expect(order.getTotal().getAmount()).toBe(20);
  });
});

// ❌ Unnecessary: NestJS test module for domain
describe('Order', () => {
  it('should calculate total', async () => {
    const module = await Test.createTestingModule({
      providers: [Order],
    }).compile(); // Not needed for domain tests!
  });
});
```

### 8. Transactions in Application
**Keep transaction management in application layer, not domain.**

Domain layer should not manage database transactions or connections.

**Example:**
```typescript
// ✅ Application: Transaction management
@Injectable()
export class CreateOrderUseCase {
  async execute(input: CreateOrderInput): Promise<void> {
    await this.transactionManager.run(async () => {
      const order = this.createOrder(input);
      await this.orderRepository.save(order);
      await this.inventoryRepository.updateItems(input.items);
      // Transaction spans multiple repositories
    });
  }
}

// ❌ Wrong: Transaction in domain
class Order {
  async save(): Promise<void> {
    await this.transaction.run(async () => {
      // Domain shouldn't manage transactions
    });
  }
}
```

### 9. Symbol Tokens
**Use Symbol() for DI tokens to avoid string coupling in NestJS modules.**

Symbol tokens provide unique, type-safe dependency injection tokens.

**Example:**
```typescript
// ✅ Symbol tokens
export const ORDER_REPOSITORY = Symbol('ORDER_REPOSITORY');

@Module({
  providers: [
    {
      provide: ORDER_REPOSITORY,
      useClass: OrderRepository,
    },
  ],
})

// ❌ String tokens (fragile)
@Module({
  providers: [
    {
      provide: 'OrderRepository', // String coupling
      useClass: OrderRepository,
    },
  ],
})
```

### 10. Aggregate Roots
**Protect invariants through aggregate roots** - access entities only through aggregates.

External code should not directly modify entities within an aggregate.

**Example:**
```typescript
// ✅ Through aggregate root
const order = new Order('1', 'customer-1');
order.addItem(new OrderItem('product-1', 2, Money.create(10, 'USD')));
order.confirm(); // Aggregate protects invariants

// ❌ Direct entity manipulation (violates consistency)
const order = await orderRepository.findById('1');
order.items.push(new OrderItem('product-1', 2, Money.create(10, 'USD')));
// Bypasses aggregate business rules!
```

## Testing Strategies

### Unit Testing Domain Layer
- No NestJS TestModule required
- Test business rules in isolation
- Mock repository interfaces
- Fast execution (milliseconds)

### Integration Testing Application Layer
- Use NestJS TestModule
- Mock infrastructure adapters
- Test use case orchestration
- Verify repository interactions

### E2E Testing Adapters
- Test controllers with real HTTP
- Integration with real database (test container)
- Verify complete request flow
- Slower but comprehensive

## Performance Considerations

### Aggregate Design
- Keep aggregates small for performance
- Large aggregates = slow queries
- Consider eventual consistency for bounded contexts

### Caching Strategy
- Cache at application layer
- Domain layer remains cache-agnostic
- Use CQRS for read/write optimization

### Lazy Loading
- Avoid lazy loading in domain
- Explicitly load required data in use cases
- Prevent N+1 query problems
