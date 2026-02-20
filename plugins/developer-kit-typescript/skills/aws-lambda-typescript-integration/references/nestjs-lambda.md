# NestJS Lambda Reference

Complete guide for deploying NestJS applications on AWS Lambda with optimal performance.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Lambda Handler](#lambda-handler)
3. [Platform Adapters](#platform-adapters)
4. [Cold Start Optimization](#cold-start-optimization)
5. [Lifecycle Management](#lifecycle-management)
6. [Deployment](#deployment)

---

## Project Setup

### Installation

```bash
# Create new NestJS project
nest new my-lambda-api
cd my-lambda-api

# Install Lambda dependencies
npm install @codegenie/serverless-express aws-lambda
npm install -D @types/aws-lambda serverless-offline

# Optional: Fastify adapter for better performance
npm install @nestjs/platform-fastify aws-lambda-fastify
```

### Project Structure

```
my-nestjs-lambda/
├── src/
│   ├── app.module.ts
│   ├── main.ts                 # Standard NestJS entry
│   ├── lambda.ts               # Lambda entry point
│   ├── config/
│   │   └── lambda.config.ts
│   └── modules/
│       └── api/
│           ├── api.controller.ts
│           └── api.service.ts
├── test/
├── package.json
├── tsconfig.json
├── serverless.yml
└── webpack.config.js           # For bundling
```

---

## Lambda Handler

### Basic Express Adapter

```typescript
// lambda.ts
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { Context, Handler, APIGatewayProxyEvent } from 'aws-lambda';
import express from 'express';
import { AppModule } from './src/app.module';

let cachedServer: Handler;

async function bootstrap(): Promise<Handler> {
  const expressApp = express();
  const adapter = new ExpressAdapter(expressApp);

  const nestApp = await NestFactory.create(AppModule, adapter);

  // Enable CORS
  nestApp.enableCors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || [],
    credentials: true,
  });

  // Set global prefix
  nestApp.setGlobalPrefix('api');

  await nestApp.init();

  return serverlessExpress({ app: expressApp });
}

export const handler: Handler = async (
  event: APIGatewayProxyEvent,
  context: Context,
) => {
  if (!cachedServer) {
    cachedServer = await bootstrap();
  }
  return cachedServer(event, context);
};
```

---

## Platform Adapters

### Express Adapter (Recommended)

Best compatibility with existing middleware and ecosystem.

```typescript
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { AppModule } from './src/app.module';

let server: Handler;

async function bootstrap(): Promise<Handler> {
  const expressApp = express();
  const app = await NestFactory.create(
    AppModule,
    new ExpressAdapter(expressApp),
  );

  // Apply global settings
  app.setGlobalPrefix('api');
  app.enableCors();

  await app.init();
  return serverlessExpress({ app: expressApp });
}
```

### Fastify Adapter (Performance)

Better performance but smaller ecosystem.

```typescript
import { NestFactory } from '@nestjs/core';
import {
  FastifyAdapter,
  NestFastifyApplication,
} from '@nestjs/platform-fastify';
import awsLambdaFastify from 'aws-lambda-fastify';

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

export const handler: Handler = async (event, context) => {
  if (!cachedProxy) {
    cachedProxy = await bootstrap();
  }
  return cachedProxy(event, context);
};
```

---

## Cold Start Optimization

### Lazy Loading

Defer heavy module initialization:

```typescript
// config/swagger.config.ts
export async function setupSwagger(app: INestApplication) {
  if (process.env.ENABLE_SWAGGER !== 'true') return;

  // Lazy load Swagger only when needed
  const { SwaggerModule, DocumentBuilder } = await import('@nestjs/swagger');

  const config = new DocumentBuilder()
    .setTitle('API')
    .setVersion('1.0')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);
}
```

### Environment-Based Feature Loading

```typescript
// lambda.ts
async function bootstrap(): Promise<Handler> {
  const app = await NestFactory.create(AppModule);

  // Conditional feature loading
  if (process.env.NODE_ENV !== 'production') {
    await setupSwagger(app);
  }

  // Only enable logging in non-production
  if (process.env.ENABLE_LOGGING === 'true') {
    app.useLogger(new CloudWatchLogger());
  }

  await app.init();
  return serverlessExpress({ app: expressApp });
}
```

### Connection Pooling

```typescript
// database.module.ts
import { Module } from '@nestjs/common';

@Module({
  providers: [
    {
      provide: 'DATABASE_CONFIG',
      useValue: {
        // Lambda-optimized pool settings
        max: 1, // Maximum 1 connection for Lambda
        min: 0, // Allow zero connections when idle
        acquireTimeoutMillis: 5000,
        idleTimeoutMillis: 10000,
      },
    },
  ],
})
export class DatabaseModule {}
```

---

## Lifecycle Management

### Module Lifecycle Hooks

```typescript
// lambda-lifecycle.service.ts
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';

@Injectable()
export class LambdaLifecycleService
  implements OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(LambdaLifecycleService.name);

  onModuleInit() {
    this.logger.log('[Lambda] Module initializing...');
    // Setup resources
  }

  onModuleDestroy() {
    this.logger.log('[Lambda] Module destroying - cleanup resources');
    // Cleanup before Lambda container freeze
  }
}
```

### Graceful Shutdown

```typescript
// main.ts (for local dev)
async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable shutdown hooks
  app.enableShutdownHooks();

  await app.listen(3000);
}

// lambda.ts (for Lambda)
async function bootstrap(): Promise<Handler> {
  const app = await NestFactory.create(AppModule);

  // No shutdown hooks needed - Lambda handles container lifecycle
  await app.init();

  return serverlessExpress({ app: expressApp });
}
```

---

## Deployment

### Serverless Framework

```yaml
# serverless.yml
service: nestjs-lambda-api

provider:
  name: aws
  runtime: nodejs20.x
  memorySize: 512
  timeout: 29
  environment:
    NODE_ENV: production
    AWS_NODEJS_CONNECTION_REUSE_ENABLED: '1'

functions:
  api:
    handler: dist/lambda.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true

plugins:
  - serverless-offline

custom:
  serverless-offline:
    httpPort: 3000
```

### AWS SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 29
    MemorySize: 512
    Runtime: nodejs20.x
    Environment:
      Variables:
        NODE_ENV: production

Resources:
  NestJSApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: dist/
      Handler: lambda.handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/'
```

### Build Configuration

```javascript
// webpack.config.js
const path = require('path');
const nodeExternals = require('webpack-node-externals');

module.exports = {
  entry: './src/lambda.ts',
  target: 'node',
  mode: 'production',
  externals: [nodeExternals()],
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.ts', '.js'],
  },
  output: {
    filename: 'lambda.js',
    path: path.resolve(__dirname, 'dist'),
    libraryTarget: 'commonjs2',
  },
};
```

---

## Best Practices

1. **Always cache the NestJS instance** - Critical for warm starts
2. **Use lazy loading** - Defer non-critical initialization
3. **Optimize connection pooling** - Max 1-2 connections for Lambda
4. **Bundle with webpack/esbuild** - Minimize deployment package
5. **Monitor cold starts** - Log initialization times
6. **Use provisioned concurrency** - For latency-sensitive APIs
7. **Implement health checks** - For ALB target group health
8. **Validate environment** - Fail fast on missing config
