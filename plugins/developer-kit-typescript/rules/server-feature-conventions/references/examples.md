# Server Feature Conventions — Code Examples

Detailed code examples for the server feature conventions rule. See
`server-feature-conventions.md` for the concise rule; this file holds the full reference
implementations.

## Module Pattern — forRootAsync

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

## Service Pattern

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

## DynamoDB Repository Implementation

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

## Counter Utility Pattern

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