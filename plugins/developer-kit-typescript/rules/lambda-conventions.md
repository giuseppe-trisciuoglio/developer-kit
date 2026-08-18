---
paths:
  - "**/*.ts"
---
# Rule: Lambda Conventions

## Context
Enforce consistent patterns for AWS Lambda functions built with NestJS and deployed via SAM. Lambda handlers follow a 6-step validation pipeline and integrate with shared server features.

> **Full code examples**: see [references/examples.md](references/examples.md) for the complete
> handler pipeline, environment validation, app module, and SAM template.

## Guidelines

### Lambda Directory Structure

```
apps/lambdas/{domain}/{lambda-name}/
├── src/
│   ├── bootstrap.ts              # Entry point - exports handler
│   ├── handlers/
│   │   ├── index.ts              # Barrel export
│   │   └── {action}-{entity}.handler.ts    # HTTP request handler
│   │   └── {action}-{entity}.handler.spec.ts # Unit tests
│   │   └── {action}-{entity}.handler.integration.spec.ts # Integration tests
│   └── modules/
│       ├── index.ts              # Barrel export
│       ├── app.module.ts         # Root NestJS module
│       └── validate-env.ts       # Environment validation schema
├── template.yaml                 # SAM template
├── samconfig.toml                # SAM deployment config
├── project.json                  # Nx project configuration
├── jest.config.ts                # Jest configuration
├── tsconfig.json                 # TypeScript config
├── events/                       # Test events for local invoke
│   └── {action}-{entity}.json
├── env.json                      # Local environment variables
└── scripts/
    └── local-dev.sh              # Local development script
```

### Naming Conventions

| Element | Pattern | Example |
|---|---|---|
| Project name | `lambda-{domain}-{action}-{entity}` | `lambda-admin-create-tenant` |
| Handler class | `{Action}{Entity}Handler` | `CreateTenantHandler` |
| Handler file | `{action}-{entity}.handler.ts` | `create-tenant.handler.ts` |
| Module file | `app.module.ts` | `app.module.ts` |
| Env validator | `validate-env.ts` | `validate-env.ts` |

### Project Configuration (project.json)

Use `apps/lambdas/admin/create-tenant/project.json` as template:

- **`name`**: `lambda-{domain}-{action}-{entity}`
- **`sourceRoot`**: `apps/lambdas/{domain}/{lambda-name}/src`
- **`tags`**: `["scope:lambda", "type:{domain}"]`
- **`targets`**:
  - `bundle`: esbuild CJS output
  - `test`: Jest unit tests
  - `lint`: ESLint
  - `sam-build`: SAM build
  - `sam-deploy`: SAM deploy
  - `sam-local`: Local invoke with Docker
  - `serve`: SAM local API

### Bootstrap Pattern

```typescript
// src/bootstrap.ts
import 'reflect-metadata';
import { bootstrapLambda } from '@sibill-erp-gateway/server/lambda-core';
import { AppModule } from './modules';
import { CreateTenantHandler } from './handlers';

export const handler = bootstrapLambda(AppModule, CreateTenantHandler);
```

### Handler 6-Step Pipeline

Every handler implements six steps in order inside `handle(...)`:

1. **Validate HTTP method** — `validateHttpMethod(event, ['POST', ...])`; return the method
   error response if the verb is not allowed.
2. **Validate body size** — `validateBodySize(event.body)`; reject oversized payloads.
3. **Parse JSON safely** — `safeJsonParse(event.body)`; never `JSON.parse` directly on
   event input.
4. **Validate with Zod schema** — `.safeParse(...)`; return `validationErrorResponse(issues)`.
5. **Execute business logic** — inject the service and call it with the validated data and `requestId`.
6. **Catch and map errors** — wrap in `try/catch` and return `handleLambdaError(...)`.

See [references/examples.md](references/examples.md#handler-pattern-6-step-validation-pipeline)
for the full implementation.

### Environment Validation

Validate environment variables with a Zod schema in `src/modules/validate-env.ts` and wire
it into `ConfigModule.forRoot({ validate })`. Required variables are explicit; optional ones
use `.optional()`. See [references/examples.md](references/examples.md#environment-validation).

### App Module

The root `app.module.ts` imports `ConfigModule` with the env validator and calls
`MyFeatureModule.forRootAsync({ imports: [ConfigModule], useFactory, inject })` for each
server feature. See [references/examples.md](references/examples.md#app-module-configuration).

### SAM Template

`template.yaml` declares the DynamoDB tables, API Gateway, and the function. The function
uses `Handler: main.handler`, points `CodeUri` at the built dist folder, and attaches
`DynamoDBCrudPolicy` scoped to the function's table. See
[references/examples.md](references/examples.md#sam-template-structure).

### DTO Pattern

**Write DTOs (Zod schemas)** in `libs/shared/{entity}-dto/`:

```typescript
// libs/shared/tenant-dto/src/lib/create-tenant.schema.ts
import { z } from 'zod';

export const CreateTenantSchema = z.object({
  tenantName: z.string().trim().min(1, 'Tenant name is required').max(255),
  vatNumber: z.string().trim().min(1).regex(/^IT\d{11}$/u, 'Invalid VAT format'),
  adminEmail: z.string().trim().toLowerCase().pipe(z.email()),
});

export type CreateTenantInput = z.infer<typeof CreateTenantSchema>;
```

**Read DTOs (Interfaces)** in `libs/shared/{entity}-dto/`:

```typescript
// libs/shared/tenant-dto/src/lib/tenant.dto.ts
export interface TenantDto {
  readonly tenantId: string;
  readonly tenantName: string;
  readonly vatNumber: string;
  readonly adminEmail: string;
  readonly status: TenantStatus;
  readonly createdAt?: string;
}
```

**Enums** in `libs/shared/{entity}-dto/`:

```typescript
// libs/shared/tenant-dto/src/lib/tenant-status.enum.ts
export enum TenantStatus {
  Created = 'created',
  Active = 'active',
  Suspended = 'suspended',
  Deleted = 'deleted',
}
```

## Examples

### ✅ Good

```typescript
// Handler with full 6-step pipeline
export class CreateTenantHandler extends BaseLambdaHandlerService {
  async handle(event: APIGatewayProxyEvent, context: Context) {
    // 1-6: All steps implemented
    const methodError = this.validateHttpMethod(event, ['POST']);
    if (methodError) return methodError;
    // ... rest of pipeline
  }
}
```

### ❌ Bad

```typescript
// Missing validation steps
async handle(event, context) {
  const body = JSON.parse(event.body || '{}'); // No safe parse, no size check
  const result = await this.service.create(body); // Direct call without validation
  return result;
}
```

## Commands

### Development

```bash
# Bundle Lambda
nx bundle lambda-admin-create-tenant

# Run tests
nx test lambda-admin-create-tenant
nx test lambda-admin-create-tenant --testPathPattern=handler.spec.ts

# SAM local (requires DynamoDB Local running)
nx serve lambda-admin-create-tenant
nx sam-local lambda-admin-create-tenant

# Deploy
nx deploy lambda-admin-create-tenant
nx deploy lambda-admin-create-tenant --configuration=staging
nx deploy lambda-admin-create-tenant --configuration=prod
```