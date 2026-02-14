# NestJS Clean Architecture Implementation

## Module Structure

### Feature Module Template

```typescript
// orders/orders.module.ts
import { Module } from '@nestjs/common';
import { CqrsModule } from '@nestjs/cqrs';
import { TypeOrmModule } from '@nestjs/typeorm';

// Controllers (Adapters)
import { OrderController } from './adapters/http/order.controller';
import { OrderEventHandler } from './adapters/event-handlers/order-event.handler';

// Use Cases (Application)
import { CreateOrderHandler } from './application/commands/create-order.handler';
import { GetOrderHandler } from './application/queries/get-order.handler';

// Repositories (Adapters)
import { OrderRepository } from './adapters/persistence/order.repository';
import { OrderEntity } from './infrastructure/database/entities/order.entity';

// Domain Ports
import { ORDER_REPOSITORY } from './domain/repositories/order-repository.port';

const CommandHandlers = [CreateOrderHandler];
const QueryHandlers = [GetOrderHandler];
const EventHandlers = [OrderEventHandler];

@Module({
  imports: [
    CqrsModule,
    TypeOrmModule.forFeature([OrderEntity]),
  ],
  controllers: [OrderController],
  providers: [
    ...CommandHandlers,
    ...QueryHandlers,
    ...EventHandlers,
    {
      provide: ORDER_REPOSITORY,
      useClass: OrderRepository,
    },
  ],
  exports: [ORDER_REPOSITORY],
})
export class OrdersModule {}
```

## CQRS Integration

### Command Handler

```typescript
// application/commands/create-order.command.ts
export class CreateOrderCommand {
  constructor(
    public readonly customerId: string,
    public readonly items: Array<{
      productId: string;
      quantity: number;
      unitPrice: number;
      currency: string;
    }>,
  ) {}
}

// application/commands/create-order.handler.ts
import { CommandHandler, ICommandHandler, EventBus } from '@nestjs/cqrs';
import { Inject } from '@nestjs/common';
import { CreateOrderCommand } from './create-order.command';
import { Order } from '../../domain/aggregates/order.aggregate';
import { OrderItem } from '../../domain/entities/order-item.entity';
import { Money } from '../../domain/value-objects/money.vo';
import { ORDER_REPOSITORY, OrderRepositoryPort } from '../../domain/repositories/order-repository.port';

@CommandHandler(CreateOrderCommand)
export class CreateOrderHandler implements ICommandHandler<CreateOrderCommand> {
  constructor(
    @Inject(ORDER_REPOSITORY)
    private readonly orderRepository: OrderRepositoryPort,
    private readonly eventBus: EventBus,
  ) {}

  async execute(command: CreateOrderCommand): Promise<{ orderId: string }> {
    const orderId = crypto.randomUUID();
    const order = new Order(orderId, command.customerId);

    for (const item of command.items) {
      const money = Money.create(item.unitPrice, item.currency);
      order.addItem(new OrderItem(item.productId, item.quantity, money));
    }

    order.confirm();
    await this.orderRepository.save(order);

    // Publish domain events
    const events = order.getDomainEvents();
    for (const event of events) {
      this.eventBus.publish(event);
    }
    order.clearEvents();

    return { orderId };
  }
}
```

### Query Handler

```typescript
// application/queries/get-order.query.ts
export class GetOrderQuery {
  constructor(public readonly orderId: string) {}
}

export interface OrderDto {
  id: string;
  customerId: string;
  status: string;
  total: number;
  currency: string;
  items: Array<{
    productId: string;
    quantity: number;
    subtotal: number;
  }>;
}

// application/queries/get-order.handler.ts
import { IQueryHandler, QueryHandler } from '@nestjs/cqrs';
import { Inject } from '@nestjs/common';
import { GetOrderQuery, OrderDto } from './get-order.query';
import { ORDER_REPOSITORY, OrderRepositoryPort } from '../../domain/repositories/order-repository.port';

@QueryHandler(GetOrderQuery)
export class GetOrderHandler implements IQueryHandler<GetOrderQuery, OrderDto | null> {
  constructor(
    @Inject(ORDER_REPOSITORY)
    private readonly orderRepository: OrderRepositoryPort,
  ) {}

  async execute(query: GetOrderQuery): Promise<OrderDto | null> {
    const order = await this.orderRepository.findById(query.orderId);
    if (!order) return null;

    const total = order.getTotal();

    return {
      id: order.id,
      customerId: order.customerId,
      status: order.getStatus(),
      total: total.getAmount(),
      currency: total.getCurrency(),
      items: order.getItems().map(item => ({
        productId: item.productId,
        quantity: item.quantity,
        subtotal: item.getSubtotal().getAmount(),
      })),
    };
  }
}
```

