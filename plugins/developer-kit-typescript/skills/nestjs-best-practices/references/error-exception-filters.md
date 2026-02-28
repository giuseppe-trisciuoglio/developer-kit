# Rule: Error Handling and Exception Filters

## Context

NestJS provides a built-in exception layer that processes unhandled exceptions. Standardizing error handling ensures consistent API responses and proper error classification.

## Guidelines

### Exception Hierarchy
- Create a base `AppException` extending `HttpException` for all domain errors
- Create specific exception classes per domain (e.g., `OrderNotFoundException`, `InsufficientStockException`)
- Include meaningful error messages and relevant context
- Always set the appropriate HTTP status code

### Exception Filters
- Implement a global `ExceptionFilter` to catch all `AppException` instances
- Return a consistent error response format across all endpoints
- Log exceptions with structured context (request ID, user, endpoint)
- Handle unknown exceptions with a generic 500 response — never expose internal details

### Error Response Format
Use a consistent structure for all error responses:

```json
{
  "type": "OrderNotFoundException",
  "title": "Order with ID '12345' was not found",
  "status": 404,
  "timestamp": "2025-01-15T10:30:00Z",
  "path": "/api/orders/12345"
}
```

### Best Practices
- Throw exceptions from services — let the exception filter handle formatting
- Use `try/catch` only at error boundaries (controllers, middleware), not in services
- Preserve the error chain with `{ cause: originalError }` option
- Never silently swallow exceptions (empty catch blocks)
- Use the Result pattern for expected business logic failures that aren't exceptional

## Examples

### ✅ Correct — Domain Exception Hierarchy

```typescript
// common/exceptions/app.exception.ts
export abstract class AppException extends HttpException {
  constructor(
    message: string,
    status: HttpStatus,
    options?: HttpExceptionOptions,
  ) {
    super(message, status, options);
  }
}

// order/exceptions/order-not-found.exception.ts
export class OrderNotFoundException extends AppException {
  constructor(orderId: string) {
    super(
      `Order with ID '${orderId}' was not found`,
      HttpStatus.NOT_FOUND,
    );
  }
}

// order/exceptions/insufficient-stock.exception.ts
export class InsufficientStockException extends AppException {
  constructor(productId: string) {
    super(
      `Insufficient stock for product '${productId}'`,
      HttpStatus.CONFLICT,
    );
  }
}
```

### ✅ Correct — Global Exception Filter

```typescript
@Catch(AppException)
export class AppExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(AppExceptionFilter.name);

  catch(exception: AppException, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();
    const status = exception.getStatus();

    this.logger.error(exception.message, exception.stack);

    response.status(status).json({
      type: exception.constructor.name,
      title: exception.message,
      status,
      timestamp: new Date().toISOString(),
      path: request.url,
    });
  }
}
```

### ✅ Correct — Service Throwing Domain Exceptions

```typescript
@Injectable()
export class OrderService {
  constructor(private readonly orderRepository: OrderRepository) {}

  async findById(orderId: string): Promise<Order> {
    const order = await this.orderRepository.findById(orderId);

    if (order === null) {
      throw new OrderNotFoundException(orderId);
    }

    return order;
  }
}
```

### ❌ Incorrect — Raw HttpException in Service

```typescript
@Injectable()
export class OrderService {
  async findById(orderId: string): Promise<Order> {
    const order = await this.orderRepository.findById(orderId);

    if (!order) {
      // Wrong: use domain-specific exception, not raw HttpException
      throw new HttpException('Not found', 404);
    }

    return order;
  }
}
```

### ❌ Incorrect — Error Handling in Controller

```typescript
@Controller('orders')
export class OrderController {
  @Get(':id')
  async findById(@Param('id') id: string) {
    try {
      return await this.orderService.findById(id);
    } catch (error) {
      // Wrong: don't handle errors in controllers — let exception filters do it
      console.log(error);
      return { error: 'Something went wrong' };
    }
  }
}

// ✅ Correct: let the exception propagate to the filter
@Controller('orders')
export class OrderController {
  @Get(':id')
  async findById(@Param('id') id: string): Promise<Order> {
    return this.orderService.findById(id);
  }
}
```
