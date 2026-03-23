# AWS CDK Core Concepts

## Table of Contents

- [App Lifecycle](#app-lifecycle)
- [Stacks](#stacks)
- [Constructs](#constructs)
- [Environments](#environments)
- [Context](#context)
- [Assets](#assets)
- [Tokens and Lazy Values](#tokens-and-lazy-values)
- [Aspects](#aspects)

---

## App Lifecycle

The CDK app lifecycle follows a predictable flow from code to deployed infrastructure:

```
Code → Construct Tree → Synthesis → CloudFormation Template → Deployment
```

### Phases

| Phase | Description | CLI Command |
|-------|-------------|-------------|
| **Construction** | Instantiate App, Stacks, Constructs | — |
| **Preparation** | Mutate construct tree (Aspects run here) | — |
| **Validation** | Validate construct configurations | — |
| **Synthesis** | Generate CloudFormation templates + assets | `cdk synth` |
| **Deployment** | Create/update CloudFormation stacks | `cdk deploy` |

```typescript
import { App } from 'aws-cdk-lib';

const app = new App();

// Construction phase: define stacks and constructs
new MyStack(app, 'MyStack', {
  env: { account: '123456789012', region: 'us-east-1' },
});

// Synthesis phase: generates cdk.out/ directory
app.synth();
```

### Output Directory

After `cdk synth`, the `cdk.out/` directory contains:

```
cdk.out/
├── MyStack.template.json     # CloudFormation template
├── manifest.json              # Assembly manifest
├── tree.json                  # Construct tree
└── asset.*                    # Bundled assets (Lambda code, Docker images)
```

---

## Stacks

A Stack is the unit of deployment — it maps 1:1 to a CloudFormation stack.

### Single Stack

```typescript
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class MyAppStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    // Define resources here
  }
}
```

### Multi-Stack Architecture

```typescript
const app = new App();

const networkStack = new NetworkStack(app, 'Network', {
  env: { account: '123456789012', region: 'us-east-1' },
});

const appStack = new AppStack(app, 'App', {
  vpc: networkStack.vpc,
  env: { account: '123456789012', region: 'us-east-1' },
});

// Explicit dependency ensures correct deploy order
appStack.addDependency(networkStack);
```

### Stack Best Practices

- Keep stacks under 500 resources (CloudFormation limit)
- Group resources by lifecycle (network rarely changes, app changes often)
- Use `terminationProtection: true` for production stacks
- Export shared resources as public properties for cross-stack references

---

## Constructs

Constructs are the building blocks of CDK apps. They form a tree hierarchy: App → Stack → Constructs.

### L1 Constructs (CloudFormation Resources)

Direct 1:1 mapping to CloudFormation resource types. Prefixed with `Cfn`.

```typescript
import * as s3 from 'aws-cdk-lib/aws-s3';

// Full control, no defaults
new s3.CfnBucket(this, 'RawBucket', {
  bucketName: 'my-raw-bucket',
  versioningConfiguration: { status: 'Enabled' },
  bucketEncryption: {
    serverSideEncryptionConfiguration: [{
      serverSideEncryptionByDefault: { sseAlgorithm: 'AES256' },
    }],
  },
});
```

### L2 Constructs (Curated)

Higher-level abstractions with sensible defaults, helper methods, and grant patterns.

```typescript
import * as s3 from 'aws-cdk-lib/aws-s3';

// Sensible defaults + helper methods
const bucket = new s3.Bucket(this, 'DataBucket', {
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
});

// Grant pattern — generates least-privilege IAM automatically
bucket.grantRead(myLambdaFunction);
```

### L3 Constructs (Patterns)

Combine multiple L2 constructs into reusable architectural patterns.

```typescript
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

// Creates API Gateway + Lambda integration + IAM permissions
new apigateway.LambdaRestApi(this, 'MyApi', {
  handler: myLambdaFunction,
  proxy: false,
});
```

### Custom Constructs

Create reusable constructs for your organization:

```typescript
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export interface ProcessingPipelineProps {
  readonly bucketName?: string;
  readonly lambdaMemory?: number;
}

export class ProcessingPipeline extends Construct {
  public readonly bucket: s3.Bucket;
  public readonly processor: lambda.Function;

  constructor(scope: Construct, id: string, props: ProcessingPipelineProps = {}) {
    super(scope, id);

    this.bucket = new s3.Bucket(this, 'InputBucket', {
      bucketName: props.bucketName,
      versioned: true,
    });

    this.processor = new lambda.Function(this, 'Processor', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda/processor'),
      memorySize: props.lambdaMemory ?? 256,
      environment: { BUCKET_NAME: this.bucket.bucketName },
    });

    this.bucket.grantRead(this.processor);
  }
}
```

---

## Environments

Environments specify the target AWS account and region for a stack.

### Explicit Environment

```typescript
new MyStack(app, 'ProdStack', {
  env: { account: '123456789012', region: 'eu-west-1' },
});
```

### Default Environment (from CLI profile)

```typescript
new MyStack(app, 'DevStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
```

### Environment-Agnostic Stacks

Omitting `env` creates environment-agnostic stacks. Some features (like `Vpc.fromLookup`) require explicit environments.

### Multi-Environment Pattern

```typescript
interface EnvironmentConfig {
  account: string;
  region: string;
  isProd: boolean;
}

const environments: Record<string, EnvironmentConfig> = {
  dev:  { account: '111111111111', region: 'us-east-1', isProd: false },
  prod: { account: '222222222222', region: 'eu-west-1', isProd: true },
};

for (const [name, config] of Object.entries(environments)) {
  new MyStack(app, `${name}-Stack`, {
    env: { account: config.account, region: config.region },
    terminationProtection: config.isProd,
  });
}
```

---

## Context

Context values are key-value pairs available at synthesis time. They configure behavior without changing code.

### Sources (in priority order)

1. `--context` CLI flag
2. `cdk.json` file
3. `~/.cdk.json` (global)
4. `construct.node.setContext()` in code

### Usage

```typescript
// Read context value in stack
const stage = this.node.tryGetContext('stage') || 'dev';
const vpcId = this.node.tryGetContext('vpcId');

// Use in resource configuration
const isProd = stage === 'prod';
```

```json
// cdk.json
{
  "context": {
    "stage": "dev",
    "vpcId": "vpc-0123456789abcdef0"
  }
}
```

```bash
# Override via CLI
cdk deploy --context stage=prod --context vpcId=vpc-abc123
```

---

## Assets

Assets are local files or Docker images that CDK uploads to S3/ECR during deployment.

### File Assets (Lambda Code)

```typescript
// Directory asset — bundled and uploaded to S3
new lambda.Function(this, 'Fn', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda/my-function'),
});
```

### Docker Assets (Container Images)

```typescript
import * as ecs from 'aws-cdk-lib/aws-ecs';

// Build Docker image and push to ECR
const taskDef = new ecs.FargateTaskDefinition(this, 'TaskDef');
taskDef.addContainer('App', {
  image: ecs.ContainerImage.fromAsset('./docker'),
  memoryLimitMiB: 512,
});
```

### Bundled Assets (esbuild)

```typescript
import * as lambdaNode from 'aws-cdk-lib/aws-lambda-nodejs';

// Automatically bundles TypeScript with esbuild
new lambdaNode.NodejsFunction(this, 'BundledFn', {
  entry: 'lambda/handler.ts',
  handler: 'handler',
  runtime: lambda.Runtime.NODEJS_20_X,
  bundling: {
    minify: true,
    sourceMap: true,
    externalModules: ['@aws-sdk/*'],
  },
});
```

---

## Tokens and Lazy Values

Tokens are placeholders for values not known until deploy time (e.g., ARNs, names).

```typescript
const bucket = new s3.Bucket(this, 'Bucket');

// bucket.bucketName is a Token (resolved at deploy time)
new lambda.Function(this, 'Fn', {
  environment: {
    BUCKET_NAME: bucket.bucketName,  // Token — resolves to actual name
  },
});

// Check if a value is a token
import { Token } from 'aws-cdk-lib';
Token.isUnresolved(bucket.bucketName); // true
```

---

## Aspects

Aspects apply operations to every construct in a scope (e.g., enforce tagging, compliance).

```typescript
import { IAspect, Tags, Aspects, Annotations } from 'aws-cdk-lib';
import { CfnBucket } from 'aws-cdk-lib/aws-s3';
import { IConstruct } from 'constructs';

class BucketVersioningChecker implements IAspect {
  visit(node: IConstruct): void {
    if (node instanceof CfnBucket) {
      if (!node.versioningConfiguration) {
        Annotations.of(node).addWarning('Bucket versioning is not enabled');
      }
    }
  }
}

// Apply aspect to entire stack
Aspects.of(myStack).add(new BucketVersioningChecker());

// Apply tags to all resources in a scope
Tags.of(app).add('Project', 'MyProject');
Tags.of(app).add('ManagedBy', 'CDK');
```
