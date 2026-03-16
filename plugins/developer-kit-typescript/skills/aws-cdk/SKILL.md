---
name: aws-cdk
description: Provides comprehensive AWS CDK (Cloud Development Kit) patterns and best practices for defining cloud infrastructure in TypeScript. Use when creating CDK apps, stacks, and constructs, designing serverless or container architectures with CDK, configuring VPCs and networking, implementing IAM security hardening, writing CDK assertion and snapshot tests, or deploying infrastructure with cdk deploy. Triggers include "create cdk app", "aws cdk typescript", "cdk stack", "cdk construct", "infrastructure as code typescript", "cdk deploy", "cdk synth", "cdk test".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# AWS CDK TypeScript

## Overview

AWS CDK (Cloud Development Kit) is an open-source IaC framework that lets you define AWS infrastructure using TypeScript. CDK synthesizes your code into CloudFormation templates and deploys them. TypeScript provides autocompletion, strong typing, and software engineering principles (modularity, DRY, testing) that static JSON/YAML templates cannot offer.

**Key advantages over CloudFormation YAML:**

| Aspect | CloudFormation YAML | AWS CDK TypeScript |
|--------|--------------------|--------------------|
| Abstraction | Low-level resources only | L1, L2, L3 constructs |
| Type safety | None | Full TypeScript types |
| Reusability | Copy-paste or nested stacks | Classes, functions, npm packages |
| Testing | Manual review | Automated assertions + snapshots |
| IDE support | Limited | Full autocompletion |

## When to Use

Use this skill when:

- Creating a new CDK application or stack from scratch
- Defining AWS resources (Lambda, API Gateway, DynamoDB, S3, ECS, RDS, etc.) with TypeScript
- Choosing between L1, L2, and L3 construct levels
- Designing multi-stack architectures with cross-stack references
- Configuring environment-aware deployments (dev/staging/prod)
- Implementing serverless patterns (Lambda + API Gateway + DynamoDB)
- Setting up VPC networking (subnets, NAT, security groups)
- Applying IAM least-privilege and encryption best practices
- Writing CDK tests (fine-grained assertions, snapshot tests)
- Running `cdk synth`, `cdk diff`, `cdk deploy`, `cdk destroy`

## Instructions

### 1. Project Initialization

```bash
# Create a new CDK app
npx cdk init app --language typescript

# Project structure
my-cdk-app/
├── bin/
│   └── my-cdk-app.ts          # App entry point (instantiates stacks)
├── lib/
│   └── my-cdk-app-stack.ts    # Stack definition
├── test/
│   └── my-cdk-app.test.ts     # Tests
├── cdk.json                    # CDK configuration
├── tsconfig.json
└── package.json
```

### 2. Core Architecture

```typescript
import { App, Stack, StackProps, CfnOutput, RemovalPolicy } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';

// Define a reusable stack
class StorageStack extends Stack {
  public readonly bucketArn: string;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, 'DataBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: RemovalPolicy.RETAIN,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    this.bucketArn = bucket.bucketArn;
    new CfnOutput(this, 'BucketName', { value: bucket.bucketName });
  }
}

// App entry point
const app = new App();

new StorageStack(app, 'DevStorage', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'us-east-1' },
  tags: { Environment: 'dev' },
});

new StorageStack(app, 'ProdStorage', {
  env: { account: '123456789012', region: 'eu-west-1' },
  tags: { Environment: 'prod' },
  terminationProtection: true,
});

app.synth();
```

### 3. Construct Levels

| Level | Description | Use When |
|-------|-------------|----------|
| **L1** (`Cfn*`) | Direct CloudFormation mapping, full control | Need properties not exposed by L2 |
| **L2** | Curated with sensible defaults and helper methods | Standard resource provisioning (recommended) |
| **L3** (Patterns) | Multi-resource architectures | Common patterns like `LambdaRestApi` |

```typescript
// L1 — Raw CloudFormation
new s3.CfnBucket(this, 'L1Bucket', { bucketName: 'my-l1-bucket' });

// L2 — Sensible defaults + grant helpers
const bucket = new s3.Bucket(this, 'L2Bucket', { versioned: true });
bucket.grantRead(myLambda);

// L3 — Multi-resource pattern
new apigateway.LambdaRestApi(this, 'Api', { handler: myLambda });
```

