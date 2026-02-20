# Raw TypeScript Lambda Reference

Complete guide for creating minimal AWS Lambda functions in pure TypeScript without frameworks like NestJS.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Minimal Handler](#minimal-handler)
3. [Dependency Injection Patterns](#dependency-injection-patterns)
4. [Cold Start Optimization](#cold-start-optimization)
5. [TypeScript Configuration](#typescript-configuration)
6. [Build and Packaging](#build-and-packaging)
7. [Testing](#testing)
8. [Deployment](#deployment)

---

## Project Structure

### Minimal Setup

```
raw-ts-lambda/
├── src/
│   ├── handlers/
│   │   ├── api.handler.ts
│   │   └── s3.handler.ts
│   ├── services/
│   │   └── user.service.ts
│   ├── models/
│   │   └── user.model.ts
│   ├── utils/
│   │   └── response.util.ts
│   └── config/
│       └── database.config.ts
├── dist/                     # Compiled output
├── tests/
│   └── handlers/
│       └── api.handler.test.ts
├── package.json
├── tsconfig.json
└── template.yaml (or serverless.yml)
```

### Package.json

```json
{
  "name": "raw-ts-lambda",
  "version": "1.0.0",
  "description": "Minimal TypeScript Lambda without frameworks",
  "main": "dist/handlers/api.handler.js",
  "scripts": {
    "build": "tsc",
    "build:prod": "tsc && npm prune --production",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "deploy": "sam build && sam deploy",
    "local": "sam local start-api"
  },
  "dependencies": {
    "@aws-sdk/client-dynamodb": "^3.450.0",
    "@aws-sdk/lib-dynamodb": "^3.450.0",
    "@aws-sdk/client-s3": "^3.450.0"
  },
  "devDependencies": {
    "@types/aws-lambda": "^8.10.131",
    "@types/jest": "^29.5.10",
    "@types/node": "^20.10.0",
    "@typescript-eslint/eslint-plugin": "^6.13.0",
    "@typescript-eslint/parser": "^6.13.0",
    "aws-lambda": "^1.0.7",
    "esbuild": "^0.19.8",
    "eslint": "^8.54.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1",
    "typescript": "^5.3.2"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
```

---

## Minimal Handler

### Basic API Gateway Handler

```typescript
// src/handlers/api.handler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';

// Static initialization - runs once per container
// Configure allowed origins via ALLOWED_ORIGINS env var (comma-separated list)
const allowedOrigins = (process.env.ALLOWED_ORIGINS || '').split(',').filter(Boolean);
const responseHeaders = {
  'Content-Type': 'application/json',
  ...(allowedOrigins.length > 0 && {
    'Access-Control-Allow-Origin': allowedOrigins.includes('*') ? '*' : allowedOrigins[0],
    'Access-Control-Allow-Credentials': 'true',
  }),
};

export const handler = async (
  event: APIGatewayProxyEvent,
  context: Context
): Promise<APIGatewayProxyResult> => {
  console.log('Request:', {
    requestId: context.awsRequestId,
    path: event.path,
    method: event.httpMethod,
  });

  try {
    const { httpMethod, path, pathParameters, queryStringParameters, body } = event;

    // Simple routing
    switch (`${httpMethod} ${path}`) {
      case 'GET /health':
        return successResponse(200, { status: 'ok', timestamp: new Date().toISOString() });

      case 'GET /users':
        return await getUsers(queryStringParameters);

      case 'GET /users/{id}':
        return await getUser(pathParameters?.id);

      case 'POST /users':
        return await createUser(body);

      default:
        return errorResponse(404, 'Not Found');
    }
  } catch (error) {
    console.error('Error:', error);
    return errorResponse(500, 'Internal Server Error');
  }
};

// Service functions
async function getUsers(queryParams: Record<string, string> | null): Promise<APIGatewayProxyResult> {
  // Implementation
  return successResponse(200, { users: [] });
}

async function getUser(id: string | undefined): Promise<APIGatewayProxyResult> {
  if (!id) {
    return errorResponse(400, 'User ID is required');
  }
  // Implementation
  return successResponse(200, { id, name: 'John Doe' });
}

async function createUser(body: string | null): Promise<APIGatewayProxyResult> {
  if (!body) {
    return errorResponse(400, 'Request body is required');
  }

  try {
    const user = JSON.parse(body);
    // Validate and save
    return successResponse(201, { id: '123', ...user });
  } catch (error) {
    return errorResponse(400, 'Invalid JSON in request body');
  }
}

// Utility functions
function successResponse(statusCode: number, data: unknown): APIGatewayProxyResult {
  return {
    statusCode,
    headers: responseHeaders,
    body: JSON.stringify(data),
  };
}

function errorResponse(statusCode: number, message: string): APIGatewayProxyResult {
  return {
    statusCode,
    headers: responseHeaders,
    body: JSON.stringify({ error: message }),
  };
}
```

### Handler with Service Layer

```typescript
// src/handlers/user.handler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';
import { UserService } from '../services/user.service';
import { DynamoDbUserRepository } from '../repositories/dynamodb-user.repository';

// Lazy-initialized singleton
let userService: UserService | null = null;

function getUserService(): UserService {
  if (!userService) {
    const repository = new DynamoDbUserRepository();
    userService = new UserService(repository);
  }
  return userService;
}

export const handler = async (
  event: APIGatewayProxyEvent,
  context: Context
): Promise<APIGatewayProxyResult> => {
  const service = getUserService();

  try {
    switch (event.httpMethod) {
      case 'GET':
        if (event.pathParameters?.id) {
          const user = await service.findById(event.pathParameters.id);
          return user
            ? { statusCode: 200, body: JSON.stringify(user) }
            : { statusCode: 404, body: JSON.stringify({ error: 'User not found' }) };
        }
        const users = await service.findAll();
        return { statusCode: 200, body: JSON.stringify(users) };

      case 'POST':
        const created = await service.create(JSON.parse(event.body || '{}'));
        return { statusCode: 201, body: JSON.stringify(created) };

      case 'PUT':
        const updated = await service.update(
          event.pathParameters?.id!,
          JSON.parse(event.body || '{}')
        );
        return { statusCode: 200, body: JSON.stringify(updated) };

      case 'DELETE':
        await service.delete(event.pathParameters?.id!);
        return { statusCode: 204, body: '' };

      default:
        return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
    }
  } catch (error) {
    console.error('Handler error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' }),
    };
  }
};
```

### S3 Event Handler

```typescript
// src/handlers/s3.handler.ts
import { S3Handler, S3Event, Context } from 'aws-lambda';
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';

// Static client instance
const s3Client = new S3Client({});

export const handler: S3Handler = async (event: S3Event, context: Context): Promise<void> => {
  console.log('S3 Event:', JSON.stringify(event));

  for (const record of event.Records) {
    const bucket = record.s3.bucket.name;
    const key = decodeURIComponent(record.s3.object.key.replace(/\+/g, ' '));

    try {
      // Process the S3 object
      const response = await s3Client.send(
        new GetObjectCommand({
          Bucket: bucket,
          Key: key,
        })
      );

      // Process based on file type
      if (key.endsWith('.json')) {
        await processJsonFile(response.Body, key);
      } else if (key.endsWith('.csv')) {
        await processCsvFile(response.Body, key);
      }

      console.log(`Successfully processed s3://${bucket}/${key}`);
    } catch (error) {
      console.error(`Error processing s3://${bucket}/${key}:`, error);
      throw error; // Let Lambda retry
    }
  }
};

async function processJsonFile(body: ReadableStream | undefined, key: string): Promise<void> {
  if (!body) return;
  // Implementation
}

async function processCsvFile(body: ReadableStream | undefined, key: string): Promise<void> {
  if (!body) return;
  // Implementation
}
```

### SQS Event Handler

```typescript
// src/handlers/sqs.handler.ts
import { SQSHandler, SQSEvent, SQSRecord, Context } from 'aws-lambda';

interface MessagePayload {
  type: string;
  data: unknown;
}

export const handler: SQSHandler = async (event: SQSEvent, context: Context): Promise<void> => {
  console.log('SQS Event:', {
    recordCount: event.Records.length,
    requestId: context.awsRequestId,
  });

  const batchItemFailures: { itemIdentifier: string }[] = [];

  for (const record of event.Records) {
    try {
      await processMessage(record);
    } catch (error) {
      console.error(`Failed to process message ${record.messageId}:`, error);
      batchItemFailures.push({ itemIdentifier: record.messageId });
    }
  }

  // Return partial batch response for failed items
  if (batchItemFailures.length > 0) {
    throw new Error(`Batch item failures: ${JSON.stringify(batchItemFailures)}`);
  }
};

async function processMessage(record: SQSRecord): Promise<void> {
  const payload: MessagePayload = JSON.parse(record.body);

  console.log('Processing message:', {
    messageId: record.messageId,
    type: payload.type,
  });

  switch (payload.type) {
    case 'SEND_EMAIL':
      await sendEmail(payload.data);
      break;
    case 'PROCESS_ORDER':
      await processOrder(payload.data);
      break;
    default:
      console.warn('Unknown message type:', payload.type);
  }
}

async function sendEmail(data: unknown): Promise<void> {
  // Implementation
}

async function processOrder(data: unknown): Promise<void> {
  // Implementation
}
```

---

## Dependency Injection Patterns

### Simple DI Container

```typescript
// src/config/container.ts
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

// Service interfaces
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<User>;
  delete(id: string): Promise<void>;
}

export interface IEmailService {
  send(to: string, subject: string, body: string): Promise<void>;
}

// Simple container
class Container {
  private services = new Map<string, unknown>();

  register<T>(key: string, factory: () => T): void {
    this.services.set(key, factory);
  }

  resolve<T>(key: string): T {
    const service = this.services.get(key);
    if (!service) {
      throw new Error(`Service ${key} not registered`);
    }
    if (typeof service === 'function') {
      const instance = (service as () => T)();
      this.services.set(key, instance); // Cache instance
      return instance;
    }
    return service as T;
  }
}

// Global container instance
export const container = new Container();

// Registration
export function initializeContainer(): void {
  // Database client
  container.register('dynamoClient', () => {
    const client = new DynamoDBClient({});
    return DynamoDBDocumentClient.from(client);
  });

  // Repositories
  container.register('userRepository', () => {
    return new DynamoDbUserRepository(container.resolve('dynamoClient'));
  });

  // Services
  container.register('userService', () => {
    return new UserService(container.resolve('userRepository'));
  });

  container.register('emailService', () => {
    return new SesEmailService();
  });
}

// Type definitions
export interface User {
  id: string;
  email: string;
  name: string;
}

// Repository implementation
class DynamoDbUserRepository implements IUserRepository {
  constructor(private client: DynamoDBDocumentClient) {}

  async findById(id: string): Promise<User | null> {
    // Implementation
    return null;
  }

  async save(user: User): Promise<User> {
    // Implementation
    return user;
  }

  async delete(id: string): Promise<void> {
    // Implementation
  }
}

// Service implementation
class UserService {
  constructor(private repository: IUserRepository) {}

  async findById(id: string): Promise<User | null> {
    return this.repository.findById(id);
  }
}

// Email service
class SesEmailService implements IEmailService {
  async send(to: string, subject: string, body: string): Promise<void> {
    // SES implementation
  }
}
```

### Handler with DI

```typescript
// src/handlers/di-handler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';
import { container, initializeContainer } from '../config/container';

// Initialize container on first import
let initialized = false;

function ensureInitialized(): void {
  if (!initialized) {
    initializeContainer();
    initialized = true;
  }
}

export const handler = async (
  event: APIGatewayProxyEvent,
  context: Context
): Promise<APIGatewayProxyResult> => {
  ensureInitialized();

  const userService = container.resolve<UserService>('userService');

  // Handler logic
  return {
    statusCode: 200,
    body: JSON.stringify({ message: 'OK' }),
  };
};
```

---

## Cold Start Optimization

### Lazy Loading Pattern

```typescript
// src/utils/lazy-loader.ts
export class LazyLoader<T> {
  private instance: T | null = null;
  private initializing = false;
  private initPromise: Promise<T> | null = null;

  constructor(private factory: () => Promise<T> | T) {}

  async get(): Promise<T> {
    if (this.instance) {
      return this.instance;
    }

    if (!this.initPromise) {
      this.initPromise = Promise.resolve(this.factory()).then((instance) => {
        this.instance = instance;
        return instance;
      });
    }

    return this.initPromise;
  }

  getSync(): T | null {
    return this.instance;
  }
}

// Usage
const dbConnection = new LazyLoader(async () => {
  console.log('Initializing database connection...');
  const connection = await createConnection({
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    // Connection pool optimized for Lambda
    max: 2,
    min: 0,
    idleTimeoutMillis: 10000,
  });
  return connection;
});

// In handler
export const handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  const db = await dbConnection.get();
  // Use db
};
```

### Module-Level Caching

```typescript
// src/config/database.ts
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

// Module-level cache - persists across warm invocations
let cachedClient: DynamoDBDocumentClient | null = null;

export function getDynamoClient(): DynamoDBDocumentClient {
  if (!cachedClient) {
    const client = new DynamoDBClient({
      // Optimize for Lambda
      maxAttempts: 3,
      requestHandler: {
        requestTimeout: 5000,
      },
    });

    cachedClient = DynamoDBDocumentClient.from(client, {
      marshallOptions: {
        convertEmptyValues: false,
        removeUndefinedValues: true,
        convertClassInstanceToMap: true,
      },
    });

    console.log('DynamoDB client initialized');
  }

  return cachedClient;
}

// For testing - allow reset
export function resetDynamoClient(): void {
  cachedClient = null;
}
```

---

## TypeScript Configuration

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "removeComments": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts", "**/*.spec.ts"]
}
```

### tsconfig.prod.json (Production)

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "sourceMap": false,
    "declaration": false,
    "declarationMap": false,
    "removeComments": true
  },
  "exclude": ["node_modules", "dist", "**/*.test.ts", "**/*.spec.ts", "tests"]
}
```

---

## Build and Packaging

### esbuild Configuration

```javascript
// build.js
const esbuild = require('esbuild');

