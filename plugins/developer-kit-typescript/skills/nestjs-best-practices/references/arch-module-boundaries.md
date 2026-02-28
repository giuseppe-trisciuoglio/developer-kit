# Rule: Module Boundaries and Encapsulation

## Context

NestJS modules define the boundaries of your application's domain features. Proper encapsulation prevents tight coupling and makes the codebase scalable and testable.

## Guidelines

### Module Organization
- Each domain feature must have its own `@Module()` (e.g., `OrderModule`, `UserModule`)
- Only export providers that other modules genuinely need — keep everything else private
- Import only the modules you depend on — avoid importing unrelated modules
- Use a `SharedModule` for cross-cutting utilities (logging, caching, configuration)

### Circular Dependencies
- **Avoid `forwardRef()` by default** — it is a code smell indicating poor module design
- If two modules depend on each other, extract shared logic into a third module
- Only use `forwardRef()` when architectural constraints make extraction impractical
- Document every `forwardRef()` usage with a comment explaining why it's necessary

### Module Registration
- Use `forRoot()` / `forRootAsync()` for global singleton modules (database, config)
- Use `forFeature()` for domain-specific module registration
- Use dynamic modules for configurable providers

## Examples

### ✅ Correct — Proper Module Encapsulation

```typescript
// order/order.module.ts
@Module({
  imports: [PaymentModule, UserModule],
  controllers: [OrderController],
  providers: [OrderService, OrderRepository],
  exports: [OrderService], // Only export what others need
})
export class OrderModule {}

// payment/payment.module.ts
@Module({
  controllers: [PaymentController],
  providers: [PaymentService, PaymentGateway],
  exports: [PaymentService], // Exported for OrderModule to use
})
export class PaymentModule {}
```

### ❌ Incorrect — God Module Anti-Pattern

```typescript
// app.module.ts — everything dumped in root module
@Module({
  controllers: [
    OrderController,
    UserController,
    PaymentController,
    ProductController,
  ],
  providers: [
    OrderService,
    UserService,
    PaymentService,
    ProductService,
    OrderRepository,
    UserRepository,
  ],
})
export class AppModule {} // No encapsulation, all providers are shared
```

### ❌ Incorrect — Unnecessary forwardRef

```typescript
// Instead of this circular dependency:
@Module({
  imports: [forwardRef(() => UserModule)],
  providers: [OrderService],
})
export class OrderModule {}

@Module({
  imports: [forwardRef(() => OrderModule)],
  providers: [UserService],
})
export class UserModule {}

// ✅ Extract shared logic into a third module:
@Module({
  providers: [UserOrderLinkService],
  exports: [UserOrderLinkService],
})
export class UserOrderModule {}
```
