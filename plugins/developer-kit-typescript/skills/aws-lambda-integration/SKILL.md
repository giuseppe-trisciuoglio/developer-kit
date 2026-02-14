---
name: aws-lambda-integration
description: Provides AWS Lambda integration patterns for NestJS applications with cold start optimization, instance caching, and lifecycle management. Use when deploying NestJS to AWS Lambda, handling serverless architecture, optimizing cold starts, configuring API Gateway/ALB integration, or implementing warm start patterns with Express/Fastify adapters.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# AWS Lambda Integration for NestJS

## Overview

This skill provides comprehensive patterns for deploying NestJS applications on AWS Lambda with optimal performance. It covers cold start optimization, instance caching between invocations, lifecycle management, and support for both Express and Fastify platforms.

## When to Use

- Deploying NestJS applications to AWS Lambda
- Optimizing cold start performance
- Implementing warm start instance caching
- Configuring API Gateway or ALB integration
- Handling Lambda lifecycle hooks
- Building serverless REST APIs
- Migrating existing NestJS apps to Lambda

## Instructions

Follow these steps to integrate NestJS with AWS Lambda:

1. **Install dependencies**: Add `@codegenie/serverless-express` and `aws-lambda` packages
2. **Choose adapter**: Select Express (recommended for compatibility) or Fastify (better performance)
3. **Create Lambda handler**: Implement singleton pattern to cache NestJS instance between invocations
4. **Configure serverless**: Set up `serverless.yml` or SAM template with proper memory and timeout
5. **Optimize cold starts**: Use lazy loading, disable unnecessary features in production
6. **Add lifecycle hooks**: Implement `OnModuleInit` and `OnModuleDestroy` for resource management
7. **Configure database**: Use connection pooling limits optimized for Lambda (max 1-2 connections)
8. **Test locally**: Use `serverless-offline` plugin for local development and testing
9. **Deploy**: Package with esbuild and deploy using Serverless Framework or SAM

## Core Concepts

### Instance Caching (Warm Starts)

Lambda reuses execution contexts for subsequent invocations. Cache the NestJS application instance to avoid re-initialization:

```typescript
// lambda.ts - Singleton pattern for warm starts
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { Context, Handler } from 'aws-lambda';
import express from 'express';
import { AppModule } from './src/app.module';

let cachedServer: Handler;

async function bootstrap(): Promise<Handler> {
  const expressApp = express();
  const adapter = new ExpressAdapter(expressApp);

  const nestApp = await NestFactory.create(AppModule, adapter);
  nestApp.enableCors();
  nestApp.useGlobalPipes(/* your pipes */);

  await nestApp.init();

  return serverlessExpress({ app: expressApp });
}

export const handler: Handler = async (
  event: any,
  context: Context,
  callback: any,
) => {
  if (!cachedServer) {
    cachedServer = await bootstrap();
  }
  return cachedServer(event, context, callback);
};
```

### Cold Start Optimization

Minimize cold start time through lazy loading and selective initialization:

```typescript
// main.ts - Lazy loading configuration
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    // Disable logger in production for faster startup
    logger: process.env.NODE_ENV === 'production' ? ['error', 'warn'] : undefined,
    // Skip automatic listening - Lambda handles this
    abortOnError: false,
  });

  // Conditionally initialize heavy services
  if (process.env.ENABLE_SWAGGER === 'true') {
    const { SwaggerModule, DocumentBuilder } = await import('@nestjs/swagger');
    const config = new DocumentBuilder().build();
    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup('api', app, document);
  }

  return app;
}
```

## Platform Adapters

### Express Adapter (API Gateway)

```typescript
// lambda-express.ts
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { Context, Handler, APIGatewayProxyEvent } from 'aws-lambda';
import express from 'express';
import { AppModule } from './src/app.module';

let server: Handler;

async function bootstrap(): Promise<Handler> {
  const expressApp = express();
  const adapter = new ExpressAdapter(expressApp);

  const app = await NestFactory.create(AppModule, adapter);

  // Lambda-specific configurations
  app.setGlobalPrefix('api');
  app.enableCors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true,
  });

  await app.init();

  return serverlessExpress({
    app: expressApp,
    eventSource: {
      getRequest: (event: APIGatewayProxyEvent) => ({
        method: event.httpMethod,
        url: event.path,
        headers: event.headers,
        body: event.body,
      }),
    },
  });
}

export const handler: Handler = async (
  event: APIGatewayProxyEvent,
  context: Context,
) => {
  if (!server) {
    server = await bootstrap();
  }
  return server(event, context);
};
```

