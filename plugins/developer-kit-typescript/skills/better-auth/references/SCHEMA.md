# Better Auth Database Schema Reference

This document provides the complete Drizzle ORM schema for Better Auth with PostgreSQL.

## Core Tables

### User Table

```typescript
import {
  pgTable,
  text,
  timestamp,
  boolean,
  primaryKey,
  integer,
} from 'drizzle-orm/pg-core';

export const users = pgTable('user', {
  id: text('id').notNull().primaryKey(),
  name: text('name'),
  email: text('email').notNull(),
  emailVerified: timestamp('emailVerified', { mode: 'date' }),
  image: text('image'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});
```

### Account Table (OAuth)

```typescript
export const accounts = pgTable(
  'account',
  {
    userId: text('userId')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    type: text('type').$type<'email' | 'oauth' | 'oidc' | 'webauthn'>().notNull(),
    provider: text('provider').notNull(),
    providerAccountId: text('providerAccountId').notNull(),
    refresh_token: text('refresh_token'),
    access_token: text('access_token'),
    expires_at: integer('expires_at'),
    token_type: text('token_type'),
    scope: text('scope'),
    id_token: text('id_token'),
    session_state: text('session_state'),
  },
  (account) => ({
    compoundKey: primaryKey({
      columns: [account.provider, account.providerAccountId],
    }),
  })
);
```

### Session Table

```typescript
export const sessions = pgTable('session', {
  sessionToken: text('sessionToken').notNull().primaryKey(),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  expires: timestamp('expires', { mode: 'date' }).notNull(),
});
```

### Verification Token Table

```typescript
export const verificationTokens = pgTable(
  'verificationToken',
  {
    identifier: text('identifier').notNull(),
    token: text('token').notNull(),
    expires: timestamp('expires', { mode: 'date' }).notNull(),
  },
  (vt) => ({
    compoundKey: primaryKey({ columns: [vt.identifier, vt.token] }),
  })
);
```

## Plugin Tables

### Two-Factor Authentication

```typescript
export const totp = pgTable('totp', {
  id: text('id').notNull().primaryKey(),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  secret: text('secret').notNull(),
  createdAt: timestamp('createdAt').defaultNow(),
});
```

### Organization Tables

```typescript
export const organizations = pgTable('organizations', {
  id: text('id').notNull().primaryKey(),
  name: text('name').notNull(),
  slug: text('slug').notNull().unique(),
  logo: text('logo'),
  metadata: text('metadata').$type<Record<string, any>>(),
  createdAt: timestamp('createdAt').defaultNow(),
});

export const members = pgTable('members', {
  id: text('id').notNull().primaryKey(),
  organizationId: text('organizationId')
    .notNull()
    .references(() => organizations.id, { onDelete: 'cascade' }),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  role: text('role').notNull(), // owner, admin, member
  createdAt: timestamp('createdAt').defaultNow(),
});

export const invitations = pgTable('invitations', {
  id: text('id').notNull().primaryKey(),
  organizationId: text('organizationId')
    .notNull()
    .references(() => organizations.id, { onDelete: 'cascade' }),
  email: text('email').notNull(),
  role: text('role').notNull(),
  status: text('status').notNull(), // pending, accepted, rejected
  expiresAt: timestamp('expiresAt').notNull(),
  createdAt: timestamp('createdAt').defaultNow(),
});
```

### Passkey Table

```typescript
export const authenticators = pgTable(
  'authenticator',
  {
    credentialID: text('credentialID').notNull().primaryKey(),
    userId: text('userId')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    providerAccountId: text('providerAccountId').notNull(),
    credentialPublicKey: text('credentialPublicKey').notNull(),
    counter: integer('counter').notNull(),
    credentialDeviceType: text('credentialDeviceType').notNull(),
    credentialBackedUp: boolean('credentialBackedUp').notNull(),
    transports: text('transports'),
    name: text('name'),
  },
  (authenticator) => ({
    compositePK: primaryKey({
      columns: [authenticator.userId, authenticator.credentialID],
    }),
  })
);
```

### Magic Link Table

```typescript
export const magicLinks = pgTable('magic_links', {
  id: text('id').notNull().primaryKey(),
  email: text('email').notNull(),
  token: text('token').notNull().unique(),
  expiresAt: timestamp('expiresAt').notNull(),
  createdAt: timestamp('createdAt').defaultNow(),
});
```

