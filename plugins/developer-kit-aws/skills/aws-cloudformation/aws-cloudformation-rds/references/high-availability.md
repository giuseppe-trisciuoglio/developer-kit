# RDS High Availability and Disaster Recovery

## Multi-AZ Deployment

```yaml
Parameters:
  EnableMultiAZ:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      # Multi-AZ is not supported for Aurora clusters (automatic)
      MultiAZ: !Ref EnableMultiAZ
      # For multi-AZ, use a standby in a different AZ
      AvailabilityZone: !If
        - IsMultiAZ
        - !Select [1, !GetAZs '']
        - !Ref AWS::NoValue
```

## Multi-AZ with Instance Class Selection

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  IsMultiAZ: !If [IsProduction, true, false]

Resources:
  ProductionDBInstance:
    Type: AWS::RDS::DBInstance
    Condition: IsProduction
    Properties:
      DBInstanceClass: db.r5.large
      MultiAZ: true
      StorageEncrypted: true
      BackupRetentionPeriod: 35
      DeletionProtection: true

  DevelopmentDBInstance:
    Type: AWS::RDS::DBInstance
    Condition: IsDev
    Properties:
      DBInstanceClass: db.t3.micro
      MultiAZ: false
      BackupRetentionPeriod: 7
```

## Read Replicas

```yaml
Resources:
  # Primary instance
  PrimaryDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: mysql
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      BackupRetentionPeriod: 35
      MultiAZ: true

  # Read replica in same region
  ReadReplica:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: my-read-replica
      SourceDBInstanceIdentifier: !Ref PrimaryDBInstance
      DBInstanceClass: db.r5.large
      MultiAZ: false

  # Read replica in different region
  CrossRegionReadReplica:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: my-cross-region-replica
      SourceDBInstanceIdentifier: !Sub arn:aws:rds:us-west-2:${AWS::AccountId}:db:${PrimaryDBInstance}
      DBInstanceClass: db.r5.large
      Engine: mysql
```

## Read Replica with Different Instance Class

```yaml
Resources:
  PrimaryDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.xlarge
      Engine: postgres
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword

  # Smaller replica for read-only workloads
  ReadReplica:
    Type: AWS::RDS::DBInstance
    Properties:
      SourceDBInstanceIdentifier: !Ref PrimaryDBInstance
      DBInstanceClass: db.r5.large
      BackupRetentionPeriod: 0
      MultiAZ: false
```

## Aurora Auto Scaling

```yaml
Resources:
  AuroraCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: aurora-mysql-cluster
      Engine: aurora-mysql
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DatabaseName: mydb
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      # Enable parallel query for faster reads
      EnableHttpEndpoint: true

  # Auto-scaling policy for read replicas
  AuroraReadReplicaScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: AuroraReadReplicaAutoScaling
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref AuroraScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 70.0
        PredefinedMetricSpecification:
          PredefinedMetricType: RDSReaderAverageCPUUtilization
        ScaleOutCooldown: 300
        ScaleInCooldown: 300

  AuroraScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 5
      MinCapacity: 1
      ResourceId: !Sub cluster:${AuroraCluster}
      RoleARN: !GetAtt AutoScalingRole.Arn
      ScalableDimension: rds:cluster:ReadReplicaCount
      ServiceNamespace: rds
```

## Enhanced Monitoring and Performance Insights

```yaml
Resources:
  # IAM role for enhanced monitoring
  MonitoringRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: monitoring.rds.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: postgres
      EnablePerformanceInsights: true
      PerformanceInsightsRetentionPeriod: 731
      PerformanceInsightsKMSKeyId: !Ref PerformanceInsightsKey

      # Enhanced Monitoring
      MonitoringInterval: 60
      MonitoringRoleArn: !GetAtt MonitoringRole.Arn

      # Database logs export
      EnableCloudwatchLogsExports:
        - audit
        - error
        - general
        - slowquery
