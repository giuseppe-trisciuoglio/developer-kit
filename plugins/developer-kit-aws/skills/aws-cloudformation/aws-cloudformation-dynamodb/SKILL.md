---
name: aws-cloudformation-dynamodb
description: Provides AWS CloudFormation patterns for DynamoDB tables, GSIs, LSIs, auto-scaling, and streams. Use when creating DynamoDB tables with CloudFormation, configuring primary keys, local/global secondary indexes, capacity modes (on-demand/provisioned), point-in-time recovery, encryption, TTL, and implementing template structure with Parameters, Outputs, Mappings, Conditions, cross-stack references.
category: aws
tags: [aws, cloudformation, dynamodb, nosql, database, serverless, tables, indexes, scaling, infrastructure, iaac]
version: 2.2.0
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation DynamoDB

## Overview

Create production-ready NoSQL database infrastructure using AWS CloudFormation templates. This skill covers DynamoDB tables, primary keys, secondary indexes (GSI/LSI), capacity modes, auto-scaling, encryption, TTL, streams, and best practices for parameters, outputs, and cross-stack references.

## When to Use

Use this skill when:
- Creating new DynamoDB tables with CloudFormation
- Configuring primary keys (partition key, sort key)
- Creating Global Secondary Indexes (GSI) and Local Secondary Indexes (LSI)
- Setting up capacity modes (on-demand or provisioned)
- Implementing auto-scaling with Application Auto Scaling
- Enabling point-in-time recovery and backup
- Configuring encryption at rest with KMS
- Setting up TTL for automatic data expiration
- Enabling DynamoDB Streams for change data capture
- Implementing cross-stack references with export/import

## Instructions

1. **Define Table Parameters**: Specify table name, billing mode (PAY_PER_REQUEST or PROVISIONED)
2. **Configure Primary Key**: Set partition key (HASH) and optional sort key (RANGE) with AttributeDefinitions
3. **Add Global Secondary Indexes**: Create GSIs for alternative access patterns with their own key schema and projection
4. **Add Local Secondary Indexes**: Create LSIs sharing the partition key but with different sort keys
5. **Configure Encryption**: Enable SSE with AWS owned, AWS managed, or customer managed KMS keys
6. **Set Up TTL**: Define TimeToLiveSpecification with timestamp attribute name
7. **Enable Streams**: Set StreamViewType (NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES, KEYS_ONLY)
8. **Add Auto Scaling**: Create ScalableTarget and ScalingPolicy for read/write capacity
9. **Enable PITR**: Set PointInTimeRecoveryEnabled to true for continuous backups
10. **Export Outputs**: Export TableName, TableArn, StreamArn for cross-stack references

## Best Practices

### Design
- Choose partition keys with high cardinality for even distribution
- Use composite keys (partition + sort) for hierarchical data
- Design GSIs based on query access patterns, not data structure
- Use sparse indexes to reduce GSI costs

### Performance
- Use on-demand billing for unpredictable workloads, provisioned for steady-state
- Enable DAX for microsecond read latency
- Use BatchGetItem/BatchWriteItem for bulk operations
- Configure auto-scaling with appropriate min/max capacity

### Security
- Enable encryption at rest with KMS (customer managed keys for compliance)
- Use IAM policies with condition keys for fine-grained access
- Enable PITR for continuous backups
- Use VPC endpoints for private access

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: DynamoDB table with GSI and auto-scaling

Resources:
  Table:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      SSESpecification:
        SSEEnabled: true
        SSEType: KMS
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      Tags:
        - Key: Environment
          Value: !Ref Environment

Outputs:
  TableName:
    Value: !Ref Table
    Export:
      Name: !Sub "${AWS::StackName}-TableName"
  TableArn:
    Value: !GetAtt Table.Arn
    Export:
      Name: !Sub "${AWS::StackName}-TableArn"
  StreamArn:
    Value: !GetAtt Table.StreamArn
    Export:
      Name: !Sub "${AWS::StackName}-StreamArn"
```

## Constraints and Warnings

- **GSI Limits**: Max 20 GSIs per table; LSIs max 5 per table
- **LSI Restriction**: LSIs must be created at table creation time, cannot be added later
- **Partition Key Size**: Max 2048 bytes; Sort key max 1024 bytes
- **Item Size**: Max 400 KB per item including attribute names
- **Provisioned Capacity**: Max 40,000 RCU/WCU per table (can request increase)
- **On-Demand**: Can handle up to double previous peak within 30 minutes
- **Streams**: Records available for 24 hours; max 2 processes reading simultaneously
- **Encryption**: Cannot change from customer managed KMS to AWS owned after creation

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
