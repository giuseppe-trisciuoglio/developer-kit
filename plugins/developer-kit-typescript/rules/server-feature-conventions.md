---
paths:
  - "**/*.ts"
---
# Rule: Server Feature Conventions

## Context
Enforce consistent patterns for server-side feature libraries in `libs/server/`. Features encapsulate domain logic with DynamoDB repositories, services, and NestJS modules following the forRootAsync pattern.

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

```typescript
// src/lib/tenant-feature.module.ts
import {
  type DynamicModule,
  type InjectionToken,
  Module,
  type OptionalFactoryDependency,
  type Provider,
} from '@nestjs/common';
import type { ModuleMetadata } from '@nestjs/common';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { MY_FEATURE_OPTIONS, MY_SERVICE, MY_REPOSITORY } from './tokens';
import { DYNAMODB_CLIENT } from '@sibill-erp-gateway/server/dynamodb-utils';
import type { MyFeatureOptions } from './my-feature-options';
import { MyService } from './services';
import { MyRepository } from './repositories';
import { createLambdaOptimizedConfig } from '@sibill-erp-gateway/server/dynamodb-utils';

@Module({})
export class MyFeatureModule {
  private static createProviders(optionsProvider: Provider): Omit<DynamicModule, 'module'> {
    const repositoryProvider: Provider = {
      provide: MY_REPOSITORY,
      useClass: DynamoDbMyRepository,
    };

    const dynamoDbClientProvider: Provider = {
      provide: DYNAMODB_CLIENT,
      useFactory: (options: MyFeatureOptions) => {
        const dynamoClientConfig = createLambdaOptimizedConfig({
          region: options.region,
          endpoint: options.endpoint,
        });
        const client = new DynamoDBClient(dynamoClientConfig);
        return DynamoDBDocumentClient.from(client, {
          marshallOptions: {
            convertEmptyValues: false,
            removeUndefinedValues: true,
            convertClassInstanceToMap: true,
          },
          unmarshallOptions: {
            wrapNumbers: false,
          },
        });
      },
      inject: [MY_FEATURE_OPTIONS],
    };

    const serviceProvider: Provider = {
      provide: MY_SERVICE,
      useClass: MyService,
    };

    return {
      providers: [optionsProvider, repositoryProvider, dynamoDbClientProvider, serviceProvider],
      exports: [MY_SERVICE],
    };
  }

  static forRoot(options: MyFeatureOptions): DynamicModule {
    return {
      module: MyFeatureModule,
      providers: [{ provide: MY_FEATURE_OPTIONS, useValue: options }],
      ...MyFeatureModule.createProviders({ provide: MY_FEATURE_OPTIONS, useValue: options }),
    };
  }

  static forRootAsync<T extends Array<unknown> = []>(options: {
    imports?: ModuleMetadata['imports'];
    useFactory: (...args: T) => MyFeatureOptions | Promise<MyFeatureOptions>;
    inject?: Array<InjectionToken | OptionalFactoryDependency>;
  }): DynamicModule {
    const optionsProvider: Provider = {
      provide: MY_FEATURE_OPTIONS,
      useFactory: options.useFactory,
      inject: options.inject || [],
    };

    return {
      module: MyFeatureModule,
      imports: options.imports,
      ...MyFeatureModule.createProviders(optionsProvider),
    };
  }
}
```

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

```typescript
// src/lib/services/create-tenant.service.ts
import { Inject, Injectable, Logger } from '@nestjs/common';
import type { TenantRepository } from '../repositories';
import { MY_REPOSITORY } from '../tokens';
import type { CreateTenantInput } from '@sibill-erp-gateway/shared/tenant-dto';
import type { TenantDto } from '@sibill-erp-gateway/shared/tenant-dto';

@Injectable()
export class CreateTenantService {
  private readonly logger = new Logger(CreateTenantService.name);

  constructor(
    @Inject(MY_REPOSITORY)
    private readonly tenantRepository: TenantRepository,
  ) {}

  async execute(input: CreateTenantInput, requestId: string): Promise<TenantDto> {
    this.logger.log({ requestId, input }, 'Creating tenant');

    const existing = await this.tenantRepository.findByVatNumber(input.vatNumber);
    if (existing) {
      throw new TenantAlreadyExistsException(input.vatNumber);
    }

    const tenant = await this.tenantRepository.create(input, requestId);
    return tenant;
  }
}
```

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

```typescript
// src/lib/repositories/dynamodb-tenant.repository.ts
import { Inject, Injectable, Logger } from '@nestjs/common';
import { DynamoDBDocumentClient, PutCommand, GetCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';
import { DYNAMODB_CLIENT } from '@sibill-erp-gateway/server/dynamodb-utils';
import type { TenantRepository } from './tenant.repository';
import type { CreateTenantInput, TenantDto } from '@sibill-erp-gateway/shared/tenant-dto';
import { TenantStatus } from '@sibill-erp-gateway/shared/tenant-dto';

@Injectable()
export class DynamoDbTenantRepository implements TenantRepository {
  private readonly logger = new Logger(DynamoDbTenantRepository.name);
  private readonly tableName: string;

  constructor(
    @Inject(DYNAMODB_CLIENT)
    private readonly docClient: DynamoDBDocumentClient,
    @Inject('TENANT_FEATURE_OPTIONS')
    private readonly options: { tableName: string },
  ) {
    this.tableName = options.tableName;
  }

  async create(input: CreateTenantInput, requestId: string): Promise<TenantDto> {
    const tenantId = crypto.randomUUID();
    const now = new Date().toISOString();

    const item = {
      tenantId,
      tenantName: input.tenantName,
      vatNumber: input.vatNumber,
      adminEmail: input.adminEmail,
      status: TenantStatus.Created,
      createdAt: now,
      updatedAt: now,
    };

    await this.docClient.send(
      new PutCommand({
        TableName: this.tableName,
        Item: item,
      }),
    );

    return item;
  }

  async findById(tenantId: string): Promise<TenantDto | null> {
    const result = await this.docClient.send(
      new GetCommand({
        TableName: this.tableName,
        Key: { tenantId },
      }),
    );

    return result.Item ? (result.Item as TenantDto) : null;
  }

  async findByVatNumber(vatNumber: string): Promise<TenantDto | null> {
    const result = await this.docClient.send(
      new QueryCommand({
        TableName: this.tableName,
        IndexName: 'vatNumber-index',
        KeyConditionExpression: 'vatNumber = :vatNumber',
        ExpressionAttributeValues: { ':vatNumber': vatNumber },
      }),
    );

    return result.Items?.[0] ? (result.Items[0] as TenantDto) : null;
  }
}
```

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

```typescript
// src/lib/utils/counter.util.ts
import { DynamoDBDocumentClient, UpdateCommand } from '@aws-sdk/lib-dynamodb';

export class CounterService {
  constructor(
    private readonly docClient: DynamoDBDocumentClient,
    private readonly countersTableName: string,
  ) {}

  async increment(counterId: string): Promise<number> {
    const result = await this.docClient.send(
      new UpdateCommand({
        TableName: this.countersTableName,
        Key: { counterId },
        UpdateExpression: 'SET #count = if_not_exists(#count, :zero) + :inc',
        ExpressionAttributeNames: { '#count': 'count' },
        ExpressionAttributeValues: { ':inc': 1, ':zero': 0 },
        ReturnValues: 'UPDATED_NEW',
      }),
    );

    return Number(result.Attributes?.count);
  }
}
```

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
