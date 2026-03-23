---
name: drizzle-orm-patterns
description: Provides comprehensive Drizzle ORM patterns for schema definition, CRUD operations, relations, queries, transactions, and migrations. Proactively use for any Drizzle ORM development including defining database schemas, writing type-safe queries, implementing relations, managing transactions, and setting up migrations with Drizzle Kit. Supports PostgreSQL, MySQL, SQLite, MSSQL, and CockroachDB.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Drizzle ORM Patterns

## Overview

Expert guide for building type-safe database applications with Drizzle ORM. Covers schema definition, relations, queries, transactions, and migrations for all supported databases.

## When to Use

- Defining database schemas with tables, columns, and constraints
- Creating relations between tables (one-to-one, one-to-many, many-to-many)
- Writing type-safe CRUD queries
- Implementing complex joins and aggregations
- Managing database transactions with rollback
- Setting up migrations with Drizzle Kit
- Working with PostgreSQL, MySQL, SQLite, MSSQL, or CockroachDB

## Instructions

1. **Identify your database dialect** - Choose PostgreSQL, MySQL, SQLite, MSSQL, or CockroachDB
2. **Define your schema** - Use the appropriate table function (pgTable, mysqlTable, etc.)
3. **Set up relations** - Define relations using `relations()` or `defineRelations()` for complex relationships
4. **Initialize the database client** - Create your Drizzle client with proper credentials
5. **Write queries** - Use the query builder for type-safe CRUD operations
6. **Handle transactions** - Wrap multi-step operations in transactions when needed
7. **Set up migrations** - Configure Drizzle Kit for schema management

## Quick Reference

### Basic Schema Definition

```typescript
import { pgTable, serial, text, integer, timestamp } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow(),
});

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  authorId: integer('author_id').references(() => users.id),
});

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));
```

### CRUD Operations

```typescript
import { eq } from 'drizzle-orm';

// Insert
const [newUser] = await db.insert(users).values({
  name: 'John',
  email: 'john@example.com',
}).returning();

// Select
const [user] = await db.select().from(users).where(eq(users.id, 1));

// Update
await db.update(users)
  .set({ name: 'John Updated' })
  .where(eq(users.id, 1));

// Delete
await db.delete(users).where(eq(users.id, 1));
```

### Transaction with Rollback

```typescript
await db.transaction(async (tx) => {
  const [from] = await tx.select().from(accounts).where(eq(accounts.userId, fromId));

  if (from.balance < amount) {
    tx.rollback();
  }

  await tx.update(accounts)
    .set({ balance: sql`${accounts.balance} - ${amount}` })
    .where(eq(accounts.userId, fromId));
});
```

## References

For detailed patterns and examples, see:

- [references/patterns.md](references/patterns.md) - Detailed patterns for schema definition, CRUD operations, relations, joins, aggregations, transactions, and migrations
- [references/examples.md](references/examples.md) - Complete working examples for common use cases
- [references/best-practices.md](references/best-practices.md) - Best practices, constraints, and warnings

## Examples

See [references/examples.md](references/examples.md) for complete working examples including:
- Complete schema with relations
- CRUD operations
- Transaction with rollback
- Complex queries with joins
- Pagination implementation
- Aggregation queries
- Soft delete pattern
- Full-featured repository pattern

## Best Practices

See [references/best-practices.md](references/best-practices.md) for comprehensive best practices including:
- Type safety with `$inferInsert` / `$inferSelect`
- Relations definition patterns
- Transaction usage
- Migration strategies
- Index recommendations
- Soft delete implementation
- Pagination strategies
- Query optimization

## Constraints and Warnings

See [references/best-practices.md#constraints-and-warnings](references/best-practices.md#constraints-and-warnings) for important considerations including:
- Foreign key constraint patterns
- Transaction rollback behavior
- Returning clause compatibility
- Batch operation limits
- Migration safety in production
- Soft delete query requirements
