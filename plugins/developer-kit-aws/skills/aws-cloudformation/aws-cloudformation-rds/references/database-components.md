# RDS Database Components

## DB Subnet Group

Required for VPC deployment. Must include at least 2 subnets in different AZs.

```yaml
Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS instance
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
        - !Ref PrivateSubnet3
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-dbsubnet
```

## DB Parameter Group

Custom parameter groups for database configuration.

```yaml
Resources:
  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Custom parameter group for MySQL 8.0
      Family: mysql8.0
      Parameters:
        # Connection settings
        max_connections: 200
        max_user_connections: 200

        # Memory settings
        innodb_buffer_pool_size: 1073741824
        innodb_buffer_pool_instances: 4

        # Query cache (MySQL 5.7)
        query_cache_type: 1
        query_cache_size: 268435456

        # Timezone
        default_time_zone: "+00:00"

        # Character set
        character_set_server: utf8mb4
        collation_server: utf8mb4_unicode_ci

      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-dbparam
```

## DB Option Group

For database features like Oracle XML or SQL Server features.

```yaml
Resources:
  DBOptionGroup:
    Type: AWS::RDS::DBOptionGroup
    Properties:
      EngineName: oracle-ee
      MajorEngineVersion: "19"
      OptionGroupDescription: Option group for Oracle 19c
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

## DB Instance - MySQL

```yaml
Resources:
  MySQLDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: mysql-instance
      DBInstanceClass: db.t3.medium
      Engine: mysql
      EngineVersion: "8.0.35"
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      AllocatedStorage: "100"
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      StorageEncrypted: true
      MultiAZ: true
      BackupRetentionPeriod: 35
      DeletionProtection: true
      EnablePerformanceInsights: true
      PerformanceInsightsRetentionPeriod: 731
      AutoMinorVersionUpgrade: false
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

## DB Instance - PostgreSQL

```yaml
Resources:
  PostgreSQLDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: postgres-instance
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EngineVersion: "16.1"
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      AllocatedStorage: "100"
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      StorageEncrypted: true
      MultiAZ: true
      BackupRetentionPeriod: 35
      DeletionProtection: true
      EnablePerformanceInsights: true
      PubliclyAccessible: false
```

## Aurora MySQL Cluster

```yaml
Resources:
  AuroraMySQLCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: aurora-mysql-cluster
      Engine: aurora-mysql
      EngineVersion: "8.0.mysql_aurora.3.02.0"
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DatabaseName: mydb
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBClusterParameterGroupName: !Ref AuroraClusterParameterGroup
      StorageEncrypted: true
      EngineMode: provisioned
      Port: 3306
      EnableIAMDatabaseAuthentication: true

  AuroraDBInstanceWriter:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: aurora-writer
      DBClusterIdentifier: !Ref AuroraMySQLCluster
      Engine: aurora-mysql
      DBInstanceClass: db.r5.large
      PromotionTier: 1

  AuroraDBInstanceReader:
    Type: AWS::RDS::DBInstance
    DependsOn: AuroraDBInstanceWriter
    Properties:
      DBInstanceIdentifier: aurora-reader
      DBClusterIdentifier: !Ref AuroraMySQLCluster
      Engine: aurora-mysql
      DBInstanceClass: db.r5.large
      PromotionTier: 2
```

## Aurora PostgreSQL Cluster

```yaml
Resources:
  AuroraPostgresCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: aurora-pg-cluster
      Engine: aurora-postgresql
      EngineVersion: "15.4"
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DatabaseName: mydb
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      StorageEncrypted: true
      EngineMode: provisioned
      Port: 5432

  AuroraPostgresInstanceWriter:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: aurora-pg-writer
      DBClusterIdentifier: !Ref AuroraPostgresCluster
      Engine: aurora-postgresql
      DBInstanceClass: db.r5.large
      PromotionTier: 1

  AuroraPostgresInstanceReader:
    Type: AWS::RDS::DBInstance
    DependsOn: AuroraPostgresInstanceWriter
    Properties:
      DBInstanceIdentifier: aurora-pg-reader
      DBClusterIdentifier: !Ref AuroraPostgresCluster
      Engine: aurora-postgresql
      DBInstanceClass: db.r5.large
      PromotionTier: 2
```

## Aurora Serverless Cluster

```yaml
Resources:
  AuroraServerlessCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: aurora-serverless
      Engine: aurora-mysql
      EngineVersion: "5.6.mysql_aurora.2.12.0"
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DatabaseName: mydb
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      EngineMode: serverless
      ScalingConfiguration:
        AutoPause: true
        MinCapacity: 2
        MaxCapacity: 32
        SecondsUntilAutoPause: 300
```

## DB Cluster Parameter Group (Aurora)

```yaml
Resources:
  AuroraClusterParameterGroup:
    Type: AWS::RDS::DBClusterParameterGroup
    Properties:
      Description: Custom cluster parameter group for Aurora MySQL
      Family: aurora-mysql8.0
      Parameters:
        character_set_server: utf8mb4
        collation_server: utf8mb4_unicode_ci
        max_connections: 1000
        innodb_buffer_pool_size: 2147483648
        slow_query_log: "ON"
        long_query_time: 2
```

## PostgreSQL Parameter Group

```yaml
Resources:
  PostgreSQLParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Custom parameter group for PostgreSQL
      Family: postgres16
      Parameters:
        max_connections: 200
        shared_buffers: 268435456
        effective_cache_size: 1073741824
        maintenance_work_mem: 65536
        checkpoint_completion_target: 0.9
        wal_buffers: 16384
        default_statistics_target: 100
        random_page_cost: 1.1
        effective_io_concurrency: 200
        work_mem: 4096
        min_wal_size: 1073741824
        max_wal_size: 4294967296
```

## Oracle Parameter Group

```yaml
Resources:
  OracleParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Custom parameter group for Oracle
      Family: oracle-ee-19
      Parameters:
        compatible: "19.0"
        cursor_sharing: FORCE
        db_files: 200
        job_queue_processes: 4
        open_cursors: 300
        optimizer_adaptive_features: TRUE
        processes: 200
        sessions: 400
        sga_target: 2147483648
        shared_servers: 0
```

## SQL Server Parameter Group

```yaml
Resources:
  SQLServerParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Custom parameter group for SQL Server
      Family: sqlserver-ee-15.0
      Parameters:
        backup retention period: "7"
        max degree of parallelism: "0"
        optimize for ad hoc workloads: "1"
        max server memory (MB): "2621"
        min memory per query (MB): "1024"
```

## Event Subscription

```yaml
Resources:
  DBEventSubscription:
    Type: AWS::RDS::EventSubscription
    Properties:
      SnsTopicArn: !Ref DBEventsTopic
      SourceType: db-instance
      EventCategories:
        - availability
        - backup
        - configuration change
        - failover
        - maintenance
        - notification
      Snstopic: !Ref DBEventsTopic
```
