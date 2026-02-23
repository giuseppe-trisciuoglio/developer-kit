---
name: aws-cloudformation-elasticache
description: Provides AWS CloudFormation patterns for Amazon ElastiCache. Use when creating ElastiCache clusters (Redis, Memcached), replication groups, parameter groups, subnet groups, and implementing template structure with Parameters, Outputs, Mappings, Conditions, and cross-stack references for distributed caching infrastructure.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation ElastiCache

## Overview

Create production-ready Amazon ElastiCache infrastructure using AWS CloudFormation templates. This skill covers Redis clusters, Memcached clusters, replication groups, parameter groups, subnet groups, security groups, and cross-stack references for modular caching infrastructure.

## When to Use

Use this skill when:
- Creating new ElastiCache Redis clusters (standalone or clustered)
- Setting up Redis Replication Groups for high availability
- Creating Memcached clusters for distributed caching
- Configuring ElastiCache Parameter Groups
- Setting up ElastiCache Subnet Groups for VPC deployment
- Creating Outputs for cross-stack references
- Organizing templates with Mappings and Conditions

## Instructions

1. **Define Cluster Parameters**: Specify engine (redis/memcached), node type, and number of nodes
2. **Configure Subnet Group**: Create CacheSubnetGroup with VPC subnets across AZs
3. **Create Parameter Group**: Define engine-specific settings (maxmemory-policy, timeout, etc.)
4. **Set Up Security Groups**: Configure ingress rules for application access (port 6379 Redis, 11211 Memcached)
5. **Create Replication Group**: For Redis HA, set NumNodeGroups, ReplicasPerNodeGroup, AutomaticFailoverEnabled
6. **Configure Backups**: Set SnapshotRetentionLimit and SnapshotWindow for Redis
7. **Enable Encryption**: Set AtRestEncryptionEnabled and TransitEncryptionEnabled for Redis
8. **Enable Auth**: Set AuthToken for Redis AUTH password
9. **Add Monitoring**: Enable CloudWatch metrics for cache hit ratio, evictions, memory
10. **Export Outputs**: Export endpoint addresses and ports for cross-stack references

## Best Practices

### High Availability
- Use Multi-AZ replication groups for Redis
- Configure automatic failover with at least one replica
- Use cluster mode enabled for horizontal scaling
- Set appropriate backup and maintenance windows

### Performance
- Choose node type based on memory and network requirements
- Configure maxmemory-policy (allkeys-lru for cache, noeviction for data store)
- Use connection pooling in application code
- Monitor cache hit ratio and evictions

### Security
- Enable encryption at rest and in transit for Redis
- Use AUTH tokens for Redis authentication
- Deploy in private subnets with security groups
- Use VPC endpoints for ElastiCache access

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Redis replication group with encryption

Resources:
  SubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Cache subnet group
      SubnetIds: !Ref PrivateSubnets

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: ElastiCache security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroup

  ParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      CacheParameterGroupFamily: redis7
      Description: Custom Redis parameters
      Properties:
        maxmemory-policy: allkeys-lru
        timeout: "300"

  ReplicationGroup:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupDescription: !Sub "${AWS::StackName}-redis"
      Engine: redis
      EngineVersion: "7.1"
      CacheNodeType: cache.r7g.large
      NumNodeGroups: 1
      ReplicasPerNodeGroup: 1
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
      CacheSubnetGroupName: !Ref SubnetGroup
      SecurityGroupIds:
        - !Ref SecurityGroup
      CacheParameterGroupName: !Ref ParameterGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
      SnapshotRetentionLimit: 7
      SnapshotWindow: "03:00-05:00"

Outputs:
  PrimaryEndpoint:
    Value: !GetAtt ReplicationGroup.PrimaryEndPoint.Address
    Export:
      Name: !Sub "${AWS::StackName}-Endpoint"
  Port:
    Value: !GetAtt ReplicationGroup.PrimaryEndPoint.Port
    Export:
      Name: !Sub "${AWS::StackName}-Port"
```

## Constraints and Warnings

- **Node Type Limits**: Available node types vary by engine and region
- **Cluster Mode**: Cannot change cluster mode after creation
- **Encryption**: Cannot enable encryption on existing clusters; must create new
- **AUTH Token**: Cannot change after creation; plan token rotation strategy
- **Backup**: Only available for Redis, not Memcached
- **Multi-AZ**: Requires at least one replica for automatic failover
- **Subnet Group**: Must have subnets in at least two AZs for Multi-AZ
- **Parameter Group**: Some parameters require cluster restart to take effect

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
