# Lambda Conventions — Code Examples

Detailed code examples for the Lambda conventions rule. See `lambda-conventions.md` for
the concise rule; this file holds the full reference implementations.

## Handler Pattern (6-Step Validation Pipeline)

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

## Environment Validation

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

## App Module Configuration

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

## SAM Template Structure

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