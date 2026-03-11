# Rule: Zod 4 Validation Patterns

## Context
Enforce consistent validation patterns using Zod v4 for input DTOs in `libs/shared/{domain}-dto/`. Zod schemas provide type-safe runtime validation with clean TypeScript inference.

## Guidelines

### Schema File Organization
- Place Zod schemas in `libs/shared/{domain}-dto/src/lib/{action}-{entity}.schema.ts`
- Export both the schema (`const`) and the inferred type (`type`)
- Use descriptive schema names: `{Action}{Entity}Schema` (e.g., `CreateTenantSchema`)

```typescript
// libs/shared/tenant-dto/src/lib/create-tenant.schema.ts
import { z } from 'zod';

export const CreateTenantSchema = z.object({
  tenantName: z.string().trim().min(1).max(255),
  adminEmail: z.string().trim().toLowerCase().pipe(z.email()),
});

export type CreateTenantInput = z.infer<typeof CreateTenantSchema>;
```

### String Validation Chain
Always apply transformations **before** validations. The correct order:
1. `.string()` — base type
2. `.trim()` — remove whitespace
3. `.toLowerCase()` / `.toUpperCase()` — normalize case if applicable
4. `.pipe()` — complex transformations (email, UUID parsing)
5. `.min()`, `.max()`, `.regex()` — validations
6. Custom error messages as last parameter

```typescript
// ✅ Correct order
z.string()
  .trim()
  .toLowerCase()
  .pipe(z.email('Invalid email format'))
  .max(254, 'Email must be at most 254 characters')

// ❌ Wrong: validations before trim
z.string().min(1).trim()  // trim happens after min check
```

### Required Fields
Use `.min(1, 'message')` for required non-empty strings:

```typescript
tenantName: z
  .string()
  .trim()
  .min(1, 'Tenant name is required')
  .max(255, 'Tenant name must be at most 255 characters')
```

### Email Validation
Use `.pipe(z.email())` with trim and lowercase:

```typescript
email: z
  .string()
  .trim()
  .toLowerCase()
  .max(254, 'Email must be at most 254 characters')
  .pipe(z.email('Invalid email format'))
```

### Regex Patterns
- Define regex constants at module level with descriptive names
- Use `u` flag for Unicode patterns
- Provide clear error messages showing expected format

```typescript
const SUPPORTED_VAT_REGEX = /^IT\d{11}$/u;

vatNumber: z
  .string()
  .trim()
  .min(1, 'VAT number is required')
  .max(14, 'VAT number must be IT followed by 11 digits')
  .regex(SUPPORTED_VAT_REGEX, 'VAT number must be in format IT followed by 11 digits (e.g., IT12345678901)')
```

### Enum Validation with Zod
Export native TypeScript enums from `*-enum.ts` files. For Zod schemas, use `.enum()` or literal unions:

```typescript
// tenant-status.enum.ts
export enum TenantStatus {
  Created = 'created',
  Active = 'active',
  Suspended = 'suspended',
  Deleted = 'deleted',
}

// In schema: use z.enum() for Zod-native validation
status: z.enum(['created', 'active', 'suspended', 'deleted'])

// Or import enum values
import { TenantStatus } from './tenant-status.enum';
status: z.nativeEnum(TenantStatus)
```

### Type Inference
Always export the inferred type using `z.infer`:

```typescript
export const CreateTenantSchema = z.object({ /* ... */ });
export type CreateTenantInput = z.infer<typeof CreateTenantSchema>;
```

### Optional Fields
Use `.optional()` for nullable fields:

```typescript
description: z
  .string()
  .trim()
  .max(1000)
  .optional(),
```

### Barrel Export Pattern
Export schemas and types from the library index:

```typescript
// src/index.ts
export { CreateTenantSchema } from './lib/create-tenant.schema';
export type { CreateTenantInput } from './lib/create-tenant.schema';
```

### Usage in Lambda Handlers
Use `.safeParse()` for validation with error handling:

```typescript
import { CreateTenantSchema, type CreateTenantInput } from '@sibill-erp-gateway/shared/tenant-dto';

const validationResult = CreateTenantSchema.safeParse(parseResult.data);
if (!validationResult.success) {
  return this.validationErrorResponse(validationResult.error.issues, requestId);
}
// validationResult.data is typed as CreateTenantInput
```

## Zod 4 Specific Patterns

### .pipe() for Transformations
Zod 4 uses `.pipe()` for sequential transformations:

```typescript
// Transform and validate email
z.string()
  .trim()
  .toLowerCase()
  .pipe(z.email())  // pipe creates new zod schema

// Custom transformation with validation
z.string()
  .transform(val => val.toUpperCase())
  .pipe(z.enum(['VALUE1', 'VALUE2']))
```

### Refine with Custom Validation
Use `.refine()` for business logic validation:

```typescript
vatNumber: z
  .string()
  .trim()
  .min(1)
  .refine(
    (val) => validateVatChecksum(val),
    { message: 'VAT checksum validation failed' }
  )
```

## Examples

### ✅ Good
```typescript
export const CreateTenantSchema = z.object({
  tenantName: z
    .string()
    .trim()
    .min(1, 'Tenant name is required')
    .max(255, 'Tenant name must be at most 255 characters')
    .regex(/^[a-zA-Z0-9_\-\s]+$/u, 'Tenant name contains invalid characters'),
  vatNumber: z
    .string()
    .trim()
    .min(1, 'VAT number is required')
    .regex(SUPPORTED_VAT_REGEX, 'Invalid VAT format'),
  adminEmail: z
    .string()
    .trim()
    .toLowerCase()
    .max(254)
    .pipe(z.email('Invalid email format')),
});

export type CreateTenantInput = z.infer<typeof CreateTenantSchema>;
```

### ❌ Bad
```typescript
// No trim before validation — accepts "  value  "
z.string().min(1).max(255)

// No lowercase for email — case-sensitive comparison
z.string().email()

// Missing error messages — generic Zod errors
z.string().min(1).max(255).regex(/^[a-z]+$/)

// Missing type export
export const schema = z.object({ name: z.string() });
// No: export type SchemaInput = z.infer<typeof schema>;

// Regex without unicode flag
z.string().regex(/^[a-z]+$/)  // Should be /^[a-z]+$/u
```

## File Naming

| Type | Naming | Example |
|---|---|---|
| Schema file | `{action}-{entity}.schema.ts` | `create-tenant.schema.ts` |
| Schema const | `{Action}{Entity}Schema` | `CreateTenantSchema` |
| Inferred type | `{Action}{Entity}Input` | `CreateTenantInput` |
| Enum file | `{entity}-status.enum.ts` | `tenant-status.enum.ts` |
| DTO file | `{entity}.dto.ts` | `tenant.dto.ts` |
