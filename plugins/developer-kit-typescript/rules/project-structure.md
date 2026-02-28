---
globs: "**/*.ts"
---
# Rule: TypeScript Project Structure

## Context
Enforce a consistent, modular project structure for TypeScript applications (NestJS, React, full-stack) to maintain separation of concerns and scalability.

## Guidelines

### NestJS Backend Structure
Organize by domain module with NestJS conventions:

```
src/
├── main.ts                      # Application bootstrap
├── app.module.ts                # Root module
├── common/                      # Shared utilities
│   ├── decorators/
│   ├── filters/
│   │   └── http-exception.filter.ts
│   ├── guards/
│   ├── interceptors/
│   ├── pipes/
│   └── types/
├── config/                      # Configuration
│   ├── app.config.ts
│   └── database.config.ts
├── order/                       # Domain module: Order
│   ├── order.module.ts
│   ├── order.controller.ts
│   ├── order.service.ts
│   ├── order.repository.ts
│   ├── dto/
│   │   ├── create-order.dto.ts
│   │   └── order-response.dto.ts
│   ├── entities/
│   │   └── order.entity.ts
│   └── __tests__/
│       ├── order.controller.spec.ts
│       └── order.service.spec.ts
└── user/                        # Domain module: User
    ├── user.module.ts
    ├── user.controller.ts
    └── ...
```

### React Frontend Structure
```
src/
├── main.tsx                     # Entry point
├── App.tsx                      # Root component
├── components/                  # Shared UI components
│   ├── ui/                      # Primitive UI (Button, Input, Card)
│   └── layout/                  # Layout components (Header, Sidebar)
├── features/                    # Feature modules
│   ├── orders/
│   │   ├── components/
│   │   │   ├── OrderList.tsx
│   │   │   └── OrderDetail.tsx
│   │   ├── hooks/
│   │   │   └── useOrders.ts
│   │   ├── types/
│   │   │   └── order.types.ts
│   │   └── api/
│   │       └── order.api.ts
│   └── auth/
├── hooks/                       # Global custom hooks
├── lib/                         # Utility functions and configurations
├── types/                       # Global type definitions
└── styles/                      # Global styles
```

### File Organization Rules
- One module/component per file
- Use barrel exports (`index.ts`) to define public API of each module
- Co-locate tests with source files using `__tests__/` directory or `.spec.ts` suffix
- Keep module boundaries clear — import through public barrel exports, not deep paths
- Place shared types in `common/types/` or feature-specific `types/` directories
- Configuration files in `config/` directory, not scattered across modules

### Test Structure
Co-locate tests with source:
```
order/
├── order.service.ts
├── order.controller.ts
└── __tests__/
    ├── order.service.spec.ts
    └── order.controller.spec.ts
```

## Examples

### ✅ Good
```typescript
// src/order/dto/create-order.dto.ts
export class CreateOrderDto {
  readonly productId!: string;
  readonly quantity!: number;
}

// src/order/index.ts (barrel export)
export { OrderModule } from './order.module';
export { CreateOrderDto } from './dto/create-order.dto';
```

### ❌ Bad
```typescript
// src/models/everything.ts — mixing all domain models in one file
export interface Order { ... }
export interface User { ... }
export interface Product { ... }
// All DTOs, entities, types in one file — violates modularity
```
