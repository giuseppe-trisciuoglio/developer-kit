# RDS CloudFormation Reference

This file contains detailed reference information for Amazon RDS CloudFormation resources.

## Table of Contents

- [AWS::RDS::DBInstance](#awsrdsdbinstance)
- [AWS::RDS::DBCluster](#awsrdsdbcluster)
- [AWS::RDS::DBParameterGroup](#awsrdsdbparametergroup)
- [AWS::RDS::DBClusterParameterGroup](#awsrdsdbclusterparametergroup)
- [AWS::RDS::DBSubnetGroup](#awsrdsdbsubnetgroup)
- [AWS::RDS::DBOptionGroup](#awsrdsdboptiongroup)
- [AWS::RDS::EventSubscription](#awsrdseventsubscription)
- [Engine Versions and Families](#engine-versions-and-families)
- [Instance Classes](#instance-classes)
- [Common Configuration Options](#common-configuration-options)

---

## AWS::RDS::DBInstance

The `AWS::RDS::DBInstance` resource creates an Amazon RDS DB instance.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| DBInstanceClass | String | The compute and memory capacity of the DB instance |
| Engine | String | The name of the database engine |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| AllocatedStorage | Number | - | The allocated storage size in gibibytes (GiB) |
| AutoMinorVersionUpgrade | Boolean | true | Whether minor version upgrades are applied automatically |
| AvailabilityZone | String | - | The AZ for the DB instance |
| BackupRetentionPeriod | Number | 1 | The number of days to retain automated backups |
| DBInstanceIdentifier | String | - | The identifier for the DB instance |
| DBName | String | - | The name of the initial database |
| DBParameterGroupName | String | - | The parameter group to associate |
| DBSecurityGroups | List | - | EC2-Classic security groups |
| DBSubnetGroupName | String | - | The subnet group for the DB instance |
| DeletionProtection | Boolean | false | Whether deletion protection is enabled |
| EnableIAMDatabaseAuthentication | Boolean | false | Whether IAM auth is enabled |
| EnablePerformanceInsights | Boolean | false | Whether Performance Insights is enabled |
| EngineVersion | String | - | The version number of the database engine |
| KmsKeyId | String | - | The KMS key for encryption |
| LicenseModel | String | - | The license model |
| MasterUsername | String | - | The master username |
| MasterUserPassword | String | - | The master user password |
| MonitoringInterval | Number | 0 | The interval for monitoring |
| MonitoringRoleArn | String | - | The IAM role for monitoring |
| MultiAZ | Boolean | false | Whether it's a Multi-AZ deployment |
| PerformanceInsightsKMSKeyId | String | - | The KMS key for Performance Insights |
| PerformanceInsightsRetentionPeriod | Number | 7 | The retention period for PI data |
| Port | Number | - | The port number |
| PreferredBackupWindow | String | - | The backup window |
| PreferredMaintenanceWindow | String | - | The maintenance window |
| PubliclyAccessible | Boolean | false | Whether it's publicly accessible |
| SourceDBInstanceIdentifier | String | - | The source DB instance identifier |
| StorageEncrypted | Boolean | false | Whether storage is encrypted |
| StorageType | String | gp2 | The storage type |
| Tags | List | - | Tags for the DB instance |
| VPCSecurityGroups | List | - | VPC security groups |

### Important Attributes

| Attribute | Description |
|-----------|-------------|
| Endpoint.Address | The DNS address of the DB instance |
| Endpoint.Port | The port number |
| Endpoint.HostedZoneId | The hosted zone ID |
| Arn | The ARN of the DB instance |
| DBInstanceArn | The ARN of the DB instance |

### Important Notes

- **MasterUserPassword**: Use `NoEcho: true` to hide the password
- **StorageEncrypted**: Required for Multi-AZ and some instance types
- **MultiAZ**: Creates a standby in a different AZ
- **DeletionProtection**: Prevents accidental deletion, required for production
- **SourceDBInstanceIdentifier**: Use for creating read replicas

### Example

```yaml
Resources:
  MyDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: mydbinstance
      DBInstanceClass: db.t3.medium
      Engine: mysql
      EngineVersion: "8.0.35"
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 100
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      StorageEncrypted: true
      MultiAZ: true
      BackupRetentionPeriod: 35
      DeletionProtection: true
```

---

## AWS::RDS::DBCluster

The `AWS::RDS::DBCluster` resource creates an Amazon Aurora DB cluster.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| Engine | String | The name of the database engine |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| AssociatedRoles | List | - | IAM roles associated with the cluster |
| AvailabilityZones | List | - | The Availability Zones |
| BacktrackWindow | Number | 0 | The backtrack window |
| BackupRetentionPeriod | Number | 1 | The number of days for backups |
| ClusterIdentifier | String | - | The cluster identifier |
| DatabaseName | String | - | The name of the initial database |
| DBClusterInstanceClass | String | - | The compute and memory capacity |
| DBClusterParameterGroupName | String | - | The cluster parameter group |
| DBSubnetGroupName | String | - | The subnet group |
| DeletionProtection | Boolean | false | Whether deletion protection is enabled |
| EnableCloudwatchLogsExports | List | - | Log types to export |
| EnableHttpEndpoint | Boolean | false | Whether HTTP endpoint is enabled |
| EnableIAMDatabaseAuthentication | Boolean | false | Whether IAM auth is enabled |
| EngineMode | String | - | The engine mode (provisioned or serverless) |
| EngineVersion | String | - | The engine version |
| GlobalClusterIdentifier | String | - | The global cluster identifier |
| KmsKeyId | String | - | The KMS key for encryption |
| MasterUsername | String | - | The master username |
| MasterUserPassword | String | - | The master user password |
| Port | Number | - | The port number |
| PreferredBackupWindow | String | - | The backup window |
| PreferredMaintenanceWindow | String | - | The maintenance window |
| ReplicationSourceIdentifier | String | - | The source for replication |
| ScalingConfiguration | Map | - | Serverless scaling configuration |
| StorageEncrypted | Boolean | false | Whether storage is encrypted |
| Tags | List | - | Tags for the cluster |
| VPCSecurityGroups | List | - | VPC security groups |

### Important Attributes

| Attribute | Description |
|-----------|-------------|
| Endpoint | The writer endpoint |
| ReadEndpoint | The reader endpoint |
| Endpoint.Address | The endpoint address |
| Endpoint.Port | The port number |
| Arn | The ARN of the DB cluster |

### Engine Modes

- **provisioned**: Traditional provisioned capacity
- **serverless**: Auto-scaling capacity
- **parallelquery**: Optimized for analytics
- **global**: Global database (used with GlobalClusterIdentifier)

### ScalingConfiguration (Serverless)

```yaml
ScalingConfiguration:
  AutoPause: true
  MinCapacity: 2
  MaxCapacity: 16
  SecondsUntilAutoPause: 300
```

### Example

```yaml
Resources:
  MyDBCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: my-aurora-cluster
      Engine: aurora-mysql
      EngineVersion: "8.0.mysql_aurora.3.02.0"
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      DatabaseName: mydb
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      StorageEncrypted: true
      EngineMode: provisioned
      Port: 3306
      EnableIAMDatabaseAuthentication: true
      BackupRetentionPeriod: 35
      DeletionProtection: true

  MyDBInstanceWriter:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: my-writer
      DBClusterIdentifier: !Ref MyDBCluster
      Engine: aurora-mysql
      DBInstanceClass: db.r5.large
      PromotionTier: 1
```

---

## AWS::RDS::DBParameterGroup

The `AWS::RDS::DBParameterGroup` resource creates a custom parameter group for a DB instance.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| Description | String | The description of the parameter group |
| Family | String | The parameter group family |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| DBParameterGroupName | String | The name of the parameter group |
| Parameters | Map | The parameters to set |
| Tags | List | Tags for the parameter group |

### Common Parameters for MySQL

```yaml
Parameters:
  # Connection settings
  max_connections: 200
  max_user_connections: 200

  # Memory settings
  innodb_buffer_pool_size: 1073741824
  innodb_buffer_pool_instances: 4

  # Query cache (MySQL 5.7 only)
  query_cache_type: 1
  query_cache_size: 268435456

  # Character set
  character_set_server: utf8mb4
  collation_server: utf8mb4_unicode_ci

  # Logging
  slow_query_log: "ON"
  long_query_time: 2
  log_queries_not_using_indexes: "ON"
  log_error_verbosity: 3

  # Timezone
  default_time_zone: "+00:00"

  # Timeout
  wait_timeout: 28800
  interactive_timeout: 28800
```

### Common Parameters for PostgreSQL

```yaml
Parameters:
  # Connection settings
  max_connections: 200
  superuser_reserved_connections: 3

  # Memory settings
  shared_buffers: 524288
  work_mem: 4096
  maintenance_work_mem: 524288
  effective_cache_size: 1572864

  # Query settings
  log_min_duration_statement: 2000
  log_connections: "ON"
  log_disconnections: "ON"
  log_lock_waits: "ON"

  # Temporary files
  log_temp_files: 0

  # Character set
  client_encoding: UTF8
  server_encoding: UTF8
```

### Example

```yaml
Resources:
  MyDBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: MySQL 8.0 parameter group
      Family: mysql8.0
      Parameters:
        max_connections: 200
        innodb_buffer_pool_size: 1073741824
        character_set_server: utf8mb4
        collation_server: utf8mb4_unicode_ci
        slow_query_log: "ON"
        long_query_time: 2
```

---

## AWS::RDS::DBClusterParameterGroup

The `AWS::RDS::DBClusterParameterGroup` resource creates a custom parameter group for a DB cluster (Aurora).

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| Description | String | The description of the parameter group |
| Family | String | The parameter group family |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| DBClusterParameterGroupName | String | The name of the parameter group |
| Parameters | Map | The parameters to set |
| Tags | List | Tags for the parameter group |

### Common Parameters for Aurora MySQL

```yaml
Parameters:
  # Connection settings
  max_connections: 1000
  max_connections_per_hour: 0

  # Memory settings
  innodb_buffer_pool_size: 2147483648
  innodb_buffer_pool_instances: 4

  # Query cache (Aurora MySQL 5.7 only)
  query_cache_type: 1
  query_cache_size: 268435456

  # Character set
  character_set_server: utf8mb4
  collation_server: utf8mb4_unicode_ci

  # Logging
  slow_query_log: "ON"
  long_query_time: 2

  # Aurora-specific
  aurora_enable_repl_bin_logging: 0
  aurora_use_relay_logs: 1
```

### Common Parameters for Aurora PostgreSQL

```yaml
Parameters:
  # Connection settings
  max_connections: 1000

  # Memory settings
  shared_buffers: 2097152
  work_mem: 32768
  maintenance_work_mem: 524288
  effective_cache_size: 6291456

  # Logging
  log_min_duration_statement: 2000
  log_connections: "ON"
  log_disconnections: "ON"

  # Aurora-specific
  rds.accepted_password_auth_max_retries: 10
```

### Example

```yaml
Resources:
  MyDBClusterParameterGroup:
    Type: AWS::RDS::DBClusterParameterGroup
    Properties:
      Description: Aurora MySQL 8.0 parameter group
      Family: aurora-mysql8.0
      Parameters:
        max_connections: 1000
        innodb_buffer_pool_size: 2147483648
        character_set_server: utf8mb4
        collation_server: utf8mb4_unicode_ci
        slow_query_log: "ON"
        long_query_time: 2
```

---

## AWS::RDS::DBSubnetGroup

The `AWS::RDS::DBSubnetGroup` resource creates a DB subnet group for a DB instance or cluster.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| DBSubnetGroupDescription | String | The description of the subnet group |
| SubnetIds | List | The IDs of the subnets |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| DBSubnetGroupName | String | The name of the subnet group |
| Tags | List | Tags for the subnet group |

### Requirements

- Must include at least 2 subnets in different Availability Zones
- Subnets must be in the same VPC
- All subnets must have available IP addresses

### Example

```yaml
Resources:
  MyDBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for production RDS
      DBSubnetGroupName: production-rds-subnet-group
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
        - !Ref PrivateSubnet3
      Tags:
        - Key: Environment
          Value: production
```

---

## AWS::RDS::DBOptionGroup

The `AWS::RDS::DBOptionGroup` resource creates a DB option group for database features.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| EngineName | String | The database engine name |
| MajorEngineVersion | String | The major engine version |
| OptionGroupDescription | String | The description of the option group |

### Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| OptionGroupName | String | The name of the option group |
| Options | List | The options to configure |
| Tags | List | Tags for the option group |

### Options

#### Oracle Options

```yaml
Options:
  - OptionName: OEM
    OptionVersion: "19"
    Port: 5500
    VpcSecurityGroupMemberships:
      - !Ref OEMSecurityGroup
    OptionSettings:
      - Name: OMS_HOST
        Value: oms.example.com
      - Name: OMS_PORT
        Value: "9900"

  - OptionName: SSL
    OptionSettings:
      - Name: SQLNET.SSL_VERSION
        Value: "1.2"
      - Name: SQLNET.CIPHER_SUITE
        Value: "SSL_RSA_WITH_AES_256_CBC_SHA"

  - OptionName: APEX
    OptionVersion: "22.1.0"
    OptionSettings:
      - Name: APEX_LISTENER_PORT
        Value: "8080"
      - Name: APEX_WS_PORT
        Value: "8181"
```

#### SQL Server Options

```yaml
Options:
  - OptionName: SQLSERVER_BACKUP
    OptionSettings:
      - Name: BACKUP_RETENTION_PERIOD
        Value: "15"

  - OptionName: SQLSERVER_AUDIT
    OptionSettings:
      - Name: S3_BUCKET_ARN
        Value: !Ref AuditLogBucketArn
      - Name: IAM_ROLE_ARN
        Value: !GetAtt AuditRole.Arn
```

### Example

```yaml
Resources:
  MyDBOptionGroup:
    Type: AWS::RDS::DBOptionGroup
    Properties:
      EngineName: oracle-ee
      MajorEngineVersion: "19"
      OptionGroupDescription: Oracle 19c option group with OEM
      OptionGroupName: oracle-19c-oem
      Options:
        - OptionName: OEM
          OptionVersion: "19"
          Port: 5500
          VpcSecurityGroupMemberships:
            - !Ref OEMSecurityGroup
        - OptionName: SSL
          OptionSettings:
            - Name: SQLNET.SSL_VERSION
              Value: "1.2"
```

---

## AWS::RDS::EventSubscription

The `AWS::RDS::EventSubscription` resource creates an event subscription for RDS events.

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| SnsTopicArn | String | The ARN of the SNS topic |
| SourceType | String | The source type (db-instance, db-cluster, etc.) |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| Enabled | Boolean | true | Whether the subscription is enabled |
| EventCategories | List | - | The event categories |
| SourceIds | List | - | The source identifiers |
| SubscriptionName | String | - | The name of the subscription |

### Event Categories

| Category | Description |
|----------|-------------|
| availability | Availability zone issues |
| backup | Backup operations |
| configuration change | Configuration changes |
| creation | Resource creation |
| deletion | Resource deletion |
| failover | Failover events |
| low storage | Storage issues |
| maintenance | Maintenance events |
| notification | General notifications |
| read replica | Read replica events |
| recovery | Recovery events |
| restoration | Restoration events |

### Example

```yaml
Resources:
  MyEventSubscription:
    Type: AWS::RDS::EventSubscription
    Properties:
      SnsTopicArn: !Ref NotificationTopic
      SourceType: db-instance
      EventCategories:
        - availability
        - backup
        - configuration change
        - deletion
        - failover
        - maintenance
      SourceIds:
        - !Ref MyDBInstance
      Enabled: true
```

---

## Engine Versions and Families

### MySQL

| Family | Versions |
|--------|----------|
| mysql5.6 | 5.6.40, 5.6.41, 5.6.42, 5.6.44, 5.6.51 |
| mysql5.7 | 5.7.26, 5.7.30, 5.7.32, 5.7.33, 5.7.37, 5.7.38, 5.7.39, 5.7.40, 5.7.41, 5.7.42 |
| mysql8.0 | 8.0.11, 8.0.16, 8.0.17, 8.0.20, 8.0.23, 8.0.25, 8.0.26, 8.0.28, 8.0.32, 8.0.33, 8.0.35 |

### PostgreSQL

| Family | Versions |
|--------|----------|
| postgres11 | 11.9, 11.10, 11.11, 11.12, 11.13, 11.14, 11.15, 11.16, 11.17, 11.18, 11.20, 11.21, 11.22 |
| postgres12 | 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 12.11, 12.12, 12.13, 12.14, 12.15, 12.17 |
| postgres13 | 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 13.9, 13.10, 13.11, 13.12, 13.13, 13.14, 13.15 |
| postgres14 | 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 14.11, 14.12, 14.13, 14.14 |
| postgres15 | 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8 |
| postgres16 | 16.1, 16.2, 16.3, 16.4 |

### Aurora MySQL

| Family | Versions |
|--------|----------|
| aurora5.6 | 5.6.mysql_aurora.1.19.0, 5.6.mysql_aurora.1.19.1, 5.6.mysql_aurora.1.19.2, 5.6.mysql_aurora.1.19.5, 5.6.mysql_aurora.1.22.0, 5.6.mysql_aurora.1.22.1, 5.6.mysql_aurora.1.22.2, 5.6.mysql_aurora.1.22.3, 5.6.mysql_aurora.1.23.0, 5.6.mysql_aurora.1.23.1 |
| aurora-mysql5.7 | 5.7.mysql_aurora.2.07.0, 5.7.mysql_aurora.2.07.1, 5.7.mysql_aurora.2.07.2, 5.7.mysql_aurora.2.07.3, 5.7.mysql_aurora.2.07.4, 5.7.mysql_aurora.2.07.5, 5.7.mysql_aurora.2.07.6, 5.7.mysql_aurora.2.08.0, 5.7.mysql_aurora.2.09.0, 5.7.mysql_aurora.2.09.1, 5.7.mysql_aurora.2.10.0, 5.7.mysql_aurora.2.10.1, 5.7.mysql_aurora.2.10.2, 5.7.mysql_aurora.2.11.0, 5.7.mysql_aurora.2.11.1, 5.7.mysql_aurora.2.12.0 |
| aurora-mysql8.0 | 8.0.mysql_aurora.3.01.0, 8.0.mysql_aurora.3.01.1, 8.0.mysql_aurora.3.02.0, 8.0.mysql_aurora.3.02.1, 8.0.mysql_aurora.3.03.0, 8.0.mysql_aurora.3.04.0, 8.0.mysql_aurora.3.05.0 |

### Aurora PostgreSQL

| Family | Versions |
|--------|----------|
| aurora-postgresql11 | 11.9, 11.13, 11.14, 11.17, 11.18, 11.19, 11.20, 11.21 |
| aurora-postgresql12 | 12.4, 12.8, 12.9, 12.10, 12.11, 12.12, 12.13, 12.14 |
| aurora-postgresql13 | 13.3, 13.4, 13.6, 13.7, 13.8, 13.9, 13.10, 13.11, 13.12, 13.13, 13.14 |
| aurora-postgresql14 | 14.1, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 14.11, 14.12 |
| aurora-postgresql15 | 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8 |

---

## Instance Classes

### General Purpose (Burstable)

| Instance Class | vCPU | Memory (GiB) |
|----------------|------|--------------|
| db.t3.micro | 2 | 1 |
| db.t3.small | 2 | 2 |
| db.t3.medium | 2 | 4 |
| db.t3.large | 2 | 8 |
| db.t3.xlarge | 4 | 16 |
| db.t3.2xlarge | 8 | 32 |

### General Purpose (Provisioned IOPS)

| Instance Class | vCPU | Memory (GiB) |
|----------------|------|--------------|
| db.m5.large | 2 | 8 |
| db.m5.xlarge | 4 | 16 |
| db.m5.2xlarge | 8 | 32 |
| db.m5.4xlarge | 16 | 64 |
| db.m5.8xlarge | 32 | 128 |
| db.m5.12xlarge | 48 | 192 |
| db.m5.16xlarge | 64 | 256 |
| db.m5.24xlarge | 96 | 384 |

### Memory Optimized

| Instance Class | vCPU | Memory (GiB) |
|----------------|------|--------------|
| db.r5.large | 2 | 16 |
| db.r5.xlarge | 4 | 32 |
| db.r5.2xlarge | 8 | 64 |
| db.r5.4xlarge | 16 | 128 |
| db.r5.8xlarge | 32 | 256 |
| db.r5.12xlarge | 48 | 384 |
| db.r5.16xlarge | 64 | 512 |
| db.r5.24xlarge | 96 | 768 |

### Aurora-Specific

| Instance Class | vCPU | Memory (GiB) | Use Case |
|----------------|------|--------------|----------|
| db.t3.medium | 2 | 4 | Development/test |
| db.r5.large | 2 | 16 | Production-small |
| db.r5.xlarge | 4 | 32 | Production-medium |
| db.r5.2xlarge | 8 | 64 | Production-large |
| db.r5.4xlarge | 16 | 128 | Production-xlarge |
| db.r6g.large | 2 | 16 | Graviton-small |
| db.r6g.xlarge | 4 | 32 | Graviton-medium |
| db.r6g.2xlarge | 8 | 64 | Graviton-large |

---

## Common Configuration Options

### Storage Types

| Storage Type | Description | Use Case |
|--------------|-------------|----------|
| gp2 | General Purpose SSD | Most workloads |
| gp3 | General Purpose SSD (latest) | Cost-effective, flexible IOPS |
| io1 | Provisioned IOPS SSD | I/O-intensive, predictable performance |
| io2 | Provisioned IOPS SSD (newer) | Highest durability, 99.999% SLA |

### Storage Encryption

```yaml
StorageEncrypted: true
KmsKeyId: !Ref EncryptionKey
```

### Multi-AZ Deployment

```yaml
MultiAZ: true
```

### Performance Insights

```yaml
EnablePerformanceInsights: true
PerformanceInsightsRetentionPeriod: 731  # 2 years
PerformanceInsightsKMSKeyId: !Ref PIKey
```

### Enhanced Monitoring

```yaml
MonitoringInterval: 60  # seconds
MonitoringRoleArn: !GetAtt MonitoringRole.Arn
```

### CloudWatch Logs Export

```yaml
EnableCloudwatchLogsExports:
  - audit
  - error
  - general
  - slowquery
```

### IAM Database Authentication

```yaml
EnableIAMDatabaseAuthentication: true
```

### Deletion Protection

```yaml
DeletionProtection: true
```

### Automatic Minor Version Upgrades

```yaml
AutoMinorVersionUpgrade: false  # Disable for production
```

### Backup Settings

```yaml
BackupRetentionPeriod: 35  # 35 days for production
PreferredBackupWindow: "07:00-09:00"
```

### Maintenance Settings

```yaml
PreferredMaintenanceWindow: "sun:04:00-sun:05:00"
AutoMinorVersionUpgrade: false
```

---

## Useful Links

- [AWS::RDS::DBInstance Documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html)
- [AWS::RDS::DBCluster Documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbcluster.html)
- [AWS::RDS::DBParameterGroup Documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-dbparametergroup.html)
- [RDS Instance Classes](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html)
- [RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [Aurora Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/)
