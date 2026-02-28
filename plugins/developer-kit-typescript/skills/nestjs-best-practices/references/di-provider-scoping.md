# Rule: Dependency Injection and Provider Scoping

## Context

NestJS provides three injection scopes (`DEFAULT`, `REQUEST`, `TRANSIENT`) that control provider lifecycle and instance sharing. Choosing the wrong scope leads to memory leaks, shared state bugs, or unnecessary overhead.

## Guidelines

### Scope Selection
- **`DEFAULT` (Singleton)**: Use for stateless services, repositories, and utilities — the vast majority of providers
- **`REQUEST`**: Use only when the provider needs request-specific data (e.g., tenant context, authenticated user)
- **`TRANSIENT`**: Use when each consumer needs its own isolated instance (e.g., per-consumer loggers, stateful builders)

### Scope Propagation
- A `REQUEST`-scoped provider forces all its dependents to also become request-scoped
- Minimize `REQUEST` scope usage to avoid cascading performance impact
- Use `@Inject(REQUEST)` to access the request object in request-scoped providers

### Injection Patterns
- Always use **constructor injection** — never property injection with `@Inject()` on class fields
- Use `@Injectable()` on every provider class
- Use `@Inject('TOKEN')` for custom provider tokens
- Use `@Optional()` for providers that may not be available

### Custom Providers
- Use `useClass` to swap implementations (e.g., testing mocks)
- Use `useValue` for constants and configuration objects
- Use `useFactory` for providers requiring async initialization or complex setup
- Use `useExisting` to alias an existing provider under a new token

## Examples

### ✅ Correct — Singleton (DEFAULT) Scope

```typescript
@Injectable() // DEFAULT scope — singleton, shared across the app
export class OrderService {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly paymentService: PaymentService,
  ) {}

  async createOrder(dto: CreateOrderDto): Promise<Order> {
    return this.orderRepository.save(dto);
  }
}
```

### ✅ Correct — REQUEST Scope with Justification

```typescript
// Only use REQUEST scope when you need per-request state
@Injectable({ scope: Scope.REQUEST })
export class TenantService {
  constructor(@Inject(REQUEST) private readonly request: Request) {}

  getTenantId(): string {
    return this.request.headers['x-tenant-id'] as string;
  }
}
```

### ✅ Correct — Custom Factory Provider

```typescript
// Async factory for providers needing initialization
@Module({
  providers: [
    {
      provide: 'DATABASE_CONNECTION',
      useFactory: async (configService: ConfigService) => {
        const dbUrl = configService.get<string>('DATABASE_URL');
        return drizzle(dbUrl);
      },
      inject: [ConfigService],
    },
  ],
  exports: ['DATABASE_CONNECTION'],
})
export class DatabaseModule {}
```

### ❌ Incorrect — Unnecessary REQUEST Scope

```typescript
// This service has no request-specific state — should be DEFAULT
@Injectable({ scope: Scope.REQUEST }) // Wrong: causes performance overhead
export class MathService {
  add(a: number, b: number): number {
    return a + b;
  }
}
```

### ❌ Incorrect — Property Injection

```typescript
@Injectable()
export class OrderService {
  @Inject() // Wrong: use constructor injection instead
  private orderRepository: OrderRepository;
}
```

### ✅ Correct — Constructor Injection

```typescript
@Injectable()
export class OrderService {
  constructor(
    private readonly orderRepository: OrderRepository,
  ) {}
}
```
