# Rule: Drizzle ORM Integration Patterns

## Context

Drizzle ORM is a lightweight, type-safe ORM for TypeScript. When used within NestJS, it must be integrated through the provider system to maintain testability and proper dependency management.

## Guidelines

### Drizzle Client Provider
- Wrap the Drizzle client in a custom provider using `useFactory`
- Register the provider in a dedicated `DatabaseModule`
- Export the provider token so domain modules can inject it
- Use `ConfigService` for database connection configuration — never hardcode

### Repository Pattern
- Create a repository class per domain entity (e.g., `OrderRepository`)
- Inject the Drizzle client via constructor injection using the provider token
- Encapsulate all database queries inside repositories — never expose Drizzle directly to services
- Return domain entities from repository methods, not raw query results

### Schema Organization
- Define Drizzle schemas in dedicated files per domain (e.g., `order/schemas/order.schema.ts`)
- Co-locate schemas with their domain module
- Use Drizzle's type inference for TypeScript types: `typeof orders.$inferSelect`

### Transactions
- Use `db.transaction()` for operations that span multiple tables
- Pass the transaction client as a parameter to repository methods
- Handle transaction rollback via exception propagation

## Examples

### ✅ Correct — Database Module with Factory Provider

```typescript
// database/database.module.ts
import { Module } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

export const DRIZZLE = Symbol('DRIZZLE');

@Module({
  providers: [
    {
      provide: DRIZZLE,
      useFactory: async (configService: ConfigService) => {
        const pool = new Pool({
          connectionString: configService.get<string>('DATABASE_URL'),
        });
        return drizzle(pool);
      },
      inject: [ConfigService],
    },
  ],
  exports: [DRIZZLE],
})
export class DatabaseModule {}
```

### ✅ Correct — Repository with Injected Drizzle Client

```typescript
// order/order.repository.ts
import { Inject, Injectable } from '@nestjs/common';
import { NodePgDatabase } from 'drizzle-orm/node-postgres';
import { eq } from 'drizzle-orm';
import { DRIZZLE } from '../database/database.module';
import { orders } from './schemas/order.schema';

@Injectable()
export class OrderRepository {
  constructor(
    @Inject(DRIZZLE) private readonly db: NodePgDatabase,
  ) {}

  async findById(id: string): Promise<Order | null> {
    const result = await this.db
      .select()
      .from(orders)
      .where(eq(orders.id, id))
      .limit(1);

    return result[0] ?? null;
  }

  async save(data: NewOrder): Promise<Order> {
    const result = await this.db
      .insert(orders)
      .values(data)
      .returning();

    return result[0];
  }
}
```

### ✅ Correct — Schema Definition

```typescript
// order/schemas/order.schema.ts
import { pgTable, uuid, varchar, integer, timestamp } from 'drizzle-orm/pg-core';

export const orders = pgTable('orders', {
  id: uuid('id').primaryKey().defaultRandom(),
  customerId: uuid('customer_id').notNull(),
  status: varchar('status', { length: 50 }).notNull().default('pending'),
  totalAmount: integer('total_amount').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

export type Order = typeof orders.$inferSelect;
export type NewOrder = typeof orders.$inferInsert;
```

### ✅ Correct — Transaction Usage

```typescript
@Injectable()
export class OrderService {
  constructor(
    @Inject(DRIZZLE) private readonly db: NodePgDatabase,
    private readonly orderRepository: OrderRepository,
  ) {}

  async createOrderWithItems(dto: CreateOrderDto): Promise<Order> {
    return this.db.transaction(async (tx) => {
      const order = await tx
        .insert(orders)
        .values({ customerId: dto.customerId, totalAmount: dto.totalAmount })
        .returning();

      await tx.insert(orderItems).values(
        dto.items.map((item) => ({
          orderId: order[0].id,
          productId: item.productId,
          quantity: item.quantity,
        })),
      );

      return order[0];
    });
  }
}
```

### ❌ Incorrect — Direct DB Access in Controller

```typescript
@Controller('orders')
export class OrderController {
  constructor(@Inject(DRIZZLE) private readonly db: NodePgDatabase) {}

  @Get(':id')
  async findById(@Param('id') id: string) {
    // Wrong: database access should be in a repository, not controller
    return this.db.select().from(orders).where(eq(orders.id, id));
  }
}
```

### ❌ Incorrect — Hardcoded Connection String

```typescript
// Wrong: hardcoded database URL
const pool = new Pool({
  connectionString: 'postgresql://user:pass@localhost:5432/mydb',
});
export const db = drizzle(pool);

// ✅ Correct: use ConfigService via a provider factory
```