### Fastify Adapter (Performance Optimized)

```typescript
// lambda-fastify.ts
import { NestFactory } from '@nestjs/core';
import { FastifyAdapter, NestFastifyApplication } from '@nestjs/platform-fastify';
import awsLambdaFastify from 'aws-lambda-fastify';
import { Context, Handler, APIGatewayProxyEvent } from 'aws-lambda';
import { AppModule } from './src/app.module';

let cachedProxy: Handler;

async function bootstrap(): Promise<Handler> {
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter({
      // Optimize for Lambda environment
      logger: false,
      trustProxy: true,
    }),
  );

  app.setGlobalPrefix('api');
  app.enableCors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true,
  });

  await app.init();

  return awsLambdaFastify(app.getHttpAdapter().getInstance(), {
    binaryMimeTypes: ['application/pdf', 'image/*'],
  });
}

export const handler: Handler = async (
  event: APIGatewayProxyEvent,
  context: Context,
) => {
  if (!cachedProxy) {
    cachedProxy = await bootstrap();
  }
  return cachedProxy(event, context);
};
```

### ALB Support (Multi-value headers)

```typescript
// lambda-alb.ts - Application Load Balancer support
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { Context, Handler, ALBEvent, ALBResult } from 'aws-lambda';
import express from 'express';
import { AppModule } from './src/app.module';

let server: Handler;

async function bootstrap(): Promise<Handler> {
  const expressApp = express();
  const adapter = new ExpressAdapter(expressApp);

  const app = await NestFactory.create(AppModule, adapter);
  await app.init();

  return serverlessExpress({
    app: expressApp,
    // ALB requires multi-value headers support
    binaryMimeTypes: ['*/*'],
  });
}

export const handler: Handler = async (
  event: ALBEvent,
  context: Context,
): Promise<ALBResult> => {
  if (!server) {
    server = await bootstrap();
  }

  // ALB specific: handle multi-value headers
  const modifiedEvent = {
    ...event,
    multiValueHeaders: event.multiValueHeaders || {},
    multiValueQueryStringParameters: event.multiValueQueryStringParameters || {},
  };

  return server(modifiedEvent, context) as Promise<ALBResult>;
};
```

## Lifecycle Management

### Custom Lifecycle Service

```typescript
// src/lambda/lambda-lifecycle.service.ts
import { Injectable, OnModuleInit, OnApplicationBootstrap, OnModuleDestroy } from '@nestjs/common';

@Injectable()
export class LambdaLifecycleService implements OnModuleInit, OnApplicationBootstrap, OnModuleDestroy {
  private startupTime: number;

  onModuleInit() {
    // Called during module initialization
    console.log('[Lambda] Module initializing...');
    this.startupTime = Date.now();
  }

  onApplicationBootstrap() {
    // Called after all modules initialized
    const initTime = Date.now() - this.startupTime;
    console.log(`[Lambda] Application bootstrapped in ${initTime}ms`);

    // Report cold start metrics
    if (process.env.NODE_ENV === 'production') {
      this.reportColdStartMetric(initTime);
    }
  }

  onModuleDestroy() {
    // Cleanup before Lambda container is frozen
    console.log('[Lambda] Module destroying - cleanup resources');
  }

  private reportColdStartMetric(duration: number) {
    // Send to CloudWatch or other monitoring
    console.log(JSON.stringify({
      metric: 'ColdStartDuration',
      value: duration,
      unit: 'Milliseconds',
      timestamp: new Date().toISOString(),
    }));
  }
}
```

### Connection Management for Lambda

