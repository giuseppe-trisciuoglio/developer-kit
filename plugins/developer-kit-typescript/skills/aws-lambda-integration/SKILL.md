---
name: aws-lambda-integration
description: Provides AWS Lambda integration patterns for NestJS applications with cold start optimization, instance caching, and lifecycle management. Use when deploying NestJS to AWS Lambda, handling serverless architecture, optimizing cold starts, configuring API Gateway/ALB integration, or implementing warm start patterns with Express/Fastify adapters.
category: backend
tags: [aws, lambda, nestjs, typescript, serverless, cold-start]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# AWS Lambda Integration for NestJS

## Overview

This skill provides patterns for deploying NestJS applications on AWS Lambda with optimal performance. It covers cold start optimization, instance caching between invocations, lifecycle management, and support for both Express and Fastify platforms.

## When to Use

- Deploying NestJS applications to AWS Lambda
- Optimizing cold start performance
- Implementing warm start instance caching
- Configuring API Gateway or ALB integration
- Handling Lambda lifecycle hooks
- Building serverless REST APIs

## Instructions

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

Cache the NestJS application instance to avoid re-initialization between invocations:

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
  await nestApp.init();

  return serverlessExpress({ app: expressApp });
}

export const handler: Handler = async (event: any, context: Context) => {
  if (!cachedServer) {
    cachedServer = await bootstrap();
  }
  return cachedServer(event, context);
};
```

### Cold Start Optimization

Minimize cold start time through lazy loading:

```typescript
// Lazy load heavy modules only when needed
if (process.env.ENABLE_SWAGGER === 'true') {
  const { SwaggerModule, DocumentBuilder } = await import('@nestjs/swagger');
  const config = new DocumentBuilder().build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);
}
```

## Platform Adapters

### Express Adapter

```typescript
// lambda.ts
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { Context, Handler, APIGatewayProxyEvent } from 'aws-lambda';
import express from 'express';
import { AppModule } from './src/app.module';

let server: Handler;

async function bootstrap(): Promise<Handler> {
  const expressApp = express();
  const app = await NestFactory.create(AppModule, new ExpressAdapter(expressApp));

  app.setGlobalPrefix('api');
  app.enableCors({
    origin: process.env.ALLOWED_ORIGINS
      ? process.env.ALLOWED_ORIGINS.split(',')
      : [], // Default to no origins - must be explicitly configured
    credentials: true,
  });

  await app.init();
  return serverlessExpress({ app: expressApp });
}

export const handler: Handler = async (event: APIGatewayProxyEvent, context: Context) => {
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
    new FastifyAdapter({ logger: false, trustProxy: true }),
  );

  app.setGlobalPrefix('api');
  await app.init();

  return awsLambdaFastify(app.getHttpAdapter().getInstance(), {
    binaryMimeTypes: ['application/pdf', 'image/*'],
  });
}

export const handler: Handler = async (event: APIGatewayProxyEvent, context: Context) => {
  if (!cachedProxy) {
    cachedProxy = await bootstrap();
  }
  return cachedProxy(event, context);
};
```

## Lifecycle Management

```typescript
// Lambda lifecycle service
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';

@Injectable()
export class LambdaLifecycleService implements OnModuleInit, OnModuleDestroy {
  onModuleInit() {
    console.log('[Lambda] Module initializing...');
  }

  onModuleDestroy() {
    // Cleanup before Lambda container is frozen
    console.log('[Lambda] Module destroying - cleanup resources');
  }
}
```

## Environment Configuration

```typescript
// src/config/lambda.config.ts
export const lambdaConfig = () => ({
  lambda: {
    functionName: process.env.AWS_LAMBDA_FUNCTION_NAME,
    memorySize: parseInt(process.env.AWS_LAMBDA_FUNCTION_MEMORY_SIZE || '512', 10),
    region: process.env.AWS_REGION,
    keepAlive: process.env.KEEP_ALIVE === 'true',
    skipSwagger: process.env.NODE_ENV === 'production',
  },
  features: {
    enableCache: process.env.ENABLE_CACHE === 'true',
    enableLogging: process.env.ENABLE_LOGGING !== 'false',
    enableMetrics: process.env.ENABLE_METRICS === 'true',
  },
});
```

## Error Handling

```typescript
// Lambda error filter
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

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();
      message = typeof exceptionResponse === 'string'
        ? exceptionResponse
        : (exceptionResponse as any).message || message;
    }

    this.logger.error({ error: exception instanceof Error ? exception.message : 'Unknown error', status });

    response.status(status).json({
      statusCode: status,
      message,
      requestId: process.env.AWS_REQUEST_ID,
      timestamp: new Date().toISOString(),
    });
  }
}
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
@Controller('health')
export class HealthController {
  @Get()
  check() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV,
    };
  }
}
```

### Request Context Interceptor

```typescript
@Injectable()
export class LambdaContextInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();

    request.lambdaContext = {
      requestId: request.headers['x-amzn-requestid'],
      traceId: request.headers['x-amzn-trace-id'],
    };

    return next.handle();
  }
}
```

## Examples

### Example 1: Basic Express Lambda Handler

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

```yaml
# serverless.yml
service: nestjs-lambda-api

provider:
  name: aws
  runtime: nodejs20.x
  memorySize: 512
  timeout: 29

functions:
  api:
    handler: dist/lambda.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

## Constraints and Warnings

### Lambda Limitations

- **Timeout**: Maximum 29 seconds (API Gateway), 15 minutes for async invocations
- **Memory**: 128 MB to 10 GB (cost increases with memory)
- **Payload size**: Request/response limited to 6 MB (API Gateway)
- **Cold starts**: Can range from 100ms to several seconds depending on initialization

### Common Pitfalls

1. **Don't initialize connections in constructor**: Use lazy initialization
2. **Don't rely on in-memory state**: Containers can be frozen and reused
3. **Don't use traditional server patterns**: Disable keep-alive connections
4. **Don't forget to close connections**: Implement `OnModuleDestroy` for cleanup

### Security Considerations

- Use AWS Secrets Manager or SSM Parameter Store for sensitive data
- Configure CORS properly to avoid unauthorized access
- Validate all incoming requests

## References

- [references/testing.md](references/testing.md) - Unit and integration testing patterns
- [references/serverless-config.md](references/serverless-config.md) - Serverless Framework and SAM configuration
- [references/raw-typescript-lambda.md](references/raw-typescript-lambda.md) - Minimal TypeScript Lambda without frameworks
- [references/serverless-deployment.md](references/serverless-deployment.md) - Deployment strategies and CI/CD
