---
globs: "**/*.ts"
---
# Rule: TypeScript Error Handling

## Context
Establish a consistent error handling strategy for TypeScript applications, ensuring meaningful error reporting, proper error classification, and clean recovery patterns.

## Guidelines

### Custom Error Classes
- Create a base `AppError` extending `Error` for all application-specific errors
- Create specific error classes for each error domain (e.g., `OrderNotFoundError`, `ValidationError`)
- Include meaningful error messages and relevant context properties
- Always set `name` property to match the class name

```typescript
abstract class AppError extends Error {
  abstract readonly statusCode: number;

  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = this.constructor.name;
  }
}

class NotFoundError extends AppError {
  readonly statusCode = 404;

  constructor(resource: string, id: string) {
    super(`${resource} with ID '${id}' was not found`);
  }
}

class OrderNotFoundError extends NotFoundError {
  constructor(orderId: string) {
    super('Order', orderId);
  }
}
```

### Result Type Pattern
For expected failures, prefer a Result type over throwing exceptions:

```typescript
type Result<T, E = AppError> =
  | { success: true; data: T }
  | { success: false; error: E };

function ok<T>(data: T): Result<T, never> {
  return { success: true, data };
}

function fail<E>(error: E): Result<never, E> {
  return { success: false, error };
}
```

### Exception Handling Best Practices
- Type `catch` variables as `unknown` and narrow before use
- **Never** silently swallow errors (empty catch blocks)
- Use `try/catch` only at error boundaries (controllers, middleware), not in business logic
- Preserve the error chain: `new AppError('message', { cause: originalError })`
- Log errors with full context using a structured logger

### NestJS Exception Filters
```typescript
@Catch(AppError)
export class AppExceptionFilter implements ExceptionFilter {
  catch(exception: AppError, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    response.status(exception.statusCode).json({
      type: exception.name,
      title: exception.message,
      status: exception.statusCode,
    });
  }
}
```

### Error Response Format
```json
{
  "type": "OrderNotFoundError",
  "title": "Order with ID '12345' was not found",
  "status": 404
}
```

### Validation
- Use class-validator decorators (NestJS) or Zod schemas (React/general) for input validation
- Validate at the boundary (controller/API layer), not deep inside business logic
- Let framework middleware handle validation error formatting

## Examples

### ✅ Good
```typescript
class OrderService {
  async findById(orderId: string): Promise<Order> {
    const order = await this.orderRepository.findById(orderId);

    if (order === null) {
      throw new OrderNotFoundError(orderId);
    }

    return order;
  }

  async processOrder(orderId: string): Promise<Result<OrderResult>> {
    try {
      const order = await this.findById(orderId);
      const result = await this.paymentGateway.charge(order);
      return ok(result);
    } catch (error: unknown) {
      if (error instanceof PaymentGatewayError) {
        this.logger.error('Payment failed', { orderId, error });
        return fail(new PaymentProcessingError(orderId, { cause: error }));
      }
      throw error;
    }
  }
}
```

### ❌ Bad
```typescript
async function processOrder(id: string) {
  try {
    const order = await getOrder(id);
    await charge(order);
  } catch (e) {           // Untyped catch variable
    console.log(e);        // console.log instead of logger
    // swallowed — no re-throw or return
  }
}

function findOrder(id: string) {
  const order = db.get(id);
  if (!order) return null;  // Returning null instead of proper error
}
```
