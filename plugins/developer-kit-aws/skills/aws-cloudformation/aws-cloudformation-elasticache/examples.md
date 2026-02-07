# ElastiCache CloudFormation Examples

This file contains comprehensive examples for Amazon ElastiCache CloudFormation templates.

## Table of Contents

- [Complete Production Redis Cluster Template](#complete-production-redis-cluster-template)
- [Complete Production Memcached Cluster Template](#complete-production-memcached-cluster-template)
- [Complete Redis Replication Group Template](#complete-redis-replication-group-template)
- [Redis Cluster Mode Template](#redis-cluster-mode-template)
- [Multi-Region Redis Replication Template](#multi-region-redis-replication-template)
- [Redis with Encryption and Auth Template](#redis-with-encryption-and-auth-template)
- [Memcached with Auto Discovery Template](#memcached-with-auto-discovery-template)
- [Complete Network Stack for ElastiCache](#complete-network-stack-for-elasticache)
- [Serverless Redis Template](#serverless-redis-template)

---

## Complete Production Redis Cluster Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production-ready Redis ElastiCache cluster with enhanced monitoring and encryption

Parameters:
  EnvironmentName:
    Type: String
    Default: production
    Description: Environment name for resource tagging

  EnvironmentType:
    Type: String
    Default: production
    AllowedValues:
      - development
      - staging
      - production

  CacheClusterIdentifier:
    Type: String
    Default: myapp-redis
    Description: Cache cluster identifier
    AllowedPattern: "[a-zA-Z][a-zA-Z0-9]*"
    MinLength: 1
    MaxLength: 50

  CacheNodeType:
    Type: String
    Default: cache.r5.large
    Description: Cache node instance type

  NumCacheNodes:
    Type: Number
    Default: 1
    Description: Number of cache nodes
    MinValue: 1
    MaxValue: 10

  EngineVersion:
    Type: String
    Default: "7.0"
    Description: Redis engine version

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC for ElastiCache deployment

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id
    Description: Private subnet 1

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id
    Description: Private subnet 2

  PrivateSubnet3Id:
    Type: AWS::EC2::Subnet::Id
    Description: Private subnet 3

  AppSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id
    Description: Application security group

  KmsKeyId:
    Type: AWS::KMS::Key::Id
    Description: KMS key for encryption

Conditions:
  IsProduction: !Equals [!Ref EnvironmentType, production]
  MultiAZ: !And
    - !Equals [!Ref NumCacheNodes, 1]
    - !Equals [!Ref EnvironmentType, production]

Resources:
  # Cache Subnet Group
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: !Sub Subnet group for ${EnvironmentName} ElastiCache
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-redis-subnet
        - Key: Environment
          Value: !Ref EnvironmentName

  # Cache Parameter Group
  CacheParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: !Sub Redis ${EngineVersion} parameter group
      Family: !Sub redis${EngineVersion.Split('.')[0]}.x
      Parameters:
        maxmemory-policy: allkeys-lru
        maxmemory-samples: 5
        timeout: 300
        tcp-keepalive: 300
        slowlog-log-slower-than: 10000
        slowlog-max-len: 128
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-redis-param
        - Key: Environment
          Value: !Ref EnvironmentName

  # Cache Security Group
  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Redis
      VpcId: !Ref VPCId
      GroupName: !Sub ${EnvironmentName}-redis-sg
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroupId
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-redis-sg
        - Key: Environment
          Value: !Ref EnvironmentName

  # Cache Cluster
  CacheCluster:
    Type: AWS::ElastiCache::Cluster
    Properties:
      CacheClusterIdentifier: !Ref CacheClusterIdentifier
      CacheNodeType: !Ref CacheNodeType
      NumCacheNodes: !Ref NumCacheNodes
      Engine: redis
      EngineVersion: !Ref EngineVersion
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref CacheParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      AutoMinorVersionUpgrade: true
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
      # For multi-AZ, use ReplicationGroup instead
      SnapshotRetentionLimit: !If [IsProduction, 35, 7]
      SnapshotWindow: "05:00-06:00"
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-redis
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: EnvironmentType
          Value: !Ref EnvironmentType
        - Key: ManagedBy
          Value: CloudFormation

Outputs:
  CacheClusterId:
    Description: Cache Cluster ID
    Value: !Ref CacheCluster

  CacheClusterEndpoint:
    Description: Cache cluster endpoint address
    Value: !GetAtt CacheCluster.RedisEndpoint.Address

  CacheClusterPort:
    Description: Cache cluster port
    Value: !GetAtt CacheCluster.RedisEndpoint.Port

  CacheClusterArn:
    Description: Cache Cluster ARN
    Value: !GetAtt CacheCluster.Arn

  ConnectionString:
    Description: Redis connection string
    Value: !Sub redis://${CacheClusterEndpoint}:${CacheClusterPort}/0

  SecurityGroupId:
    Description: Security Group ID for reference
    Value: !Ref CacheSecurityGroup

  ParameterGroupName:
    Description: Parameter Group Name for reference
    Value: !Ref CacheParameterGroup
```

---

## Complete Production Memcached Cluster Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production-ready Memcached ElastiCache cluster with auto discovery

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  CacheClusterIdentifier:
    Type: String
    Default: myapp-memcached
    AllowedPattern: "[a-zA-Z][a-zA-Z0-9]*"

  CacheNodeType:
    Type: String
    Default: cache.m5.xlarge
    Description: Cache node instance type

  NumCacheNodes:
    Type: Number
    Default: 3
    Description: Number of cache nodes
    MinValue: 1
    MaxValue: 20

  EngineVersion:
    Type: String
    Default: "1.6"
    Description: Memcached engine version

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet3Id:
    Type: AWS::EC2::Subnet::Id

  AppSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id

Resources:
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: !Sub Subnet group for ${EnvironmentName} Memcached
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  MemcachedParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: Memcached parameter group
      Family: memcached1.6
      Parameters:
        max_item_size: 10485760
        request_max_size: 2097152
        connection_idle_timeout: 600
        disable_cas: on
        backlog_queue_limit: 1024

  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Memcached security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 11211
          ToPort: 11211
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  MemcachedCluster:
    Type: AWS::ElastiCache::Cluster
    Properties:
      CacheClusterIdentifier: !Ref CacheClusterIdentifier
      CacheNodeType: !Ref CacheNodeType
      NumCacheNodes: !Ref NumCacheNodes
      Engine: memcached
      EngineVersion: !Ref EngineVersion
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref MemcachedParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      AutoMinorVersionUpgrade: true
      AzMode: cross-az

Outputs:
  CacheClusterId:
    Description: Cache Cluster ID
    Value: !Ref MemcachedCluster

  ConfigurationEndpoint:
    Description: Memcached configuration endpoint
    Value: !GetAtt MemcachedCluster.ConfigurationEndpoint.Address

  ConfigurationPort:
    Description: Memcached configuration port
    Value: !GetAtt MemcachedCluster.ConfigurationEndpoint.Port

  NodeEndpoints:
    Description: Individual node endpoints
    Value: !Join [",", !GetAtt MemcachedCluster.MemberClusters]
```

---

## Complete Redis Replication Group Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Redis Replication Group with primary and read replicas for high availability

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  ReplicationGroupIdentifier:
    Type: String
    Default: myapp-redis-rg
    Description: Replication group identifier

  CacheNodeType:
    Type: String
    Default: cache.r5.large
    Description: Cache node instance type

  NumReplicasPerNodeGroup:
    Type: Number
    Default: 2
    Description: Number of replicas per node group
    MinValue: 1
    MaxValue: 5

  EngineVersion:
    Type: String
    Default: "7.0"

  DatabaseName:
    Type: String
    Default: 0

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet3Id:
    Type: AWS::EC2::Subnet::Id

  AppSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id

  KmsKeyId:
    Type: AWS::KMS::Key::Id

Resources:
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for Redis replication
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  CacheParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: Redis parameter group
      Family: redis7.x
      Parameters:
        maxmemory-policy: allkeys-lru
        maxmemory-samples: 5
        timeout: 300
        tcp-keepalive: 300

  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Redis replication security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  RedisReplicationGroup:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupIdentifier: !Ref ReplicationGroupIdentifier
      ReplicationGroupDescription: !Sub Redis replication for ${EnvironmentName}
      Engine: redis
      EngineVersion: !Ref EngineVersion
      CacheNodeType: !Ref CacheNodeType
      NumNodeGroups: 1
      ReplicasPerNodeGroup: !Ref NumReplicasPerNodeGroup
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref CacheParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
      SnapshotRetentionLimit: 35
      SnapshotWindow: "05:00-06:00"

Outputs:
  PrimaryEndpoint:
    Description: Primary endpoint for write operations
    Value: !GetAtt RedisReplicationGroup.PrimaryEndPoint.Address

  PrimaryPort:
    Description: Primary endpoint port
    Value: !GetAtt RedisReplicationGroup.PrimaryEndPoint.Port

  ReaderEndpoint:
    Description: Reader endpoint for read operations
    Value: !GetAtt RedisReplicationGroup.ReaderEndPoint.Address

  ReaderPort:
    Description: Reader endpoint port
    Value: !GetAtt RedisReplicationGroup.ReaderEndPoint.Port

  MemberClusters:
    Description: Member cluster IDs
    Value: !Join [",", !GetAtt RedisReplicationGroup.MemberClusters]

  ReplicationGroupArn:
    Description: Replication Group ARN
    Value: !GetAtt RedisReplicationGroup.Arn
```

---

## Redis Cluster Mode Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Redis Cluster with data partitioning across multiple node groups

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  CacheNodeType:
    Type: String
    Default: cache.r5.xlarge

  NumNodeGroups:
    Type: Number
    Default: 3
    Description: Number of node groups for data partitioning
    MinValue: 2
    MaxValue: 500

  ReplicasPerNodeGroup:
    Type: Number
    Default: 1
    Description: Number of replicas per node group
    MinValue: 1
    MaxValue: 5

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet3Id:
    Type: AWS::EC2::Subnet::Id

  AppSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id

Resources:
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for Redis Cluster
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  CacheParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: Redis Cluster parameter group
      Family: redis7.x
      Parameters:
        cluster-enabled: yes
        cluster-node-timeout: 5000
        maxmemory-policy: allkeys-lru
        timeout: 5000

  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Redis Cluster security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  RedisCluster:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupIdentifier: !Sub ${EnvironmentName}-redis-cluster
      ReplicationGroupDescription: Redis Cluster with data partitioning
      Engine: redis
      EngineVersion: "7.0"
      CacheNodeType: !Ref CacheNodeType
      NumNodeGroups: !Ref NumNodeGroups
      ReplicasPerNodeGroup: !Ref ReplicasPerNodeGroup
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref CacheParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true

Outputs:
  ClusterEndpoint:
    Description: Redis Cluster configuration endpoint
    Value: !GetAtt RedisCluster.ConfigurationEndPoint.Address

  ClusterPort:
    Description: Redis Cluster configuration port
    Value: !GetAtt RedisCluster.ConfigurationEndPoint.Port

  MemberClusters:
    Description: All member clusters
    Value: !Join [",", !GetAtt RedisCluster.MemberClusters]
```

---

## Multi-Region Redis Replication Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Cross-region Redis replication for disaster recovery

Parameters:
  PrimaryRegion:
    Type: String
    Default: us-east-1
    Description: Primary region

  SecondaryRegion:
    Type: String
    Default: us-west-2
    Description: Secondary region

  ReplicationGroupIdPrefix:
    Type: String
    Default: myapp
    Description: Prefix for replication group IDs

Resources:
  # Primary Replication Group (created in primary region)
  PrimaryReplicationGroup:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupIdentifier: !Sub ${ReplicationGroupIdPrefix}-primary
      ReplicationGroupDescription: Primary Redis replication group
      Engine: redis
      EngineVersion: "7.0"
      CacheNodeType: cache.r5.large
      NumNodeGroups: 1
      ReplicasPerNodeGroup: 2
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
      CacheSubnetGroupName: !Ref PrimaryCacheSubnetGroup
      VpcSecurityGroupIds:
        - !Ref PrimaryCacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true

  # Secondary Replication Group (created in secondary region)
  SecondaryReplicationGroup:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupIdentifier: !Sub ${ReplicationGroupIdPrefix}-secondary
      ReplicationGroupDescription: Secondary Redis replication group
      Engine: redis
      EngineVersion: "7.0"
      CacheNodeType: cache.r5.large
      NumNodeGroups: 1
      ReplicasPerNodeGroup: 2
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
      CacheSubnetGroupName: !Ref SecondaryCacheSubnetGroup
      VpcSecurityGroupIds:
        - !Ref SecondaryCacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true

  # Global Replication Group
  GlobalReplicationGroup:
    Type: AWS::ElastiCache::GlobalReplicationGroup
    Properties:
      GlobalReplicationGroupIdSuffix: global
      GlobalReplicationGroupDescription: Global Redis replication
      Members:
        - ReplicationGroupId: !Ref PrimaryReplicationGroup
          ReplicationGroupRegion: !Ref PrimaryRegion
        - ReplicationGroupId: !Ref SecondaryReplicationGroup
          ReplicationGroupRegion: !Ref SecondaryRegion

Outputs:
  PrimaryEndpoint:
    Description: Primary region endpoint
    Value: !GetAtt PrimaryReplicationGroup.PrimaryEndPoint.Address

  SecondaryEndpoint:
    Description: Secondary region endpoint
    Value: !GetAtt SecondaryReplicationGroup.PrimaryEndPoint.Address

  GlobalReplicationGroupId:
    Description: Global replication group ID
    Value: !Ref GlobalReplicationGroup
```

---

## Redis with Encryption and Auth Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Redis with encryption at rest, encryption in transit, and AUTH

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  CacheNodeType:
    Type: String
    Default: cache.r5.large

  CacheClusterIdentifier:
    Type: String
    Default: secured-redis

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

  AppSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id

Resources:
  # Secrets Manager Secret for Auth Token
  RedisAuthTokenSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub ${EnvironmentName}/redis/auth-token
      Description: Redis AUTH token
      GenerateSecretString:
        SecretStringTemplate: '{"username": "default"}'
        GenerateStringKey: "password"
        PasswordLength: 32
        ExcludeCharacters: '"@/\'

  # Cache Parameter Group with TLS
  CacheParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: Redis with TLS enabled
      Family: redis7.x
      Parameters:
        tls-enabled: yes

  # Security Group with TLS port
  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Secured Redis security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for secured Redis
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id

  # Redis Cluster with full encryption
  CacheCluster:
    Type: AWS::ElastiCache::Cluster
    Properties:
      CacheClusterIdentifier: !Ref CacheClusterIdentifier
      CacheNodeType: !Ref CacheNodeType
      NumCacheNodes: 1
      Engine: redis
      EngineVersion: "7.0"
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref CacheParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      TransitEncryptionEnabled: true
      AtRestEncryptionEnabled: true
      AuthToken: !Sub '{{resolve:secretsmanager:${RedisAuthTokenSecret}:SecretString:password}}'

Outputs:
  RedisEndpoint:
    Description: Redis endpoint
    Value: !GetAtt CacheCluster.RedisEndpoint.Address

  RedisPort:
    Description: Redis port
    Value: !GetAtt CacheCluster.RedisEndpoint.Port

  AuthTokenSecretArn:
    Description: ARN of the AUTH token secret
    Value: !Ref RedisAuthTokenSecret
```

---

## Memcached with Auto Discovery Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Memcached cluster with auto discovery endpoints

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  CacheClusterIdentifier:
    Type: String
    Default: myapp-memcached

  CacheNodeType:
    Type: String
    Default: cache.m5.xlarge

  NumCacheNodes:
    Type: Number
    Default: 6
    MinValue: 1
    MaxValue: 20

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet3Id:
    Type: AWS::EC2::Subnet::Id

  AppSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id

Resources:
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for Memcached
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  MemcachedParameterGroup:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: Memcached parameter group
      Family: memcached1.6
      Parameters:
        max_item_size: 10485760
        request_max_size: 2097152
        connection_idle_timeout: 600

  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Memcached security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 11211
          ToPort: 11211
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  MemcachedCluster:
    Type: AWS::ElastiCache::Cluster
    Properties:
      CacheClusterIdentifier: !Ref CacheClusterIdentifier
      CacheNodeType: !Ref CacheNodeType
      NumCacheNodes: !Ref NumCacheNodes
      Engine: memcached
      EngineVersion: "1.6"
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      CacheParameterGroupName: !Ref MemcachedParameterGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      AutoMinorVersionUpgrade: true
      AzMode: cross-az

Outputs:
  ConfigurationEndpoint:
    Description: Memcached configuration endpoint for auto discovery
    Value: !GetAtt MemcachedCluster.ConfigurationEndpoint.Address

  ConfigurationPort:
    Description: Memcached configuration port
    Value: !GetAtt MemcachedCluster.ConfigurationEndpoint.Port

  MemberClusters:
    Description: Individual cache node endpoints
    Value: !Join [",", !GetAtt MemcachedCluster.MemberClusters]

  NodeCount:
    Description: Number of cache nodes
    Value: !Ref NumCacheNodes
```

---

## Complete Network Stack for ElastiCache

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Network infrastructure for ElastiCache deployment

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-igw

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Public Subnets (for bastion/jump host)
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-1
        - Key: SubnetType
          Value: Public

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-2

  # Private Subnets (for ElastiCache)
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-1
        - Key: SubnetType
          Value: Private

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.11.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-2
        - Key: SubnetType
          Value: Private

  PrivateSubnet3:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.12.0/24
      AvailabilityZone: !Select [2, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-3
        - Key: SubnetType
          Value: Private

  # NAT Gateway
  NatGatewayEIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat-eip

  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGatewayEIP.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat

  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-rt

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnetRouteTableAssociation1:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable

  PublicSubnetRouteTableAssociation2:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref PublicRouteTable

  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-rt

  DefaultPrivateRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway

  PrivateSubnetRouteTableAssociation1:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRouteTable

  PrivateSubnetRouteTableAssociation2:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet2
      RouteTableId: !Ref PrivateRouteTable

  PrivateSubnetRouteTableAssociation3:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet3
      RouteTableId: !Ref PrivateRouteTable

  # Application Security Group
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Application security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-app-sg

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC

  PrivateSubnetIds:
    Description: Private subnet IDs for ElastiCache
    Value: !Join [",", [!Ref PrivateSubnet1, !Ref PrivateSubnet2, !Ref PrivateSubnet3]]

  PrivateSubnet1Id:
    Description: Private subnet 1 ID
    Value: !Ref PrivateSubnet1

  PrivateSubnet2Id:
    Description: Private subnet 2 ID
    Value: !Ref PrivateSubnet2

  PrivateSubnet3Id:
    Description: Private subnet 3 ID
    Value: !Ref PrivateSubnet3

  AppSecurityGroupId:
    Description: Application security group ID
    Value: !Ref AppSecurityGroup
```

---

## Serverless Redis Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Serverless ElastiCache for Redis

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  ServerlessCacheName:
    Type: String
    Description: Name of the serverless cache
    Default: myapp-serverless-redis

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet3Id:
    Type: AWS::EC2::Subnet::Id

  AppSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id

Resources:
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for serverless Redis
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Serverless Redis security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  ServerlessCache:
    Type: AWS::ElastiCache::ServerlessCache
    Properties:
      ServerlessCacheName: !Ref ServerlessCacheName
      Description: !Sub Serverless Redis for ${EnvironmentName}
      Engine: redis
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup
      TransitEncryptionEnabled: true

Outputs:
  ServerlessCacheEndpoint:
    Description: Serverless cache endpoint
    Value: !GetAtt ServerlessCache.RedisEndpoint.Address

  ServerlessCachePort:
    Description: Serverless cache port
    Value: !GetAtt ServerlessCache.RedisEndpoint.Port

  ServerlessCacheName:
    Description: Serverless cache name
    Value: !Ref ServerlessCacheName

  ServerlessCacheArn:
    Description: Serverless cache ARN
    Value: !GetAtt ServerlessCache.Arn
```
