---
name: aws-cloudformation-lambda
description: Provides AWS CloudFormation patterns for Lambda functions, layers, event sources, and integrations. Use when creating Lambda functions with CloudFormation, configuring API Gateway, Step Functions, EventBridge, SQS, SNS triggers, and implementing template structure with Parameters, Outputs, Mappings, Conditions, cross-stack references, and best practices for cold start optimization.
category: aws
tags: [aws, cloudformation, lambda, serverless, functions, api-gateway, step-functions, events, infrastructure, iaac]
version: 2.2.0
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation Lambda Serverless

## Overview

Create production-ready serverless infrastructure using AWS CloudFormation templates. This skill covers Lambda functions, layers, event sources, API Gateway, Step Functions, cold start optimization, and best practices for parameters, outputs, and cross-stack references.

## When to Use

Use this skill when:
- Creating new Lambda functions with CloudFormation
- Configuring Lambda layers for shared code
- Integrating Lambda with API Gateway (REST and HTTP API)
- Implementing event sources (SQS, SNS, EventBridge, S3, DynamoDB Streams)
- Creating Step Functions with Lambda workflows
- Optimizing cold start and performance
- Implementing cross-stack references with export/import

## Instructions

1. **Define Function Parameters**: Specify runtime, handler, memory (128-10240 MB), timeout (max 900s)
2. **Configure Code Source**: Set S3Bucket/S3Key or use inline Code for small functions
3. **Set Up Execution Role**: Create role with `AWSLambdaBasicExecutionRole` + specific permissions
4. **Add Environment Variables**: Configure via `Environment.Variables`, use SSM/Secrets Manager for secrets
5. **Implement Event Sources**: Add EventSourceMapping for SQS/DynamoDB, or resource-based policy for S3/SNS
6. **Configure Layers**: Create layers for shared dependencies, reference via LayerVersionArn
7. **Set Up Dead Letter Queue**: Configure DLQ (SQS or SNS) for failed async invocations
8. **Add Monitoring**: Enable X-Ray tracing (`TracingConfig: Mode: Active`), configure log retention
9. **Optimize Cold Start**: Use SnapStart (Java), provisioned concurrency, or keep-warm strategies
10. **Configure VPC**: Add VpcConfig for private resource access (requires NAT for internet)

## Best Practices

### Security
- Use least-privilege execution roles scoped to specific resources
- Store secrets in SSM Parameter Store or Secrets Manager (not env vars)
- Enable X-Ray tracing for debugging
- Use reserved concurrency to prevent runaway scaling

### Performance
- Minimize deployment package size
- Use layers for shared dependencies
- Configure appropriate memory (also scales CPU proportionally)
- Use provisioned concurrency for latency-sensitive functions
- Use SnapStart for Java functions

### Cost
- Set appropriate timeout (not max 900s)
- Use reserved concurrency to limit costs
- Choose ARM64 architecture for 20% cost savings
- Use Graviton2 (arm64) when possible

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda function with SQS trigger

Resources:
  Function:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-processor"
      Runtime: python3.12
      Handler: app.handler
      Architectures: [arm64]
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Ref CodeKey
      MemorySize: 256
      Timeout: 30
      Role: !GetAtt FunctionRole.Arn
      Environment:
        Variables:
          TABLE_NAME: !Ref TableName
      TracingConfig:
        Mode: Active
      DeadLetterConfig:
        TargetArn: !GetAtt DLQ.Arn
      ReservedConcurrentExecutions: 100

  FunctionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: SQSAccess
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - sqs:ReceiveMessage
                  - sqs:DeleteMessage
                  - sqs:GetQueueAttributes
                Resource: !GetAtt Queue.Arn

  EventSource:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      FunctionName: !Ref Function
      EventSourceArn: !GetAtt Queue.Arn
      BatchSize: 10
      MaximumBatchingWindowInSeconds: 5

  DLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-dlq"

Outputs:
  FunctionArn:
    Value: !GetAtt Function.Arn
    Export:
      Name: !Sub "${AWS::StackName}-FunctionArn"
```

## Constraints and Warnings

- **Memory**: 128 MB to 10,240 MB in 1 MB increments
- **Timeout**: Max 900 seconds (15 minutes)
- **Package Size**: 50 MB zipped, 250 MB unzipped (including layers)
- **Layers**: Max 5 layers per function
- **Concurrency**: Default 1,000 concurrent executions per region (can request increase)
- **VPC**: Functions in VPC need NAT Gateway for internet access; adds cold start latency
- **Environment Variables**: Max 4 KB total for all variables
- **Ephemeral Storage**: /tmp max 10,240 MB
- **SnapStart**: Only available for Java 11+ managed runtimes

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
