---
globs: "**/*.ts"
---
# Rule: TypeScript Best Practices

## Context
Enforce modern TypeScript best practices to produce clean, maintainable, and fully type-safe code.

## Guidelines

### Strict Typing
- **Never** use `any` — use `unknown` for truly unknown types, then narrow with type guards
- Prefer `interface` over `type` for public API contracts and object shapes
- Use `type` for unions, intersections, mapped types, and utility types
- Enable `strict: true` in `tsconfig.json` (includes `strictNullChecks`, `noImplicitAny`, etc.)
- Use `readonly` for properties that should not be reassigned
- Use `as const` for literal type assertions on constant values
- Avoid non-null assertions (`!`) — use proper null checks or `?` optional chaining

### Functions
- Always annotate return types for exported/public functions
- Use `async`/`await` instead of raw Promises with `.then()` chains
- Prefer arrow functions for callbacks and short functions
- Use function declarations for named, hoisted functions
- Use parameter destructuring with type annotations for options objects
- Avoid more than 3 positional parameters — use an options object instead

### Interfaces and Types
- Use `interface` for object shapes that may be extended or implemented
- Use discriminated unions for state management and error handling
- Avoid `enum` — prefer `const` objects with `as const` or string literal unions
- Use generics for reusable, type-safe abstractions

```typescript
// Prefer string literal unions over enums
type OrderStatus = 'pending' | 'processing' | 'completed' | 'cancelled';

// Prefer const objects when you need runtime values
const ORDER_STATUS = {
  Pending: 'pending',
  Processing: 'processing',
  Completed: 'completed',
} as const;
type OrderStatus = (typeof ORDER_STATUS)[keyof typeof ORDER_STATUS];
```

### Error Handling
- Use discriminated unions or Result types for expected error cases
- Use `try/catch` only for truly exceptional situations
- Always type catch variables as `unknown` and narrow before use
- Create custom error classes extending `Error` for domain exceptions

### Imports and Modules
- Use named exports over default exports (better refactoring, IDE support)
- Use path aliases (`@/`) configured in `tsconfig.json` for cleaner imports
- Group imports: external → internal → relative (separated by blank lines)
- Avoid circular dependencies — restructure modules if detected

### Immutability
- Prefer `const` over `let` — never use `var`
- Use `readonly` arrays: `readonly string[]` or `ReadonlyArray<string>`
- Use `Readonly<T>` for immutable object types
- Prefer spread operator for object/array copies over mutation

## Examples

### ✅ Good
```typescript
interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<Order>;
}

type CreateOrderInput = {
  readonly productId: string;
  readonly quantity: number;
};

async function createOrder(
  input: CreateOrderInput,
  repository: OrderRepository,
): Promise<Order> {
  const existingOrder = await repository.findById(input.productId);

  if (existingOrder !== null) {
    throw new DuplicateOrderError(input.productId);
  }

  return repository.save({
    productId: input.productId,
    quantity: input.quantity,
    status: 'pending',
  });
}
```

### ❌ Bad
```typescript
// Using any, no return types, var, default export
export default function createOrder(input: any) {
  var order = input;  // var instead of const
  return fetch('/api/orders', {
    method: 'POST',
    body: JSON.stringify(order),
  }).then((res: any) => res.json());  // .then instead of async/await
}
```
