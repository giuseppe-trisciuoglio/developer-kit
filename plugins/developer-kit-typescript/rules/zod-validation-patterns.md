---
paths:
  - "**/*.ts"
---

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
Export native TypeScript enums from `*-enum.ts` files. For Zod schemas, use `.enum()` which handles both string unions AND native enums in Zod v4:

```typescript
// tenant-status.enum.ts
export enum TenantStatus {
  Created = 'created',
  Active = 'active',
  Suspended = 'suspended',
  Deleted = 'deleted',
}

// In schema: use z.enum() for Zod-native validation with string literals
status: z.enum(['created', 'active', 'suspended', 'deleted'])

// In Zod v4, z.enum() also accepts native TypeScript enums
// z.nativeEnum() is deprecated - prefer z.enum()
import { TenantStatus } from './tenant-status.enum';
status: z.enum(TenantStatus)
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

### UUID Validation

Zod v4 supports one UUID validation approaches:

```typescript
// Standalone z.uuid() - RFC 9562/4122 compliant
const strictUuidSchema = z.uuid();

strictUuidSchema.parse('550e8400-e29b-41d4-a716-446655440000'); // ✅
```

Use `z.guid()` for permissive UUID-like patterns (any 8-4-4-4-12 hex format).

### Record Schemas (Zod v4 Breaking Change)

Zod v4 **requires both key and value types** explicitly - single-argument usage is removed:

```typescript
// ❌ Zod 3 (deprecated in v4)
z.string().uuid();
z.record(z.string())  // Error: Expected 2-3 arguments, got 1

// ✅ Zod 4 - both key and value types required
z.record(z.string(), z.string())     // Record<string, string>
z.record(z.string(), z.unknown())    // Record<string, unknown>
z.record(z.enum(['a', 'b']), z.number())  // Record<'a'|'b', number>
```

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

### Error Handling (Zod v4)

Zod v4 uses a unified `error` parameter instead of separate `invalid_type_error`/`required_error`:

```typescript
// ❌ Zod 3 style (deprecated in v4)
z.string({ invalid_type_error: 'Must be a string', required_error: 'Required' })

// ✅ Zod 4 style - unified error parameter
z.string({ error: 'Invalid string value' })

// ✅ Zod 4 with error function for dynamic messages
z.string({
  error: (issue) => issue.input === undefined ? 'Required' : 'Invalid'
})
```

### Default Values (Zod v4)

`.default()` in Zod v4 short-circuits for `undefined`. Use `.prefault()` to replicate Zod 3's pre-parse default behavior:

```typescript
// .default() only applies when value is undefined
const schema = z.string().default('fallback');
schema.parse(undefined); // 'fallback'
schema.parse(null);      // Error (null is not undefined)

// Use .prefault() for Zod 3-like behavior
const prefaultSchema = z.string().prefault(() => 'fallback');
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

// UUID validation
const uuidSchema = z.uuid();
const userIdSchema = z.string().uuid();

// Record with key and value types (Zod v4)
const metadataSchema = z.record(z.string(), z.string());
const payloadSchema = z.record(z.string(), z.unknown());

// Enum validation with TypeScript native enum
const statusSchema = z.enum(TenantStatus);  // z.enum() handles native enums in v4
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

// Record with single argument (Zod v4 breaking change)
z.record(z.string())  // Error: Expected 2-3 arguments, got 1

// Native enum with z.nativeEnum() (deprecated in v4)
z.nativeEnum(MyEnum)  // Use z.enum(MyEnum) instead
```

## File Naming

| Type | Naming | Example |
|---|---|---|
| Schema file | `{action}-{entity}.schema.ts` | `create-tenant.schema.ts` |
| Schema const | `{Action}{Entity}Schema` | `CreateTenantSchema` |
| Inferred type | `{Action}{Entity}Input` | `CreateTenantInput` |
| Enum file | `{entity}-status.enum.ts` | `tenant-status.enum.ts` |
| DTO file | `{entity}.dto.ts` | `tenant.dto.ts` |
