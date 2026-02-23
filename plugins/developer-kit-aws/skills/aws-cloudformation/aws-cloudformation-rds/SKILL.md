---
name: aws-cloudformation-rds
description: Provides AWS CloudFormation patterns for Amazon RDS databases. Use when creating RDS instances (MySQL, PostgreSQL, Aurora), DB clusters, multi-AZ deployments, parameter groups, subnet groups, and implementing template structure with Parameters, Outputs, Mappings, Conditions, and cross-stack references.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation RDS Database

## Overview

Create production-ready Amazon RDS infrastructure using AWS CloudFormation templates. This skill covers RDS instances (MySQL, PostgreSQL, Aurora, MariaDB), DB clusters, multi-AZ deployments, parameter groups, subnet groups, security groups, and cross-stack references.

## When to Use

Use this skill when:
- Creating new RDS database instances (MySQL, PostgreSQL, Aurora, MariaDB)
- Configuring Aurora DB clusters with read replicas
- Setting up multi-AZ deployments for high availability
- Creating DB parameter groups and option groups
- Configuring DB subnet groups for VPC deployment
- Integrating with Secrets Manager for credential management
- Creating Outputs for cross-stack references

## Instructions

1. **Define Database Parameters**: Specify engine, engine version, instance class, and allocated storage
2. **Configure Subnet Group**: Create DBSubnetGroup with subnets in at least 2 AZs
3. **Create Parameter Group**: Define engine-specific parameters (max_connections, innodb_buffer_pool_size, etc.)
4. **Set Up Security Groups**: Allow ingress on DB port (3306 MySQL, 5432 PostgreSQL) from application SG only
5. **Configure Credentials**: Use Secrets Manager with `ManageMasterUserPassword: true` or `MasterUserSecret`
6. **Enable Multi-AZ**: Set `MultiAZ: true` for automatic failover (RDS) or add replicas (Aurora)
7. **Configure Backup**: Set BackupRetentionPeriod (1-35 days), PreferredBackupWindow
8. **Enable Monitoring**: Set MonitoringInterval (1-60s) and EnablePerformanceInsights
9. **Configure Encryption**: Set StorageEncrypted with KmsKeyId
10. **Export Outputs**: Export endpoint address, port, and secret ARN for cross-stack use

## Best Practices

### High Availability
- Use Multi-AZ for automatic failover
- Use Aurora with multiple read replicas for read scaling
- Configure appropriate backup retention (minimum 7 days for production)
- Set maintenance and backup windows during low-traffic periods

### Security
- Use Secrets Manager with automatic rotation for credentials
- Deploy in private subnets with no public accessibility
- Encrypt storage at rest with KMS
- Enable SSL/TLS for connections
- Restrict security groups to specific application security groups

### Performance
- Right-size instance class based on workload
- Use Aurora for high-performance workloads (5x MySQL, 3x PostgreSQL)
- Configure parameter groups for workload optimization
- Enable Performance Insights for query analysis
- Use read replicas for read-heavy workloads

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: RDS PostgreSQL with Multi-AZ

Resources:
  SubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Database subnets
      SubnetIds: !Ref PrivateSubnets

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: RDS security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroup

  ParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Family: postgres16
      Description: Custom parameters
      Parameters:
        max_connections: "200"
        shared_buffers: "{DBInstanceClassMemory/4}"

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub "${AWS::StackName}-db"
      Engine: postgres
      EngineVersion: "16.4"
      DBInstanceClass: db.r6g.large
      AllocatedStorage: 100
      StorageType: gp3
      StorageEncrypted: true
      MultiAZ: true
      ManageMasterUserPassword: true
      MasterUsername: dbadmin
      DBSubnetGroupName: !Ref SubnetGroup
      VPCSecurityGroups:
        - !Ref SecurityGroup
      DBParameterGroupName: !Ref ParameterGroup
      BackupRetentionPeriod: 7
      DeletionProtection: true
      EnablePerformanceInsights: true
      MonitoringInterval: 60
      MonitoringRoleArn: !GetAtt MonitoringRole.Arn

Outputs:
  Endpoint:
    Value: !GetAtt Database.Endpoint.Address
    Export:
      Name: !Sub "${AWS::StackName}-Endpoint"
  Port:
    Value: !GetAtt Database.Endpoint.Port
    Export:
      Name: !Sub "${AWS::StackName}-Port"
```

## Constraints and Warnings

- **Storage**: Min 20 GB for gp2/gp3; max 64 TB for most engines
- **Instance Classes**: Not all instance classes support all engines/versions
- **Multi-AZ**: Doubles cost; Aurora uses separate pricing model
- **Backup Retention**: Max 35 days; cannot disable for Aurora
- **Encryption**: Cannot encrypt an existing unencrypted instance
- **Parameter Group**: Some changes require reboot (static parameters)
- **Deletion Protection**: Must be disabled before stack deletion
- **Secrets Manager**: ManageMasterUserPassword creates a secret automatically
- **Aurora**: Uses cluster endpoint (writer) and reader endpoint separately

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