```typescript
// src/database/lambda-database.service.ts
import { Injectable, OnModuleDestroy } from '@nestjs/common';
import { Pool } from 'pg';

@Injectable()
export class LambdaDatabaseService implements OnModuleDestroy {
  private pool: Pool;
  private isConnected = false;

  constructor() {
    // Lazy initialization - don't connect during constructor
  }

  async getPool(): Promise<Pool> {
    if (!this.pool) {
      this.pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        // Lambda-optimized pool settings
        max: 2, // Limit connections for Lambda
        min: 0, // Don't keep connections alive
        idleTimeoutMillis: 10000,
        connectionTimeoutMillis: 5000,
      });
      this.isConnected = true;
    }
    return this.pool;
  }

  async onModuleDestroy() {
    if (this.pool && this.isConnected) {
      await this.pool.end();
      this.isConnected = false;
    }
  }

  // Lambda-specific: check if running in warm container
  isWarmContainer(): boolean {
    return process.env.AWS_LAMBDA_FUNCTION_NAME !== undefined &&
           process.env.LAMBDA_WARM === 'true';
  }
}
```

## Environment Configuration

### Lambda-specific Configuration

```typescript
// src/config/lambda.config.ts
export const lambdaConfig = () => ({
  lambda: {
    // Function configuration
    functionName: process.env.AWS_LAMBDA_FUNCTION_NAME,
    memorySize: parseInt(process.env.AWS_LAMBDA_FUNCTION_MEMORY_SIZE || '512', 10),
    region: process.env.AWS_REGION,

    // Optimization flags
    keepAlive: process.env.KEEP_ALIVE === 'true',
    skipSwagger: process.env.NODE_ENV === 'production',
    lazyLoadModules: process.env.LAZY_LOAD === 'true',

    // Timeouts
    connectionTimeout: parseInt(process.env.CONNECTION_TIMEOUT || '5000', 10),
    requestTimeout: parseInt(process.env.REQUEST_TIMEOUT || '29000', 10),
  },

  // Conditional feature flags
  features: {
    enableCache: process.env.ENABLE_CACHE === 'true',
    enableLogging: process.env.ENABLE_LOGGING !== 'false',
    enableMetrics: process.env.ENABLE_METRICS === 'true',
  },
});
```

### Dynamic Module Loading

```typescript
// src/app.module.ts
import { Module, DynamicModule } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { lambdaConfig } from './config/lambda.config';

@Module({})
export class AppModule {
  static forRoot(): DynamicModule {
    const isLambda = !!process.env.AWS_LAMBDA_FUNCTION_NAME;

    const imports = [
      ConfigModule.forRoot({
        isGlobal: true,
        load: [lambdaConfig],
      }),
    ];

    // Conditionally add modules based on environment
    if (process.env.ENABLE_CACHE === 'true') {
      // Add cache module
    }

    return {
      module: AppModule,
      imports,
      providers: [
        // Lambda-specific providers
        ...(isLambda ? [{ provide: 'IS_LAMBDA', useValue: true }] : []),
      ],
    };
  }
}
```

## Error Handling

### Lambda Error Handler

```typescript
// src/common/filters/lambda-exception.filter.ts
import { ExceptionFilter, Catch, ArgumentsHost, HttpException, Logger } from '@nestjs/common';
import { Response } from 'express';

@Catch()
export class LambdaExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(LambdaExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    let status = 500;
    let message = 'Internal server error';
    let code = 'INTERNAL_ERROR';

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();
      message = typeof exceptionResponse === 'string'
        ? exceptionResponse
        : (exceptionResponse as any).message || message;
      code = `HTTP_${status}`;
    }

    // Log for CloudWatch
    this.logger.error({
      error: exception instanceof Error ? exception.message : 'Unknown error',
      stack: exception instanceof Error ? exception.stack : undefined,
      status,
      code,
    });

    // Lambda-friendly error response
    response.status(status).json({
      statusCode: status,
      error: code,
      message,
      requestId: process.env.AWS_REQUEST_ID,
      timestamp: new Date().toISOString(),
    });
  }
}
```

## Testing Lambda Functions

### Unit Test for Handler