```

## Performance Insights with Custom Retention

```yaml
Resources:
  # KMS key for Performance Insights encryption
  PerformanceInsightsKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for Performance Insights
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow RDS Service
            Effect: Allow
            Principal:
              Service: rds.amazonaws.com
            Action:
              - 'kms:Decrypt'
              - 'kms:GenerateDataKey'
            Resource: '*'

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: mysql
      EnablePerformanceInsights: true
      PerformanceInsightsRetentionPeriod: 731
      PerformanceInsightsKMSKeyId: !Ref PerformanceInsightsKey
```

## CloudWatch Alarms for High Availability

```yaml
Resources:
  # CPU utilization alarm
  CPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: Alarm if DB CPU > 90%
      MetricName: CPUUtilization
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 90
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstance

  # Freeable memory alarm
  MemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: Alarm if freeable memory < 256MB
      MetricName: FreeableMemory
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 268435456
      ComparisonOperator: LessThanThreshold

  # Connection count alarm
  ConnectionAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: Alarm if connections > 90% of max
      MetricName: DatabaseConnections
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 180
      ComparisonOperator: GreaterThanThreshold
```

## Backup Strategy

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  ProductionDBInstance:
    Type: AWS::RDS::DBInstance
    Condition: IsProduction
    Properties:
      DBInstanceClass: db.r5.large
      Engine: postgres
      # 35-day retention for production
      BackupRetentionPeriod: 35
      # Backup window (2-3 AM UTC)
      PreferredBackupWindow: 02:00-03:00
      # Maintenance window (Sunday 3-4 AM UTC)
      PreferredMaintenanceWindow: sun:03:00-sun:04:00
      # Copy backups to another region
      EnablePerformanceInsights: true

  # Automated cross-region snapshot copy
  CrossRegionSnapshotCopy:
    Type: AWS::RDS::DBSnapshot
    Properties:
      DBSnapshotIdentifier: !Sub ${DBInstance}-snapshot-copy
      DBInstanceIdentifier: !Ref DBInstance
      CopyTags: true

  DevelopmentDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: postgres
      # 7-day retention for development
      BackupRetentionPeriod: 7
```

## Point-in-Time Recovery

```yaml
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: postgres
      # Enable automated backups (required for PITR)
      BackupRetentionPeriod: 35
      # Transaction logs enable point-in-time recovery
      EnablePerformanceInsights: true

  # Restore from specific timestamp
  RestoredDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: postgres
      DBInstanceIdentifier: restored-db
      RestoreType: to-time
      SourceDBInstanceIdentifier: !Ref DBInstance
      UseLatestRestorableTime: false
      RestoreTime: '2024-01-15T12:00:00Z'
```

## Disaster Recovery Plan

```yaml
Resources:
  # Primary production instance
  PrimaryDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: postgres
      MultiAZ: true
      BackupRetentionPeriod: 35
      StorageEncrypted: true
      DeletionProtection: true

  # Cross-region read replica for DR
  DRReplica:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: dr-replica
      SourceDBInstanceIdentifier: !Ref PrimaryDBInstance
      DBInstanceClass: db.r5.large
      # Deploy in different region
      AvailabilityZone: us-west-2a
      # Can be promoted to standalone
      BackupRetentionPeriod: 35

  # Alarm for replication lag
  ReplicationLagAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: Alarm if replica lag > 5 minutes
      MetricName: ReplicaLag
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 300
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DRReplica
```

## Failover Strategy

```yaml
Resources:
  # Aurora cluster with automatic failover
  AuroraCluster:
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
      # Multi-AZ for automatic failover
      # Aurora storage is replicated across AZs by default
      Port: 5432

  # Writer instance (primary)
  WriterInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBClusterIdentifier: !Ref AuroraCluster
      DBInstanceClass: db.r5.large
      Engine: aurora-postgresql
      PromotionTier: 1

  # Reader instances (standby)
  ReaderInstance1:
    Type: AWS::RDS::DBInstance
    Properties:
      DBClusterIdentifier: !Ref AuroraCluster
      DBInstanceClass: db.r5.large
      Engine: aurora-postgresql
      PromotionTier: 2

  ReaderInstance2:
    Type: AWS::RDS::DBInstance
    Properties:
      DBClusterIdentifier: !Ref AuroraCluster
      DBInstanceClass: db.r5.large
      Engine: aurora-postgresql
      PromotionTier: 2
```
