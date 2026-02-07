# ElastiCache CloudFormation Reference

This file contains detailed reference information for Amazon ElastiCache CloudFormation resources.

## Table of Contents

- [AWS::ElastiCache::Cluster](#awselasticachecluster)
- [AWS::ElastiCache::ReplicationGroup](#awselasticachereplicationgroup)
- [AWS::ElastiCache::ParameterGroup](#awselasticacheparametergroup)
- [AWS::ElastiCache::SubnetGroup](#awselasticachesubnetgroup)
- [AWS::ElastiCache::SecurityGroup](#awselasticachesecuritygroup)
- [AWS::ElastiCache::SecurityGroupIngress](#awselasticachesecuritygroupingress)
- [AWS::ElastiCache::GlobalReplicationGroup](#awselasticacheglobalreplicationgroup)
- [Cache Node Types](#cache-node-types)
- [Engine Versions](#engine-versions)
- [Common Configuration Options](#common-configuration-options)

---

## AWS::ElastiCache::Cluster

The `AWS::ElastiCache::Cluster` resource creates an Amazon ElastiCache cache cluster.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| CacheNodeType | String | The compute and memory capacity of the cache node |
| Engine | String | The name of the cache engine (redis or memcached) |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| AutoMinorVersionUpgrade | Boolean | true | Whether minor version upgrades are applied automatically |
| CacheClusterIdentifier | String | - | The identifier for the cache cluster |
| CacheParameterGroupName | String | default | The parameter group to associate |
| CacheSubnetGroupName | String | - | The subnet group for the cache cluster |
| EngineVersion | String | - | The version number of the cache engine |
| NumCacheNodes | Number | 1 | The number of cache nodes |
| SnapshotArns | List | - | The ARN of a snapshot to use |
| SnapshotRetentionLimit | Number | 0 | The number of days to retain snapshots |
| SnapshotWindow | String | - | The daily time range for snapshot creation |
| VpcSecurityGroupIds | List | - | VPC security groups |
| AtRestEncryptionEnabled | Boolean | false | Whether encryption at rest is enabled |
| TransitEncryptionEnabled | Boolean | false | Whether encryption in transit is enabled |
| AuthToken | String | - | The password for Redis AUTH |
| Tags | List | - | Tags for the cache cluster |

### Important Attributes

| Attribute | Description |
|-----------|-------------|
| RedisEndpoint.Address | The DNS address of the cache cluster |
| RedisEndpoint.Port | The port number |
| ConfigurationEndpoint.Address | For memcached cluster, the configuration endpoint |
| ConfigurationEndpoint.Port | For memcached cluster, the configuration port |
| Arn | The ARN of the cache cluster |

### Important Notes

- **NumCacheNodes**: For Redis, setting >1 enables clustering features
- **AtRestEncryptionEnabled**: Requires Redis 3.2.6 or later
- **TransitEncryptionEnabled**: Requires Redis 3.2.6 or later
- **AuthToken**: Redis AUTH command password, requires TLS enabled
- **SnapshotRetentionLimit**: Maximum 35 days

### Example

```yaml
Resources:
  MyCacheCluster:
    Type: AWS::ElastiCache::Cluster
    Properties:
      CacheClusterIdentifier: my-redis-cluster
      CacheNodeType: cache.t3.medium
      NumCacheNodes: 1
      Engine: redis
      EngineVersion: "7.0"
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref CacheParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      AutoMinorVersionUpgrade: true
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
```

---

## AWS::ElastiCache::ReplicationGroup

The `AWS::ElastiCache::ReplicationGroup` resource creates an Amazon ElastiCache replication group.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| ReplicationGroupDescription | String | The description of the replication group |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| AtRestEncryptionEnabled | Boolean | false | Whether encryption at rest is enabled |
| AuthToken | String | - | The password for Redis AUTH |
| AutomaticFailoverEnabled | Boolean | false | Whether automatic failover is enabled |
| CacheNodeType | String | cache.t3.micro | The compute and memory capacity |
| CacheParameterGroupName | String | - | The parameter group to associate |
| CacheSubnetGroupName | String | - | The subnet group |
| Engine | String | redis | The cache engine |
| EngineVersion | String | - | The engine version |
| GlobalReplicationGroupId | String | - | The global replication group ID |
| KmsKeyId | String | - | The KMS key for encryption |
| MultiAZEnabled | Boolean | false | Whether Multi-AZ is enabled |
| NodeGroupConfiguration | List | - | Configuration for node groups |
| NumNodeGroups | Number | 1 | Number of node groups (for cluster mode) |
| ReplicasPerNodeGroup | Number | 0 | Replicas per node group |
| ReplicationGroupIdentifier | String | - | The replication group identifier |
| SecurityGroupIds | List | - | VPC security groups |
| Tags | List | - | Tags for the replication group |

### Important Attributes

| Attribute | Description |
|-----------|-------------|
| PrimaryEndPoint.Address | The primary endpoint address |
| PrimaryEndPoint.Port | The primary endpoint port |
| ReaderEndPoint.Address | The reader endpoint address |
| ReaderEndPoint.Port | The reader endpoint port |
| MemberClusters | List of cluster IDs in the replication group |
| Arn | The ARN of the replication group |

### Important Notes

- **AutomaticFailoverEnabled**: Requires at least one replica
- **MultiAZEnabled**: Requires AutomaticFailoverEnabled
- **NumNodeGroups**: For Redis Cluster mode, must be >1
- **ReplicasPerNodeGroup**: Each node group needs primary + replicas
- **GlobalReplicationGroupId**: For cross-region replication

### Example

```yaml
Resources:
  MyReplicationGroup:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupIdentifier: my-redis-rg
      ReplicationGroupDescription: Primary and replicas for HA
      Engine: redis
      EngineVersion: "7.0"
      CacheNodeType: cache.r5.large
      NumNodeGroups: 1
      ReplicasPerNodeGroup: 2
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref CacheParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
```

### NodeGroupConfiguration

```yaml
NodeGroupConfiguration:
  - NodeGroupId: "0001"
    Slots: "0-8191"
    ReplicaCount: 2
    PrimaryAvailabilityZone: us-east-1a
    ReplicaAvailabilityZones:
      - us-east-1b
      - us-east-1c
```

---

## AWS::ElastiCache::ParameterGroup

The `AWS::ElastiCache::ParameterGroup` resource creates a custom parameter group for cache configuration.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| Description | String | The description of the parameter group |
| Family | String | The parameter group family (redis7.x, memcached1.6, etc.) |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| CacheParameterGroupName | String | The name of the parameter group |
| Parameters | Map | The parameters to set |
| Tags | List | Tags for the parameter group |

### Redis 7.x Parameters

```yaml
Parameters:
  # Memory management
  maxmemory-policy: allkeys-lru
  maxmemory-samples: 5
  maxmemory-eviction-tenacity: 10

  # Connection settings
  timeout: 300
  tcp-keepalive: 300
  tcp-backlog: 511

  # Slow log
  slowlog-log-slower-than: 10000
  slowlog-max-len: 128

  # Logging
  logfile: /var/log/redis/redis-server.log
  loglevel: notice

  # Cluster settings
  cluster-enabled: yes
  cluster-require-full-coverage: no

  # Client settings
  maxclients: 10000
  timeout: 0
  tcp-keepalive: 300

  # Persistence
  save: "900 1 300 100 60 10000"
  appendonly: yes
  appendfsync: everysec
```

### Redis 6.x Parameters

```yaml
Parameters:
  maxmemory-policy: allkeys-lru
  timeout: 300
  tcp-keepalive: 300
  slowlog-log-slower-than: 10000
  cluster-enabled: no
```

### Memcached 1.6 Parameters

```yaml
Parameters:
  max_item_size: 10485760
  request_max_size: 2097152
  connection_idle_timeout: 600
  disable_cas: on
  backlog_queue_limit: 1024
  chunk_size: 48
  item_size_max: 1048576
```

### Example

```yaml
Resources:
  MyCacheParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: Custom Redis 7.0 parameter group
      Family: redis7.x
      Parameters:
        maxmemory-policy: allkeys-lru
        timeout: 300
        slowlog-log-slower-than: 10000
        cluster-enabled: no
```

---

## AWS::ElastiCache::SubnetGroup

The `AWS::ElastiCache::SubnetGroup` resource creates a cache subnet group for VPC deployment.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| Description | String | The description of the subnet group |
| SubnetIds | List | The IDs of the subnets |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| CacheSubnetGroupName | String | The name of the subnet group |
| Tags | List | Tags for the subnet group |

### Requirements

- Must include at least 2 subnets in different Availability Zones
- Subnets must be in the same VPC
- All subnets must have available IP addresses

### Example

```yaml
Resources:
  MyCacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for production ElastiCache
      CacheSubnetGroupName: production-cache-subnet
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
        - !Ref PrivateSubnet3
```

---

## AWS::ElastiCache::SecurityGroup

The `AWS::ElastiCache::SecurityGroup` resource creates an EC2-Classic security group for ElastiCache (deprecated, use VPC security groups instead).

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| Description | String | The description of the security group |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| CacheSecurityGroupName | String | The name of the security group |
| Tags | List | Tags for the security group |

### Example (EC2-Classic)

```yaml
Resources:
  MyCacheSecurityGroup:
    Type: AWS::ElastiCache::SecurityGroup
    Properties:
      Description: Security group for ElastiCache
      CacheSecurityGroupName: cache-sg
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-cache-sg
```

### Note

For VPC deployments, use `AWS::EC2::SecurityGroup` instead:

```yaml
Resources:
  MyCacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ElastiCache
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroup
```

---

## AWS::ElastiCache::SecurityGroupIngress

The `AWS::ElastiCache::SecurityGroupIngress` resource authorizes ingress to a cache security group.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| CacheSecurityGroupName | String | The name of the cache security group |
| EC2SecurityGroupName | String | The name of the EC2 security group |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| EC2SecurityGroupOwnerId | String | The AWS account ID for the EC2 security group |

### Example

```yaml
Resources:
  MyCacheSecurityGroupIngress:
    Type: AWS::ElastiCache::SecurityGroupIngress
    Properties:
      CacheSecurityGroupName: !Ref CacheSecurityGroup
      EC2SecurityGroupName: !Ref AppSecurityGroup
```

---

## AWS::ElastiCache::GlobalReplicationGroup

The `AWS::ElastiCache::GlobalReplicationGroup` resource creates a global replication group for cross-region replication.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| GlobalReplicationGroupIdSuffix | String | The suffix for the global replication group ID |
| Members | List | The replication groups to include |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| GlobalReplicationGroupDescription | String | The description of the global replication group |

### Member Configuration

| Property | Type | Description |
|----------|------|-------------|
| ReplicationGroupId | String | The replication group ID |
| ReplicationGroupRegion | String | The region of the replication role |

### Example

```yaml
Resources:
  MyGlobalReplicationGroup:
    Type: AWS::ElastiCache::GlobalReplicationGroup
    Properties:
      GlobalReplicationGroupIdSuffix: global
      GlobalReplicationGroupDescription: Global Redis replication
      Members:
        - ReplicationGroupId: !Ref PrimaryReplicationGroup
          ReplicationGroupRegion: !Ref AWS::Region
        - ReplicationGroupId: !Ref SecondaryReplicationGroup
          ReplicationGroupRegion: us-west-2
```

---

## Cache Node Types

### Burstable Performance (T3/T2)

| Node Type | vCPU | Memory (GiB) | Use Case |
|-----------|------|--------------|----------|
| cache.t3.micro | 2 | 0.5 | Development, test |
| cache.t3.small | 2 | 1.4 | Small workloads |
| cache.t3.medium | 2 | 3.1 | Medium workloads |
| cache.t3.large | 2 | 6.1 | Large development |
| cache.t2.micro | 1 | 0.5 | Free tier |
| cache.t2.small | 1 | 1.6 | Small test |
| cache.t2.medium | 2 | 3.3 | Medium test |

### General Purpose (M5/M4)

| Node Type | vCPU | Memory (GiB) | Use Case |
|-----------|------|--------------|----------|
| cache.m5.large | 2 | 6.7 | General purpose |
| cache.m5.xlarge | 4 | 13.4 | Medium production |
| cache.m5.2xlarge | 8 | 26.9 | Large production |
| cache.m5.4xlarge | 16 | 53.9 | XLarge production |
| cache.m5.12xlarge | 48 | 162 | Enterprise |
| cache.m4.large | 2 | 6.1 | Legacy general |
| cache.m4.xlarge | 4 | 12.3 | Legacy medium |
| cache.m4.2xlarge | 8 | 24.6 | Legacy large |

### Memory Optimized (R5/R4)

| Node Type | vCPU | Memory (GiB) | Use Case |
|-----------|------|--------------|----------|
| cache.r5.large | 2 | 13.5 | Memory optimized |
| cache.r5.xlarge | 4 | 27.0 | Medium memory |
| cache.r5.2xlarge | 8 | 54.0 | Large memory |
| cache.r5.4xlarge | 16 | 108 | XLarge memory |
| cache.r5.8xlarge | 32 | 208 | Enterprise |
| cache.r5.12xlarge | 48 | 335 | Large enterprise |
| cache.r4.large | 2 | 12.3 | Legacy memory |
| cache.r4.xlarge | 4 | 24.6 | Legacy medium |
| cache.r4.2xlarge | 8 | 49.0 | Legacy large |

### Memory Optimized Graviton (R6g/R6gd)

| Node Type | vCPU | Memory (GiB) | Use Case |
|-----------|------|--------------|----------|
| cache.r6g.large | 2 | 13.5 | Graviton memory |
| cache.r6g.xlarge | 4 | 27.0 | Graviton medium |
| cache.r6g.2xlarge | 8 | 54.0 | Graviton large |
| cache.r6g.4xlarge | 16 | 108 | Graviton xlarge |
| cache.r6gd.large | 2 | 13.5 | Graviton + NVMe |
| cache.r6gd.xlarge | 4 | 27.0 | Graviton + NVMe |
| cache.r6gd.2xlarge | 8 | 54.0 | Graviton + NVMe |

### Current Generation Selection

For new workloads, prefer:
- **General Purpose**: cache.m6g, cache.m5
- **Memory Optimized**: cache.r6g, cache.r5
- **Burstable**: cache.t3 (avoid t2 for new workloads)

---

## Engine Versions

### Redis Versions

| Version | Family | Status | Notes |
|---------|--------|--------|-------|
| 7.0 | redis7.x | Current | Latest features |
| 6.2 | redis6.x | Supported | TLS improvements |
| 6.0 | redis6.x | Supported | Redis 6 features |
| 5.0.6 | redis5.0.6 | Legacy | Redis 5.0 |

### Memcached Versions

| Version | Family | Status | Notes |
|---------|--------|--------|-------|
| 1.6 | memcached1.6 | Current | Latest features |
| 1.5 | memcached1.5 | Supported | Legacy |

### Version Selection Best Practices

- Use the latest Redis version (7.0) for new deployments
- Memcached 1.6 includes performance improvements
- Consider application compatibility when upgrading

---

## Common Configuration Options

### Redis Memory Management

```yaml
Parameters:
  # LRU (Least Recently Used) eviction
  maxmemory-policy: allkeys-lru

  # LFU (Least Frequently Used) eviction
  maxmemory-policy: allkeys-lfu

  # No eviction (will error on write)
  maxmemory-policy: noeviction

  # Volatile keys only
  maxmemory-policy: volatile-lru
  maxmemory-policy: volatile-lfu
  maxmemory-policy: volatile-ttl
  maxmemory-policy: volatile-random

  # Eviction sample count
  maxmemory-samples: 5
```

### Redis Cluster Configuration

```yaml
Parameters:
  # Enable cluster mode
  cluster-enabled: yes

  # Cluster node timeout
  cluster-node-timeout: 5000

  # Cluster configuration
  cluster-config-file: nodes.conf

  # Full coverage requirement
  cluster-require-full-coverage: no
```

### Memcached Configuration

```yaml
Parameters:
  # Maximum item size (10MB)
  max_item_size: 10485760

  # Request maximum size
  request_max_size: 2097152

  # Connection idle timeout
  connection_idle_timeout: 600

  # Disable CAS
  disable_cas: on

  # Backlog queue limit
  backlog_queue_limit: 1024
```

### Backup and Recovery

```yaml
Resources:
  CacheCluster:
    Type: AWS::ElastiCache::Cluster
    Properties:
      # Snapshot window (UTC)
      SnapshotWindow: "05:00-06:00"

      # Retention period (days)
      SnapshotRetentionLimit: 35

      # Snapshot ARN (for restore)
      SnapshotArns:
        - !Ref SnapshotArn
```

### Monitoring and Logging

```yaml
Parameters:
  # Slow log settings
  slowlog-log-slower-than: 10000
  slowlog-max-len: 128

  # Log level
  logfile: /var/log/redis/redis-server.log
  loglevel: notice
```

### Connection Settings

```yaml
Parameters:
  # Client connection timeout
  timeout: 300

  # TCP keepalive
  tcp-keepalive: 300

  # TCP backlog
  tcp-backlog: 511

  # Maximum clients
  maxclients: 10000

  # Timeout disabled
  timeout: 0
```

---

## Useful Links

- [AWS::ElastiCache::Cluster Documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-cache-cluster.html)
- [AWS::ElastiCache::ReplicationGroup Documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html)
- [AWS::ElastiCache::ParameterGroup Documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-parameter-group.html)
- [AWS::ElastiCache::SubnetGroup Documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticache-subnetgroup.html)
- [ElastiCache Node Types](https://docs.aws.amazon.com/AmazonElastiCache/latest/redsug/节点类型.html)
- [ElastiCache User Guide](https://docs.aws.amazon.com/AmazonElastiCache/latest/redsug/)
- [Redis Documentation](https://redis.io/documentation)
- [Memcached Documentation](https://memcached.org/documentation)
