---
paths:
  - "**/*.ts"
---
# Rule: Lambda Conventions

## Context
Enforce consistent patterns for AWS Lambda functions built with NestJS and deployed via SAM. Lambda handlers follow a 6-step validation pipeline and integrate with shared server features.

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

### Handler Pattern (6-Step Validation Pipeline)

```typescript
// src/handlers/create-tenant.handler.ts
@Injectable()
export class CreateTenantHandler extends BaseLambdaHandlerService {
  constructor(
    @Inject(MY_SERVICE)
    private readonly myService: MyService,
  ) {
    super();
  }

  async handle(event: APIGatewayProxyEvent, context: Context): Promise<APIGatewayProxyResult> {
    const requestId = context.awsRequestId;
    const startTime = Date.now();

    // 1. Validate HTTP method
    const methodError = this.validateHttpMethod(event, ['POST']);
    if (methodError) return methodError;

    // 2. Validate body size
    const sizeValidation = validateBodySize(event.body);
    if (!sizeValidation.valid) {
      this.logger.warn({ requestId }, 'Request body too large');
      return sizeValidation.response;
    }

    // 3. Parse JSON safely
    const parseResult = safeJsonParse(event.body);
    if (!parseResult.success) {
      this.logger.warn({ requestId }, 'Invalid JSON payload');
      return parseResult.response;
    }

    // 4. Validate with Zod schema
    const validationResult = MySchema.safeParse(parseResult.data);
    if (!validationResult.success) {
      this.logger.warn({ requestId }, 'Input validation failed');
      return validationErrorResponse(validationResult.error.issues);
    }

    // 5. Execute business logic
    try {
      const result = await this.myService.execute(validationResult.data, requestId);
      return successResponse(HttpStatus.CREATED, result);
    } catch (error: unknown) {
      return handleLambdaError(error, requestId, this.logger);
    }
  }
}
```

### Environment Validation

```typescript
// src/modules/validate-env.ts
import { z } from 'zod';

const environmentSchema = z.object({
  MY_TABLE: z.string().min(1, 'MY_TABLE is required'),
  COUNTERS_TABLE: z.string().min(1, 'COUNTERS_TABLE is required'),
  DYNAMODB_ENDPOINT: z.string().optional(),
  AWS_REGION: z.string().optional(),
  NODE_ENV: z.string().optional(),
});

export type EnvironmentVariables = z.infer<typeof environmentSchema>;

export function validate(config: Record<string, unknown>): EnvironmentVariables {
  const parsed = environmentSchema.safeParse(config);
  if (!parsed.success) {
    const errors = parsed.error.issues.map(i => `[${i.path.join('.')}]: ${i.message}`).join('\n');
    throw new Error(`Environment validation failed:\n${errors}`);
  }
  return parsed.data;
}
```

### App Module Configuration

```typescript
// src/modules/app.module.ts
import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { MyHandler } from '../handlers';
import { MyFeatureModule } from '@sibill-erp-gateway/server/my-feature';
import { type EnvironmentVariables, validate } from './validate-env';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validate,
    }),
    MyFeatureModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (config: ConfigService) => ({
        tableName: config.get<string>('MY_TABLE')!,
        countersTableName: config.get<string>('COUNTERS_TABLE')!,
        endpoint: config.get<string>('DYNAMODB_ENDPOINT'),
        region: config.get<string>('AWS_REGION') || 'eu-central-1',
      }),
      inject: [ConfigService],
    }),
  ],
  providers: [MyHandler],
})
export class AppModule {}
```

### SAM Template Structure

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: nodejs22.x
    Environment:
      Variables:
        AWS_REGION: !Ref AWS::Region

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Resources:
  # DynamoDB Tables
  MyTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub 'sg-my-table-${Environment}'
      # ... table configuration

  # API Gateway
  ApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      # ... API configuration

  # Lambda Function
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub '${Environment}-my-action-entity'
      Handler: main.handler
      CodeUri: ../../../../dist/apps/lambdas/{domain}/{lambda-name}
      Events:
        MyApi:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /{domain}/{entity}
            Method: POST
      Environment:
        Variables:
          MY_TABLE: !Ref MyTable
          DYNAMODB_ENDPOINT: ''
          NODE_ENV: 'production'
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref MyTable

Outputs:
  ApiGatewayEndpoint:
    Value: !Sub 'https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Environment}'
```

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
