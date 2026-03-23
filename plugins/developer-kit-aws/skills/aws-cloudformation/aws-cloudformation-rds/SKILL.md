---
name: aws-cloudformation-rds
description: Provides AWS CloudFormation patterns for Amazon RDS databases. Use when creating RDS instances (MySQL, PostgreSQL, Aurora), DB clusters, multi-AZ deployments, parameter groups, subnet groups, and implementing template structure with Parameters, Outputs, Mappings, Conditions, and cross-stack references.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation RDS Database

## Overview

Create production-ready Amazon RDS infrastructure using AWS CloudFormation templates. Covers RDS instances (MySQL, PostgreSQL, Aurora), DB clusters, multi-AZ deployments, parameter groups, subnet groups, security groups, and cross-stack references.

## When to Use

Use this skill when:
- Creating RDS database instances (MySQL, PostgreSQL, Aurora, MariaDB)
- Configuring DB clusters with read replicas
- Setting up multi-AZ deployments for high availability
- Creating DB parameter groups and option groups
- Configuring DB subnet groups for VPC deployment
- Implementing cross-stack references
- Integrating with Secrets Manager for credentials

## Quick Reference

| Component | CloudFormation Type | Use Case |
|-----------|-------------------|----------|
| DB Instance | `AWS::RDS::DBInstance` | Single database instance |
| DB Cluster | `AWS::RDS::DBCluster` | Aurora cluster |
| DB Subnet Group | `AWS::RDS::DBSubnetGroup` | VPC deployment |
| Parameter Group | `AWS::RDS::DBParameterGroup` | Database configuration |
| Security Group | `AWS::EC2::SecurityGroup` | Network access control |
| Secrets Manager | `AWS::SecretsManager::Secret` | Credential storage |

## Instructions

### Step 1 — Define Database Parameters

Use AWS-specific parameter types for validation.

```yaml
Parameters:
  DBInstanceClass:
    Type: AWS::RDS::DBInstance::InstanceType
    Default: db.t3.micro
    AllowedValues: [db.t3.micro, db.t3.small, db.t3.medium]

  Engine:
    Type: String
    Default: mysql
    AllowedValues: [mysql, postgres, aurora-mysql, aurora-postgresql]

  MasterUsername:
    Type: String
    Default: admin
    AllowedPattern: "^[a-zA-Z][a-zA-Z0-9]*$"
    MinLength: 1
    MaxLength: 16

  MasterUserPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    MaxLength: 41
```

See [template-structure.md](references/template-structure.md) for advanced parameter patterns, mappings, conditions, and cross-stack references.

### Step 2 — Create DB Subnet Group

Required for VPC deployment with subnets in different AZs.

```yaml
DBSubnetGroup:
  Type: AWS::RDS::DBSubnetGroup
  Properties:
    DBSubnetGroupDescription: Subnet group for RDS
    SubnetIds:
      - !Ref PrivateSubnet1
      - !Ref PrivateSubnet2
```

See [database-components.md](references/database-components.md) for parameter groups, option groups, and engine-specific configurations.

### Step 3 — Configure Security Group

Restrict access to application tier only.

```yaml
DBSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Security group for RDS
    VpcId: !Ref VpcId
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 3306
        ToPort: 3306
        SourceSecurityGroupId: !Ref AppSecurityGroup
```

See [security-secrets.md](references/security-secrets.md) for VPC security groups, encryption, Secrets Manager integration, and IAM authentication.

### Step 4 — Launch RDS Instance

Configure instance with subnet group, security group, and settings.

```yaml
DBInstance:
  Type: AWS::RDS::DBInstance
  Properties:
    DBInstanceIdentifier: !Sub "${AWS::StackName}-mysql"
    DBInstanceClass: !Ref DBInstanceClass
    Engine: !Ref Engine
    MasterUsername: !Ref MasterUsername
    MasterUserPassword: !Ref MasterUserPassword
    AllocatedStorage: 20
    StorageType: gp3
    DBSubnetGroupName: !Ref DBSubnetGroup
    VPCSecurityGroups: [!Ref DBSecurityGroup]
    StorageEncrypted: true
    MultiAZ: true
    BackupRetentionPeriod: 7
    DeletionProtection: false
```

See [database-components.md](references/database-components.md) for MySQL, PostgreSQL, Aurora cluster configurations, and parameter groups.

### Step 5 — Enable High Availability

