# Drizzle ORM Detailed Examples

## Schema Definition

### PostgreSQL Table

```typescript
import { pgTable, serial, text, integer, boolean, timestamp, pgEnum } from 'drizzle-orm/pg-core';

export const rolesEnum = pgEnum('roles', ['guest', 'user', 'admin']);

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  role: rolesEnum().default('user'),
  verified: boolean('verified').notNull().default(false),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});
```

### MySQL Table

```typescript
import { mysqlTable, serial, text, tinyint, datetime } from 'drizzle-orm/mysql-core';

export const users = mysqlTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  verified: tinyint('verified').notNull().default(0),
  createdAt: datetime('created_at').notNull().defaultNow(),
});
```

### SQLite Table

```typescript
import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
});
```

### Indexes and Constraints

```typescript
import { uniqueIndex, index, primaryKey } from 'drizzle-orm/pg-core';

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  slug: text('slug').notNull(),
  authorId: integer('author_id').references(() => users.id),
  createdAt: timestamp('created_at').notNull().defaultNow(),
}, (table) => [
  uniqueIndex('slug_idx').on(table.slug),
  index('author_idx').on(table.authorId),
]);
```

### Composite Primary Key

```typescript
export const usersToGroups = pgTable('users_to_groups', {
  userId: integer('user_id').notNull().references(() => users.id),
  groupId: integer('group_id').notNull().references(() => groups.id),
}, (table) => [
  primaryKey({ columns: [table.userId, table.groupId] }),
]);
```

## Relations

### One-to-Many

```typescript
import { relations } from 'drizzle-orm';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, { fields: [posts.authorId], references: [users.id] }),
}));
```

### One-to-One

```typescript
export const profiles = pgTable('profiles', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id).unique(),
  bio: text('bio'),
});

export const profilesRelations = relations(profiles, ({ one }) => ({
  user: one(users, { fields: [profiles.userId], references: [users.id] }),
}));
```

### Many-to-Many (v2 syntax)

```typescript
import * as schema from './schema';
import { defineRelations } from 'drizzle-orm';

export const relations = defineRelations(schema, (r) => ({
  users: {
    groups: r.many.groups({
      from: r.users.id.through(r.usersToGroups.userId),
      to: r.groups.id.through(r.usersToGroups.groupId),
    }),
  },
  groups: {
    participants: r.many.users(),
  },
}));
```

### Self-Referential

```typescript
import { type AnyPgColumn, integer, pgTable, serial, text } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  invitedBy: integer('invited_by').references((): AnyPgColumn => users.id),
});
```

## CRUD Operations

### Insert

```typescript
// Single
await db.insert(users).values({ name: 'John', email: 'john@example.com' });

// Multiple
await db.insert(users).values([
  { name: 'John', email: 'john@example.com' },
  { name: 'Jane', email: 'jane@example.com' },
]);

// With returning
const [newUser] = await db.insert(users).values({ name: 'John', email: 'john@example.com' }).returning();
```

### Select

```typescript
const allUsers = await db.select().from(users);
const result = await db.select({ id: users.id, name: users.name }).from(users);
const [user] = await db.select().from(users).where(eq(users.id, 1));
const count = await db.$count(users);
```

### Update

```typescript
await db.update(users).set({ name: 'Updated' }).where(eq(users.id, 1));
const [updated] = await db.update(users).set({ verified: true }).where(eq(users.email, 'john@example.com')).returning();
```

### Delete

```typescript
await db.delete(users).where(eq(users.id, 1));
const [deleted] = await db.delete(users).where(eq(users.email, 'john@example.com')).returning();
```

## Query Operators

```typescript
import { eq, ne, gt, gte, lt, lte, like, ilike, inArray, isNull, isNotNull, and, or, between } from 'drizzle-orm';

eq(users.id, 1)               // =
ne(users.name, 'John')        // !=
gt(users.age, 18)             // >
like(users.name, '%John%')    // LIKE (case-sensitive)
ilike(users.name, '%john%')   // ILIKE (case-insensitive)
isNull(users.deletedAt)       // IS NULL
inArray(users.id, [1, 2, 3])  // IN
between(users.createdAt, startDate, endDate) // BETWEEN

// Combining
and(gte(users.age, 18), eq(users.verified, true))
or(eq(users.role, 'admin'), eq(users.role, 'moderator'))
```

