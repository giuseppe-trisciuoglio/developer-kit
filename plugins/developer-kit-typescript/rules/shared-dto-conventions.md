---
globs: "**/*.dto.ts"
---
# Rule: Shared DTO Conventions

## Context
Enforce consistent Data Transfer Object (DTO) patterns that bridge frontend and backend type safety in full-stack TypeScript monorepos.

## Guidelines

### DTOs as Single Source of Truth
DTOs in `libs/shared/` are the **single source of truth** for data shapes used by both frontend and backend:

- Frontend imports them as TypeScript interfaces/types for API responses
- Backend imports them and adds `class-validator` decorators for input validation
- Both sides use the same enum values for consistency

### Write DTOs — Classes with class-validator
DTOs used for **input validation** (request bodies) MUST be `class` with `class-validator` decorators:

```typescript
// libs/shared/order-dto/src/lib/create-order.dto.ts
import { IsString, IsNumber, IsBoolean, ValidateNested, IsOptional } from 'class-validator';
import { Type } from 'class-transformer';

export class CreateOrderDto {
  @IsString()
  product_id: string;

  @IsNumber()
  quantity: number;

  @IsBoolean()
  is_draft: boolean;

  @IsOptional()
  @Type(() => ShippingAddressDto)
  @ValidateNested()
  shipping_address?: ShippingAddressDto;
}
```

### Read DTOs — Interfaces
DTOs used for **response types** (read-only) MUST be `interface`:

```typescript
// libs/shared/order-dto/src/lib/order.dto.ts
export interface OrderDto {
  order_uuid: string;
  status: OrderStatus;
  total_amount: number;
  customer_name: string;
  created_at: string;
}
```

### Generic Response Types — Classes
Reusable container DTOs use `class`:

```typescript
export class PaginatedResponseDto<T> {
  count: number;
  data: Array<T>;
}
```

### Enum Patterns — String Enums with Domain Values
Enums use **string values** (never numeric). Enum values match their domain semantics:

```typescript
// Status enums
export enum OrderStatus {
  pending = 'pending',
  processing = 'processing',
  shipped = 'shipped',
  delivered = 'delivered',
  cancelled = 'cancelled',
}

// Role enums — code/acronym values
export enum UserRoleEnum {
  superadmin = 'IT',
  manager = 'MGR',
  operator = 'OPR',
  external = 'EXT',
}

// Type enums
export enum OrderType {
  standard = 'standard',
  express = 'express',
  bulk = 'bulk',
}
```

### DTO File Organization
Place DTOs in shared libraries, grouped by domain:

```
libs/shared/
├── order-dto/
│   └── src/
│       ├── index.ts                    # Barrel export
│       └── lib/
│           ├── order.dto.ts            # Read DTO (interface)
│           ├── create-order.dto.ts     # Write DTO (class)
│           ├── update-order.dto.ts     # Write DTO (class)
│           └── order-filters.dto.ts    # Query params DTO
├── user-dto/
│   └── src/
│       ├── index.ts
│       └── lib/
│           ├── user.dto.ts
│           └── safe-user.dto.ts        # Sanitized user (no sensitive fields)
└── global-types/
    └── src/
        ├── index.ts
        ├── order-status.enum.ts
        ├── user-role.enum.ts
        └── paginated-response.dto.ts
```

### DTO Naming Convention

| Type | Naming | Example |
|---|---|---|
| Read DTO | `{Entity}Dto` | `OrderDto`, `UserDto` |
| Create DTO | `{Entity}CreateDto` or `Create{Entity}Dto` | `OrderCreateDto` |
| Update DTO | `{Entity}UpdateDto` or `Update{Entity}Dto` | `OrderUpdateDto` |
| Sanitized DTO | `Safe{Entity}Dto` | `SafeUserDto` |
| Filter/Query DTO | `{Entity}FiltersDto` | `OrderFiltersDto` |
| Paginated response | `PaginatedResponseDto<T>` | `PaginatedResponseDto<OrderDto>` |

### Cross-Stack Usage

```typescript
// Backend controller — uses class DTO for input, interface DTO for output
@Post('/orders')
async createOrder(
  @Body() body: CreateOrderDto,    // class with class-validator
): Promise<OrderDto> {             // interface for response type
  return this.orderService.create(body);
}

// Frontend hook — uses interface DTO for type safety
const result = useSwr<PaginatedResponseDto<OrderDto>>(
  '/api/orders',
  fetcher
);
```

### Role and Permission Utilities
Export shared utility functions alongside role enums:

```typescript
// libs/shared/role-dto/src/lib/role-utils.ts
export const InternalRoles = [UserRoleEnum.superadmin, UserRoleEnum.manager, UserRoleEnum.operator];
export const ExternalRoles = [UserRoleEnum.external];

export function canCreateOrders(role: UserRoleEnum): boolean {
  return InternalRoles.includes(role);
}

export function canViewAllOrders(role: UserRoleEnum): boolean {
  return [UserRoleEnum.superadmin, UserRoleEnum.manager].includes(role);
}
```

## Examples

### ✅ Good
```typescript
// Shared enum — same file imported by both FE and BE
export enum OrderStatus {
  pending = 'pending',
  shipped = 'shipped',
}

// Frontend usage
const { data } = useSwr<OrderDto>(`/api/orders/${id}`, fetcher);
if (data?.status === OrderStatus.shipped) { /* ... */ }

// Backend usage
@UseGuards(AuthGuard)
@Get('/orders/:id')
async getOrder(@Param('id', ParseUUIDPipe) id: string): Promise<OrderDto> {
  return this.orderService.findById(id);
}
```

### ❌ Bad
```typescript
// Duplicating types between FE and BE
// frontend/types/order.ts
interface Order { id: string; status: string; }

// backend/dto/order.dto.ts
class OrderDto { id: string; status: string; }
// These will inevitably drift out of sync!

// Using 'any' instead of shared DTOs
const response = await fetch('/api/orders');
const data: any = await response.json();

// Numeric enum values
export enum OrderStatus {
  Pending = 0,    // Don't use numbers — use string values
  Shipped = 1,
}
```
