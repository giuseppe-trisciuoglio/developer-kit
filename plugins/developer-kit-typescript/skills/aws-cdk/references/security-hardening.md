# AWS CDK Security Hardening

## Table of Contents

- [IAM Least Privilege](#iam-least-privilege)
- [KMS Encryption](#kms-encryption)
- [Secrets Manager](#secrets-manager)
- [Resource Policies](#resource-policies)
- [WAF Integration](#waf-integration)
- [Security Compliance Patterns](#security-compliance-patterns)
- [Secure Defaults Checklist](#secure-defaults-checklist)

---

## IAM Least Privilege

### Grant Helpers (Recommended)

CDK L2 constructs provide `.grant*()` methods that generate least-privilege IAM policies automatically.

```typescript
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';

const bucket = new s3.Bucket(this, 'Bucket');
const table = new dynamodb.Table(this, 'Table', {
  partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
});

const fn = new lambda.Function(this, 'Fn', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda'),
});

// Least-privilege grants — only necessary actions
bucket.grantRead(fn);           // s3:GetObject, s3:GetBucket*
table.grantReadWriteData(fn);   // dynamodb:GetItem, PutItem, UpdateItem, DeleteItem, Query, Scan
```

### Custom IAM Policies

When grant helpers are insufficient, create targeted policies:

```typescript
import * as iam from 'aws-cdk-lib/aws-iam';

fn.addToRolePolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: ['ses:SendEmail', 'ses:SendRawEmail'],
  resources: [`arn:aws:ses:${this.region}:${this.account}:identity/*`],
  conditions: {
    StringEquals: { 'ses:FromAddress': 'noreply@myapp.com' },
  },
}));
```

### Service Roles

```typescript
const role = new iam.Role(this, 'LambdaRole', {
  assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
  managedPolicies: [
    iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
  ],
  description: 'Role for order processing Lambda',
});

// Add permissions boundary
const boundary = iam.ManagedPolicy.fromAwsManagedPolicyName('PowerUserAccess');
iam.PermissionsBoundary.of(role).apply(boundary);
```

### Cross-Account Access

```typescript
const crossAccountRole = new iam.Role(this, 'CrossAccountRole', {
  assumedBy: new iam.AccountPrincipal('999999999999'),
  externalIds: ['unique-external-id'],
});

bucket.grantRead(crossAccountRole);
```

---

## KMS Encryption

### Customer-Managed Key

```typescript
import { RemovalPolicy } from 'aws-cdk-lib';
import * as kms from 'aws-cdk-lib/aws-kms';

const key = new kms.Key(this, 'AppKey', {
  alias: 'my-app-key',
  description: 'Encryption key for application data',
  enableKeyRotation: true,
  removalPolicy: RemovalPolicy.RETAIN,
});

// Encrypt S3 bucket
const encryptedBucket = new s3.Bucket(this, 'EncryptedBucket', {
  encryption: s3.BucketEncryption.KMS,
  encryptionKey: key,
  bucketKeyEnabled: true,  // Reduces KMS API calls
});

// Encrypt DynamoDB table
const encryptedTable = new dynamodb.Table(this, 'EncryptedTable', {
  partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
  encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
  encryptionKey: key,
});

// Grant decrypt to Lambda
key.grantDecrypt(fn);
```

### SQS Encryption

```typescript
const encryptedQueue = new sqs.Queue(this, 'EncryptedQueue', {
  encryption: sqs.QueueEncryption.KMS,
  encryptionMasterKey: key,
});
```

---

## Secrets Manager

### Creating and Using Secrets

```typescript
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

// Create a secret with auto-generated password
const dbSecret = new secretsmanager.Secret(this, 'DbSecret', {
  secretName: 'my-app/db-credentials',
  generateSecretString: {
    secretStringTemplate: JSON.stringify({ username: 'admin' }),
    generateStringKey: 'password',
    excludePunctuation: true,
    passwordLength: 32,
  },
});

// Use in RDS
import * as rds from 'aws-cdk-lib/aws-rds';

const database = new rds.DatabaseInstance(this, 'Database', {
  engine: rds.DatabaseInstanceEngine.postgres({
    version: rds.PostgresEngineVersion.VER_16,
  }),
  vpc,
  credentials: rds.Credentials.fromSecret(dbSecret),
  instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
});

// Grant Lambda read access to the secret
dbSecret.grantRead(fn);
```

### Referencing Secrets in Lambda

```typescript
const apiKeySecret = new secretsmanager.Secret(this, 'ApiKey', {
  secretName: 'my-app/api-key',
});

const fn = new lambda.Function(this, 'Fn', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda'),
  environment: {
    SECRET_ARN: apiKeySecret.secretArn,
  },
});

apiKeySecret.grantRead(fn);
```

### Secret Rotation

```typescript
import { Duration } from 'aws-cdk-lib';

dbSecret.addRotationSchedule('Rotation', {
  automaticallyAfter: Duration.days(30),
  hostedRotation: secretsmanager.HostedRotation.postgreSqlSingleUser({
    vpc,
    excludeCharacters: '"@/\\',
  }),
});
```

---

## Resource Policies

### S3 Bucket Policy

```typescript
const bucket = new s3.Bucket(this, 'SecureBucket', {
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  enforceSSL: true,
});

bucket.addToResourcePolicy(new iam.PolicyStatement({
  effect: iam.Effect.DENY,
  principals: [new iam.AnyPrincipal()],
  actions: ['s3:*'],
  resources: [bucket.bucketArn, `${bucket.bucketArn}/*`],
  conditions: {
    Bool: { 'aws:SecureTransport': 'false' },
  },
}));
```

### SQS Queue Policy

```typescript
queue.addToResourcePolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  principals: [new iam.ServicePrincipal('sns.amazonaws.com')],
  actions: ['sqs:SendMessage'],
  resources: [queue.queueArn],
  conditions: {
    ArnEquals: { 'aws:SourceArn': topic.topicArn },
  },
}));
```

---

## WAF Integration

```typescript
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';

const webAcl = new wafv2.CfnWebACL(this, 'WebAcl', {
  defaultAction: { allow: {} },
  scope: 'REGIONAL',
  visibilityConfig: {
    sampledRequestsEnabled: true,
    cloudWatchMetricsEnabled: true,
    metricName: 'MyApiWAF',
  },
  rules: [
    {
      name: 'AWSManagedRulesCommonRuleSet',
      priority: 1,
      overrideAction: { none: {} },
      statement: {
        managedRuleGroupStatement: {
          vendorName: 'AWS',
          name: 'AWSManagedRulesCommonRuleSet',
        },
      },
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: 'CommonRules',
      },
    },
    {
      name: 'RateLimitRule',
      priority: 2,
      action: { block: {} },
      statement: {
        rateBasedStatement: {
          limit: 2000,
          aggregateKeyType: 'IP',
        },
      },
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: 'RateLimit',
      },
    },
  ],
});

// Associate WAF with API Gateway
new wafv2.CfnWebACLAssociation(this, 'WafAssociation', {
  resourceArn: api.deploymentStage.stageArn,
  webAclArn: webAcl.attrArn,
});
```

---

## Security Compliance Patterns

### Enforce Tags with Aspects

```typescript
import { IAspect, Annotations, Tags } from 'aws-cdk-lib';
import { IConstruct } from 'constructs';
import { CfnResource } from 'aws-cdk-lib';

class RequiredTagsAspect implements IAspect {
  constructor(private requiredTags: string[]) {}

  visit(node: IConstruct): void {
    if (CfnResource.isCfnResource(node)) {
      for (const tag of this.requiredTags) {
        if (!Tags.of(node).tagValues()[tag]) {
          Annotations.of(node).addError(`Missing required tag: ${tag}`);
        }
      }
    }
  }
}

Aspects.of(app).add(new RequiredTagsAspect(['Environment', 'Owner', 'CostCenter']));
```

### Suppress Specific CDK Nag Rules

```typescript
import { NagSuppressions } from 'cdk-nag';

NagSuppressions.addResourceSuppressions(bucket, [
  {
    id: 'AwsSolutions-S1',
    reason: 'Access logging not required for this dev bucket',
  },
]);
```

---

## Secure Defaults Checklist

| Resource | Security Setting | CDK Property |
|----------|-----------------|--------------|
| S3 Bucket | Block public access | `blockPublicAccess: BLOCK_ALL` |
| S3 Bucket | Enforce SSL | `enforceSSL: true` |
| S3 Bucket | Enable encryption | `encryption: BucketEncryption.S3_MANAGED` |
| S3 Bucket | Enable versioning | `versioned: true` |
| DynamoDB | Enable PITR | `pointInTimeRecovery: true` |
| DynamoDB | Encryption | `encryption: TableEncryption.AWS_MANAGED` |
| Lambda | Timeout | `timeout: Duration.seconds(30)` |
| Lambda | Reserved concurrency | `reservedConcurrentExecutions: N` |
| RDS | Storage encryption | `storageEncrypted: true` |
| RDS | Multi-AZ | `multiAz: true` |
| RDS | Deletion protection | `deletionProtection: true` |
| API Gateway | Throttling | `deployOptions: { throttlingRateLimit }` |
| SQS | Encryption | `encryption: QueueEncryption.KMS` |
| SQS | Dead letter queue | `deadLetterQueue: { queue, maxReceiveCount }` |
