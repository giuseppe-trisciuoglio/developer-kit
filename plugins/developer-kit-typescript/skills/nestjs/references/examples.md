# NestJS with Drizzle ORM - Complete Examples

## Drizzle ORM Setup

### Installation

```bash
npm install drizzle-orm pg
npm install -D drizzle-kit tsx @types/pg
```

### Configuration

```typescript
// drizzle.config.ts
import 'dotenv/config';
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  out: './drizzle',
  schema: './src/db/schema.ts',
  dialect: 'postgresql',
  dbCredentials: { url: process.env.DATABASE_URL! },
});
```

### Database Schema

```typescript
// src/db/schema.ts
import { pgTable, serial, text, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow(),
});
```

### Database Service

```typescript
// src/db/database.service.ts
import { Injectable } from '@nestjs/common';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './schema';

@Injectable()
export class DatabaseService {
  private db: ReturnType<typeof drizzle>;

  constructor() {
    const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    this.db = drizzle(pool, { schema });
  }

  get database() { return this.db; }
}
```

### User Repository

```typescript
// src/users/user.repository.ts
import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../db/database.service';
import { users } from '../db/schema';
import { eq } from 'drizzle-orm';

@Injectable()
export class UserRepository {
  constructor(private db: DatabaseService) {}

  async findAll() { return this.db.database.select().from(users); }

  async findOne(id: number) {
    const result = await this.db.database.select().from(users).where(eq(users.id, id)).limit(1);
    return result[0];
  }

  async create(data: typeof users.$inferInsert) {
    const result = await this.db.database.insert(users).values(data).returning();
    return result[0];
  }

  async update(id: number, data: Partial<typeof users.$inferInsert>) {
    const result = await this.db.database.update(users).set(data).where(eq(users.id, id)).returning();
    return result[0];
  }

  async remove(id: number) {
    const result = await this.db.database.delete(users).where(eq(users.id, id)).returning();
    return result[0];
  }
}
```

### Complete Module

```typescript
// src/users/users.module.ts
import { Module } from '@nestjs/common';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { UserRepository } from './user.repository';
import { DatabaseService } from '../db/database.service';

@Module({
  controllers: [UsersController],
  providers: [UsersService, UserRepository, DatabaseService],
  exports: [UsersService],
})
export class UsersModule {}
```

### Service Implementation

```typescript
// src/users/users.service.ts
import { Injectable } from '@nestjs/common';
import { UserRepository } from './user.repository';

@Injectable()
export class UsersService {
  constructor(private userRepository: UserRepository) {}

  async findAll() { return this.userRepository.findAll(); }

  async findOne(id: number) {
    const user = await this.userRepository.findOne(id);
    if (!user) throw new Error('User not found');
    return user;
  }

  async create(userData: any) { return this.userRepository.create(userData); }
  async update(id: number, userData: any) {
    await this.findOne(id);
    return this.userRepository.update(id, userData);
  }
  async remove(id: number) {
    await this.findOne(id);
    return this.userRepository.remove(id);
  }
}
```

## Authentication & Authorization

### Roles-Based Guard

```typescript
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.get<string[]>('roles', context.getHandler());
    if (!requiredRoles) return true;
    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some((role) => user.roles?.includes(role));
  }
}
```

## Migrations

```bash
npx drizzle-kit generate
```

```typescript
// src/migrations/migration.service.ts
import { Injectable } from '@nestjs/common';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { DatabaseService } from '../db/database.service';

@Injectable()
export class MigrationService {
  constructor(private db: DatabaseService) {}

  async runMigrations() {
    await migrate(this.db.database, { migrationsFolder: './drizzle' });
  }
}
```

## Common Drizzle Patterns

### Transactions

```typescript
async transferFunds(fromId: number, toId: number, amount: number) {
  return this.db.database.transaction(async (tx) => {
    await tx.update(accounts).set({ balance: sql`${accounts.balance} - ${amount}` })
      .where(eq(accounts.id, fromId));
    await tx.update(accounts).set({ balance: sql`${accounts.balance} + ${amount}` })
      .where(eq(accounts.id, toId));
  });
}
```

### Soft Deletes

```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  deletedAt: timestamp('deleted_at'),
});

async softDelete(id: number) {
  return this.db.database.update(users).set({ deletedAt: new Date() }).where(eq(users.id, id));
}
```

### Complex Queries with Relations

```typescript
async getUsersWithPosts() {
  return this.db.database.select().from(users).leftJoin(posts, eq(posts.userId, users.id));
}
```

## Testing

### Unit Testing Services

```typescript
describe('UsersService', () => {
  let service: UsersService;
  let repository: jest.Mocked<UserRepository>;

  beforeEach(async () => {
    const mockRepository = {
      findAll: jest.fn(), findOne: jest.fn(),
      create: jest.fn(), update: jest.fn(), remove: jest.fn(),
    } as any;

    const module = await Test.createTestingModule({
      providers: [
        UsersService,
        { provide: UserRepository, useValue: mockRepository },
      ],
    }).compile();

    service = module.get<UsersService>(UsersService);
    repository = module.get(UserRepository);
  });

  it('should return all users', async () => {
    const expected = [{ id: 1, name: 'John', email: 'john@example.com' }];
    repository.findAll.mockResolvedValue(expected);
    expect(await service.findAll()).toEqual(expected);
  });
});
```

### E2E Testing

```typescript
describe('UsersController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const module = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = module.createNestApplication();
    await app.init();
  });

  it('/users (POST)', () => {
    return request(app.getHttpServer())
      .post('/users')
      .send({ name: 'Test User', email: 'test@example.com' })
      .expect(201)
      .expect((res) => { expect(res.body).toHaveProperty('id'); });
  });
});
```

## Configuration

```typescript
// src/config/configuration.ts
export default () => ({
  database: { url: process.env.DATABASE_URL },
  jwt: {
    secret: process.env.JWT_SECRET || 'default-secret',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
  },
  app: { port: parseInt(process.env.PORT, 10) || 3000 },
});
```
