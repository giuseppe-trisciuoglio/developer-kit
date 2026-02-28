---
globs: "**/*.ts"
---
# Rule: TypeScript Naming Conventions

## Context
Standardize identifier naming across TypeScript projects to improve readability and maintain consistency.

## Guidelines

### Classes, Interfaces, and Types
- **Classes**: Must use `PascalCase` (e.g., `OrderService`, `UserRepository`)
- **Interfaces**: Must use `PascalCase` without `I` prefix (e.g., `PaymentGateway`, not `IPaymentGateway`)
- **Type aliases**: Must use `PascalCase` (e.g., `OrderStatus`, `ApiResponse<T>`)
- **Enums**: Must use `PascalCase` for type name and `PascalCase` for members (e.g., `OrderStatus.Pending`)
- **Generic type parameters**: Use descriptive single letters or short names (e.g., `T`, `TKey`, `TValue`)

### Functions and Methods
- **Functions**: Must use `camelCase` (e.g., `processOrder()`, `findByEmail()`)
- **Methods**: Must use `camelCase` (e.g., `calculateTotal()`, `getUserName()`)
- **Boolean functions/methods**: Use `is`, `has`, `can`, `should` prefixes (e.g., `isActive()`, `hasPermission()`)
- **Event handlers**: Use `handle` or `on` prefix (e.g., `handleSubmit`, `onClick`)

### Variables and Constants
- **Variables**: Must use `camelCase` (e.g., `orderTotal`, `customerName`)
- **Constants**: Must use `camelCase` for object-level, `UPPER_SNAKE_CASE` for true module-level constants
- **Boolean variables**: Use `is`, `has`, `can`, `should` prefixes (e.g., `isLoading`, `hasError`)
- **Private properties**: Use `#` private fields or `private` modifier without underscore prefix

### Files and Modules
- **File names**: Must use `kebab-case` (e.g., `order-service.ts`, `user-repository.ts`)
- **Test files**: Use `.spec.ts` or `.test.ts` suffix (e.g., `order-service.spec.ts`)
- **Type definition files**: Use `.d.ts` suffix for ambient declarations
- **Barrel exports**: Use `index.ts` for module re-exports

### React/Component Specific
- **Components**: Must use `PascalCase` (e.g., `OrderList`, `UserProfile`)
- **Component files**: Must use `PascalCase` matching the component name (e.g., `OrderList.tsx`)
- **Hooks**: Must use `use` prefix in `camelCase` (e.g., `useAuth`, `useOrderList`)
- **Props types**: Use component name with `Props` suffix (e.g., `OrderListProps`)

## Examples

### ✅ Good
```typescript
// order-service.ts
const MAX_RETRY_COUNT = 3;

interface OrderRepository {
  findById(orderId: string): Promise<Order | null>;
}

class OrderService {
  readonly #orderRepository: OrderRepository;

  constructor(orderRepository: OrderRepository) {
    this.#orderRepository = orderRepository;
  }

  async findById(orderId: string): Promise<Order> { ... }
  isProcessable(order: Order): boolean { ... }
}

// React component
function OrderList({ orders, isLoading }: OrderListProps): JSX.Element { ... }
```

### ❌ Bad
```typescript
// OrderService.ts  — wrong file name (should be kebab-case)
const maxRetryCount = 3;  // Module constant should be UPPER_SNAKE_CASE

interface IOrderRepository { ... }  // No "I" prefix

class order_service {  // Should be PascalCase
  private _repo: any;  // No underscore prefix, no "any"

  public FindById(Id: string) { ... }  // Should be camelCase
}
```
