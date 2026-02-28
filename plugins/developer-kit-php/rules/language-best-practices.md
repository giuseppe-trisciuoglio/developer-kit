---
globs: "**/*.php"
---
# Rule: PHP Best Practices

## Context
Enforce modern PHP (8.1+) and framework best practices to produce clean, maintainable, and type-safe code.

## Guidelines

### Strict Typing
- **Always** add `declare(strict_types=1)` as the first statement in every PHP file
- Annotate all method parameters, return types, and property types
- Use union types (`string|int`) instead of `mixed` where possible
- Use `void` return type for methods that return nothing
- Use `never` return type for methods that always throw or exit

### Modern PHP Features (8.1+)
- Use **readonly properties** for immutable data (e.g., DTOs, value objects)
- Use **constructor property promotion** to reduce boilerplate
- Use **Enums** for fixed sets of values (status, type, category)
- Use **named arguments** for better readability with multiple optional parameters
- Use **match expressions** instead of `switch` for value mapping
- Use **fibers** or async libraries for concurrent I/O operations
- Use **first-class callable syntax** (`$this->process(...)`) for callbacks
- Mark classes as `final` by default — open for extension only when explicitly intended

### Dependency Injection
- **Always** use constructor injection via type-hinted parameters
- Depend on interfaces, not concrete implementations
- Register services in the DI container, never instantiate with `new` inside business logic
- Use `readonly` for injected dependencies

### Collections and Arrays
- Prefer typed collections or `array<string, mixed>` docblock annotations
- Use `array_map()`, `array_filter()`, `array_reduce()` for transformations
- Consider using Collection libraries (e.g., Laravel Collections, Doctrine Collections)
- Avoid associative arrays for structured data — use DTOs or value objects

### Code Quality
- Keep methods short (max ~20 lines of logic)
- Favor composition over inheritance
- Use meaningful names — avoid abbreviations
- One responsibility per class (Single Responsibility Principle)
- Use value objects for domain concepts (e.g., `Money`, `EmailAddress`)
- Prefer early returns to reduce nesting

## Examples

### ✅ Good
```php
<?php

declare(strict_types=1);

namespace App\Order\Service;

final class OrderService
{
    public function __construct(
        private readonly OrderRepositoryInterface $orderRepository,
        private readonly PaymentGatewayInterface $paymentGateway,
    ) {}

    public function process(int $orderId): OrderResponse
    {
        $order = $this->orderRepository->findOrFail($orderId);

        if (!$order->isProcessable()) {
            throw new OrderNotProcessableException($orderId);
        }

        $result = $this->paymentGateway->charge($order);

        return new OrderResponse(
            id: $order->getId(),
            status: $result->status->value,
            total: $order->getTotal(),
        );
    }
}
```

### ❌ Bad
```php
<?php

namespace App\Service;

class OrderService
{
    private $repo;  // No type hint, no readonly

    public function process($id)  // No type hints
    {
        $repo = new OrderRepository();  // Direct instantiation
        $order = $repo->find($id);
        if ($order) {
            if ($order->status == 'pending') {  // String comparison instead of enum
                // deeply nested logic...
            }
        }
        return $order;
    }
}
```