### 4. CDK Lifecycle Commands

```bash
cdk synth          # Synthesize CloudFormation template
cdk diff           # Compare deployed vs local changes
cdk deploy         # Deploy stack(s) to AWS
cdk deploy --all   # Deploy all stacks
cdk destroy        # Tear down stack(s)
cdk ls             # List all stacks in the app
cdk doctor         # Check environment setup
```

### 5. Cross-Stack References

```typescript
// Stack A exports a value
class NetworkStack extends Stack {
  public readonly vpc: ec2.Vpc;
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    this.vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 2 });
  }
}

// Stack B imports it via props
interface AppStackProps extends StackProps {
  vpc: ec2.Vpc;
}
class AppStack extends Stack {
  constructor(scope: Construct, id: string, props: AppStackProps) {
    super(scope, id, props);
    new lambda.Function(this, 'Fn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda'),
      vpc: props.vpc,
    });
  }
}

// Wire them together
const network = new NetworkStack(app, 'Network');
new AppStack(app, 'App', { vpc: network.vpc });
```

## Examples

### Example 1: Serverless API

```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

class ServerlessApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const table = new dynamodb.Table(this, 'Items', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const fn = new lambda.Function(this, 'Handler', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: { TABLE_NAME: table.tableName },
    });

    table.grantReadWriteData(fn);

    new apigateway.LambdaRestApi(this, 'Api', { handler: fn });
  }
}
```

### Example 2: CDK Assertion Test

```typescript
import { Template } from 'aws-cdk-lib/assertions';
import { App } from 'aws-cdk-lib';
import { ServerlessApiStack } from '../lib/serverless-api-stack';

test('creates DynamoDB table with PAY_PER_REQUEST', () => {
  const app = new App();
  const stack = new ServerlessApiStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::DynamoDB::Table', {
    BillingMode: 'PAY_PER_REQUEST',
  });

  template.resourceCountIs('AWS::Lambda::Function', 1);
});
```

## Best Practices

1. **One concern per stack** — Separate network, compute, storage, and monitoring into dedicated stacks
2. **Use L2 constructs** — Prefer curated constructs over raw `Cfn*` resources for safer defaults
3. **Environment-aware configuration** — Pass `env` with explicit account/region; never hardcode
4. **Tag everything** — Use `Tags.of(scope).add(key, value)` or `cdk.Tags` for cost allocation
5. **Least privilege IAM** — Use `.grant*()` helpers instead of manually crafting IAM policies
6. **Pin construct versions** — Lock `aws-cdk-lib` version in `package.json` for reproducible builds
7. **Use `cdk diff` before deploy** — Always review changes before applying to production
8. **Test your infrastructure** — Write fine-grained assertions and snapshot tests
9. **Avoid hardcoded values** — Use `CfnParameter`, `context`, or environment variables
10. **RemovalPolicy** — Set `RETAIN` for production data, `DESTROY` for dev/test only

## Constraints and Warnings

- **CloudFormation limits** — Max 500 resources per stack; split large apps into multiple stacks
- **Synthesis is not deployment** — `cdk synth` only generates templates; `cdk deploy` applies changes
- **Cross-stack references** create CloudFormation exports; removing them requires careful ordering
- **Stateful resources** (RDS, DynamoDB, S3 with data) — Always set `removalPolicy: RETAIN` in production
- **Bootstrap required** — Run `cdk bootstrap` once per account/region before first deploy
- **Asset bundling** — Lambda code and Docker images are uploaded to the CDK bootstrap bucket

## References

Detailed implementation guides are available in the `references/` directory:

- [Core Concepts](references/core-concepts.md) — App lifecycle, stacks, constructs, environments, assets
- [Serverless Patterns](references/serverless-patterns.md) — Lambda, API Gateway, DynamoDB, S3 events, Step Functions
- [Networking & VPC](references/networking-vpc.md) — VPC design, subnets, NAT, security groups, VPC endpoints
- [Security Hardening](references/security-hardening.md) — IAM, KMS, Secrets Manager, WAF, compliance
- [Testing Strategies](references/testing-strategies.md) — Assertions, snapshots, integration tests, CDK Nag
