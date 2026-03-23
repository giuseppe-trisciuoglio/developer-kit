---
name: aws-cloudformation-security
description: Provides AWS CloudFormation patterns for security infrastructure including KMS encryption, Secrets Manager, IAM security, VPC security, ACM certificates, parameter security, outputs, and secure cross-stack references. Use when implementing security best practices, encrypting data, managing secrets, applying least privilege IAM policies, securing VPC configurations, managing TLS/SSL certificates, and implementing defense in depth strategies.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation Security Infrastructure

## Overview

Create production-ready security infrastructure using AWS CloudFormation templates. This skill covers KMS encryption, Secrets Manager, IAM security with least privilege, VPC security configurations, ACM certificates, parameter security, secure outputs, cross-stack references, CloudWatch Logs encryption, defense in depth strategies, and security best practices.

## When to Use

Use this skill when:
- Implementing AWS KMS for encryption at rest and in transit
- Managing secrets with AWS Secrets Manager
- Applying IAM least privilege policies and roles
- Securing VPC configurations with security groups and NACLs
- Managing TLS/SSL certificates with ACM
- Implementing secure parameter handling in CloudFormation
- Creating secure cross-stack references and outputs
- Encrypting CloudWatch Logs for compliance
- Implementing defense in depth strategies
- Applying security best practices across AWS resources

## Instructions

Follow these steps to create security infrastructure with CloudFormation:

### 1. Define KMS Encryption Keys

Create customer-managed keys for encryption:

```yaml
Resources:
  EncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Customer-managed key for data encryption
      KeyPolicy:
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action:
              - kms:Decrypt
              - kms:GenerateDataKey
            Resource: "*"
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Action:
              - kms:*
            Resource: "*"

  KeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub "${AWS::StackName}/encryption-key"
      TargetKeyId: !Ref EncryptionKey
```

### 2. Manage Secrets with Secrets Manager

Store and retrieve sensitive data securely:

```yaml
Resources:
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/database"
      Description: Database credentials
      SecretString: !Sub |
        {
          "username": "admin",
          "password": "${DatabasePassword}",
          "engine": "mysql",
          "host": "${DatabaseEndpoint}",
          "port": 3306
        }
      KmsKeyId: !Ref EncryptionKey

  SecretRotationSchedule:
    Type: AWS::SecretsManager::RotationSchedule
    Properties:
      SecretId: !Ref DatabaseSecret
      RotationLambdaARN: !Ref RotationLambda.Arn
      RotationRules:
        AutomaticallyAfterDays: 30
```

### 3. Apply IAM Least Privilege

Create roles and policies with minimal required permissions:

```yaml
Resources:
  ExecutionRole:
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
        - PolicyName: SpecificPermissions
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "${DataBucket.Arn}/*"
```

### 4. Secure VPC Configuration

Implement network security with security groups and NACLs:

```yaml
Resources:
  ApplicationSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Application security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0

  ApplicationNACL:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC

  NACLEntry:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref ApplicationNACL
      RuleNumber: 100
      Protocol: "6"
      RuleAction: allow
      Egress: false
      CidrBlock: 0.0.0.0/0
      PortRange:
        From: 443
        To: 443
```

### 5. Request ACM Certificates

Manage TLS/SSL certificates for secure communication:

```yaml
Resources:
  Certificate:
    Type: AWS::ACM::Certificate
    Properties:
      DomainName: !Ref DomainName
      SubjectAlternativeNames:
        - !Sub "www.${DomainName}"
        - !Sub "api.${DomainName}"
      DomainValidationOptions:
        - DomainName: !Ref DomainName
          ValidationDomain: !Ref DomainName
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # DNS validation record
  DnsValidationRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneName: !Ref HostedZone
      Name: !Sub "_${DomainName}."
      Type: CNAME
      TTL: 300
      ResourceRecords:
        - !Ref Certificate
```

### 6. Implement Secure Parameters

Use SecureString for sensitive parameter values:

```yaml
Resources:
  DatabasePasswordParameter:
    Type: AWS::SSM::Parameter
    Properties:
      Name: !Sub "/${AWS::StackName}/database/password"
      Type: SecureString
      Value: !Ref DatabasePassword
      Description: Database master password
      KmsKeyId: !Ref EncryptionKey

  # Reference in other resources
  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      MasterUsername: admin
      MasterUserPassword: !Ref DatabasePasswordParameter
```

### 7. Create Secure Outputs

Export only non-sensitive values from stacks:

```yaml
Outputs:
  # Safe to export
  KMSKeyArn:
    Description: KMS Key ARN for encryption
    Value: !GetAtt EncryptionKey.Arn
    Export:
      Name: !Sub "${AWS::StackName}-KMSKeyArn"

  SecretArn:
    Description: Secret ARN (not the secret value)
    Value: !Ref DatabaseSecret
    Export:
      Name: !Sub "${AWS::StackName}-SecretArn"

  # DO NOT export sensitive data
  # Incorrect:
  # SecretValue:
  #   Value: !GetAtt DatabaseSecret.SecretString
```

### 8. Encrypt CloudWatch Logs

Enable encryption for log groups:

```yaml
Resources:
  EncryptedLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/applications/${ApplicationName}"
      RetentionInDays: 30
      KmsKeyId: !Ref EncryptionKey
```

## Best Practices

### KMS Key Management

- Use separate keys for different data classifications
- Enable automatic key rotation annually
- Apply key policies limiting access to specific services
- Use customer-managed keys for compliance requirements
- Monitor key usage with CloudWatch metrics
- Back up key material outside AWS (for customer-managed keys)

### Secrets Management

- Rotate secrets automatically (every 30 days for databases)
- Use Secrets Manager for credentials, API keys, and certificates
- Apply least privilege access to secrets
- Enable CloudTrail logging for secret access
- Use IAM policies to control secret access
- Never store secrets in plain text or in code

### IAM Security

- Apply least privilege: grant only necessary permissions
- Use IAM roles for applications, not access keys
- Rotate IAM credentials regularly
- Enable MFA for root account and IAM users
- Use IAM Access Analyzer for permission auditing
- Implement permission boundaries for delegated administration

### Network Security

- Use security groups as primary network control
- Apply NACLs for subnet-level traffic control
- Implement defense in depth with multiple layers
- Use VPC endpoints for private AWS service access
- Enable VPC Flow Logs for network monitoring
- Restrict security group rules to specific CIDR ranges

### Certificate Management

- Use ACM for certificate lifecycle management
- Enable automatic certificate renewal
- Request certificates well before deployment deadlines
- Use DNS validation for faster certificate provisioning
- Monitor certificate expiration with CloudWatch alarms
- Implement certificate rotation for services

### Data Encryption

- Encrypt data at rest and in transit
- Use AWS-managed keys for standard encryption
- Use customer-managed keys for compliance requirements
- Enable SSL/TLS for all network communications
- Use S3 bucket policies for encrypted data access
- Implement encryption in transit with TLS 1.2+

## References

For detailed implementation guidance, see:

- **[constraints.md](references/constraints.md)** - Resource limits (security group rules, VPC limits, NACL rules), security constraints (default security groups, VPC peering, NACL stateless behavior), operational constraints (CIDR overlap, ENI limits, Elastic IP limits), network constraints (Transit Gateway, VPN, Direct Connect), cost considerations (NAT Gateway, traffic mirroring, flow logs, PrivateLink), and access control constraints (IAM vs resource policies, permission boundaries, session policies)

## Related Resources

- [AWS KMS Documentation](https://docs.aws.amazon.com/kms/)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/)
- [VPC Security Documentation](https://docs.aws.amazon.com/vpc/)
- [ACM Certificate Documentation](https://docs.aws.amazon.com/acm/)
- [CloudFormation Security Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [AWS Security Hub Documentation](https://docs.aws.amazon.com/securityhub/)
