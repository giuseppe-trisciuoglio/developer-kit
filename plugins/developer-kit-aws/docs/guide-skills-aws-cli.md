# AWS CLI Skills Guide

This guide covers the AWS CLI Beast Mode skill for advanced cloud operations, automation, and resource management from the command line.

## Overview

The AWS CLI (Command Line Interface) is a unified tool to manage your AWS services. The `aws-cli-beast` skill provides advanced patterns, automation scripts, and best practices for power users who need to manage AWS resources efficiently at scale.

## When to Use AWS CLI Skills

Use the AWS CLI skills when you need to:

- Perform bulk operations across thousands of AWS resources
- Create automated scripts for routine AWS operations
- Troubleshoot AWS networking, security, or compute issues
- Manage multiple AWS profiles and regions simultaneously
- Implement infrastructure-as-code workflows via CLI
- Perform security audits and compliance checks
- Work with AWS services that require waiters and polling
- Handle AWS CLI pagination for large datasets

## Available Skills

| Skill | Description |
|-------|-------------|
| `aws-cli-beast` | Comprehensive AWS CLI mastery for advanced cloud engineers |

## Core Capabilities

### Service Coverage

The `aws-cli-beast` skill covers the following AWS services with advanced CLI patterns:

1. **Compute**: EC2 (instances, spot fleets, ASG), Lambda (deployment, invocation, layers)
2. **Storage**: S3 (sync, multipart, lifecycle, replication, presigned URLs)
3. **Database**: DynamoDB (queries, batch operations, TTL), RDS (snapshots, parameter groups)
4. **Networking**: VPC (subnets, security groups, flow logs, NAT Gateway)
5. **Security & Identity**: IAM (policies, roles, access keys, password policy)
6. **AI/ML**: Bedrock (model invocation, provisioning, custom models)
7. **Observability**: CloudWatch (logs, metrics, alarms, dashboards)

### Beast Mode Features

#### Advanced Querying with JMESPath

Use `--query` flag to transform and filter AWS CLI output server-side:

```bash
# Get instance IDs and private IPs in one command
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,PrivateIpAddress,State.Name]' \
  --output table

# Filter by tag and get only running instances
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId,Tags[?Key==`Name`].Value[0]]' \
  --output json
```

#### Bulk Operations

Handle thousands of resources efficiently:

```bash
# Stop all EC2 instances in a specific tag
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=development" \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text | xargs aws ec2 stop-instances --instance-ids

# Delete old CloudWatch log streams
aws logs describe-log-streams \
  --log-group-name /aws/lambda/my-function \
  --query 'logStreams[?lastIngestionTime<`${cutoff_timestamp}`].logStreamName' \
  --output text | xargs -r aws logs delete-log-stream --log-group-name /aws/lambda/my-function --log-stream-name
```

#### Waiters and Polling

Properly handle asynchronous resource provisioning:

```bash
# Wait for EC2 instance to be running
aws ec2 wait instance-running --instance-ids i-1234567890abcdef0

# Wait for Lambda function to be active
aws lambda wait function-active --function-name my-function

# Wait for RDS instance to be available
aws rds wait db-instance-available --db-instance-identifier my-db
```

#### Security-First Patterns

Always apply security best practices:

```bash
# Dry run before any destructive operation
aws s3 rm s3://my-bucket/important/ --dryrun

# Validate IAM policy before attaching
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/myuser \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/*
```

#### Profile and Region Management

Seamlessly switch between AWS accounts and regions:

```bash
# List all available profiles
aws configure list-profiles

# Use specific profile
aws --profile production ec2 describe-instances

# Multi-region query
for region in us-east-1 us-west-2 eu-west-1; do
  aws --region $region ec2 describe-vpcs --query 'Vpcs[].VpcId'
done
```

## Reference Materials

The `aws-cli-beast` skill includes comprehensive reference guides:

### Reference Guides

| Guide | Description |
|-------|-------------|
| `compute-mastery.md` | EC2 and Lambda advanced patterns |
| `data-ops-beast.md` | S3, DynamoDB, and RDS bulk operations |
| `networking-security-hardened.md` | VPC, IAM, and security auditing |
| `automation-patterns.md` | Scripts, aliases, and JMESPath templates |

### Helper Scripts

| Script | Description |
|--------|-------------|
| `aws-blast.sh` | 30+ ready-to-use shell aliases for daily AWS operations |
| `jmespath-templates.json` | 20+ JMESPath query templates for common use cases |

## Best Practices

1. **Always use `--output json`** for programmatically processable output
2. **Use JMESPath** to filter data server-side, reducing bandwidth
3. **Implement proper error handling** with exit codes and retry logic
4. **Use waiters** instead of manual polling for resource state changes
5. **Enable CloudTrail** for audit compliance on all operations
6. **Use least-privilege IAM policies** with `iam-simulate-principal-policy`
7. **Tag all resources** for cost allocation and automation
8. **Use `--dry-run`** for any operation that modifies state
9. **Enable MFA** for operations that modify security settings
10. **Use profiles** for separating development, staging, and production

## Trigger Phrases

The skill activates on phrases like:
- "aws beast mode"
- "optimize aws resources via cli"
- "bulk s3 migration cli"
- "audit iam policies beast"
- "troubleshoot vpc networking cli"
- "aws cli automation"
- "lambda deployment cli beast"
- "dynamodb bulk operations"
- "ec2 fleet management cli"
- "iam policy audit cli"

## Integration with Other Skills

The AWS CLI skill complements other AWS-related capabilities:

- **CloudFormation Skills**: Use CLI for stack operations and drift detection
- **Java AWS SDK Skills**: Combine CLI for quick checks with SDK for application integration
- **Architecture Review**: Use CLI to gather resource information for architecture reviews

## See Also

- [CloudFormation Skills Guide](./guide-skills-cloudformation.md) - Infrastructure as Code with CloudFormation
- [AWS Agents Guide](./guide-agents.md) - AWS specialized agents
- [Java AWS Skills Guide](../developer-kit-java/docs/guide-skills-aws-java.md) - AWS SDK integration from Java
