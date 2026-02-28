# NestJS Architectural Patterns Reference

## Module Architecture

### Domain Module Pattern

Every bounded context in the application should map to a NestJS module. A well-structured module contains:

```
order/
├── order.module.ts          # Module definition
├── order.controller.ts      # HTTP layer
├── order.service.ts         # Business logic
├── order.repository.ts      # Data access
├── dto/                     # Data Transfer Objects
│   ├── create-order.dto.ts
│   ├── update-order.dto.ts
│   └── order-response.dto.ts
├── entities/                # Domain entities
│   └── order.entity.ts
├── exceptions/              # Domain-specific exceptions
│   └── order-not-found.exception.ts
├── schemas/                 # Drizzle ORM schemas
│   └── order.schema.ts
├── guards/                  # Module-specific guards
├── interceptors/            # Module-specific interceptors
└── __tests__/               # Co-located tests
    ├── order.controller.spec.ts
    └── order.service.spec.ts
```

### Shared Module Pattern

Cross-cutting concerns belong in a `SharedModule`:

```typescript
@Module({
  providers: [
    LoggerService,
    CacheService,
    PaginationHelper,
  ],
  exports: [
    LoggerService,
    CacheService,
    PaginationHelper,
  ],
})
export class SharedModule {}
```

Import `SharedModule` in any module that needs these utilities.

### Configuration Module

Use `@nestjs/config` with typed configuration:

```typescript
// config/database.config.ts
import { registerAs } from '@nestjs/config';

export default registerAs('database', () => ({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  name: process.env.DB_NAME || 'myapp',
  url: process.env.DATABASE_URL,
}));

// Usage in a provider
@Injectable()
export class DatabaseService {
  constructor(
    @Inject(databaseConfig.KEY)
    private readonly dbConfig: ConfigType<typeof databaseConfig>,
  ) {}
}
```

## Request Lifecycle Deep-Dive

### Execution Order

```
1. Incoming Request
2. Globally-bound middleware
3. Module-bound middleware
4. Global guards
5. Controller guards
6. Route guards
7. Global interceptors (pre-controller)
8. Controller interceptors (pre-controller)
9. Route interceptors (pre-controller)
10. Global pipes
11. Controller pipes
12. Route pipes
13. Route parameter pipes
14. Controller method (route handler)
15. Route interceptors (post-request)
16. Controller interceptors (post-request)
17. Global interceptors (post-request)
18. Exception filters (route → controller → global)
19. Response
```

### Guard Pattern — Authentication

```typescript
@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private readonly jwtService: JwtService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();
    const token = this.extractToken(request);

    if (!token) {
      throw new UnauthorizedException('Missing authentication token');
    }

    try {
      const payload = await this.jwtService.verifyAsync(token);
      request['user'] = payload;
      return true;
    } catch {
      throw new UnauthorizedException('Invalid authentication token');
    }
  }

  private extractToken(request: Request): string | undefined {
    const [type, token] = request.headers.authorization?.split(' ') ?? [];
    return type === 'Bearer' ? token : undefined;
  }
}
```

### Interceptor Pattern — Response Transformation

```typescript
@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, ApiResponse<T>> {
  intercept(context: ExecutionContext, next: CallHandler): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map((data) => ({
        success: true,
        data,
        timestamp: new Date().toISOString(),
      })),
    );
  }
}
```

## Testing Strategy

### Unit Tests

Test services in isolation with mocked dependencies:

```typescript
describe('OrderService', () => {
  let service: OrderService;
  let repository: jest.Mocked<OrderRepository>;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        OrderService,
        {
          provide: OrderRepository,
          useValue: {
            findById: jest.fn(),
            save: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get(OrderService);
    repository = module.get(OrderRepository);
  });

  it('should throw OrderNotFoundException when order not found', async () => {
    repository.findById.mockResolvedValue(null);

    await expect(service.findById('non-existent'))
      .rejects
      .toThrow(OrderNotFoundException);
  });
});
```

### E2E Tests

Test the full HTTP lifecycle:

```typescript
describe('OrderController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const module = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = module.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ transform: true, whitelist: true }));
    await app.init();
  });

  it('POST /orders — should validate input', () => {
    return request(app.getHttpServer())
      .post('/orders')
      .send({ invalidField: true })
      .expect(400);
  });

  afterAll(async () => {
    await app.close();
  });
});
```