## Repository Implementation with TypeORM

```typescript
// infrastructure/database/entities/order.entity.ts
import { Entity, PrimaryColumn, Column, OneToMany } from 'typeorm';
import { OrderItemEntity } from './order-item.entity';

@Entity('orders')
export class OrderEntity {
  @PrimaryColumn('uuid')
  id: string;

  @Column('uuid')
  customerId: string;

  @Column({
    type: 'enum',
    enum: ['PENDING', 'CONFIRMED', 'SHIPPED', 'CANCELLED'],
  })
  status: string;

  @OneToMany(() => OrderItemEntity, item => item.order, { cascade: true })
  items: OrderItemEntity[];

  @Column('timestamp')
  createdAt: Date;

  @Column('timestamp', { nullable: true })
  updatedAt: Date;
}

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
    return entity ? this.mapToDomain(entity) : null;
  }

  async findByCustomerId(customerId: string): Promise<Order[]> {
    const entities = await this.repository.find({
      where: { customerId },
      relations: ['items'],
    });
    return entities.map(e => this.mapToDomain(e));
  }

  async save(order: Order): Promise<void> {
    const entity = this.mapToEntity(order);
    await this.repository.save(entity);
  }

  async delete(id: string): Promise<void> {
    await this.repository.delete(id);
  }

  private mapToDomain(entity: OrderEntity): Order {
    const order = new Order(entity.id, entity.customerId);
    // Restore items and status
    return order;
  }

  private mapToEntity(order: Order): OrderEntity {
    const entity = new OrderEntity();
    entity.id = order.id;
    entity.customerId = order.customerId;
    entity.status = order.getStatus();
    return entity;
  }
}
```

## Repository with Prisma

```typescript
// adapters/persistence/prisma-order.repository.ts
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../infrastructure/database/prisma.service';
import { OrderRepositoryPort } from '../../domain/repositories/order-repository.port';
import { Order } from '../../domain/aggregates/order.aggregate';

@Injectable()
export class PrismaOrderRepository implements OrderRepositoryPort {
  constructor(private readonly prisma: PrismaService) {}

  async findById(id: string): Promise<Order | null> {
    const data = await this.prisma.order.findUnique({
      where: { id },
      include: { items: true },
    });
    return data ? this.mapToDomain(data) : null;
  }

  async save(order: Order): Promise<void> {
    const total = order.getTotal();

    await this.prisma.order.upsert({
      where: { id: order.id },
      create: {
        id: order.id,
        customerId: order.customerId,
        status: order.getStatus(),
        total: total.getAmount(),
        currency: total.getCurrency(),
        items: {
          create: order.getItems().map(item => ({
            productId: item.productId,
            quantity: item.quantity,
            unitPrice: item.getUnitPrice().getAmount(),
            currency: item.getUnitPrice().getCurrency(),
          })),
        },
      },
      update: {
        status: order.getStatus(),
        total: total.getAmount(),
        currency: total.getCurrency(),
      },
    });
  }

  // ... other methods
}
```

## DTO Validation with class-validator

```typescript
// adapters/http/dto/create-order.dto.ts
import {
  IsString,
  IsUUID,
  IsArray,
  ValidateNested,
  IsNumber,
  IsPositive,
  IsCurrency,
  Min,
} from 'class-validator';
import { Type } from 'class-transformer';

class OrderItemDto {
  @IsUUID()
  productId: string;

  @IsNumber()
  @Min(1)
  quantity: number;

  @IsNumber()
  @IsPositive()
  unitPrice: number;

  @IsString()
  @IsCurrency()
  currency: string;
}

export class CreateOrderDto {
  @IsUUID()
  customerId: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];
}
```

## Controller Implementation

```typescript
// adapters/http/order.controller.ts
import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  UsePipes,
  ValidationPipe,
  ParseUUIDPipe,
} from '@nestjs/common';
import { CommandBus, QueryBus } from '@nestjs/cqrs';
import { CreateOrderDto } from './dto/create-order.dto';
import { CreateOrderCommand } from '../../application/commands/create-order.command';
import { GetOrderQuery } from '../../application/queries/get-order.query';

@Controller('orders')
export class OrderController {
  constructor(
    private readonly commandBus: CommandBus,
    private readonly queryBus: QueryBus,
  ) {}

  @Post()
  @UsePipes(new ValidationPipe({ transform: true }))
  async create(@Body() dto: CreateOrderDto) {
    const command = new CreateOrderCommand(
      dto.customerId,
      dto.items.map(item => ({
        productId: item.productId,
        quantity: item.quantity,
        unitPrice: item.unitPrice,
        currency: item.currency,
      })),
    );

    return this.commandBus.execute(command);
  }

  @Get(':id')
  async findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.queryBus.execute(new GetOrderQuery(id));
  }
}
```

