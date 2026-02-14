# Fastify Adapter for Lambda

## Overview

Fastify offers superior performance compared to Express for Lambda workloads, with lower cold start times and better throughput.

## Installation

```bash
npm install @nestjs/platform-fastify fastify aws-lambda-fastify
npm install -D @types/aws-lambda
```

## Basic Configuration

### Standard Setup

```typescript
import { NestFactory } from '@nestjs/core';
import { FastifyAdapter, NestFastifyApplication } from '@nestjs/platform-fastify';
import awsLambdaFastify from 'aws-lambda-fastify';
import { AppModule } from './app.module';

let cachedProxy: any;

async function bootstrap() {
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter({
      logger: false,
      trustProxy: true,
      genReqId: () => `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    }),
  );

  await app.init();

  return awsLambdaFastify(app.getHttpAdapter().getInstance(), {
    binaryMimeTypes: ['application/pdf', 'image/*'],
    serializeLambdaArguments: false,
  });
}

export const handler = async (event, context) => {
  if (!cachedProxy) {
    cachedProxy = await bootstrap();
  }
  return cachedProxy(event, context);
};
```

## Fastify Options

### Performance Tuning

```typescript
const adapter = new FastifyAdapter({
  // Disable logging for cold start performance
  logger: false,

  // Trust proxy headers from API Gateway
  trustProxy: true,

  // Connection timeout (Lambda max is 30s)
  connectionTimeout: 29000,

  // Keep alive timeout
  keepAliveTimeout: 5000,

  // Max payload size (API Gateway limit is 10MB)
  bodyLimit: 10485760,

  // Case-sensitive routing
  caseSensitive: true,

  // Ignore trailing slashes
  ignoreTrailingSlash: true,

  // Max param length for URL parameters
  maxParamLength: 100,
});
```

## Plugins

### Compression

```typescript
import compression from '@fastify/compress';

// Register compression plugin
app.register(compression, {
  global: true,
  encodings: ['gzip', 'deflate'],
  threshold: 1024, // Only compress responses > 1KB
});
```

### CORS

```typescript
import cors from '@fastify/cors';

app.register(cors, {
  origin: (origin, cb) => {
    const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];
    if (!origin || allowedOrigins.includes(origin)) {
      cb(null, true);
      return;
    }
    cb(new Error('Not allowed'), false);
  },
  credentials: true,
  methods: ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-Id'],
});
```

### Helmet (Security Headers)

```typescript
import helmet from '@fastify/helmet';

app.register(helmet, {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
  },
});
```

### Rate Limit

```typescript
import rateLimit from '@fastify/rate-limit';

app.register(rateLimit, {
  max: 100,
  timeWindow: '15 minutes',
  keyGenerator: (req) => req.headers['x-forwarded-for'] || req.ip,
  errorResponseBuilder: (req, context) => ({
    statusCode: 429,
    error: 'Too Many Requests',
    message: `Rate limit exceeded. Try again in ${context.after}`,
    retryAfter: context.after,
  }),
});
```

## Request/Response Hooks

### Lifecycle Hooks

```typescript
// On request hook
app.getHttpAdapter().getInstance().addHook('onRequest', async (request, reply) => {
  // Add request ID
  reply.header('x-request-id', request.id);

  // Log request
  console.log({
    event: 'request_start',
    method: request.method,
    url: request.url,
    requestId: request.id,
    timestamp: new Date().toISOString(),
  });
});

// On send hook
app.getHttpAdapter().getInstance().addHook('onSend', async (request, reply, payload) => {
  // Log response
  console.log({
    event: 'request_end',
    method: request.method,
    url: request.url,
    statusCode: reply.statusCode,
    duration: Date.now() - (request as any).startTime,
  });
});
```

## Validation

### JSON Schema Validation

```typescript
// Fastify uses JSON Schema for validation
const createUserSchema = {
  schema: {
    body: {
      type: 'object',
      required: ['name', 'email'],
      properties: {
        name: { type: 'string', minLength: 1, maxLength: 100 },
        email: { type: 'string', format: 'email' },
        age: { type: 'integer', minimum: 0, maximum: 150 },
      },
    },
    response: {
      201: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          email: { type: 'string' },
        },
      },
    },
  },
};

// Use in controller
@Post()
@UsePipes(new ValidationPipe())
async create(@Body() createUserDto: CreateUserDto) {
  return this.usersService.create(createUserDto);
}
```

## Serialization

### Custom Serializer

```typescript
// Fastify-serialize options
app.register(require('@fastify/response-validation'), {
  onError: (error) => {
    console.error('Response validation error:', error);
  },
});

// Use class-transformer for serialization
@Controller('users')
@UseInterceptors(ClassSerializerInterceptor)
export class UsersController {
  // Responses automatically serialized
}
```

## Error Handling

### Global Error Handler

```typescript
// Set error handler on Fastify instance
app.getHttpAdapter().getInstance().setErrorHandler((error, request, reply) => {
  console.error({
    error: error.message,
    stack: error.stack,
    code: error.code,
    validation: error.validation,
  });

  // Handle validation errors
  if (error.validation) {
    reply.status(400).send({
      statusCode: 400,
      error: 'Bad Request',
      message: error.message,
      validation: error.validation,
    });
    return;
  }

  // Handle other errors
  const statusCode = error.statusCode || 500;
  reply.status(statusCode).send({
    statusCode,
    error: error.name || 'Internal Server Error',
    message: process.env.NODE_ENV === 'production'
      ? 'Internal server error'
      : error.message,
  });
});
```

## File Upload

### Multipart Support

```typescript
import multipart from '@fastify/multipart';

app.register(multipart, {
  limits: {
    fieldNameSize: 100,
    fieldSize: 1000000, // 1MB
    fields: 10,
    fileSize: 10000000, // 10MB
    files: 5,
  },
});

// Controller handling
@Post('upload')
async upload(@Req() req: FastifyRequest) {
  const data = await req.file();

  // Process file
  const buffer = await data.toBuffer();

  return {
    filename: data.filename,
    mimetype: data.mimetype,
    size: buffer.length,
  };
}
```

## Performance Comparison

### Benchmarks

| Metric | Express | Fastify | Improvement |
|--------|---------|---------|-------------|
| Cold Start | ~250ms | ~180ms | 28% faster |
| Throughput | 15k req/s | 25k req/s | 67% higher |
| Memory Usage | 85MB | 65MB | 24% less |
| JSON Parsing | 12k ops/s | 25k ops/s | 108% faster |

### When to Choose Fastify

- **High throughput APIs** - Many concurrent requests
- **JSON-heavy APIs** - Superior JSON parsing performance
- **Memory-constrained environments** - Lower memory footprint
- **Cold start sensitive** - Faster initialization

### When to Choose Express

- **Existing Express middleware** - Large ecosystem compatibility
- **Migration projects** - Easier migration path
- **Complex routing** - More mature routing patterns
- **Team familiarity** - If team knows Express well
