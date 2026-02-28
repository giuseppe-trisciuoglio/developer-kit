---
globs: "src/**/*.ts"
---
# Rule: NestJS Architecture

## Context
Enforce NestJS architectural principles: modular design, proper dependency management, core/shared module separation, and circular dependency prevention.

## Guidelines

### Feature Module Organization
- Encapsulate related functionality into self-contained feature modules
- Each feature module owns its controllers, services, entities, DTOs, and tests
- Export only what other modules need via `exports` array
- Import only required modules — avoid importing the entire application

```typescript
// ✅ Self-contained feature module
@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],
})
export class UsersModule {}
```

### Core Module
Place global, application-wide artifacts in a dedicated `src/core/` module:
- **Global exception filters** for centralized error handling
- **Global middleware** for request management (logging, correlation IDs)
- **Guards** for permission and authentication management
- **Interceptors** for response transformation, caching, and timing

```typescript
@Module({
  providers: [
    { provide: APP_FILTER, useClass: AllExceptionsFilter },
    { provide: APP_INTERCEPTOR, useClass: LoggingInterceptor },
    { provide: APP_INTERCEPTOR, useClass: TransformInterceptor },
    { provide: APP_GUARD, useClass: JwtAuthGuard },
  ],
})
export class CoreModule {}
```

### Shared Module
Place cross-module utilities in `src/shared/`:
- Utility functions and helpers
- Shared business logic used by multiple feature modules
- Common DTOs, types, and interfaces
- Custom decorators and validators

### Avoid Circular Dependencies
Circular dependencies are the #1 cause of runtime crashes in NestJS. Never let Module A import Module B while Module B imports Module A.

```typescript
// ❌ Circular: UsersModule ↔ OrdersModule
@Module({ imports: [OrdersModule] })
export class UsersModule {}

@Module({ imports: [UsersModule] })
export class OrdersModule {}
```

**Resolution strategies:**
1. **Extract shared logic** to a third module both can import
2. **Use events** (`EventEmitter2`) for decoupled cross-module communication
3. **Use `forwardRef()`** only as a last resort — it masks design problems

```typescript
// ✅ Option 1: Shared module
@Module({
  providers: [SharedService],
  exports: [SharedService],
})
export class SharedModule {}

// ✅ Option 2: Event-driven communication
@Injectable()
export class UsersService {
  constructor(private eventEmitter: EventEmitter2) {}

  async createUser(data: CreateUserDto): Promise<User> {
    const user = await this.userRepo.save(data);
    this.eventEmitter.emit('user.created', user);
    return user;
  }
}

@Injectable()
export class OrdersService {
  @OnEvent('user.created')
  handleUserCreated(user: User): void {
    // React without direct dependency
  }
}
```

### Module Design Rules
- One module per main domain/route
- One primary controller per module, additional controllers for secondary routes
- One service per entity within the module
- Keep module boundaries clear — never reach into another module's internals
- Prefer composition over inheritance for module capabilities

## Examples

### ✅ Good
```
// Feature-based organization
src/
├── core/                    # Global filters, guards, interceptors
├── shared/                  # Shared utilities and business logic
├── users/                   # Feature module
│   ├── dto/
│   ├── entities/
│   ├── users.controller.ts
│   ├── users.service.ts
│   └── users.module.ts
├── orders/                  # Feature module
│   ├── dto/
│   ├── entities/
│   ├── orders.controller.ts
│   ├── orders.service.ts
│   └── orders.module.ts
└── app.module.ts
```

### ❌ Bad
```
// Technical layer organization (anti-pattern)
src/
├── controllers/
│   ├── users.controller.ts
│   └── orders.controller.ts
├── services/
│   ├── users.service.ts
│   └── orders.service.ts
├── entities/
│   ├── user.entity.ts
│   └── order.entity.ts
└── app.module.ts            // Imports everything directly
```
