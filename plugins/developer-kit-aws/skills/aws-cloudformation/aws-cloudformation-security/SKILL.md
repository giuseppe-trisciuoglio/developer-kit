---
name: aws-cloudformation-security
description: Provides AWS CloudFormation patterns for infrastructure security, secrets management, encryption, and secure data handling. Use when creating secure CloudFormation templates with AWS Secrets Manager, KMS encryption, secure parameters, IAM policies, VPC security groups, TLS/SSL certificates, and encrypted traffic configurations. Covers template structure, parameter best practices, cross-stack references, and defense-in-depth strategies.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation Security

## Overview

Create secure AWS infrastructure using CloudFormation templates with security best practices. This skill covers encryption with AWS KMS, secrets management with Secrets Manager, secure parameters, IAM least privilege, security groups, TLS/SSL certificates, and defense-in-depth strategies.

## When to Use

Use this skill when:
- Creating CloudFormation templates with encryption at-rest and in-transit
- Managing secrets and credentials with AWS Secrets Manager
- Configuring AWS KMS for encryption keys
- Implementing secure parameters with SSM Parameter Store
- Creating IAM policies with least privilege
- Configuring security groups and network security
- Configuring TLS/SSL certificates with ACM
- Applying defense-in-depth for infrastructure

## Instructions

1. **Create KMS Keys**: Define symmetric or asymmetric keys with key policies and rotation
2. **Set Up Secrets Manager**: Store credentials with automatic rotation using Lambda
3. **Configure SSM Parameters**: Use SecureString for sensitive values with KMS encryption
4. **Implement IAM Policies**: Apply least privilege with specific actions, resource ARNs, and conditions
5. **Create Security Groups**: Define restrictive ingress/egress referencing source security groups
6. **Set Up TLS Certificates**: Use ACM for SSL/TLS certificates with DNS validation
7. **Enable Encryption**: Configure storage encryption (S3, EBS, RDS, DynamoDB) with KMS
8. **Enable Audit Logging**: Configure CloudTrail for API auditing, VPC Flow Logs for network
9. **Use NoEcho Parameters**: Mark sensitive parameters with `NoEcho: true`
10. **Implement WAF**: Add WAFv2 rules for application-layer protection

## Best Practices

### Encryption
- Use KMS customer managed keys for compliance-sensitive workloads
- Enable automatic key rotation (annual for symmetric keys)
- Encrypt all data at rest (S3, EBS, RDS, DynamoDB, ElastiCache)
- Enforce TLS 1.2+ for all connections
- Use separate keys per service/environment

### Secrets Management
- Never hardcode credentials in templates
- Use Secrets Manager with automatic rotation
- Reference secrets dynamically with `{{resolve:secretsmanager:...}}`
- Use `NoEcho: true` for sensitive parameters
- Rotate secrets on a schedule (30-90 days)

### Network Security
- Use private subnets for sensitive resources
- Restrict security groups to specific CIDRs/security groups
- Implement VPC endpoints for AWS service access
- Enable VPC Flow Logs for network monitoring
- Use NACLs as additional layer of defense

### IAM
- Use condition keys (`aws:SourceAccount`, `aws:SourceArn`, `aws:RequestedRegion`)
- Implement permission boundaries
- Use service-linked roles when available
- Enable MFA for sensitive operations

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Security infrastructure with KMS and Secrets Manager

Resources:
  EncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Application encryption key
      EnableKeyRotation: true
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: EnableRootAccess
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Action: kms:*
            Resource: "*"
          - Sid: AllowServiceUse
            Effect: Allow
            Principal:
              AWS: !GetAtt AppRole.Arn
            Action:
              - kms:Decrypt
              - kms:GenerateDataKey
            Resource: "*"

  KeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub "alias/${AWS::StackName}-key"
      TargetKeyId: !Ref EncryptionKey

  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/db-credentials"
      GenerateSecretString:
        SecretStringTemplate: '{"username": "dbadmin"}'
        GenerateStringKey: password
        PasswordLength: 32
        ExcludeCharacters: '"@/\'

  SecretRotationSchedule:
    Type: AWS::SecretsManager::RotationSchedule
    Properties:
      SecretId: !Ref DatabaseSecret
      RotationRules:
        AutomaticallyAfterDays: 30

Outputs:
  KmsKeyArn:
    Value: !GetAtt EncryptionKey.Arn
    Export:
      Name: !Sub "${AWS::StackName}-KmsKeyArn"
  SecretArn:
    Value: !Ref DatabaseSecret
    Export:
      Name: !Sub "${AWS::StackName}-SecretArn"
```

## Constraints and Warnings

- **KMS Key Deletion**: Keys scheduled for deletion have 7-30 day waiting period; cannot be recovered after
- **KMS Limits**: Max 30,000 cryptographic operations per second per key
- **Secrets Manager**: Max 65,536 bytes per secret value; rotation requires Lambda function
- **ACM Certificates**: Must be in us-east-1 for CloudFront; DNS validation preferred over email
- **Security Groups**: Max 5 per ENI; changes take effect immediately
- **SSM Parameters**: SecureString parameters cannot be referenced with `!Ref` in CloudFormation
- **NoEcho**: Parameters with NoEcho are masked in console but stored in template
- **CloudTrail**: Enable in all regions for comprehensive audit logging

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