## Pagination

```typescript
import { asc, gt } from 'drizzle-orm';

// Offset-based
const usersPage = await db.select().from(users).orderBy(asc(users.id)).limit(10).offset(20);

// Cursor-based (more efficient)
const nextUsersPage = await db.select().from(users).where(gt(users.id, lastId)).orderBy(asc(users.id)).limit(10);
```

## Joins

```typescript
import { alias, eq } from 'drizzle-orm';

// Left join
const leftJoinRows = await db.select().from(users).leftJoin(posts, eq(users.id, posts.authorId));

// Inner join
const innerJoinRows = await db.select().from(users).innerJoin(posts, eq(users.id, posts.authorId));

// Partial select with join
const usersWithPosts = await db.select({
  userId: users.id, userName: users.name, postTitle: posts.title,
}).from(users).leftJoin(posts, eq(users.id, posts.authorId));

// Self-join with alias
const parent = alias(users, 'parent');
const selfJoinRows = await db.select().from(users).leftJoin(parent, eq(parent.id, users.parentId));
```

## Aggregations

```typescript
import { count, sum, avg, min, max, sql, gt } from 'drizzle-orm';

const [{ value }] = await db.select({ value: count() }).from(users);
const [stats] = await db.select({ totalAge: sum(users.age), avgAge: avg(users.age) }).from(users);

// Group by with having
const ageGroups = await db.select({
  age: users.age,
  count: sql<number>`cast(count(${users.id}) as int)`,
}).from(users).groupBy(users.age).having(({ count }) => gt(count, 1));
```

## Transactions

```typescript
import { eq, sql } from 'drizzle-orm';

// Basic
await db.transaction(async (tx) => {
  await tx.update(accounts).set({ balance: sql`${accounts.balance} - 100` }).where(eq(accounts.userId, 1));
  await tx.update(accounts).set({ balance: sql`${accounts.balance} + 100` }).where(eq(accounts.userId, 2));
});

// With rollback
await db.transaction(async (tx) => {
  const [account] = await tx.select().from(accounts).where(eq(accounts.userId, 1));
  if (account.balance < 100) tx.rollback();
  await tx.update(accounts).set({ balance: sql`${accounts.balance} - 100` }).where(eq(accounts.userId, 1));
});

// Nested (savepoints)
await db.transaction(async (tx) => {
  await tx.insert(users).values({ name: 'John' });
  await tx.transaction(async (tx2) => {
    await tx2.insert(posts).values({ title: 'Hello', authorId: 1 });
  });
});
```

## Drizzle Kit Config

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: { url: process.env.DATABASE_URL! },
});
```

```json
{ "scripts": { "generate": "drizzle-kit generate", "migrate": "drizzle-kit migrate", "push": "drizzle-kit push", "pull": "drizzle-kit pull" } }
```

### Programmatic Migration

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { migrate } from 'drizzle-orm/node-postgres/migrator';

const db = drizzle(process.env.DATABASE_URL);
await migrate(db, { migrationsFolder: './drizzle' });
```

## Type Inference

```typescript
type NewUser = typeof users.$inferInsert;
type User = typeof users.$inferSelect;

async function createUser(data: typeof users.$inferInsert) {
  return db.insert(users).values(data).returning();
}
```

## Common Patterns

### Soft Delete

```typescript
const activeUsers = await db.select().from(users).where(isNull(users.deletedAt));
await db.update(users).set({ deletedAt: new Date() }).where(eq(users.id, id));
```

### Upsert

```typescript
// PostgreSQL / SQLite - onConflictDoUpdate
await db.insert(users)
  .values({ id: 1, name: 'John', email: 'john@example.com' })
  .onConflictDoUpdate({
    target: users.id,
    set: { name: 'John', email: 'john@example.com' }
  });

// On conflict do nothing
await db.insert(users)
  .values({ id: 1, name: 'John', email: 'john@example.com' })
  .onConflictDoNothing({ target: users.id });

// MySQL - onDuplicateKeyUpdate
await db.insert(users)
  .values({ id: 1, name: 'John', email: 'john@example.com' })
  .onDuplicateKeyUpdate({ set: { name: 'John' } });
```
