---
globs: "**/*.php"
---
# Rule: PHP Project Structure

## Context
Enforce a consistent, PSR-4 compliant project structure for PHP applications (Laravel, Symfony) to maintain separation of concerns and scalability.

## Guidelines

### Namespace and Directory Layout
Follow PSR-4 autoloading with domain-driven organization:

```
project-root/
├── composer.json
├── config/                      # Framework configuration
├── public/
│   └── index.php                # Application entry point
├── src/                         # Application source (PSR-4 root: App\)
│   ├── Common/                  # Shared utilities
│   │   ├── Exception/
│   │   │   ├── BusinessException.php
│   │   │   └── ExceptionHandler.php
│   │   └── Util/
│   ├── Order/                   # Domain module: Order
│   │   ├── Controller/
│   │   │   └── OrderController.php
│   │   ├── DTO/
│   │   │   ├── OrderRequest.php
│   │   │   └── OrderResponse.php
│   │   ├── Service/
│   │   │   └── OrderService.php
│   │   ├── Repository/
│   │   │   ├── OrderRepositoryInterface.php
│   │   │   └── EloquentOrderRepository.php
│   │   └── Entity/
│   │       ├── Order.php
│   │       └── OrderStatus.php
│   └── User/                    # Domain module: User
│       ├── Controller/
│       ├── Service/
│       ├── Repository/
│       └── Entity/
├── tests/
│   ├── Unit/
│   │   └── Order/
│   │       └── OrderServiceTest.php
│   └── Feature/
│       └── Order/
│           └── OrderControllerTest.php
├── database/
│   └── migrations/
└── resources/
```

### Layer Responsibilities
- **Controller/**: HTTP request handling, input validation, response formatting
- **DTO/**: Data Transfer Objects for request/response shapes
- **Service/**: Business logic, orchestration, transaction management
- **Repository/**: Data access abstraction (interface + implementation)
- **Entity/**: Domain models, Eloquent models, Doctrine entities
- **Exception/**: Custom exception classes and exception handlers

### File Organization Rules
- One class per file, file name must match class name
- Use `declare(strict_types=1)` in every PHP file
- Repository pattern: define interfaces in domain, implement in infrastructure
- Keep controllers thin — delegate all logic to services
- Group related DTOs near their controller or service
- Use Enums (PHP 8.1+) for status fields and fixed option sets

### Test Structure
Mirror the source structure under `tests/`:
```
tests/
├── Unit/
│   └── Order/
│       ├── OrderServiceTest.php
│       └── OrderRepositoryTest.php
└── Feature/
    └── Order/
        └── OrderControllerTest.php
```

## Examples

### ✅ Good
```php
<?php
// src/Order/DTO/OrderResponse.php

declare(strict_types=1);

namespace App\Order\DTO;

final readonly class OrderResponse
{
    public function __construct(
        public int $id,
        public string $status,
        public float $total,
    ) {}
}
```

### ❌ Bad
```php
<?php
// src/Order.php — mixing entity, DTO, and service logic in one file

class Order
{
    // ORM mapping AND business logic AND DTO conversion
    public function toArray() { ... }
    public function process() { ... }
}
```
