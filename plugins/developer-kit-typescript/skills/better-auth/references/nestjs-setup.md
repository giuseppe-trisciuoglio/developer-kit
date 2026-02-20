# Better Auth NestJS Setup Guide

## Version Requirements

```json
{
  "dependencies": {
    "better-auth": "^1.1.0",
    "@auth/drizzle-adapter": "^1.0.0",
    "drizzle-orm": "^0.35.0",
    "pg": "^8.12.0",
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/config": "^3.0.0",
    "@nestjs/platform-express": "^10.0.0"
  },
  "devDependencies": {
    "drizzle-kit": "^0.24.0",
    "@types/pg": "^8.11.0",
    "@types/node": "^20.0.0"
  }
}
```

## Installation

```bash
npm install better-auth @auth/drizzle-adapter drizzle-orm pg
npm install @nestjs/common @nestjs/core @nestjs/config @nestjs/platform-express
npm install -D drizzle-kit @types/pg
```

## Step 1: Database Configuration

### Create Drizzle Config

```typescript
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';
import 'dotenv/config';

export default defineConfig({
  schema: './src/auth/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

### Create Database Module

```typescript
// src/database/database.module.ts
import { Module, Global } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Global()
@Module({
  providers: [DatabaseService],
  exports: [DatabaseService],
})
export class DatabaseModule {}
```

```typescript
// src/database/database.service.ts
import { Injectable, OnModuleDestroy } from '@nestjs/common';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

@Injectable()
export class DatabaseService implements OnModuleDestroy {
  private pool: Pool;
  public db: ReturnType<typeof drizzle>;

  constructor() {
    this.pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });

    this.db = drizzle(this.pool, {
      schema: {},
    });
  }

  async onModuleDestroy() {
    await this.pool.end();
  }
}
```

## Step 2: Better Auth Schema

```typescript
// src/auth/schema.ts
import {
  pgTable,
  text,
  timestamp,
  boolean,
  primaryKey,
  integer,
} from 'drizzle-orm/pg-core';
import type { AdapterAccount } from '@auth/drizzle-adapter';

export const users = pgTable('user', {
  id: text('id').notNull().primaryKey(),
  name: text('name'),
  email: text('email').notNull(),
  emailVerified: timestamp('emailVerified', { mode: 'date' }),
  image: text('image'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

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

export const sessions = pgTable('session', {
  sessionToken: text('sessionToken').notNull().primaryKey(),
  userId: text('userId')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  expires: timestamp('expires', { mode: 'date' }).notNull(),
});

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
  },
  (authenticator) => ({
    compositePK: primaryKey({
      columns: [authenticator.userId, authenticator.credentialID],
    }),
  })
);
```

## Step 3: Better Auth Instance

```typescript
// src/auth/auth.instance.ts
import { betterAuth } from 'better-auth';
import { drizzleAdapter } from '@auth/drizzle-adapter';
import * as schema from './schema';

export const auth = betterAuth({
  database: drizzleAdapter(schema, {
    provider: 'postgresql',
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  socialProviders: {
    github: {
      clientId: process.env.AUTH_GITHUB_CLIENT_ID!,
      clientSecret: process.env.AUTH_GITHUB_CLIENT_SECRET!,
      enabled: true,
    },
    google: {
      clientId: process.env.AUTH_GOOGLE_CLIENT_ID!,
      clientSecret: process.env.AUTH_GOOGLE_CLIENT_SECRET!,
      enabled: true,
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  advanced: {
    cookiePrefix: 'better-auth',
    crossSubDomainCookies: {
      enabled: false,
    },
  },
});
```

## Step 4: Auth Service

```typescript
// src/auth/auth.service.ts
import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../database/database.service';
import { auth } from './auth.instance';
import { headers } from 'next/headers';

@Injectable()
export class AuthService {
  constructor(private db: DatabaseService) {}

  async getSession(token: string) {
    return auth.api.getSession({
      headers: new Headers({
        authorization: `Bearer ${token}`,
      }),
    });
  }

  async getUserSessions(userId: string) {
    return auth.api.listSessions({
      body: { userId },
    });
  }

  async revokeSession(sessionToken: string) {
    return auth.api.revokeSession({
      body: { token: sessionToken },
    });
  }

  async revokeAllSessions(userId: string) {
    const sessions = await auth.api.listSessions({
      body: { userId },
    });

    await Promise.all(
      sessions.map((s) =>
        auth.api.revokeSession({
          body: { token: s.token },
        })
      )
    );
  }
}
```

## Step 5: Auth Controller

```typescript
// src/auth/auth.controller.ts
import { Controller, Post, Body, Get, Req, UseGuards } from '@nestjs/common';
import { AuthService } from './auth.service';
import { AuthGuard } from './auth.guard';

@Controller('auth')
export class AuthController {
  constructor(private authService: AuthService) {}

  @Get('session')
  async getSession(@Req() req) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    return this.authService.getSession(token);
  }

  @Post('sign-out')
  @UseGuards(AuthGuard)
  async signOut(@Req() req) {
    // Requires authentication to prevent session enumeration attacks
    return this.authService.revokeSession(req.session.sessionToken);
  }

  @Get('sessions')
  @UseGuards(AuthGuard)
  async getSessions(@Req() req) {
    return this.authService.getUserSessions(req.user.id);
  }

  @Post('sessions/revoke-all')
  @UseGuards(AuthGuard)
  async revokeAll(@Req() req) {
    return this.authService.revokeAllSessions(req.user.id);
  }
}
```

## Step 6: Auth Guard

```typescript
// src/auth/auth.guard.ts
import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { auth } from './auth.instance';

@Injectable()
export class AuthGuard implements CanActivate {
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const token = request.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      throw new UnauthorizedException('No token provided');
    }

    const session = await auth.api.getSession({
      headers: new Headers({
        authorization: `Bearer ${token}`,
      }),
    });

    if (!session) {
      throw new UnauthorizedException('Invalid session');
    }

    request.user = session.user;
    return true;
  }
}
```

## Step 7: Auth Module

```typescript
// src/auth/auth.module.ts
import { Module } from '@nestjs/common';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { AuthGuard } from './auth.guard';
import { DatabaseModule } from '../database/database.module';

@Module({
  imports: [DatabaseModule],
  controllers: [AuthController],
  providers: [AuthService, AuthGuard],
  exports: [AuthService, AuthGuard],
})
export class AuthModule {}
```

## Step 8: Generate and Run Migrations

```bash
# Generate migration files
npx drizzle-kit generate

# Run migrations
npx drizzle-kit migrate

# Or push directly (development only)
npx drizzle-kit push
```

## Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
AUTH_GITHUB_CLIENT_ID=your-github-client-id
AUTH_GITHUB_CLIENT_SECRET=your-github-client-secret
AUTH_GOOGLE_CLIENT_ID=your-google-client-id
AUTH_GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## Usage in Other Controllers

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import { AuthGuard } from '../auth/auth.guard';

@Controller('api/protected')
@UseGuards(AuthGuard)
export class ProtectedController {
  @Get()
  getProtectedData(@Request() req) {
    // req.user is available here
    return { message: 'Protected data', user: req.user };
  }
}
```
