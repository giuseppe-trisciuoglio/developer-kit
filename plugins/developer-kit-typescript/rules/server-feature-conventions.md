---
paths:
  - "**/*.ts"
---
# Rule: Server Feature Conventions

## Context
Enforce consistent patterns for server-side feature libraries in `libs/server/`. Features encapsulate domain logic with DynamoDB repositories, services, and NestJS modules following the forRootAsync pattern.

> **Full code examples**: see [references/examples.md](references/examples.md) for the complete
> module, service, DynamoDB repository, and counter util implementations.

## Guidelines

### Feature Library Structure

```
libs/server/{feature-name}/
├── src/
│   ├── index.ts                         # Barrel export
│   └── lib/
│       ├── {feature-name}.module.ts    # Root module with forRoot/forRootAsync
│       ├── {feature-name}-options.ts   # Options interface + injection token
│       ├── tokens.ts                    # All injection tokens
│       ├── controllers/
│       │   ├── index.ts
│       │   └── {resource}.controller.ts
│       ├── services/
│       │   ├── index.ts
│       │   ├── {action}-{entity}.service.ts
│       │   ├── {action}-{entity}.service.spec.ts
│       │   └── index.ts
│       ├── repositories/
│       │   ├── index.ts
│       │   ├── {entity}.repository.ts    # Interface
│       │   ├── dynamodb-{entity}.repository.ts
│       │   └── dynamodb-{entity}.repository.spec.ts
│       ├── exceptions/
│       │   ├── index.ts
│       │   ├── {domain}-not-found.exception.ts
│       │   └── {domain}-already-exists.exception.ts
│       └── utils/
│           ├── index.ts
│           ├── counter.util.ts
│           └── counter.util.spec.ts
├── jest.config.ts
└── tsconfig.json
```

### Naming Conventions

| Element | Pattern | Example |
|---|---|---|
| Feature name | `{entity}-feature` | `tenant-feature` |
| Module | `{Feature}Module` | `TenantFeatureModule` |
| Service | `{Action}{Entity}Service` | `CreateTenantService` |
| Repository | `{Entity}Repository` / `DynamoDb` | `Tenant{Entity}RepositoryRepository` / `DynamoDbTenantRepository` |
| Options | `{Feature}Options` | `TenantFeatureOptions` |
| Token | `{SERVICE_NAME}_TOKEN` | `CREATE_TENANT_SERVICE` |

### Module Pattern — forRootAsync

Expose `forRoot(options)` and `forRootAsync({ imports, useFactory, inject })` from the
feature module. Both share a private `createProviders(optionsProvider)` helper that wires
the repository, DynamoDB document client, and service providers. Configuration is injected
via the `MY_FEATURE_OPTIONS` token; service is exported via `MY_SERVICE`. Always keep the
module free of hardcoded configuration — options come from the consumer. See
[references/examples.md](references/examples.md#module-pattern--forrootasync).

### Options Interface

```typescript
// src/lib/my-feature-options.ts
export interface MyFeatureOptions {
  tableName: string;
  countersTableName?: string;
  region: string;
  endpoint?: string;
}
```

### Injection Tokens

```typescript
// src/lib/tokens.ts
import type { InjectionToken } from '@nestjs/common';

export const MY_FEATURE_OPTIONS: InjectionToken = 'MY_FEATURE_OPTIONS';
export const MY_SERVICE = 'MY_SERVICE';
export const MY_REPOSITORY = 'MY_REPOSITORY';
```

### Service Pattern

Services are `@Injectable()`, receive the repository via `@Inject(MY_REPOSITORY)`, and
encode business rules such as uniqueness checks before delegating persistence. They throw
domain exceptions rather than returning error values. See
[references/examples.md](references/examples.md#service-pattern).

### Repository Interface

```typescript
// src/lib/repositories/tenant.repository.ts
import type { CreateTenantInput } from '@sibill-erp-gateway/shared/tenant-dto';
import type { TenantDto } from '@sibill-erp-gateway/shared/tenant-dto';

export interface TenantRepository {
  create(input: CreateTenantInput, requestId: string): Promise<TenantDto>;
  findById(tenantId: string): Promise<TenantDto | null>;
  findByVatNumber(vatNumber: string): Promise<TenantDto | null>;
  findAll(cursor?: string, limit?: number): Promise<{ data: TenantDto[]; nextCursor?: string }>;
}
```

### DynamoDB Repository Implementation

Implement the repository interface in a `DynamoDb*` class using `@aws-sdk/lib-dynamodb`
(`PutCommand`, `GetCommand`, `QueryCommand`) on the injected `DYNAMODB_CLIENT` document
client. Key-value lookups use `GetCommand`; secondary indexes use `QueryCommand`. See
[references/examples.md](references/examples.md#dynamodb-repository-implementation).

### Custom Exceptions

```typescript
// src/lib/exceptions/tenant-already-exists.exception.ts
export class TenantAlreadyExistsException extends Error {
  constructor(vatNumber: string) {
    super(`Tenant with VAT number ${vatNumber} already exists`);
    this.name = 'TenantAlreadyExistsException';
  }
}
```

### Counter Utility Pattern

Atomic counters use a single `UpdateCommand` on the counters table with
`SET #count = if_not_exists(#count, :zero) + :inc`. See
[references/examples.md](references/examples.md#counter-utility-pattern).

### Barrel Exports

```typescript
// src/lib/services/index.ts
export * from './create-tenant.service';
```

```typescript
// src/lib/repositories/index.ts
export * from './tenant.repository';
export * from './dynamodb-tenant.repository';
```

```typescript
// src/index.ts
export * from './lib/tenant-feature.module';
export * from './lib/services';
export * from './lib/repositories';
export * from './lib/exceptions';
export { CreateTenantService, CREATE_TENANT_SERVICE } from './lib/services';
```

## Examples

### ✅ Good

```typescript
// Feature with forRootAsync for dynamic config
MyFeatureModule.forRootAsync({
  imports: [ConfigModule],
  useFactory: (config: ConfigService) => ({
    tableName: config.get<string>('MY_TABLE')!,
    region: config.get<string>('AWS_REGION') || 'eu-central-1',
  }),
  inject: [ConfigService],
})
```

### ❌ Bad

```typescript
// Hardcoded table name in module
@Module({
  providers: [
    {
      provide: MY_REPOSITORY,
      useFactory: () => new DynamoDbRepository('hardcoded-table'),
    },
  ],
})
export class MyFeatureModule {}

// Direct AWS SDK without abstraction
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
const client = new DynamoDBClient({ region: 'eu-central-1' });
```

## Integration with Lambda Handlers

```typescript
// In Lambda handler
import {
  CREATE_TENANT_SERVICE,
  CreateTenantService,
} from '@sibill-erp-gateway/server/tenant-feature';

@Injectable()
export class CreateTenantHandler extends BaseLambdaHandlerService {
  constructor(
    @Inject(CREATE_TENANT_SERVICE)
    private readonly createTenantService: CreateTenantService,
  ) {
    super();
  }

  async handle(event, context) {
    const result = await this.createTenantService.execute(validatedInput, context.awsRequestId);
    return successResponse(HttpStatus.CREATED, result);
  }
}
```