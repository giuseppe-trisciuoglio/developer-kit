---
globs: "**/*.schema.ts"
---
# Rule: Drizzle ORM Conventions

## Context
Enforce consistent database schema definitions, naming patterns, and query conventions when using Drizzle ORM with PostgreSQL.

## Guidelines

### Table Definitions
Define tables using `pgTable` with consistent naming:

```typescript
import { pgTable, uuid, text, boolean, timestamp, uniqueIndex } from 'drizzle-orm/pg-core';

export const usersTable = pgTable('users', {
  user_uuid: uuid('user_uuid').defaultRandom().primaryKey(),
  email: text('email').notNull().unique(),
  full_name: text('full_name').notNull(),
  role: text('role').notNull().$type<UserRoleEnum>(),
  is_active: boolean('is_active').notNull().default(true),
  ...createDeleteAndUpdateTimeStamps,
}, (table) => ({
  usersTableEmailIndex: uniqueIndex('usersTable_email_INDEX').on(table.email),
}));
```

### Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Table variable | `camelCase` + `Table` suffix | `usersTable`, `ordersTable` |
| SQL table name | `snake_case` plural | `'users'`, `'order_items'` |
| Primary key | `{entity_singular}_uuid` | `user_uuid`, `order_uuid` |
| Foreign key | `{referenced_entity}_uuid` | `user_uuid`, `product_uuid` |
| Column names (SQL) | `snake_case` | `created_at`, `full_name` |
| Index names | `{tableName}_{column}_INDEX` | `usersTable_email_INDEX` |
| Relations variable | `{entity_plural}Relations` | `usersRelations`, `ordersRelations` |
| Schema file | `{entity}.schema.ts` | `user.schema.ts`, `order.schema.ts` |

### Primary Keys
Always use UUID with `defaultRandom()` for primary keys:

```typescript
user_uuid: uuid('user_uuid').defaultRandom().primaryKey(),
```

### Foreign Keys
Reference parent table's primary key column directly:

```typescript
user_uuid: uuid('user_uuid')
  .notNull()
  .references(() => usersTable.user_uuid),
```

### Shared Timestamps Mixin
Create a reusable timestamp mixin for `created_at`, `updated_at`, and `deleted_at` (soft-delete):

```typescript
export const createDeleteAndUpdateTimeStamps = {
  created_at: timestamp('created_at').defaultNow().notNull(),
  updated_at: timestamp('updated_at').defaultNow().notNull(),
  deleted_at: timestamp('deleted_at'),
};
```

Every table MUST spread this mixin to support soft-delete and audit tracking.

### Type-Safe Enums in Columns
Use `.$type<EnumType>()` to enforce TypeScript enum types on text columns:

```typescript
role: text('role').notNull().$type<UserRoleEnum>(),
status: text('status').notNull().$type<OrderStatus>(),
```

### Relations
Define relations in a separate variable using `relations()`:

```typescript
export const ordersRelations = relations(ordersTable, ({ one, many }) => ({
  user: one(usersTable, {
    fields: [ordersTable.user_uuid],
    references: [usersTable.user_uuid],
  }),
  items: many(orderItemsTable),
}));
```

### Custom Drizzle Injection (NestJS)
Inject the Drizzle client via a custom decorator:

```typescript
// database/utils.ts
export const DB_INJECTION_KEY = 'DB_INJECTION_KEY';
export const InjectDrizzle = () => Inject(DB_INJECTION_KEY);

// Custom types
export type DrizzleDatabase = PostgresJsDatabase<typeof schema>;
export type DrizzleTransaction = Parameters<Parameters<DrizzleDatabase['transaction']>['0']>['0'];

// Usage in services/controllers
constructor(@InjectDrizzle() private db: DrizzleDatabase) {}
```

### Query Patterns
- Always filter out soft-deleted records: `where: isNull(table.deleted_at)`
- Use transactions for multi-table operations
- Prefer `select()` with explicit columns over `select(*)`

## Examples

### ✅ Good
```typescript
// order.schema.ts
export const ordersTable = pgTable('orders', {
  order_uuid: uuid('order_uuid').defaultRandom().primaryKey(),
  user_uuid: uuid('user_uuid').notNull().references(() => usersTable.user_uuid),
  status: text('status').notNull().$type<OrderStatus>(),
  total_amount: integer('total_amount').notNull(),
  ...createDeleteAndUpdateTimeStamps,
}, (table) => ({
  ordersTableUserIndex: index('ordersTable_user_uuid_INDEX').on(table.user_uuid),
}));

export const ordersRelations = relations(ordersTable, ({ one, many }) => ({
  user: one(usersTable, {
    fields: [ordersTable.user_uuid],
    references: [usersTable.user_uuid],
  }),
  items: many(orderItemsTable),
}));

// Service usage
const orders = await this.db
  .select()
  .from(ordersTable)
  .where(and(
    eq(ordersTable.user_uuid, userId),
    isNull(ordersTable.deleted_at),
  ));
```

### ❌ Bad
```typescript
// Wrong naming conventions
export const OrderTable = pgTable('Order', {  // SQL name should be snake_case plural
  id: serial('id').primaryKey(),               // Should use UUID, named entity_uuid
  userId: integer('userId'),                   // Column name should be snake_case
  // Missing timestamps mixin
});

// Deep import instead of injection
import { db } from '../../../database/connection';
```
