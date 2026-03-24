# Clean Architecture Examples

This file contains comprehensive code examples demonstrating Clean Architecture, DDD, and Hexagonal Architecture patterns in NestJS/TypeScript applications.

## Example 1: Value Objects

Value objects are immutable and validated at construction:

```typescript
// domain/value-objects/email.vo.ts
export class Email {
  private constructor(private readonly value: string) {}

  static create(email: string): Email {
    if (!this.isValid(email)) {
      throw new Error('Invalid email format');
    }
    return new Email(email.toLowerCase().trim());
  }

  private static isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  getValue(): string {
    return this.value;
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }
}

// domain/value-objects/money.vo.ts
export class Money {
  private constructor(
    private readonly amount: number,
    private readonly currency: string,
  ) {}

  static create(amount: number, currency: string): Money {
    if (amount < 0) throw new Error('Amount cannot be negative');
    return new Money(amount, currency);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Cannot add different currencies');
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  getAmount(): number { return this.amount; }
  getCurrency(): string { return this.currency; }
}
```

## Example 2: Entity with Business Logic

Entities contain identity and encapsulate business rules:

```typescript
// domain/entities/order-item.entity.ts
import { Money } from '../value-objects/money.vo';

export class OrderItem {
  constructor(
    private readonly productId: string,
    private readonly quantity: number,
    private readonly unitPrice: Money,
  ) {
    if (quantity <= 0) throw new Error('Quantity must be positive');
  }

  getSubtotal(): Money {
    return Money.create(
      this.unitPrice.getAmount() * this.quantity,
      this.unitPrice.getCurrency(),
    );
  }
}
```

## Example 3: Aggregate Root with Domain Events

Aggregate roots protect invariants and emit domain events:

```typescript
// domain/aggregates/order.aggregate.ts
import { AggregateRoot } from '@nestjs/cqrs';
import { OrderItem } from '../entities/order-item.entity';
import { Money } from '../value-objects/money.vo';
import { OrderCreatedEvent } from '../events/order-created.event';

export enum OrderStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  SHIPPED = 'SHIPPED',
  CANCELLED = 'CANCELLED',
}

export class Order extends AggregateRoot {
  private items: OrderItem[] = [];
  private status: OrderStatus = OrderStatus.PENDING;

  constructor(
    private readonly id: string,
    private readonly customerId: string,
  ) {
    super();
  }

  addItem(item: OrderItem): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Cannot modify confirmed order');
    }
    this.items.push(item);
  }

  getTotal(): Money {
    return this.items.reduce(
      (sum, item) => sum.add(item.getSubtotal()),
      Money.create(0, 'USD'),
    );
  }

  confirm(): void {
    if (this.items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this.status = OrderStatus.CONFIRMED;
    this.apply(new OrderCreatedEvent(this.id, this.customerId));
  }

  getStatus(): OrderStatus {
    return this.status;
  }
}
```

## Example 4: Repository Port (Interface)

Define repository contracts in the domain layer:

```typescript
// domain/repositories/order-repository.port.ts
import { Order } from '../aggregates/order.aggregate';

export interface OrderRepositoryPort {
  findById(id: string): Promise<Order | null>;
  findByCustomerId(customerId: string): Promise<Order[]>;
  save(order: Order): Promise<void>;
  delete(id: string): Promise<void>;
}

// Token for dependency injection
export const ORDER_REPOSITORY = Symbol('ORDER_REPOSITORY');
```

## Example 5: Use Case (Application Layer)

Use cases orchestrate business logic and infrastructure:

