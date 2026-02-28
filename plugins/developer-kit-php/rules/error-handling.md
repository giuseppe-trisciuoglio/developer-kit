---
globs: "**/*.php"
---
# Rule: PHP Error Handling

## Context
Establish a consistent error handling strategy for PHP applications, ensuring meaningful error reporting, proper exception hierarchies, and clean recovery patterns.

## Guidelines

### Exception Hierarchy
- Create a base `BusinessException` extending `\RuntimeException` for all domain-specific errors
- Create specific exceptions for each error domain (e.g., `OrderNotFoundException`, `PaymentDeclinedException`)
- Include meaningful error messages with relevant context (IDs, parameters)
- Use exception codes for machine-readable error identification

```php
abstract class BusinessException extends \RuntimeException
{
    public function __construct(string $message, int $code = 0, ?\Throwable $previous = null)
    {
        parent::__construct($message, $code, $previous);
    }
}

final class OrderNotFoundException extends BusinessException
{
    public function __construct(int $orderId)
    {
        parent::__construct(
            message: sprintf('Order with ID %d was not found', $orderId),
            code: 404,
        );
    }
}
```

### Global Exception Handling
- Use framework-specific exception handlers (Laravel: `Handler`, Symfony: `EventListener`)
- Return standardized JSON error responses for API endpoints
- Map exceptions to appropriate HTTP status codes:
  - `404 Not Found` — resource not found
  - `400 Bad Request` — validation errors
  - `409 Conflict` — business rule violations
  - `422 Unprocessable Entity` — semantically invalid input
  - `500 Internal Server Error` — unexpected errors only

### Error Response Format
```json
{
  "type": "order_not_found",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order with ID 12345 was not found"
}
```

### Best Practices
- **Never** use `@` error suppression operator
- **Never** catch `\Exception` or `\Throwable` in business logic — only at error boundaries
- **Never** silently swallow exceptions (empty catch blocks)
- Always preserve the previous exception: `throw new AppException('msg', 0, $previous)`
- Use PHP 8.0+ `throw` expression in arrow functions and null coalescing
- Log exceptions with full context using PSR-3 `LoggerInterface`
- Use `finally` for cleanup code that must always execute
- Validate input at the boundary (controller/command) using framework validation

### Validation
- Use framework validation (Laravel Requests, Symfony Constraints) at the API boundary
- Do not throw exceptions for validation — let the framework handle validation errors
- Throw domain exceptions only for business rule violations in the service layer

## Examples

### ✅ Good
```php
<?php

declare(strict_types=1);

final class OrderService
{
    public function __construct(
        private readonly OrderRepositoryInterface $repository,
        private readonly LoggerInterface $logger,
    ) {}

    public function findById(int $orderId): Order
    {
        return $this->repository->find($orderId)
            ?? throw new OrderNotFoundException($orderId);
    }

    public function process(int $orderId): OrderResult
    {
        try {
            $order = $this->findById($orderId);
            $result = $this->paymentGateway->charge($order);
        } catch (PaymentGatewayException $e) {
            $this->logger->error('Payment failed for order {orderId}', [
                'orderId' => $orderId,
                'exception' => $e,
            ]);
            throw new PaymentProcessingException($orderId, previous: $e);
        }

        $this->logger->info('Order {orderId} processed', ['orderId' => $orderId]);

        return $result;
    }
}
```

### ❌ Bad
```php
<?php

class OrderService
{
    public function process($id)
    {
        try {
            $order = $this->repo->find($id);
            $this->pay($order);
        } catch (\Exception $e) {
            // Silent swallow — bug hidden forever
        }
    }

    public function findById($id)
    {
        $order = @$this->repo->find($id);  // Error suppression
        if (!$order) {
            return null;  // Returning null instead of throwing
        }
        return $order;
    }
}
```
