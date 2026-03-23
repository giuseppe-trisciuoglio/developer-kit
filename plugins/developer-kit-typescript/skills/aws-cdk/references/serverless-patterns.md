# AWS CDK Serverless Patterns

## Table of Contents

- [Lambda Functions](#lambda-functions)
- [API Gateway Integration](#api-gateway-integration)
- [DynamoDB Tables](#dynamodb-tables)
- [S3 Event Processing](#s3-event-processing)
- [Step Functions](#step-functions)
- [EventBridge Rules](#eventbridge-rules)
- [SQS and SNS](#sqs-and-sns)
- [Complete Serverless API Pattern](#complete-serverless-api-pattern)

---

## Lambda Functions

### Basic Lambda Function

```typescript
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Duration } from 'aws-cdk-lib';

const fn = new lambda.Function(this, 'MyFunction', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda/my-function'),
  timeout: Duration.seconds(30),
  memorySize: 256,
  environment: {
    NODE_ENV: 'production',
  },
});
```

### NodejsFunction (TypeScript with esbuild)

```typescript
import * as lambdaNode from 'aws-cdk-lib/aws-lambda-nodejs';

const fn = new lambdaNode.NodejsFunction(this, 'TsFunction', {
  entry: 'lambda/handler.ts',
  handler: 'handler',
  runtime: lambda.Runtime.NODEJS_20_X,
  timeout: Duration.seconds(30),
  memorySize: 256,
  bundling: {
    minify: true,
    sourceMap: true,
    externalModules: ['@aws-sdk/*'],
    format: lambdaNode.OutputFormat.ESM,
  },
  environment: {
    NODE_OPTIONS: '--enable-source-maps',
  },
});
```

### Lambda Layers

```typescript
const layer = new lambda.LayerVersion(this, 'SharedLayer', {
  code: lambda.Code.fromAsset('layers/shared'),
  compatibleRuntimes: [lambda.Runtime.NODEJS_20_X],
  description: 'Shared utilities and dependencies',
});

const fn = new lambda.Function(this, 'Fn', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda/handler'),
  layers: [layer],
});
```

### Lambda with Dead Letter Queue

```typescript
import * as sqs from 'aws-cdk-lib/aws-sqs';

const dlq = new sqs.Queue(this, 'DLQ', {
  retentionPeriod: Duration.days(14),
});

const fn = new lambda.Function(this, 'Fn', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda'),
  deadLetterQueue: dlq,
  retryAttempts: 2,
});
```

---

## API Gateway Integration

### REST API with Lambda

```typescript
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

const api = new apigateway.RestApi(this, 'ItemsApi', {
  restApiName: 'Items Service',
  description: 'CRUD API for items',
  deployOptions: {
    stageName: 'prod',
    throttlingBurstLimit: 100,
    throttlingRateLimit: 50,
  },
  defaultCorsPreflightOptions: {
    allowOrigins: apigateway.Cors.ALL_ORIGINS,
    allowMethods: apigateway.Cors.ALL_METHODS,
  },
});

const items = api.root.addResource('items');
items.addMethod('GET', new apigateway.LambdaIntegration(listFn));
items.addMethod('POST', new apigateway.LambdaIntegration(createFn));

const item = items.addResource('{id}');
item.addMethod('GET', new apigateway.LambdaIntegration(getFn));
item.addMethod('PUT', new apigateway.LambdaIntegration(updateFn));
item.addMethod('DELETE', new apigateway.LambdaIntegration(deleteFn));
```

### HTTP API (API Gateway v2)

```typescript
import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';

const httpApi = new apigatewayv2.HttpApi(this, 'HttpApi', {
  apiName: 'My HTTP API',
  corsPreflight: {
    allowOrigins: ['https://myapp.com'],
    allowMethods: [apigatewayv2.CorsHttpMethod.GET, apigatewayv2.CorsHttpMethod.POST],
  },
});

httpApi.addRoutes({
  path: '/items',
  methods: [apigatewayv2.HttpMethod.GET],
  integration: new integrations.HttpLambdaIntegration('ListItems', listFn),
});
```

### LambdaRestApi (L3 Pattern)

```typescript
// Shortcut: creates API Gateway + proxy integration
const api = new apigateway.LambdaRestApi(this, 'QuickApi', {
  handler: handlerFn,
  proxy: true,  // All requests forwarded to Lambda
});
```

---

## DynamoDB Tables

### Single Table Design

```typescript
import { RemovalPolicy } from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

const table = new dynamodb.Table(this, 'MainTable', {
  partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  pointInTimeRecovery: true,
  removalPolicy: RemovalPolicy.RETAIN,
  stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
});

// Global Secondary Index
table.addGlobalSecondaryIndex({
  indexName: 'GSI1',
  partitionKey: { name: 'GSI1PK', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'GSI1SK', type: dynamodb.AttributeType.STRING },
  projectionType: dynamodb.ProjectionType.ALL,
});

// Grant permissions to Lambda
table.grantReadWriteData(handlerFn);
```

### DynamoDB Stream Processing

```typescript
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';

const streamProcessor = new lambda.Function(this, 'StreamProcessor', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'stream.handler',
  code: lambda.Code.fromAsset('lambda/stream'),
});

streamProcessor.addEventSource(new lambdaEventSources.DynamoEventSource(table, {
  startingPosition: lambda.StartingPosition.TRIM_HORIZON,
  batchSize: 100,
  retryAttempts: 3,
  bisectBatchOnError: true,
}));
```

---

## S3 Event Processing

```typescript
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';

const uploadBucket = new s3.Bucket(this, 'UploadBucket', {
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
});

const processor = new lambda.Function(this, 'ImageProcessor', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda/image-processor'),
  timeout: Duration.minutes(5),
  memorySize: 1024,
});

uploadBucket.grantRead(processor);

uploadBucket.addEventNotification(
  s3.EventType.OBJECT_CREATED,
  new s3n.LambdaDestination(processor),
  { prefix: 'uploads/', suffix: '.jpg' },
);
```

---

## Step Functions

```typescript
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';

const validateOrder = new tasks.LambdaInvoke(this, 'ValidateOrder', {
  lambdaFunction: validateFn,
  outputPath: '$.Payload',
});

const processPayment = new tasks.LambdaInvoke(this, 'ProcessPayment', {
  lambdaFunction: paymentFn,
  outputPath: '$.Payload',
});

const sendConfirmation = new tasks.LambdaInvoke(this, 'SendConfirmation', {
  lambdaFunction: confirmFn,
});

const handleFailure = new tasks.LambdaInvoke(this, 'HandleFailure', {
  lambdaFunction: failureFn,
});

const definition = validateOrder
  .next(new sfn.Choice(this, 'IsValid?')
    .when(sfn.Condition.booleanEquals('$.isValid', true),
      processPayment.next(sendConfirmation))
    .otherwise(handleFailure));

new sfn.StateMachine(this, 'OrderWorkflow', {
  definitionBody: sfn.DefinitionBody.fromChainable(definition),
  timeout: Duration.minutes(5),
  tracingEnabled: true,
});
```

---

## EventBridge Rules

```typescript
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';

// Scheduled rule
new events.Rule(this, 'DailyCleanup', {
  schedule: events.Schedule.cron({ hour: '2', minute: '0' }),
  targets: [new targets.LambdaFunction(cleanupFn)],
});

// Custom event pattern
new events.Rule(this, 'OrderCreated', {
  eventPattern: {
    source: ['my-app.orders'],
    detailType: ['OrderCreated'],
  },
  targets: [
    new targets.LambdaFunction(processFn),
    new targets.SqsQueue(auditQueue),
  ],
});
```

---

## SQS and SNS

```typescript
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as snsSubscriptions from 'aws-cdk-lib/aws-sns-subscriptions';

// SNS Topic
const topic = new sns.Topic(this, 'OrderTopic', {
  displayName: 'Order Notifications',
});

// SQS Queue with DLQ
const dlq = new sqs.Queue(this, 'DLQ');
const queue = new sqs.Queue(this, 'OrderQueue', {
  visibilityTimeout: Duration.seconds(300),
  deadLetterQueue: { queue: dlq, maxReceiveCount: 3 },
});

// Subscribe SQS to SNS
topic.addSubscription(new snsSubscriptions.SqsSubscription(queue));

// Lambda consumes from SQS
const consumer = new lambda.Function(this, 'Consumer', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda/consumer'),
});

consumer.addEventSource(new lambdaEventSources.SqsEventSource(queue, {
  batchSize: 10,
  maxBatchingWindow: Duration.seconds(5),
}));
```

---

## Complete Serverless API Pattern

Full example combining Lambda, API Gateway, DynamoDB, and proper IAM:

```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as lambdaNode from 'aws-cdk-lib/aws-lambda-nodejs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as logs from 'aws-cdk-lib/aws-logs';

export class CrudApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const table = new dynamodb.Table(this, 'ItemsTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Shared Lambda configuration
    const sharedProps: Partial<lambdaNode.NodejsFunctionProps> = {
      runtime: lambda.Runtime.NODEJS_20_X,
      timeout: cdk.Duration.seconds(10),
      memorySize: 256,
      environment: { TABLE_NAME: table.tableName },
      logRetention: logs.RetentionDays.ONE_WEEK,
      bundling: { minify: true, sourceMap: true },
    };

    // CRUD Functions
    const createFn = new lambdaNode.NodejsFunction(this, 'CreateFn', {
      ...sharedProps, entry: 'lambda/create.ts',
    });
    const listFn = new lambdaNode.NodejsFunction(this, 'ListFn', {
      ...sharedProps, entry: 'lambda/list.ts',
    });
    const getFn = new lambdaNode.NodejsFunction(this, 'GetFn', {
      ...sharedProps, entry: 'lambda/get.ts',
    });
    const deleteFn = new lambdaNode.NodejsFunction(this, 'DeleteFn', {
      ...sharedProps, entry: 'lambda/delete.ts',
    });

    // Least-privilege permissions
    table.grantWriteData(createFn);
    table.grantReadData(listFn);
    table.grantReadData(getFn);
    table.grantWriteData(deleteFn);

    // API Gateway
    const api = new apigateway.RestApi(this, 'ItemsApi', {
      restApiName: 'Items CRUD',
      deployOptions: { stageName: 'v1' },
    });

    const items = api.root.addResource('items');
    items.addMethod('POST', new apigateway.LambdaIntegration(createFn));
    items.addMethod('GET', new apigateway.LambdaIntegration(listFn));

    const item = items.addResource('{id}');
    item.addMethod('GET', new apigateway.LambdaIntegration(getFn));
    item.addMethod('DELETE', new apigateway.LambdaIntegration(deleteFn));

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', { value: api.url });
    new cdk.CfnOutput(this, 'TableName', { value: table.tableName });
  }
}
```