```typescript
// application/use-cases/create-order.use-case.ts
import { Injectable, Inject } from '@nestjs/common';
import { Order } from '../../domain/aggregates/order.aggregate';
import { OrderItem } from '../../domain/entities/order-item.entity';
import { Money } from '../../domain/value-objects/money.vo';
import { OrderRepositoryPort, ORDER_REPOSITORY } from '../../domain/repositories/order-repository.port';

export interface CreateOrderInput {
  customerId: string;
  items: Array<{
    productId: string;
    quantity: number;
    unitPrice: number;
    currency: string;
  }>;
}

export interface CreateOrderOutput {
  orderId: string;
  total: number;
  currency: string;
}

@Injectable()
export class CreateOrderUseCase {
  constructor(
    @Inject(ORDER_REPOSITORY)
    private readonly orderRepository: OrderRepositoryPort,
  ) {}

  async execute(input: CreateOrderInput): Promise<CreateOrderOutput> {
    const orderId = crypto.randomUUID();
    const order = new Order(orderId, input.customerId);

    for (const item of input.items) {
      const money = Money.create(item.unitPrice, item.currency);
      order.addItem(new OrderItem(item.productId, item.quantity, money));
    }

    order.confirm();
    await this.orderRepository.save(order);

    const total = order.getTotal();
    return {
      orderId,
      total: total.getAmount(),
      currency: total.getCurrency(),
    };
  }
}
```

## Example 6: Repository Adapter (Infrastructure)

Implement repository interfaces in the infrastructure layer:

```typescript
// adapters/persistence/order.repository.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { OrderRepositoryPort } from '../../domain/repositories/order-repository.port';
import { Order } from '../../domain/aggregates/order.aggregate';
import { OrderEntity } from '../../infrastructure/database/entities/order.entity';

@Injectable()
export class OrderRepository implements OrderRepositoryPort {
  constructor(
    @InjectRepository(OrderEntity)
    private readonly repository: Repository<OrderEntity>,
  ) {}

  async findById(id: string): Promise<Order | null> {
    const entity = await this.repository.findOne({
      where: { id },
      relations: ['items'],
    });
    return entity ? this.toDomain(entity) : null;
  }

  async findByCustomerId(customerId: string): Promise<Order[]> {
    const entities = await this.repository.find({
      where: { customerId },
      relations: ['items'],
    });
    return entities.map(e => this.toDomain(e));
  }

  async save(order: Order): Promise<void> {
    const entity = this.toEntity(order);
    await this.repository.save(entity);
  }

  async delete(id: string): Promise<void> {
    await this.repository.delete(id);
  }

  private toDomain(entity: OrderEntity): Order {
    // Map ORM entity to domain aggregate
    const order = new Order(entity.id, entity.customerId);
    // ... populate items, status
    return order;
  }

  private toEntity(order: Order): OrderEntity {
    // Map domain aggregate to ORM entity
    const entity = new OrderEntity();
    // ... mapping logic
    return entity;
  }
}
```

## Example 7: Controller Adapter

Controllers adapt HTTP requests to use case inputs:

```typescript
// adapters/http/order.controller.ts
import { Controller, Post, Body, Get, Param } from '@nestjs/common';
import { CreateOrderUseCase, CreateOrderInput } from '../../application/use-cases/create-order.use-case';
import { IsString, IsArray, ValidateNested, IsNumber } from 'class-validator';
import { Type } from 'class-transformer';

class OrderItemDto {
  @IsString()
  productId: string;

  @IsNumber()
  quantity: number;

  @IsNumber()
  unitPrice: number;

  @IsString()
  currency: string;
}

class CreateOrderDto implements CreateOrderInput {
  @IsString()
  customerId: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];
}

@Controller('orders')
export class OrderController {
  constructor(private readonly createOrderUseCase: CreateOrderUseCase) {}

  @Post()
  async create(@Body() dto: CreateOrderDto) {
    return this.createOrderUseCase.execute(dto);
  }
}
```

## Example 8: Module Configuration

Wire dependencies together in NestJS modules:

```typescript
// orders.module.ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { OrderController } from './adapters/http/order.controller';
import { CreateOrderUseCase } from './application/use-cases/create-order.use-case';
import { OrderRepository } from './adapters/persistence/order.repository';
import { ORDER_REPOSITORY } from './domain/repositories/order-repository.port';
import { OrderEntity } from './infrastructure/database/entities/order.entity';

@Module({
  imports: [TypeOrmModule.forFeature([OrderEntity])],
  controllers: [OrderController],
  providers: [
    CreateOrderUseCase,
    {
      provide: ORDER_REPOSITORY,
      useClass: OrderRepository,
    },
  ],
})
export class OrdersModule {}
```
