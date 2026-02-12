# TypeScript Clean Architecture Patterns

## Type System for Domain Modeling

### Branded Types for Type Safety

```typescript
// domain/types/branded.ts
declare const __brand: unique symbol;

type Brand<B> = { [__brand]: B };
export type Branded<T, B> = T & Brand<B>;

// Usage
export type UserId = Branded<string, 'UserId'>;
export type OrderId = Branded<string, 'OrderId'>;
export type Email = Branded<string, 'Email'>;

// Factory functions enforce creation
export function createUserId(id: string): UserId {
  if (!id || id.length !== 36) {
    throw new Error('Invalid UserId format');
  }
  return id as UserId;
}

// Prevents mixing IDs
function findById(id: UserId) { }
findById(createUserId('valid-uuid')); // OK
findById('random-string'); // Type error
```

### Result Type for Error Handling

```typescript
// domain/types/result.ts
export type Result<T, E = Error> =
  | { success: true; value: T }
  | { success: false; error: E };

export const Result = {
  ok<T>(value: T): Result<T, never> {
    return { success: true, value };
  },

  fail<E>(error: E): Result<never, E> {
    return { success: false, error };
  },

  // Helper for async operations
  async fromPromise<T>(promise: Promise<T>): Promise<Result<T, Error>> {
    try {
      const value = await promise;
      return Result.ok(value);
    } catch (error) {
      return Result.fail(error instanceof Error ? error : new Error(String(error)));
    }
  },
};

// Usage in domain
export class Order {
  confirm(): Result<void, 'EMPTY_ORDER' | 'ALREADY_CONFIRMED'> {
    if (this.items.length === 0) {
      return Result.fail('EMPTY_ORDER');
    }
    if (this.status !== OrderStatus.PENDING) {
      return Result.fail('ALREADY_CONFIRMED');
    }
    this.status = OrderStatus.CONFIRMED;
    return Result.ok(undefined);
  }
}
```

## Value Object Patterns

### Deep Immutable Objects

```typescript
// domain/value-objects/address.vo.ts
interface AddressProps {
  street: string;
  city: string;
  postalCode: string;
  country: string;
}

export class Address {
  readonly #props: Readonly<AddressProps>;

  private constructor(props: AddressProps) {
    this.#props = Object.freeze({ ...props });
  }

  static create(props: AddressProps): Address {
    Address.validate(props);
    return new Address(props);
  }

  private static validate(props: AddressProps): void {
    if (!props.street?.trim()) throw new Error('Street required');
    if (!props.city?.trim()) throw new Error('City required');
    if (!/^[\d-]+$/.test(props.postalCode)) throw new Error('Invalid postal code');
  }

  // Computed properties
  get formatted(): string {
    return `${this.#props.street}, ${this.#props.city} ${this.#props.postalCode}`;
  }

  // Copy-on-write updates
  withCity(city: string): Address {
    return new Address({ ...this.#props, city });
  }

  equals(other: Address): boolean {
    return JSON.stringify(this.#props) === JSON.stringify(other.#props);
  }

  toJSON(): AddressProps {
    return { ...this.#props };
  }
}
```

## Entity Patterns

### Entity Base Class

```typescript
// domain/entities/entity.base.ts
import { randomUUID } from 'crypto';

export abstract class Entity<TId> {
  readonly id: TId;

  constructor(id?: TId) {
    this.id = id ?? (randomUUID() as TId);
  }

  equals(other: Entity<TId>): boolean {
    if (!(other instanceof this.constructor)) return false;
    return this.id === other.id;
  }
}

// Domain events support
export interface DomainEvent {
  readonly occurredAt: Date;
  readonly aggregateId: string;
}

export abstract class AggregateRoot<TId> extends Entity<TId> {
  #domainEvents: DomainEvent[] = [];

  protected addEvent(event: DomainEvent): void {
    this.#domainEvents.push(event);
  }

  getDomainEvents(): readonly DomainEvent[] {
    return Object.freeze([...this.#domainEvents]);
  }

  clearEvents(): void {
    this.#domainEvents = [];
  }
}
```

## Repository Pattern

### Generic Repository Interface

```typescript
// domain/repositories/repository.port.ts
export interface RepositoryPort<TEntity, TId> {
  findById(id: TId): Promise<TEntity | null>;
  findAll(): Promise<TEntity[]>;
  save(entity: TEntity): Promise<void>;
  delete(id: TId): Promise<void>;
  exists(id: TId): Promise<boolean>;
}

// Specification pattern for queries
export interface Specification<T> {
  isSatisfiedBy(entity: T): boolean;
  toQuery(): Record<string, unknown>;
}

export interface QueryableRepositoryPort<TEntity, TId> extends RepositoryPort<TEntity, TId> {
  findBySpecification(spec: Specification<TEntity>): Promise<TEntity[]>;
  findOneBySpecification(spec: Specification<TEntity>): Promise<TEntity | null>;
  count(spec?: Specification<TEntity>): Promise<number>;
}
```

## Unit of Work Pattern

```typescript
// domain/unit-of-work.port.ts
export interface UnitOfWork {
  commit(): Promise<void>;
  rollback(): Promise<void>;
}

// Usage in use case
export class CreateOrderUseCase {
  async execute(input: CreateOrderInput): Promise<void> {
    const uow = this.unitOfWorkFactory.create();

    try {
      const order = Order.create(input);
      await this.orderRepository.save(order, uow);
      await uow.commit();
    } catch (error) {
      await uow.rollback();
      throw error;
    }
  }
}
```

## Type Guards for Domain Validation

```typescript
// domain/guards/domain.guards.ts
export function assertDefined<T>(value: T | null | undefined, message: string): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error(message);
  }
}

export function assertPositive(value: number, field: string): asserts value is number {
  if (value <= 0 || !Number.isFinite(value)) {
    throw new Error(`${field} must be a positive number`);
  }
}

export function assertEmail(value: string): asserts value is string {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    throw new Error('Invalid email format');
  }
}

// Usage
function processOrder(amount: number, email: string) {
  assertPositive(amount, 'Order amount');
  assertEmail(email);
  // Now TypeScript knows amount > 0 and email is valid
}
```

## Mapper Pattern

```typescript
// application/mappers/mapper.interface.ts
export interface Mapper<TDomain, TDal> {
  toDomain(dal: TDal): TDomain;
  toDal(domain: TDomain): TDal;
}

// Implementation
export class OrderMapper implements Mapper<Order, OrderEntity> {
  toDomain(entity: OrderEntity): Order {
    const order = new Order(entity.id, entity.customerId);
    entity.items?.forEach(item => {
      order.addItem(new OrderItem(
        item.productId,
        item.quantity,
        Money.create(item.unitPrice, item.currency)
      ));
    });
    return order;
  }

  toDal(order: Order): OrderEntity {
    const entity = new OrderEntity();
    entity.id = order.id;
    entity.customerId = order.customerId;
    entity.status = order.getStatus();
    // ... map items
    return entity;
  }
}
```
