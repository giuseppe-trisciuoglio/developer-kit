---
name: aws-cloudformation-iam
description: Provides AWS CloudFormation patterns for IAM users, roles, policies, and managed policies. Use when creating IAM resources with CloudFormation, implementing least privilege access, configuring cross-account access, setting up identity centers, managing permissions boundaries, and organizing template structure with Parameters, Outputs, Mappings, Conditions for secure infrastructure deployments.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation IAM Security

## Overview

Create production-ready IAM infrastructure using AWS CloudFormation templates. This skill covers users, roles, policies, managed policies, permission boundaries, cross-account access, and best practices for implementing least privilege access.

## When to Use

Use this skill when:
- Creating IAM roles for AWS services (Lambda, ECS, EC2, etc.)
- Defining inline policies and managed policies
- Implementing cross-account access with STS AssumeRole
- Creating permission boundaries
- Configuring IAM Identity Center (SSO)
- Managing service control policies (SCP)
- Implementing cross-stack references for IAM resources

## Instructions

1. **Create IAM Roles**: Define AssumeRolePolicyDocument with specific service principals
2. **Write Policies**: Use specific actions (not `*`), scope resources with ARNs, add conditions
3. **Set Up Permission Boundaries**: Attach ManagedPolicyArn as PermissionsBoundary on roles
4. **Configure Cross-Account**: Use `sts:AssumeRole` with external account principals and ExternalId
5. **Create Managed Policies**: Define reusable policies with `AWS::IAM::ManagedPolicy`
6. **Use Condition Keys**: Add `aws:SourceAccount`, `aws:SourceArn`, `aws:RequestedRegion` conditions
7. **Create Instance Profiles**: Associate roles with EC2 via `AWS::IAM::InstanceProfile`
8. **Export Role ARNs**: Export role ARNs for cross-stack references

## Best Practices

### Least Privilege
- Never use `Action: "*"` or `Resource: "*"` in production
- Scope resources to specific ARN patterns using `!Sub`
- Use condition keys to further restrict access
- Prefer managed policies over inline for reusability
- Use permission boundaries to cap maximum permissions

### Security
- Require MFA for sensitive operations
- Use service-linked roles when available
- Rotate credentials regularly
- Enable CloudTrail for IAM API auditing
- Never embed credentials in CloudFormation templates

### Organization
- Use naming conventions: `${AWS::StackName}-<purpose>-role`
- Group related permissions in single policy statements
- Use separate roles for different services (not one role for everything)

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: IAM roles with least privilege

Resources:
  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-role"
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
        - PolicyName: DynamoDBAccess
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:Query
                Resource: !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${TableName}"
              - Effect: Allow
                Action:
                  - dynamodb:Query
                Resource: !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${TableName}/index/*"

  CrossAccountRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-cross-account"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${TrustedAccountId}:root"
            Action: sts:AssumeRole
            Condition:
              StringEquals:
                sts:ExternalId: !Ref ExternalId

Outputs:
  LambdaRoleArn:
    Value: !GetAtt LambdaRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-LambdaRoleArn"
```

## Constraints and Warnings

- **Policy Size**: Inline policy max 10,240 characters; managed policy max 6,144 characters
- **Roles per Account**: Default limit 1,000 IAM roles per account
- **Policies per Role**: Max 10 managed policies attached to a role
- **Trust Policy**: Max 2,048 characters for AssumeRolePolicyDocument
- **CAPABILITY_NAMED_IAM**: Required when creating named IAM resources
- **Circular Dependencies**: Avoid roles referencing resources that reference the role
- **Deletion**: Roles with attached policies cannot be deleted; CloudFormation handles this
- **Service-Linked Roles**: Cannot be modified or deleted via CloudFormation

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
