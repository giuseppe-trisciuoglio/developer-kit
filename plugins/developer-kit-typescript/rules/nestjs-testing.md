---
globs: "**/*.spec.ts"
---
# Rule: NestJS Testing

## Context
Enforce testing best practices for NestJS applications: use `@nestjs/testing` for proper DI, mock all external dependencies, and write E2E tests with Supertest.

## Guidelines

### Unit Tests with Testing Module
- **Always** use `Test.createTestingModule()` — never manually instantiate services
- Mock all dependencies using `useValue` with Jest mock objects
- Clear all mocks in `afterEach` to prevent test pollution
- Follow the Arrange-Act-Assert pattern
- Name test variables clearly: `inputX`, `mockX`, `actualX`, `expectedX`

```typescript
// ✅ Proper unit test with Testing Module
describe('UsersService', () => {
  let service: UsersService;
  let repo: jest.Mocked<UserRepository>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: UserRepository,
          useValue: {
            save: jest.fn(),
            findOne: jest.fn(),
            find: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<UsersService>(UsersService);
    repo = module.get(UserRepository);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('create', () => {
    it('should save and return user', async () => {
      const inputDto = { name: 'John', email: 'john@test.com' };
      const expectedUser = { id: '1', ...inputDto };
      repo.save.mockResolvedValue(expectedUser);

      const actualUser = await service.create(inputDto);

      expect(actualUser).toEqual(expectedUser);
      expect(repo.save).toHaveBeenCalledWith(inputDto);
    });

    it('should throw on duplicate email', async () => {
      repo.findOne.mockResolvedValue({ id: '1', email: 'test@test.com' });

      await expect(
        service.create({ name: 'Test', email: 'test@test.com' }),
      ).rejects.toThrow(ConflictException);
    });
  });
});
```

### Mock External Services
- **Never** call real external services (APIs, databases, queues) in unit tests
- Mock HTTP services, repositories, and third-party SDKs
- Test error scenarios: timeouts, rate limiting, 500 errors
- Use `jest.useFakeTimers()` for time-dependent tests
- Create mock factories for complex SDKs

```typescript
// ✅ Mock HTTP service with error scenarios
describe('WeatherService', () => {
  let service: WeatherService;
  let httpService: jest.Mocked<HttpService>;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        WeatherService,
        { provide: HttpService, useValue: { get: jest.fn() } },
      ],
    }).compile();

    service = module.get(WeatherService);
    httpService = module.get(HttpService);
  });

  it('should return weather data', async () => {
    const mockResponse = { data: { temperature: 72 }, status: 200 };
    httpService.get.mockReturnValue(of(mockResponse));

    const result = await service.getWeather('NYC');
    expect(result).toEqual({ temperature: 72 });
  });

  it('should handle API timeout', async () => {
    httpService.get.mockReturnValue(throwError(() => new Error('ETIMEDOUT')));

    await expect(service.getWeather('NYC')).rejects.toThrow('Weather service unavailable');
  });
});

// ✅ Mock repository instead of real database
{ provide: getRepositoryToken(User), useValue: {
    find: jest.fn(),
    findOne: jest.fn(),
    save: jest.fn(),
    delete: jest.fn(),
  },
}
```

### E2E Tests with Supertest
- Use `Test.createTestingModule` with the real `AppModule` for E2E tests
- Apply the same global configuration as production (ValidationPipe, interceptors)
- Test the full request/response cycle: routes, guards, pipes, serialization
- Clean database between tests for isolation
- Test auth flows: 401 without token, 200 with valid token

```typescript
// ✅ E2E test with proper setup
describe('UsersController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        transform: true,
        forbidNonWhitelisted: true,
      }),
    );
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('POST /users — should create a user', () => {
    return request(app.getHttpServer())
      .post('/users')
      .send({ name: 'John', email: 'john@test.com' })
      .expect(201)
      .expect((res) => {
        expect(res.body).toHaveProperty('id');
        expect(res.body.name).toBe('John');
      });
  });

  it('POST /users — should return 400 for invalid email', () => {
    return request(app.getHttpServer())
      .post('/users')
      .send({ name: 'John', email: 'invalid-email' })
      .expect(400)
      .expect((res) => {
        expect(res.body.message).toContain('email');
      });
  });

  it('GET /users/:id — should return 404 for non-existent user', () => {
    return request(app.getHttpServer())
      .get('/users/non-existent-id')
      .expect(404);
  });
});

// ✅ E2E test with authentication
describe('Protected Routes (e2e)', () => {
  let app: INestApplication;
  let authToken: string;

  beforeAll(async () => {
    // ... setup
    const loginRes = await request(app.getHttpServer())
      .post('/auth/login')
      .send({ email: 'test@test.com', password: 'password' });
    authToken = loginRes.body.accessToken;
  });

  it('should return 401 without token', () => {
    return request(app.getHttpServer()).get('/users/me').expect(401);
  });

  it('should return profile with valid token', () => {
    return request(app.getHttpServer())
      .get('/users/me')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);
  });
});
```

### Testing Guards and Interceptors
- Test guards in isolation using mocked `ExecutionContext` and `Reflector`
- Test interceptors with mocked `CallHandler`
- Write controller and service tests separately — each with their own mocks

```typescript
// ✅ Guard unit test
describe('RolesGuard', () => {
  let guard: RolesGuard;
  let reflector: Reflector;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [RolesGuard, Reflector],
    }).compile();

    guard = module.get(RolesGuard);
    reflector = module.get(Reflector);
  });

  it('should allow when no roles required', () => {
    const context = createMockExecutionContext({ user: { roles: [] } });
    jest.spyOn(reflector, 'getAllAndOverride').mockReturnValue(undefined);
    expect(guard.canActivate(context)).toBe(true);
  });
});
```

## Examples

### ✅ Good
```typescript
// Write tests for each controller and service
// Write E2E tests for each API module
// Use Test.createTestingModule for proper DI
// Mock all external dependencies
// Follow Given-When-Then for acceptance tests
// Follow Arrange-Act-Assert for unit tests
```

### ❌ Bad
```typescript
// ❌ Manual instantiation bypassing DI
const repo = new UserRepository();
const service = new UsersService(repo);

// ❌ Calling real external APIs in unit tests
const service = new PaymentService(new StripeClient(realApiKey));

// ❌ No proper setup/teardown in E2E tests
const app = await NestFactory.create(AppModule);
// No cleanup, no config, hits real database
```