async function build() {
  try {
    await esbuild.build({
      entryPoints: [
        'src/handlers/api.handler.ts',
        'src/handlers/s3.handler.ts',
        'src/handlers/sqs.handler.ts',
      ],
      bundle: true,
      platform: 'node',
      target: 'node20',
      outdir: 'dist',
      format: 'esm',
      splitting: true,
      minify: true,
      sourcemap: true,
      external: [
        'aws-sdk', // Provided by Lambda runtime
      ],
      banner: {
        js: 'import { createRequire } from "module"; import { fileURLToPath } from "url"; import { dirname } from "path"; const require = createRequire(import.meta.url); const __filename = fileURLToPath(import.meta.url); const __dirname = dirname(__filename);',
      },
      metafile: true,
    });

    console.log('Build completed successfully');
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

build();
```

### SAM Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: nodejs20.x
    MemorySize: 256
    Timeout: 10
    Architectures:
      - x86_64
    Environment:
      Variables:
        NODE_OPTIONS: '--enable-source-maps'

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Metadata:
      BuildMethod: esbuild
      BuildProperties:
        Minify: true
        Target: es2022
        Sourcemap: true
        EntryPoints:
          - src/handlers/api.handler.ts
        Format: esm
        Platform: node
    Properties:
      FunctionName: !Sub '${AWS::StackName}-api'
      Handler: api.handler
      CodeUri: ./
      Description: Raw TypeScript API handler
      Events:
        ApiRoot:
          Type: Api
          Properties:
            Path: /
            Method: ANY
        ApiProxy:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

  S3ProcessorFunction:
    Type: AWS::Serverless::Function
    Metadata:
      BuildMethod: esbuild
      BuildProperties:
        Minify: true
        Target: es2022
        EntryPoints:
          - src/handlers/s3.handler.ts
        Format: esm
    Properties:
      FunctionName: !Sub '${AWS::StackName}-s3-processor'
      Handler: s3.handler
      CodeUri: ./
      Events:
        S3Event:
          Type: S3
          Properties:
            Bucket: !Ref InputBucket
            Events: s3:ObjectCreated:*

  SQSProcessorFunction:
    Type: AWS::Serverless::Function
    Metadata:
      BuildMethod: esbuild
      BuildProperties:
        Minify: true
        Target: es2022
        EntryPoints:
          - src/handlers/sqs.handler.ts
        Format: esm
    Properties:
      FunctionName: !Sub '${AWS::StackName}-sqs-processor'
      Handler: sqs.handler
      CodeUri: ./
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt ProcessingQueue.Arn
            BatchSize: 10
            FunctionResponseTypes:
              - ReportBatchItemFailures

  InputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-input'

  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub '${AWS::StackName}-processing'
      VisibilityTimeout: 60
```

---

## Testing

### Jest Configuration

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/handlers/*.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};
```

### Handler Unit Test

```typescript
// tests/handlers/api.handler.test.ts
import { APIGatewayProxyEvent, Context } from 'aws-lambda';
import { handler } from '../../src/handlers/api.handler';

const mockContext: Partial<Context> = {
  awsRequestId: 'test-request-id',
  functionName: 'test-function',
  memoryLimitInMB: '256',
  invokedFunctionArn: 'arn:aws:lambda:us-east-1:123456789:function:test',
  getRemainingTimeInMillis: () => 30000,
};

describe('API Handler', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return 200 for health check', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      httpMethod: 'GET',
      path: '/health',
      headers: {},
      queryStringParameters: null,
      body: null,
    };

    const result = await handler(event as APIGatewayProxyEvent, mockContext as Context);

    expect(result.statusCode).toBe(200);
    const body = JSON.parse(result.body);
    expect(body.status).toBe('ok');
  });

  it('should return 404 for unknown routes', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      httpMethod: 'GET',
      path: '/unknown',
      headers: {},
    };

    const result = await handler(event as APIGatewayProxyEvent, mockContext as Context);

    expect(result.statusCode).toBe(404);
  });

  it('should return 400 for missing user ID', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      httpMethod: 'GET',
      path: '/users/{id}',
      pathParameters: {},
      headers: {},
    };

    const result = await handler(event as APIGatewayProxyEvent, mockContext as Context);

    expect(result.statusCode).toBe(400);
  });

  it('should return 400 for invalid JSON body', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      httpMethod: 'POST',
      path: '/users',
      body: 'invalid json',
      headers: {},
    };

    const result = await handler(event as APIGatewayProxyEvent, mockContext as Context);

    expect(result.statusCode).toBe(400);
  });
});
```

### Service Test with Mocks

```typescript
// tests/services/user.service.test.ts
import { UserService } from '../../src/services/user.service';
import { IUserRepository } from '../../src/config/container';

const mockRepository: jest.Mocked<IUserRepository> = {
  findById: jest.fn(),
  save: jest.fn(),
  delete: jest.fn(),
};

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService(mockRepository);
    jest.clearAllMocks();
  });

  describe('findById', () => {
    it('should return user when found', async () => {
      const user = { id: '123', name: 'John', email: 'john@example.com' };
      mockRepository.findById.mockResolvedValue(user);

      const result = await service.findById('123');

      expect(result).toEqual(user);
      expect(mockRepository.findById).toHaveBeenCalledWith('123');
    });

    it('should return null when user not found', async () => {
      mockRepository.findById.mockResolvedValue(null);

      const result = await service.findById('999');

      expect(result).toBeNull();
    });
  });

  describe('create', () => {
    it('should create and return user', async () => {
      const input = { name: 'John', email: 'john@example.com' };
      const created = { id: '123', ...input };
      mockRepository.save.mockResolvedValue(created);

      const result = await service.create(input);

      expect(result).toEqual(created);
      expect(mockRepository.save).toHaveBeenCalledWith(expect.objectContaining(input));
    });
  });
});
```

---

## Deployment

### Serverless Framework

```yaml
# serverless.yml
service: raw-ts-lambda

provider:
  name: aws
  runtime: nodejs20.x
  stage: ${opt:stage, 'dev'}
  region: ${opt:region, 'us-east-1'}
  memorySize: 256
  timeout: 10
  environment:
    NODE_OPTIONS: '--enable-source-maps'
    STAGE: ${self:provider.stage}

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource:
            - !Sub 'arn:aws:logs:${aws:region}:${aws:accountId}:log-group:/aws/lambda/${self:service}-*'
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
            - dynamodb:Query
            - dynamodb:Scan
          Resource:
            - !GetAtt UsersTable.Arn

plugins:
  - serverless-esbuild

custom:
  esbuild:
    bundle: true
    minify: ${self:custom.isProduction}
    sourcemap: true
    target: node20
    platform: node
    format: esm
    splitting: true
    entryPoints:
      - src/handlers/api.handler.ts
      - src/handlers/s3.handler.ts
      - src/handlers/sqs.handler.ts
    external:
      - aws-sdk

  isProduction: !Equals ['${self:provider.stage}', 'prod']

functions:
  api:
    handler: dist/api.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true

  s3Processor:
    handler: dist/s3.handler
    events:
      - s3:
          bucket: ${self:service}-input-${self:provider.stage}
          event: s3:ObjectCreated:*

  sqsProcessor:
    handler: dist/sqs.handler
    events:
      - sqs:
          arn:
            Fn::GetAtt:
              - ProcessingQueue
              - Arn
          batchSize: 10
          functionResponseType: ReportBatchItemFailures

resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-users-${self:provider.stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH

    ProcessingQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-processing-${self:provider.stage}
        VisibilityTimeout: 60
```

---

## Best Practices Summary

1. **Use static/module-level caching** for AWS clients and connections
2. **Implement lazy loading** for expensive resources
3. **Keep dependencies minimal** - only include what you need
4. **Use esbuild** for fast bundling and smaller package size
5. **Implement proper error handling** with structured responses
6. **Use TypeScript strict mode** for better type safety
7. **Write unit tests** with mocked dependencies
8. **Use environment variables** for configuration
9. **Enable source maps** for easier debugging
10. **Monitor cold starts** and optimize initialization code

## Cold Start Benchmarks

| Configuration | Cold Start | Warm Start | Memory |
|--------------|------------|------------|--------|
| Minimal (no deps) | ~50ms | ~2ms | 128MB |
| With DynamoDB client | ~150ms | ~5ms | 256MB |
| With full AWS SDK | ~300ms | ~10ms | 512MB |

## When to Use Raw TypeScript vs NestJS

### Use Raw TypeScript when:
- Maximum performance is critical
- Minimal cold start is required
- Simple handlers with minimal logic
- Small team with no framework experience
- Cost optimization is priority

### Use NestJS when:
- Complex application architecture
- Team familiar with NestJS
- Need dependency injection container
- Multiple modules and services
- Enterprise-grade requirements
