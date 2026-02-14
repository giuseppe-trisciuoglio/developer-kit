# Express Adapter for Lambda

## Overview

Detailed configuration options and advanced patterns for using the Express adapter with AWS Lambda.

## Installation

```bash
npm install @codegenie/serverless-express express
npm install -D @types/express
```

## Configuration Options

### serverless-express Options

```typescript
serverlessExpress({
  app: expressApp,

  // Binary MIME types for file uploads/downloads
  binaryMimeTypes: [
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/gif',
    'application/zip',
  ],

  // Request transformation
  request: (request, event, context) => {
    // Add Lambda context to request
    request.lambdaEvent = event;
    request.lambdaContext = context;
  },

  // Response transformation
  response: (response, event, context) => {
    // Add custom headers
    response.set('X-Request-Id', context.awsRequestId);
  },
});
```

## API Gateway v1 vs v2

### API Gateway v1 (REST API)

```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';

// Default format, fully featured
const server = serverlessExpress({ app: expressApp });

export const handler = async (
  event: APIGatewayProxyEvent,
  context: Context,
): Promise<APIGatewayProxyResult> => {
  return server(event, context);
};
```

### API Gateway v2 (HTTP API)

```typescript
import { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';

// Simpler, cheaper, but different event format
const server = serverlessExpress({
  app: expressApp,
  eventSource: {
    getRequest: (event: APIGatewayProxyEventV2) => ({
      method: event.requestContext.http.method,
      url: event.rawPath + (event.rawQueryString ? `?${event.rawQueryString}` : ''),
      headers: event.headers,
      body: event.body,
    }),
    getResponse: (response) => ({
      statusCode: response.statusCode,
      headers: response.headers,
      body: response.body,
      // v2 format
      cookies: response.cookies,
    }),
  },
});
```

## Middleware Configuration

### Compression

```typescript
import compression from 'compression';

// Enable compression for responses
expressApp.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
  level: 6, // Balance between speed and compression
}));
```

### Body Parsing

```typescript
import bodyParser from 'body-parser';

// JSON body parser with size limits
expressApp.use(bodyParser.json({
  limit: '10mb',
  strict: true,
}));

// URL encoded parser
expressApp.use(bodyParser.urlencoded({
  extended: true,
  limit: '10mb',
}));

// Raw body for webhooks
expressApp.use('/webhooks', bodyParser.raw({
  type: 'application/json',
  verify: (req, res, buf) => {
    // Store raw body for signature verification
    (req as any).rawBody = buf;
  },
}));
```

## Session Handling

### DynamoDB Session Store

```typescript
import session from 'express-session';
import DynamoDBStore from 'connect-dynamodb';

const DynamoDBStoreSession = DynamoDBStore(session);

expressApp.use(session({
  store: new DynamoDBStoreSession({
    table: 'sessions',
    hashKey: 'sessionId',
    readCapacityUnits: 5,
    writeCapacityUnits: 5,
  }),
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,
    httpOnly: true,
    maxAge: 1000 * 60 * 60 * 24, // 24 hours
    sameSite: 'strict',
  },
}));
```

## Security Headers

### Helmet Configuration

```typescript
import helmet from 'helmet';

expressApp.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
  // Disable features not needed for API
  xssFilter: true,
  noSniff: true,
  referrerPolicy: { policy: 'same-origin' },
}));
```

## Rate Limiting

### Express Rate Limit

```typescript
import rateLimit from 'express-rate-limit';

// Simple in-memory rate limit (use Redis for multi-instance)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    statusCode: 429,
    error: 'Too Many Requests',
    message: 'Rate limit exceeded. Please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

expressApp.use('/api/', limiter);
```

## Error Handling

### Global Express Error Handler

```typescript
// Must be last middleware
expressApp.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error({
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  // Don't leak error details in production
  const isDev = process.env.NODE_ENV !== 'production';

  res.status(err.status || 500).json({
    statusCode: err.status || 500,
    error: err.name || 'InternalServerError',
    message: isDev ? err.message : 'Internal server error',
    ...(isDev && { stack: err.stack }),
  });
});
```

## Performance Optimization

### Connection Keep-Alive

```typescript
// Enable keep-alive for connection reuse
expressApp.use((req, res, next) => {
  res.setHeader('Connection', 'keep-alive');
  next();
});
```

### Response Caching

```typescript
import apicache from 'apicache';

const cache = apicache.middleware;

// Cache GET requests for 5 minutes
expressApp.use('/api/public/', cache('5 minutes', (req) => req.method === 'GET'));
```

## Logging

### Morgan with CloudWatch

```typescript
import morgan from 'morgan';

// Custom format for CloudWatch
expressApp.use(morgan((tokens, req, res) => {
  return JSON.stringify({
    method: tokens.method(req, res),
    url: tokens.url(req, res),
    status: tokens.status(req, res),
    responseTime: tokens['response-time'](req, res),
    contentLength: tokens.res(req, res, 'content-length'),
    userAgent: tokens['user-agent'](req, res),
    timestamp: new Date().toISOString(),
  });
}));
```