Configure multi-AZ deployment for production.

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      MultiAZ: !If [IsProduction, true, false]
      BackupRetentionPeriod: !If [IsProduction, 35, 7]
      DeletionProtection: !If [IsProduction, true, false]
      EnablePerformanceInsights: !If [IsProduction, true, false]
```

See [high-availability.md](references/high-availability.md) for multi-AZ deployments, read replicas, Aurora auto-scaling, enhanced monitoring, and disaster recovery.

### Step 6 — Define Outputs

Export connection details for application stacks.

```yaml
Outputs:
  DBInstanceEndpoint:
    Description: Database endpoint address
    Value: !GetAtt DBInstance.Endpoint.Address
    Export:
      Name: !Sub ${AWS::StackName}-DBEndpoint

  DBInstancePort:
    Description: Database port
    Value: !GetAtt DBInstance.Endpoint.Port
    Export:
      Name: !Sub ${AWS::StackName}-DBPort

  DBConnectionString:
    Description: Connection string
    Value: !Sub jdbc:mysql://${DBInstance.Endpoint.Address}:${DBInstance.Endpoint.Port}/${DBName}
```

See [template-structure.md](references/template-structure.md) for cross-stack reference patterns and import/export strategies.

## Best Practices

### Security
- **Enable encryption at rest** for all production databases
- **Use Secrets Manager** for credential storage and rotation
- **Restrict security groups** to application tier only
- **Disable public access** - deploy in private subnets
- **Use IAM database authentication** where possible

### High Availability
- **Enable Multi-AZ** for production databases
- **Configure read replicas** for scaling read workloads
- **Set appropriate backup retention** (35 days for production)
- **Enable deletion protection** on production databases
- **Use Aurora** for automatic multi-AZ replication

### Cost Optimization
- **Use gp3 storage** for cost-effective performance
- **Right-size instance classes** based on workload
- **Monitor storage autoscaling** to prevent runaway costs
- **Set backup retention** appropriately per environment
- **Consider Aurora Serverless** for intermittent workloads

### Operations
- **Always use change sets** before updating production stacks
- **Enable drift detection** to maintain template compliance
- **Set stack policies** to protect critical resources
- **Enable termination protection** on production stacks
- **Configure CloudWatch alarms** for monitoring

See [operational-practices.md](references/operational-practices.md) for detailed guidance on stack policies, termination protection, drift detection, change sets, backup strategies, and monitoring.

## References

### Core Configuration
- **[template-structure.md](references/template-structure.md)** — Template sections, parameters, mappings, conditions, outputs, cross-stack references
- **[database-components.md](references/database-components.md)** — DB instances, clusters, parameter groups, subnet groups, Aurora configurations
- **[security-secrets.md](references/security-secrets.md)** — Security groups, encryption, Secrets Manager, IAM authentication
- **[high-availability.md](references/high-availability.md)** — Multi-AZ, read replicas, Aurora auto-scaling, disaster recovery

### Operational Guides
- **[operational-practices.md](references/operational-practices.md)** — Stack policies, termination protection, drift detection, change sets, monitoring
- **[constraints.md](references/constraints.md)** — Resource limits, operational constraints, security constraints, cost considerations

### Additional Resources
- **[examples.md](references/examples.md)** — Complete production-ready examples
- **[reference.md](references/reference.md)** — CloudFormation RDS resource reference

## Constraints and Warnings

### Resource Limits
- Maximum storage size varies by engine (up to 64 TB for MySQL/PostgreSQL)
- Maximum 500 resources per CloudFormation stack
- Parameter group limits vary by account/region

### Cost Considerations
- Multi-AZ deployments cost approximately double single-AZ
- Provisioned IOPS (io1) significantly increases costs
- Backup storage beyond free tier incurs monthly costs
- Manual snapshots incur storage costs even after instance deletion

### Security Constraints
- Master password cannot be retrieved after creation
- Encryption at rest cannot be disabled once enabled
- RDS instances must be in VPC (public access not recommended)
- Security group rules must restrict access to application tier

### Operational Constraints
- Certain modifications (engine version, storage type) require instance replacement with downtime
- Maintenance windows may cause brief service interruptions
- Read replicas may lag behind primary by seconds to minutes
- Not all database engines available in all regions

See [constraints.md](references/constraints.md) for complete constraints, troubleshooting guides, and performance considerations.