## Testing Strategy

### Domain Unit Tests (No NestJS)

```typescript
// domain/aggregates/order.spec.ts
describe('Order Aggregate', () => {
  it('should calculate total correctly', () => {
    const order = new Order('order-1', 'customer-1');
    order.addItem(new OrderItem('prod-1', 2, Money.create(10, 'USD')));
    order.addItem(new OrderItem('prod-2', 1, Money.create(25, 'USD')));

    const total = order.getTotal();
    expect(total.getAmount()).toBe(45);
    expect(total.getCurrency()).toBe('USD');
  });

  it('should not confirm empty order', () => {
    const order = new Order('order-1', 'customer-1');
    expect(() => order.confirm()).toThrow('Cannot confirm empty order');
  });
});
```

### Use Case Unit Tests

```typescript
// application/commands/create-order.handler.spec.ts
describe('CreateOrderHandler', () => {
  let handler: CreateOrderHandler;
  let repository: jest.Mocked<OrderRepositoryPort>;
  let eventBus: jest.Mocked<EventBus>;

  beforeEach(() => {
    repository = {
      save: jest.fn(),
      findById: jest.fn(),
    } as any;

    eventBus = {
      publish: jest.fn(),
    } as any;

    handler = new CreateOrderHandler(repository, eventBus);
  });

  it('should create order and publish events', async () => {
    const command = new CreateOrderCommand('customer-1', [
      { productId: 'prod-1', quantity: 1, unitPrice: 10, currency: 'USD' },
    ]);

    const result = await handler.execute(command);

    expect(result.orderId).toBeDefined();
    expect(repository.save).toHaveBeenCalled();
    expect(eventBus.publish).toHaveBeenCalled();
  });
});
```

### Integration Tests

```typescript
// test/orders.e2e-spec.ts
describe('OrdersController (e2e)', () => {
  let app: INestApplication;
  let commandBus: CommandBus;

  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [OrdersModule],
    })
      .overrideProvider(ORDER_REPOSITORY)
      .useClass(InMemoryOrderRepository)
      .compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    commandBus = moduleFixture.get(CommandBus);
  });

  it('/orders (POST)', () => {
    return request(app.getHttpServer())
      .post('/orders')
      .send({
        customerId: 'customer-1',
        items: [
          { productId: 'prod-1', quantity: 1, unitPrice: 10, currency: 'USD' },
        ],
      })
      .expect(201)
      .expect((res) => {
        expect(res.body).toHaveProperty('orderId');
      });
  });
});
```

## Dependency Injection Configuration

### Environment-Specific Providers

```typescript
// config/database.config.ts
export const databaseProviders = [
  {
    provide: ORDER_REPOSITORY,
    useFactory: (config: ConfigService, prisma: PrismaService) => {
      const impl = config.get('DB_IMPL');
      return impl === 'prisma'
        ? new PrismaOrderRepository(prisma)
        : new TypeOrmOrderRepository(/* ... */);
    },
    inject: [ConfigService, PrismaService],
  },
];
```

## Transaction Management

```typescript
// application/services/transactional-order.service.ts
import { Injectable } from '@nestjs/common';
import { DataSource } from 'typeorm';

@Injectable()
export class TransactionalOrderService {
  constructor(private readonly dataSource: DataSource) {}

  async transferBetweenOrders(fromId: string, toId: string, amount: number) {
    return this.dataSource.transaction(async (manager) => {
      const fromOrder = await manager.findOne(OrderEntity, { where: { id: fromId } });
      const toOrder = await manager.findOne(OrderEntity, { where: { id: toId } });

      // Business logic here

      await manager.save([fromOrder, toOrder]);
    });
  }
}
```

## Event Handling

```typescript
// adapters/event-handlers/order-event.handler.ts
import { EventsHandler, IEventHandler } from '@nestjs/cqrs';
import { OrderCreatedEvent } from '../../domain/events/order-created.event';
import { Inject } from '@nestjs/common';
import { EmailServicePort } from '../../domain/ports/email-service.port';

@EventsHandler(OrderCreatedEvent)
export class OrderEventHandler implements IEventHandler<OrderCreatedEvent> {
  constructor(
    @Inject('EMAIL_SERVICE')
    private readonly emailService: EmailServicePort,
  ) {}

  async handle(event: OrderCreatedEvent) {
    await this.emailService.send({
      to: event.customerEmail,
      subject: 'Order Confirmed',
      body: `Your order ${event.orderId} has been confirmed.`,
    });
  }
}
```