```typescript
// lambda.spec.ts
import { handler } from './lambda';
import { Context } from 'aws-lambda';

describe('Lambda Handler', () => {
  const mockContext: Partial<Context> = {
    functionName: 'test-function',
    memoryLimitInMB: '512',
    invokedFunctionArn: 'arn:aws:lambda:us-east-1:123456789:function:test',
    awsRequestId: 'test-request-id',
  };

  beforeEach(() => {
    // Reset cached server for cold start tests
    jest.resetModules();
  });

  it('should bootstrap on first invocation (cold start)', async () => {
    const event = {
      httpMethod: 'GET',
      path: '/api/health',
      headers: {},
      body: null,
    };

    const result = await handler(event, mockContext as Context, () => {});

    expect(result.statusCode).toBe(200);
  });

  it('should reuse instance on warm invocation', async () => {
    const event = {
      httpMethod: 'GET',
      path: '/api/health',
      headers: {},
      body: null,
    };

    // First invocation
    await handler(event, mockContext as Context, () => {});

    // Second invocation (should use cached server)
    const start = Date.now();
    const result = await handler(event, mockContext as Context, () => {});
    const duration = Date.now() - start;

    expect(result.statusCode).toBe(200);
    expect(duration).toBeLessThan(100); // Warm start should be fast
  });
});
```

### Integration Test with serverless-offline

```typescript
// test/lambda.integration.spec.ts
describe('Lambda Integration', () => {
  let server: any;

  beforeAll(async () => {
    // Bootstrap for local testing
    const { bootstrap } = await import('../lambda');
    server = await bootstrap();
  });

  afterAll(async () => {
    if (server) {
      // Cleanup
    }
  });

  it('should handle API Gateway events', async () => {
    const event = {
      httpMethod: 'POST',
      path: '/api/users',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Test User' }),
    };

    const result = await server(event, {});

    expect(result.statusCode).toBe(201);
    expect(JSON.parse(result.body)).toHaveProperty('id');
  });
});
```

## Serverless Framework Configuration

### serverless.yml

```yaml
service: nestjs-lambda-api

provider:
  name: aws
  runtime: nodejs20.x
  region: ${opt:region, 'us-east-1'}
  stage: ${opt:stage, 'dev'}
  memorySize: 512
  timeout: 29
  environment:
    NODE_ENV: production
    DATABASE_URL: ${ssm:/${self:service}/${self:provider.stage}/database-url}
    JWT_SECRET: ${ssm:/${self:service}/${self:provider.stage}/jwt-secret}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: '*'

package:
  individually: false
  patterns:
    - '!node_modules/**'
    - '!test/**'
    - '!.git/**'
    - 'dist/**'
    - '!dist/tsconfig.build.tsbuildinfo'

custom:
  esbuild:
    bundle: true
    minify: true
    target: node20
    platform: node
    external:
      - '@nestjs/microservices'
      - '@nestjs/websockets'
      - 'class-transformer/storage'

functions:
  api:
    handler: dist/lambda.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
      - http:
          path: /
          method: ANY
          cors: true
    provisionedConcurrency: ${self:custom.provisionedConcurrency.${self:provider.stage}, 0}

custom:
  provisionedConcurrency:
    prod: 5
    dev: 0

plugins:
  - serverless-esbuild
  - serverless-offline
```

## SAM Template

### template.yaml

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: NestJS Lambda API

Globals:
  Function:
    Timeout: 29
    MemorySize: 512
    Runtime: nodejs20.x
    Architectures:
      - x86_64

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  NestJSApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub '${AWS::StackName}-api'
      Handler: dist/lambda.handler
      CodeUri: ./
      Environment:
        Variables:
          NODE_ENV: !Ref Environment
          DATABASE_URL: !Sub '{{resolve:ssm-secure:/${AWS::StackName}/database-url}}'
      Events:
        ApiGatewayRoot:
          Type: Api
          Properties:
            Path: /
            Method: ANY
            RestApiId: !Ref ApiGatewayApi
        ApiGatewayProxy:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            RestApiId: !Ref ApiGatewayApi
      Policies:
        - AWSLambdaBasicExecutionRole

  ApiGatewayApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      Cors:
        AllowMethods: "'*'"
        AllowHeaders: "'*'"
        AllowOrigin: "'*'"

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${ApiGatewayApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}/'
```

## Best Practices

1. **Always cache the NestJS instance** - Reuse between warm invocations
2. **Use connection pooling limits** - Keep max connections low (1-2) for Lambda
3. **Lazy load heavy modules** - Defer initialization of non-critical services
4. **Minimize deployment package** - Exclude dev dependencies and unnecessary files
5. **Use provisioned concurrency** - For latency-sensitive workloads
6. **Monitor cold starts** - Log initialization times and optimize
7. **Handle container freezes** - Don't rely on in-memory state between invocations
8. **Use environment variables** - For configuration, not hardcoded values
9. **Implement proper error handling** - Return Lambda-friendly error responses
10. **Test locally with serverless-offline** - Before deploying to AWS

## Common Patterns

### Health Check Endpoint

```typescript
// src/health/health.controller.ts
import { Controller, Get } from '@nestjs/common';

