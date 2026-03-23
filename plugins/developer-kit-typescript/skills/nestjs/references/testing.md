# NestJS Testing Patterns

Unit and E2E testing patterns for NestJS applications with Drizzle ORM.

## Unit Testing Services

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { UsersService } from './users.service';
import { UserRepository } from './user.repository';

describe('UsersService', () => {
  let service: UsersService;
  let repository: jest.Mocked<UserRepository>;

  beforeEach(async () => {
    const mockRepository = {
      findAll: jest.fn(),
      findOne: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      remove: jest.fn(),
    } as any;

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: UserRepository,
          useValue: mockRepository,
        },
      ],
    }).compile();

    service = module.get<UsersService>(UsersService);
    repository = module.get(UserRepository);
  });

  it('should return all users', async () => {
    const expectedUsers = [{ id: 1, name: 'John', email: 'john@example.com' }];
    repository.findAll.mockResolvedValue(expectedUsers);

    const result = await service.findAll();
    expect(result).toEqual(expectedUsers);
    expect(repository.findAll).toHaveBeenCalled();
  });
});
```

## E2E Testing with Drizzle

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';
import { DatabaseService } from '../src/db/database.service';
import { drizzle } from 'drizzle-orm/node-postgres';
import { migrate } from 'drizzle-orm/node-postgres/migrator';

describe('UsersController (e2e)', () => {
  let app: INestApplication;
  let db: DatabaseService;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    db = moduleFixture.get<DatabaseService>(DatabaseService);

    // Run migrations
    await migrate(db.database, { migrationsFolder: './drizzle' });

    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(async () => {
    // Clean database
    await db.database.delete(users).execute();
  });

  it('/users (POST)', () => {
    const createUserDto = {
      name: 'Test User',
      email: 'test@example.com',
    };

    return request(app.getHttpServer())
      .post('/users')
      .send(createUserDto)
      .expect(201)
      .expect((res) => {
        expect(res.body).toMatchObject(createUserDto);
        expect(res.body).toHaveProperty('id');
      });
  });

  it('/users (GET)', async () => {
    // First create a user
    await db.database.insert(users).values({
      name: 'Test User',
      email: 'test@example.com',
    });

    return request(app.getHttpServer())
      .get('/users')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body)).toBe(true);
        expect(res.body).toHaveLength(1);
      });
  });
});
```

## Testing Best Practices

1. **Mock external dependencies** - Use Jest mocks for repositories and services
2. **Clean database between tests** - Use `beforeEach` to reset state
3. **Run migrations in E2E tests** - Ensures schema is up to date
4. **Test edge cases** - Error scenarios and validation failures
5. **Use supertest for HTTP assertions** - Clean API for testing endpoints
