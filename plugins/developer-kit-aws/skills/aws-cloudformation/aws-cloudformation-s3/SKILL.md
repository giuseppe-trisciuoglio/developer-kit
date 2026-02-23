---
name: aws-cloudformation-s3
description: Provides AWS CloudFormation patterns for Amazon S3. Use when creating S3 buckets, policies, versioning, lifecycle rules, and implementing template structure with Parameters, Outputs, Mappings, Conditions, and cross-stack references.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation S3 Patterns

## Overview

Create production-ready Amazon S3 infrastructure using AWS CloudFormation templates. This skill covers S3 bucket configurations, bucket policies, versioning, lifecycle rules, encryption, replication, and cross-stack references.

## When to Use

Use this skill when:
- Creating S3 buckets with custom configurations
- Implementing bucket policies for access control
- Configuring S3 versioning for data protection
- Setting up lifecycle rules for data management
- Enabling cross-region replication for disaster recovery
- Configuring event notifications (Lambda, SQS, SNS)
- Creating Outputs for cross-stack references

## Instructions

1. **Define Bucket Parameters**: Specify bucket name (globally unique) and region
2. **Block Public Access**: Always set PublicAccessBlockConfiguration to block all public access
3. **Enable Versioning**: Set VersioningConfiguration Status to Enabled
4. **Configure Encryption**: Set BucketEncryption with SSE-S3 (AES256) or SSE-KMS
5. **Set Up Lifecycle Rules**: Define transitions (Standard -> IA -> Glacier) and expiration
6. **Add Bucket Policy**: Define IAM-style policy for access control (enforce SSL, restrict principals)
7. **Configure CORS**: Add CorsConfiguration if accessed from browsers
8. **Enable Logging**: Set LoggingConfiguration to write access logs to separate bucket
9. **Set Up Replication**: Configure ReplicationConfiguration for cross-region DR
10. **Export Outputs**: Export BucketName, BucketArn, DomainName for cross-stack use

## Best Practices

### Security
- Always block public access (PublicAccessBlockConfiguration all true)
- Enforce SSL with bucket policy condition `aws:SecureTransport: false` -> Deny
- Use SSE-KMS with customer managed keys for compliance
- Enable versioning to protect against accidental deletion
- Use Object Lock for WORM compliance

### Cost
- Use Intelligent-Tiering for unknown access patterns
- Configure lifecycle rules to transition to IA (30 days) and Glacier (90 days)
- Set expiration for temporary objects
- Enable S3 Storage Lens for usage analysis

### Data Protection
- Enable versioning and MFA Delete for critical buckets
- Configure cross-region replication for disaster recovery
- Set lifecycle rules to clean up old versions
- Use S3 Object Lock for regulatory compliance

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: S3 bucket with security best practices

Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-data-${AWS::AccountId}"
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !Ref KmsKey
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LifecycleConfiguration:
        Rules:
          - Id: TransitionToIA
            Status: Enabled
            Transitions:
              - StorageClass: STANDARD_IA
                TransitionInDays: 30
              - StorageClass: GLACIER
                TransitionInDays: 90
            NoncurrentVersionExpiration:
              NoncurrentDays: 30

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref Bucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Sid: EnforceSSL
            Effect: Deny
            Principal: "*"
            Action: s3:*
            Resource:
              - !GetAtt Bucket.Arn
              - !Sub "${Bucket.Arn}/*"
            Condition:
              Bool:
                aws:SecureTransport: false

Outputs:
  BucketName:
    Value: !Ref Bucket
    Export:
      Name: !Sub "${AWS::StackName}-BucketName"
  BucketArn:
    Value: !GetAtt Bucket.Arn
    Export:
      Name: !Sub "${AWS::StackName}-BucketArn"
```

## Constraints and Warnings

- **Bucket Names**: Globally unique, 3-63 characters, lowercase, no periods for transfer acceleration
- **Objects**: Max 5 TB per object; multipart upload for > 100 MB
- **Versioning**: Cannot disable once enabled (only suspend); all versions count toward storage
- **Lifecycle**: Minimum 30 days before transition to IA; minimum 90 days for Glacier
- **Replication**: Requires versioning on both source and destination buckets
- **Bucket Policy**: Max 20 KB; bucket policies and IAM policies are evaluated together
- **Event Notifications**: Lambda/SQS/SNS must have resource-based policy allowing S3
- **Deletion**: Bucket must be empty before CloudFormation can delete it (use custom resource)

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
