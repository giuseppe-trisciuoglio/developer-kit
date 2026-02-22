---
name: drizzle-orm-patterns
version: 2.2.0
description: Provides comprehensive Drizzle ORM patterns for schema definition, CRUD operations, relations, queries, transactions, and migrations. Proactively use for any Drizzle ORM development including defining database schemas, writing type-safe queries, implementing relations, managing transactions, and setting up migrations with Drizzle Kit. Supports PostgreSQL, MySQL, SQLite, MSSQL, and CockroachDB.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
tags: [drizzle, orm, database, postgresql, mysql, sqlite, typescript, migrations, schema, queries]
category: backend
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

## Instructions

1. **Identify your database dialect** - Choose PostgreSQL, MySQL, SQLite, MSSQL, or CockroachDB
2. **Define your schema** - Use the appropriate table function (pgTable, mysqlTable, etc.)
3. **Set up relations** - Define relations using `relations()` (classic API) or `defineRelations()` (Relational Queries v2)
4. **Initialize the database client** - Create your Drizzle client with proper credentials
5. **Write queries** - Use the query builder for type-safe CRUD operations
6. **Handle transactions** - Wrap multi-step operations in transactions
7. **Set up migrations** - Configure Drizzle Kit for schema management

## Examples

### Schema with Relations

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

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, { fields: [posts.authorId], references: [users.id] }),
}));
```

### CRUD Operations

```typescript
import { eq } from 'drizzle-orm';

// Insert
const [newUser] = await db.insert(users).values({ name: 'John', email: 'john@example.com' }).returning();

// Select
const [user] = await db.select().from(users).where(eq(users.email, 'john@example.com'));

// Update
const [updated] = await db.update(users).set({ name: 'Updated' }).where(eq(users.id, 1)).returning();

// Delete
await db.delete(users).where(eq(users.id, 1));
```

### Migrations

```bash
npx drizzle-kit generate   # Generate migration files
npx drizzle-kit migrate    # Apply migrations
npx drizzle-kit push       # Push schema directly (dev)
npx drizzle-kit pull       # Introspect schema from database
```

## Constraints and Warnings

- **Foreign Key Constraints**: Always define references using arrow functions `() => table.column`
- **Transaction Rollback**: `tx.rollback()` throws an exception - use try/catch if needed
- **Returning Clauses**: Not all databases support `.returning()` - check dialect compatibility
- **Batch Operations**: Large batch inserts may hit database limits - chunk into smaller batches
- **Migrations in Production**: Always test migrations in staging first

## Best Practices

1. Always use TypeScript and leverage `$inferInsert` / `$inferSelect`
2. Define relations using the relations() API for nested queries
3. Use transactions for multi-step operations
4. Use `generate` + `migrate` in production, `push` for development
5. Add indexes on frequently queried columns and foreign keys
6. Use cursor-based pagination for large datasets
7. Use `onConflictDoUpdate()` / `onDuplicateKeyUpdate()` for upserts (dialect-specific)

## References

Consult these files for detailed patterns and examples:

- **[references/examples.md](references/examples.md)** - All dialects (PostgreSQL, MySQL, SQLite), indexes, composite keys, relation types, query operators, joins, aggregations, pagination, transactions, type inference, common patterns (soft delete, upsert, batch operations)
