# AWS CDK Testing Strategies

## Table of Contents

- [Testing Overview](#testing-overview)
- [Fine-Grained Assertions](#fine-grained-assertions)
- [Snapshot Testing](#snapshot-testing)
- [Validation Testing](#validation-testing)
- [Integration Testing](#integration-testing)
- [CDK Nag Compliance](#cdk-nag-compliance)
- [Testing Patterns](#testing-patterns)

---

## Testing Overview

CDK provides the `assertions` module for testing synthesized CloudFormation templates without deploying.

| Test Type | Purpose | Speed | Maintenance |
|-----------|---------|-------|-------------|
| **Fine-grained assertions** | Verify specific resource properties | Fast | Low |
| **Snapshot tests** | Detect unintended template changes | Fast | Medium |
| **Validation tests** | Test custom construct validation logic | Fast | Low |
| **Integration tests** | Deploy and verify real AWS resources | Slow | High |
| **CDK Nag** | Compliance and best-practice checks | Fast | Low |

### Setup

```bash
npm install --save-dev jest @types/jest ts-jest
```

```json
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/test'],
  testMatch: ['**/*.test.ts'],
  transform: { '^.+\\.tsx?$': 'ts-jest' },
};
```

---

## Fine-Grained Assertions

### Basic Resource Assertions

```typescript
import { App } from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { MyStack } from '../lib/my-stack';

describe('MyStack', () => {
  let template: Template;

  beforeEach(() => {
    const app = new App();
    const stack = new MyStack(app, 'TestStack');
    template = Template.fromStack(stack);
  });

  test('creates a DynamoDB table with PAY_PER_REQUEST', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      BillingMode: 'PAY_PER_REQUEST',
    });
  });

  test('creates a Lambda function with correct runtime', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'nodejs20.x',
      Timeout: 30,
    });
  });

  test('creates exactly 2 Lambda functions', () => {
    template.resourceCountIs('AWS::Lambda::Function', 2);
  });
});
```

### Match Helpers

```typescript
import { Match } from 'aws-cdk-lib/assertions';

// Match any value
template.hasResourceProperties('AWS::Lambda::Function', {
  Handler: Match.anyValue(),
  Runtime: 'nodejs20.x',
});

// Match object with specific keys (ignoring others)
template.hasResourceProperties('AWS::Lambda::Function', {
  Environment: {
    Variables: Match.objectLike({
      TABLE_NAME: Match.anyValue(),
    }),
  },
});

// Match absent property
template.hasResourceProperties('AWS::S3::Bucket', {
  PublicAccessBlockConfiguration: {
    BlockPublicAcls: true,
  },
  WebsiteConfiguration: Match.absent(),
});

// Match array containing specific elements
template.hasResourceProperties('AWS::IAM::Role', {
  ManagedPolicyArns: Match.arrayWith([
    Match.objectLike({
      'Fn::Join': Match.anyValue(),
    }),
  ]),
});
```

### Testing Resource Counts

```typescript
test('creates expected number of resources', () => {
  template.resourceCountIs('AWS::Lambda::Function', 3);
  template.resourceCountIs('AWS::DynamoDB::Table', 1);
  template.resourceCountIs('AWS::SQS::Queue', 2);  // main + DLQ
  template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
});
```

### Testing Outputs

```typescript
test('exports API URL', () => {
  template.hasOutput('ApiUrl', {
    Value: Match.anyValue(),
  });
});
```

---

## Snapshot Testing

Snapshot tests capture the entire synthesized template and detect any change.

### Basic Snapshot

```typescript
test('matches snapshot', () => {
  const app = new App();
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  expect(template.toJSON()).toMatchSnapshot();
});
```

### Updating Snapshots

```bash
# Regenerate snapshots after intentional changes
npx jest --updateSnapshot
```

### When to Use Snapshots

| Scenario | Recommended |
|----------|-------------|
| Detect accidental changes | ✅ Yes |
| Verify specific properties | ❌ Use fine-grained assertions |
| Stable, rarely-changing stacks | ✅ Yes |
| Rapidly iterating stacks | ❌ Too many snapshot updates |

---

## Validation Testing

Test custom validation logic in your constructs.

```typescript
import { App, Stack } from 'aws-cdk-lib';

// Custom construct with validation
class MyConstruct extends Construct {
  constructor(scope: Construct, id: string, props: { maxRetries: number }) {
    super(scope, id);
    if (props.maxRetries < 0 || props.maxRetries > 10) {
      throw new Error('maxRetries must be between 0 and 10');
    }
  }
}

// Test validation
test('throws on invalid maxRetries', () => {
  const app = new App();
  const stack = new Stack(app, 'TestStack');

  expect(() => {
    new MyConstruct(stack, 'Bad', { maxRetries: -1 });
  }).toThrow('maxRetries must be between 0 and 10');

  expect(() => {
    new MyConstruct(stack, 'Also Bad', { maxRetries: 99 });
  }).toThrow('maxRetries must be between 0 and 10');
});

test('accepts valid maxRetries', () => {
  const app = new App();
  const stack = new Stack(app, 'TestStack');

  expect(() => {
    new MyConstruct(stack, 'Good', { maxRetries: 3 });
  }).not.toThrow();
});
```

---

## Integration Testing

### CDK integ-tests Module

```typescript
import { IntegTest } from '@aws-cdk/integ-tests-alpha';
import { App } from 'aws-cdk-lib';

const app = new App();
const stack = new MyStack(app, 'IntegTestStack');

const integ = new IntegTest(app, 'MyIntegTest', {
  testCases: [stack],
  diffAssets: true,
  stackUpdateWorkflow: true,
});

// Assert deployed resources
integ.assertions
  .httpApiCall('https://my-api.execute-api.us-east-1.amazonaws.com/items')
  .expect(ExpectedResult.objectLike({ statusCode: 200 }));
```

### Running Integration Tests

```bash
# Deploy and test
npx integ-runner --directory test/integ --parallel-regions us-east-1

# Update snapshots after successful deploy
npx integ-runner --directory test/integ --update-on-failed
```

---

## CDK Nag Compliance

CDK Nag checks your stacks against best-practice rule packs.

### Setup

```bash
npm install cdk-nag
```

```typescript
import { Aspects } from 'aws-cdk-lib';
import { AwsSolutionsChecks, HIPAASecurityChecks } from 'cdk-nag';

const app = new App();
const stack = new MyStack(app, 'ProdStack');

// Add compliance checks
Aspects.of(stack).add(new AwsSolutionsChecks({ verbose: true }));
// Or HIPAA compliance
// Aspects.of(stack).add(new HIPAASecurityChecks());
```

### Available Rule Packs

| Pack | Description |
|------|-------------|
| `AwsSolutionsChecks` | AWS Solutions Library best practices |
| `HIPAASecurityChecks` | HIPAA compliance rules |
| `NIST80053R4Checks` | NIST 800-53 Rev 4 |
| `NIST80053R5Checks` | NIST 800-53 Rev 5 |
| `PCI321Checks` | PCI DSS 3.2.1 |

### Suppressing Rules

```typescript
import { NagSuppressions } from 'cdk-nag';

// Suppress at resource level
NagSuppressions.addResourceSuppressions(myBucket, [
  { id: 'AwsSolutions-S1', reason: 'Access logging not needed for dev' },
]);

// Suppress at stack level
NagSuppressions.addStackSuppressions(stack, [
  { id: 'AwsSolutions-IAM4', reason: 'Using AWS managed policies is acceptable here' },
]);
```

### Testing with CDK Nag

```typescript
import { Annotations } from 'aws-cdk-lib/assertions';
import { AwsSolutionsChecks } from 'cdk-nag';

test('passes AWS Solutions checks', () => {
  const app = new App();
  const stack = new MyStack(app, 'TestStack');
  Aspects.of(stack).add(new AwsSolutionsChecks());

  const annotations = Annotations.fromStack(stack);

  // No errors
  annotations.hasNoError('*', Match.anyValue());

  // Optionally check no warnings
  annotations.hasNoWarning('*', Match.anyValue());
});
```

---

## Testing Patterns

### Pattern: Test Environment-Specific Behavior

```typescript
test('production stack has termination protection', () => {
  const app = new App();
  const stack = new MyStack(app, 'ProdStack', {
    env: { account: '123456789012', region: 'us-east-1' },
    terminationProtection: true,
  });

  expect(stack.terminationProtection).toBe(true);
});

test('dev stack allows removal', () => {
  const app = new App();
  const stack = new MyStack(app, 'DevStack', {
    terminationProtection: false,
  });
  const template = Template.fromStack(stack);

  template.hasResource('AWS::DynamoDB::Table', {
    DeletionPolicy: 'Delete',
  });
});
```

### Pattern: Test IAM Permissions

```typescript
test('Lambda has read-only access to S3', () => {
  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::IAM::Policy', {
    PolicyDocument: {
      Statement: Match.arrayWith([
        Match.objectLike({
          Action: Match.arrayWith(['s3:GetObject*', 's3:GetBucket*']),
          Effect: 'Allow',
        }),
      ]),
    },
  });
});
```

### Pattern: Test Cross-Stack References

```typescript
test('app stack uses VPC from network stack', () => {
  const app = new App();
  const networkStack = new NetworkStack(app, 'Network');
  const appStack = new AppStack(app, 'App', { vpc: networkStack.vpc });
  const template = Template.fromStack(appStack);

  template.hasResourceProperties('AWS::Lambda::Function', {
    VpcConfig: {
      SubnetIds: Match.anyValue(),
      SecurityGroupIds: Match.anyValue(),
    },
  });
});
```

### Pattern: Parameterized Tests

```typescript
describe.each([
  ['dev', false, 'PAY_PER_REQUEST'],
  ['prod', true, 'PAY_PER_REQUEST'],
])('environment: %s', (env, pitr, billing) => {
  test(`DynamoDB has PITR=${pitr}`, () => {
    const app = new App({ context: { stage: env } });
    const stack = new MyStack(app, 'Stack');
    const template = Template.fromStack(stack);

    if (pitr) {
      template.hasResourceProperties('AWS::DynamoDB::Table', {
        PointInTimeRecoverySpecification: { PointInTimeRecoveryEnabled: true },
      });
    }
  });
});
```