@Controller('health')
export class HealthController {
  @Get()
  check() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      environment: process.env.NODE_ENV,
    };
  }
}
```

### Request Context

```typescript
// src/common/interceptors/lambda-context.interceptor.ts
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LambdaContextInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();

    // Add Lambda request context
    request.lambdaContext = {
      requestId: request.headers['x-amzn-requestid'],
      traceId: request.headers['x-amzn-trace-id'],
      remainingTime: () => {
        // Calculate remaining time based on Lambda timeout
        return 29000; // Default 29s
      },
    };

    const start = Date.now();

    return next.handle().pipe(
      tap(() => {
        console.log(`Request processed in ${Date.now() - start}ms`);
      }),
    );
  }
}
```

## Examples

### Example 1: Basic Express Lambda Handler

**Input**: NestJS application with AppModule
**Output**: AWS Lambda handler function

```typescript
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { Context, Handler } from 'aws-lambda';
import express from 'express';
import { AppModule } from './src/app.module';

let cachedServer: Handler;

export const handler = async (event: any, context: Context) => {
  if (!cachedServer) {
    const expressApp = express();
    const app = await NestFactory.create(AppModule, new ExpressAdapter(expressApp));
    await app.init();
    cachedServer = serverlessExpress({ app: expressApp });
  }
  return cachedServer(event, context);
};
```

### Example 2: Fastify with Performance Optimization

**Input**: NestJS app requiring low latency
**Output**: Optimized Fastify Lambda handler

```typescript
import { NestFactory } from '@nestjs/core';
import { FastifyAdapter } from '@nestjs/platform-fastify';
import awsLambdaFastify from 'aws-lambda-fastify';
import { AppModule } from './src/app.module';

let cachedHandler: Handler;

export const handler = async (event: any, context: Context) => {
  if (!cachedHandler) {
    const app = await NestFactory.create(AppModule, new FastifyAdapter({ logger: false }));
    await app.init();
    cachedHandler = awsLambdaFastify(app.getHttpAdapter().getInstance());
  }
  return cachedHandler(event, context);
};
```

### Example 3: Serverless Framework Deployment

**Input**: Configured NestJS application
**Output**: Deployed Lambda function with API Gateway

```yaml
# serverless.yml
functions:
  api:
    handler: dist/lambda.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

## Constraints and Warnings

### Lambda Limitations

- **Timeout**: Maximum 29 seconds (15 minutes for Lambda@Edge)
- **Memory**: 128 MB to 10 GB (cost increases with memory)
- **Payload size**: Request/response limited to 6 MB (API Gateway)
- **Cold starts**: Can range from 100ms to several seconds depending on initialization

### Common Pitfalls

1. **Don't initialize connections in constructor**: Use lazy initialization to avoid holding connections during cold starts
2. **Don't rely on in-memory state**: Containers can be frozen and reused without notice
3. **Don't use traditional server patterns**: Disable keep-alive connections that can cause timeouts
4. **Don't forget to close connections**: Implement `OnModuleDestroy` to cleanup database connections

### Security Considerations

- **Environment variables**: Never store sensitive data in code; use AWS Secrets Manager or SSM Parameter Store
- **CORS**: Configure properly to avoid exposing APIs to unauthorized origins
- **Payload validation**: Validate all incoming requests since Lambda has no built-in protection

### Performance Warnings

- **Avoid synchronous operations**: Use async/await for all I/O operations
- **Minimize package size**: Exclude devDependencies and unnecessary files from deployment
- **Provisioned concurrency**: Consider for production workloads requiring consistent latency

## References

For advanced patterns and detailed configuration options, see:
- [references/express-adapter.md](references/express-adapter.md) - Express-specific configurations
- [references/fastify-adapter.md](references/fastify-adapter.md) - Fastify optimizations
- [references/deployment.md](references/deployment.md) - Deployment strategies and CI/CD