### Email Verification Table

```typescript
export const emailVerifications = pgTable('email_verifications', {
  id: text('id').notNull().primaryKey(),
  email: text('email').notNull(),
  code: text('code').notNull(),
  expiresAt: timestamp('expiresAt').notNull(),
  verified: boolean('verified').notNull().default(false),
  createdAt: timestamp('createdAt').defaultNow(),
});
```

## Complete Schema File

```typescript
// src/auth/schema.ts
import {
  pgTable,
  text,
  timestamp,
  boolean,
  primaryKey,
  integer,
  index,
} from 'drizzle-orm/pg-core';
import type { AdapterAccount } from '@auth/drizzle-adapter';

// User table
export const users = pgTable('user', {
  id: text('id').notNull().primaryKey(),
  name: text('name'),
  email: text('email').notNull(),
  emailVerified: timestamp('emailVerified', { mode: 'date' }),
  image: text('image'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  emailIdx: index('user_email_idx').on(table.email),
}));

// Account table
export const accounts = pgTable(
  'account',
  {
    userId: text('userId')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    type: text('type').$type<AdapterAccount['type']>().notNull(),
    provider: text('provider').notNull(),
    providerAccountId: text('providerAccountId').notNull(),
    refresh_token: text('refresh_token'),
    access_token: text('access_token'),
    expires_at: integer('expires_at'),
    token_type: text('token_type'),
    scope: text('scope'),
    id_token: text('id_token'),
    session_state: text('session_state'),
  },
  (account) => ({
    compoundKey: primaryKey({
      columns: [account.provider, account.providerAccountId],
    }),
  })
);

// Session table
export const sessions = pgTable('session', {
  sessionToken: text('sessionToken').notNull().primaryKey(),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  expires: timestamp('expires', { mode: 'date' }).notNull(),
}, (table) => ({
  userIdIdx: index('session_user_id_idx').on(table.userId),
}));

// Verification token table
export const verificationTokens = pgTable(
  'verificationToken',
  {
    identifier: text('identifier').notNull(),
    token: text('token').notNull(),
    expires: timestamp('expires', { mode: 'date' }).notNull(),
  },
  (vt) => ({
    compoundKey: primaryKey({ columns: [vt.identifier, vt.token] }),
  })
);

// Authenticator table (for passkeys)
export const authenticators = pgTable(
  'authenticator',
  {
    credentialID: text('credentialID').notNull().primaryKey(),
    userId: text('userId')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    providerAccountId: text('providerAccountId').notNull(),
    credentialPublicKey: text('credentialPublicKey').notNull(),
    counter: integer('counter').notNull(),
    credentialDeviceType: text('credentialDeviceType').notNull(),
    credentialBackedUp: boolean('credentialBackedUp').notNull(),
    transports: text('transports'),
    name: text('name'),
  },
  (authenticator) => ({
    compositePK: primaryKey({
      columns: [authenticator.userId, authenticator.credentialID],
    }),
  })
);
```

## Migrations

### Generate Migration

```bash
npx drizzle-kit generate
```

### Run Migration

```bash
npx drizzle-kit migrate
```

### Push to Database (Dev Only)

```bash
npx drizzle-kit push
```

## Type Generation

Generate TypeScript types from your schema:

```bash
npx drizzle-kit generate:pg
```

This will create types for all your tables that you can use in your application:

```typescript
type User = typeof users.$inferSelect;
type NewUser = typeof users.$inferInsert;
```

## Indexes

For better performance, add indexes to commonly queried fields:

```typescript
export const sessions = pgTable('session', {
  sessionToken: text('sessionToken').notNull().primaryKey(),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  expires: timestamp('expires', { mode: 'date' }).notNull(),
  createdAt: timestamp('created_at').defaultNow(),
}, (table) => ({
  userIdIdx: index('session_user_id_idx').on(table.userId),
  expiresIdx: index('session_expires_idx').on(table.expires),
}));
```

## Relationships

The schema establishes these relationships:

- **Account -> User**: Many-to-one (accounts belong to users)
- **Session -> User**: Many-to-one (sessions belong to users)
- **Authenticator -> User**: Many-to-one (passkeys belong to users)
- **Member -> User**: Many-to-one (organization members are users)
- **Member -> Organization**: Many-to-one (members belong to organizations)
