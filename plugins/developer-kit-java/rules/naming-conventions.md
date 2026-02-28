---
globs: "**/*.java"
---
# Rule: Java Naming Conventions

## Context
Standardize identifier naming across Java projects to improve readability and maintain consistency with industry best practices.

## Guidelines

### Classes and Interfaces
- **Classes**: Must use `PascalCase` (e.g., `OrderService`, `UserRepository`)
- **Interfaces**: Must use `PascalCase` without `I` prefix (e.g., `PaymentGateway`, not `IPaymentGateway`)
- **Abstract classes**: Use `PascalCase`, optionally prefixed with `Abstract` (e.g., `AbstractEntityMapper`)
- **Enums**: Must use `PascalCase` for type name, `UPPER_SNAKE_CASE` for enum constants

### Methods and Variables
- **Methods**: Must use `camelCase` starting with a verb (e.g., `processOrder()`, `findByEmail()`)
- **Variables**: Must use `camelCase` (e.g., `orderTotal`, `customerName`)
- **Boolean variables/methods**: Use `is`, `has`, `can`, `should` prefixes (e.g., `isActive`, `hasPermission()`)
- **Constants**: Must use `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`)

### Packages
- Must use lowercase only, no underscores (e.g., `com.company.project.module`)
- Follow domain-driven structure: `com.company.project.module.layer`
- Layers: `web`, `service`, `repository`, `domain`, `config`, `exception`, `dto`

### Test Classes
- Test class name must match the class under test with `Test` suffix (e.g., `OrderServiceTest`)
- Test methods should use descriptive names: `should_ReturnOrder_When_ValidIdProvided()`

## Examples

### ✅ Good
```java
package com.acme.orders.service;

public class OrderService {
    private static final int MAX_RETRY_COUNT = 3;
    private final OrderRepository orderRepository;
    private boolean isProcessing;

    public Order findById(Long orderId) { ... }
    public boolean hasActiveOrders(Long customerId) { ... }
}
```

### ❌ Bad
```java
package com.acme.Orders.Service;

public class order_service {
    private static final int maxRetryCount = 3;
    private final OrderRepository repo;
    private boolean processing;

    public Order GetById(Long id) { ... }
    public boolean activeOrders(Long cid) { ... }
}
```
