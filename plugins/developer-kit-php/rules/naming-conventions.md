---
globs: "**/*.php"
---
# Rule: PHP Naming Conventions

## Context
Standardize identifier naming across PHP projects following PSR-12 conventions to ensure readability and consistency.

## Guidelines

### Classes, Interfaces, and Traits
- **Classes**: Must use `PascalCase` (e.g., `OrderService`, `UserRepository`)
- **Interfaces**: Must use `PascalCase` with `Interface` suffix (e.g., `PaymentGatewayInterface`)
- **Traits**: Must use `PascalCase` with `Trait` suffix (e.g., `TimestampableTrait`)
- **Abstract classes**: Must use `PascalCase` with `Abstract` prefix (e.g., `AbstractController`)
- **Enums**: Must use `PascalCase` for type name and `PascalCase` for backed enum cases

### Methods and Functions
- **Methods**: Must use `camelCase` (e.g., `processOrder()`, `findByEmail()`)
- **Functions**: Must use `snake_case` for global/helper functions (e.g., `array_flatten()`)
- **Boolean methods**: Use `is`, `has`, `can`, `should` prefixes (e.g., `isActive()`, `hasPermission()`)
- **Static factory methods**: Use descriptive names (e.g., `Order::fromRequest()`, `Money::ofAmount()`)

### Properties and Variables
- **Properties**: Must use `camelCase` (e.g., `$orderTotal`, `$customerName`)
- **Variables**: Must use `camelCase` (e.g., `$maxRetryCount`, `$isValid`)
- **Constants**: Must use `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)
- **Boolean properties**: Use `is`, `has`, `can` prefixes (e.g., `$isActive`, `$hasExpired`)

### Namespaces
- Must follow PSR-4 autoloading standards
- Must use `PascalCase` for each segment (e.g., `App\Order\Service`)
- Must match the directory structure exactly
- Vendor namespace first, then module, then layer

### Files
- One class per file
- File name must match the class name exactly (e.g., `OrderService.php`)

## Examples

### ✅ Good
```php
<?php

declare(strict_types=1);

namespace App\Order\Service;

final class OrderService
{
    private const MAX_RETRY_COUNT = 3;

    public function __construct(
        private readonly OrderRepositoryInterface $orderRepository,
    ) {}

    public function findById(int $orderId): OrderResponse
    {
        // ...
    }

    public function isProcessable(Order $order): bool
    {
        // ...
    }
}
```

### ❌ Bad
```php
<?php

namespace app\order;  // Lowercase namespace

class order_service  // Should be PascalCase
{
    private $order_repo;  // Should be camelCase
    const max_retry = 3;  // Should be UPPER_SNAKE_CASE

    public function FindById($Id)  // Should be camelCase
    {
        // ...
    }
}
```
