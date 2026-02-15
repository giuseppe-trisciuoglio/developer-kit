# Testing Lambda Functions

Complete guide for testing NestJS Lambda handlers including unit tests, integration tests, and mocking strategies.

## Unit Tests for Handler

Test the Lambda handler in isolation with mocked AWS Lambda context.

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

## Integration Test with serverless-offline

Test the full request/response cycle using the serverless-offline plugin.

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

## Mocking Strategies

### Mock AWS Services

```typescript
// __mocks__/aws-sdk.ts
export const mockSend = jest.fn();

export const DynamoDBClient = jest.fn(() => ({
  send: mockSend,
}));

export const GetItemCommand = jest.fn();
export const PutItemCommand = jest.fn();
```

### Mock NestJS Services

```typescript
// test/mocks/services.mock.ts
export const createMockUserService = () => ({
  findById: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn(),
});

// In test
const mockUserService = createMockUserService();
mockUserService.findById.mockResolvedValue({ id: '123', name: 'Test' });
```

### Mock Lambda Context

```typescript
// test/utils/lambda-context.ts
import { Context } from 'aws-lambda';

export function createMockContext(overrides?: Partial<Context>): Context {
  return {
    awsRequestId: 'test-request-id',
    functionName: 'test-function',
    memoryLimitInMB: '512',
    invokedFunctionArn: 'arn:aws:lambda:us-east-1:123456789:function:test',
    getRemainingTimeInMillis: () => 30000,
    done: () => {},
    fail: () => {},
    succeed: () => {},
    ...overrides,
  } as Context;
}
```

## Best Practices for Testing

1. **Reset module cache** between tests to test cold/warm start behavior
2. **Mock external services** (DynamoDB, S3, etc.) to avoid real AWS calls
3. **Test both cold and warm starts** to verify caching works correctly
4. **Use realistic event payloads** matching API Gateway format
5. **Measure timing** for warm invocations to detect performance regressions
6. **Test error scenarios** including timeouts and service failures
