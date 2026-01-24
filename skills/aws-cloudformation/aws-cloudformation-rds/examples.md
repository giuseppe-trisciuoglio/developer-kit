# RDS CloudFormation Examples

This file contains comprehensive examples for Amazon RDS CloudFormation templates.

## Table of Contents

- [Complete Production MySQL Template](#complete-production-mysql-template)
- [Complete Production PostgreSQL Template](#complete-production-postgresql-template)
- [Complete Aurora MySQL Cluster Template](#complete-aurora-mysql-cluster-template)
- [Complete Aurora PostgreSQL Cluster Template](#complete-aurora-postgresql-cluster-template)
- [Multi-Region Replication Template](#multi-region-replication-template)
- [Serverless Aurora Template](#serverless-aurora-template)
- [MariaDB with Read Replicas Template](#mariadb-with-read-replicas-template)
- [Oracle with Option Group Template](#oracle-with-option-group-template)
- [SQL Server Template](#sql-server-template)
- [Complete Network Stack for RDS](#complete-network-stack-for-rds)

---

## Complete Production MySQL Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production-ready MySQL RDS instance with enhanced monitoring and encryption

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

  DBInstanceIdentifier:
    Type: String
    Default: myapp-db
    Description: Database instance identifier
    AllowedPattern: "^[a-zA-Z][a-zA-Z0-9]*$"
    MinLength: 1
    MaxLength: 63

  MasterUsername:
    Type: String
    Default: admin
    Description: Master username
    AllowedPattern: "^[a-zA-Z][a-zA-Z0-9]*$"
    MinLength: 1
    MaxLength: 16

  MasterUserPassword:
    Type: String
    NoEcho: true
    Description: Master user password
    MinLength: 8
    MaxLength: 41

  DBInstanceClass:
    Type: String
    Default: db.t3.medium
    Description: Database instance class

  AllocatedStorage:
    Type: Number
    Default: 100
    Description: Allocated storage in GB
    MinValue: 20
    MaxValue: 65536

  EngineVersion:
    Type: String
    Default: 8.0.35
    Description: MySQL engine version

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC for RDS deployment

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

  NotificationArn:
    Type: String
    Default: ""
    Description: SNS topic ARN for notifications

Conditions:
  IsProduction: !Equals [!Ref EnvironmentType, production]
  HasNotificationArn: !Not [!Equals [!Ref NotificationArn, ""]]

Resources:
  # DB Subnet Group
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: !Sub Subnet group for ${EnvironmentName} RDS
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-rds-subnet
        - Key: Environment
          Value: !Ref EnvironmentName

  # DB Parameter Group
  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: !Sub Parameter group for MySQL ${EngineVersion}
      Family: !Sub mysql${EngineVersion.Split('.')[0]}.${EngineVersion.Split('.')[1]}
      Parameters:
        max_connections: 200
        max_user_connections: 200
        innodb_buffer_pool_size: 1073741824
        innodb_buffer_pool_instances: 4
        character_set_server: utf8mb4
        collation_server: utf8mb4_unicode_ci
        slow_query_log: "ON"
        long_query_time: 2
        log_queries_not_using_indexes: "ON"
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-rds-param
        - Key: Environment
          Value: !Ref EnvironmentName

  # DB Security Group
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VPCId
      GroupName: !Sub ${EnvironmentName}-rds-sg
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroupId
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-rds-sg
        - Key: Environment
          Value: !Ref EnvironmentName

  # IAM Role for Enhanced Monitoring
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
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-rds-monitoring-role
        - Key: Environment
          Value: !Ref EnvironmentName

  # DB Instance
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Ref DBInstanceIdentifier
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: !Ref EngineVersion
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      AllocatedStorage: !Ref AllocatedStorage
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      StorageEncrypted: true
      KmsKeyId: !Ref KmsKeyId
      MultiAZ: !If [IsProduction, true, false]
      BackupRetentionPeriod: !If [IsProduction, 35, 7]
      DeletionProtection: !If [IsProduction, true, false]
      AutoMinorVersionUpgrade: !If [IsProduction, false, true]
      EnablePerformanceInsights: true
      PerformanceInsightsRetentionPeriod: 731
      PerformanceInsightsKMSKeyId: !Ref KmsKeyId
      MonitoringInterval: 60
      MonitoringRoleArn: !GetAtt MonitoringRole.Arn
      EnableCloudwatchLogsExports:
        - audit
        - error
        - general
        - slowquery
      PubliclyAccessible: false
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-rds
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: EnvironmentType
          Value: !Ref EnvironmentType
        - Key: ManagedBy
          Value: CloudFormation

  # Event Subscription
  EventSubscription:
    Type: AWS::RDS::EventSubscription
    Condition: HasNotificationArn
    Properties:
      SnsTopicArn: !Ref NotificationArn
      SourceType: db-instance
      EventCategories:
        - availability
        - backup
        - configuration change
        - creation
        - deletion
        - failover
        - low storage
        - maintenance
        - notification
        - read replica
        - recovery
        - restoration
      SourceIds:
        - !Ref DBInstance
      Enabled: true

Outputs:
  DBInstanceId:
    Description: Database Instance ID
    Value: !Ref DBInstance

  DBInstanceEndpoint:
    Description: Database endpoint address
    Value: !GetAtt DBInstance.Endpoint.Address

  DBInstancePort:
    Description: Database port
    Value: !GetAtt DBInstance.Endpoint.Port

  DBInstanceArn:
    Description: Database Instance ARN
    Value: !GetArn

  DBInstanceClass:
    Description: Database Instance Class
    ValueAtt DBInstance.: !Ref DBInstanceClass

  ConnectionString:
    Description: JDBC connection string
    Value: !Sub jdbc:mysql://${DBInstanceEndpoint}:${DBInstancePort}/mydb

  VPCId:
    Description: VPC ID for reference
    Value: !Ref VPCId

  DBSecurityGroupId:
    Description: Security Group ID for reference
    Value: !Ref DBSecurityGroup

  DBParameterGroupName:
    Description: Parameter Group Name for reference
    Value: !Ref DBParameterGroup
```

---

## Complete Production PostgreSQL Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production-ready PostgreSQL RDS instance with high availability

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  DBInstanceIdentifier:
    Type: String
    Default: myapp-postgres
    AllowedPattern: "^[a-zA-Z][a-zA-Z0-9]*$"

  MasterUsername:
    Type: String
    Default: postgres

  MasterUserPassword:
    Type: String
    NoEcho: true
    MinLength: 8

  DBInstanceClass:
    Type: String
    Default: db.t3.medium

  AllocatedStorage:
    Type: Number
    Default: 100

  EngineVersion:
    Type: String
    Default: "16.1"

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

Conditions:
  IsProduction: !Equals [!Ref EnvironmentName, production]

Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: PostgreSQL subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: PostgreSQL parameter group
      Family: !Sub postgres${EngineVersion.Split('.')[0]}
      Parameters:
        max_connections: 200
        shared_buffers: 524288
        work_mem: 4096
        maintenance_work_mem: 524288
        effective_cache_size: 1572864
        log_min_duration_statement: 2000
        log_connections: "ON"
        log_disconnections: "ON"
        log_lock_waits: "ON"
        log_temp_files: 0

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: PostgreSQL RDS security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Ref DBInstanceIdentifier
      DBInstanceClass: !Ref DBInstanceClass
      Engine: postgres
      EngineVersion: !Ref EngineVersion
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      AllocatedStorage: !Ref AllocatedStorage
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      StorageEncrypted: true
      KmsKeyId: !Ref KmsKeyId
      MultiAZ: !If [IsProduction, true, false]
      BackupRetentionPeriod: !If [IsProduction, 35, 7]
      DeletionProtection: !If [IsProduction, true, false]
      EnablePerformanceInsights: true
      PerformanceInsightsRetentionPeriod: 731
      PerformanceInsightsKMSKeyId: !Ref KmsKeyId
      PubliclyAccessible: false
      EnableIAMDatabaseAuthentication: true

Outputs:
  DBInstanceEndpoint:
    Description: PostgreSQL endpoint
    Value: !GetAtt DBInstance.Endpoint.Address

  DBInstancePort:
    Description: PostgreSQL port
    Value: !GetAtt DBInstance.Endpoint.Port

  ConnectionString:
    Description: JDBC connection string
    Value: !Sub jdbc:postgresql://${DBInstanceEndpoint}:${DBInstancePort}/mydb
```

---

## Complete Aurora MySQL Cluster Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Aurora MySQL cluster with writer and reader instances

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  DBClusterIdentifier:
    Type: String
    Default: my-aurora-mysql

  MasterUsername:
    Type: String
    Default: admin

  MasterUserPassword:
    Type: String
    NoEcho: true
    MinLength: 8

  DBInstanceClass:
    Type: String
    Default: db.r5.large

  EngineVersion:
    Type: String
    Default: "8.0.mysql_aurora.3.02.0"

  DatabaseName:
    Type: String
    Default: mydb

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
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Aurora subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  DBClusterParameterGroup:
    Type: AWS::RDS::DBClusterParameterGroup
    Properties:
      Description: Aurora MySQL cluster parameter group
      Family: aurora-mysql8.0
      Parameters:
        character_set_server: utf8mb4
        collation_server: utf8mb4_unicode_ci
        max_connections: 1000
        innodb_buffer_pool_size: 2147483648
        slow_query_log: "ON"
        long_query_time: 2

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Aurora security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  DBCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: !Ref DBClusterIdentifier
      Engine: aurora-mysql
      EngineVersion: !Ref EngineVersion
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DatabaseName: !Ref DatabaseName
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBClusterParameterGroupName: !Ref DBClusterParameterGroup
      StorageEncrypted: true
      KmsKeyId: !Ref KmsKeyId
      EngineMode: provisioned
      Port: 3306
      EnableIAMDatabaseAuthentication: true
      BackupRetentionPeriod: 35
      DeletionProtection: true

  DBInstanceWriter:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub ${DBClusterIdentifier}-writer
      DBClusterIdentifier: !Ref DBCluster
      Engine: aurora-mysql
      DBInstanceClass: !Ref DBInstanceClass
      PromotionTier: 1

  DBInstanceReader:
    Type: AWS::RDS::DBInstance
    DependsOn: DBInstanceWriter
    Properties:
      DBInstanceIdentifier: !Sub ${DBClusterIdentifier}-reader
      DBClusterIdentifier: !Ref DBCluster
      Engine: aurora-mysql
      DBInstanceClass: !Ref DBInstanceClass
      PromotionTier: 2

Outputs:
  ClusterEndpoint:
    Description: Writer endpoint for Aurora cluster
    Value: !GetAtt DBCluster.Endpoint

  ClusterReadEndpoint:
    Description: Reader endpoint for Aurora cluster
    Value: !GetAtt DBCluster.ReadEndpoint

  ClusterEndpointAddress:
    Description: Writer endpoint address
    Value: !GetAtt DBCluster.Endpoint.Address

  ClusterEndpointPort:
    Description: Writer endpoint port
    Value: !GetAtt DBCluster.Endpoint.Port

  ClusterReaderEndpointAddress:
    Description: Reader endpoint address
    Value: !GetAtt DBCluster.ReadEndpoint.Address

  ClusterArn:
    Description: Cluster ARN
    Value: !GetAtt DBCluster.Arn
```

---

## Complete Aurora PostgreSQL Cluster Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Aurora PostgreSQL cluster with writer and reader instances

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  DBClusterIdentifier:
    Type: String
    Default: my-aurora-pg

  MasterUsername:
    Type: String
    Default: postgres

  MasterUserPassword:
    Type: String
    NoEcho: true
    MinLength: 8

  DBInstanceClass:
    Type: String
    Default: db.r5.large

  EngineVersion:
    Type: String
    Default: "15.4"

  DatabaseName:
    Type: String
    Default: mydb

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
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Aurora PostgreSQL subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  DBClusterParameterGroup:
    Type: AWS::RDS::DBClusterParameterGroup
    Properties:
      Description: Aurora PostgreSQL cluster parameter group
      Family: aurora-postgresql15
      Parameters:
        max_connections: 1000
        shared_buffers: 2097152
        work_mem: 32768
        maintenance_work_mem: 524288
        effective_cache_size: 6291456
        log_min_duration_statement: 2000

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Aurora PostgreSQL security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  DBCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: !Ref DBClusterIdentifier
      Engine: aurora-postgresql
      EngineVersion: !Ref EngineVersion
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DatabaseName: !Ref DatabaseName
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      StorageEncrypted: true
      KmsKeyId: !Ref KmsKeyId
      EngineMode: provisioned
      Port: 5432
      EnableIAMDatabaseAuthentication: true
      BackupRetentionPeriod: 35
      DeletionProtection: true

  DBInstanceWriter:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub ${DBClusterIdentifier}-writer
      DBClusterIdentifier: !Ref DBCluster
      Engine: aurora-postgresql
      DBInstanceClass: !Ref DBInstanceClass
      PromotionTier: 1

  DBInstanceReader:
    Type: AWS::RDS::DBInstance
    DependsOn: DBInstanceWriter
    Properties:
      DBInstanceIdentifier: !Sub ${DBClusterIdentifier}-reader
      DBClusterIdentifier: !Ref DBCluster
      Engine: aurora-postgresql
      DBInstanceClass: !Ref DBInstanceClass
      PromotionTier: 2

Outputs:
  ClusterEndpoint:
    Description: Writer endpoint
    Value: !GetAtt DBCluster.Endpoint

  ClusterReadEndpoint:
    Description: Reader endpoint
    Value: !GetAtt DBCluster.ReadEndpoint

  ConnectionString:
    Description: JDBC connection string
    Value: !Sub jdbc:postgresql://${DBClusterEndpoint}:${DBClusterEndpoint.Port}/${DatabaseName}

  ReaderConnectionString:
    Description: JDBC connection string for read replica
    Value: !Sub jdbc:postgresql://${DBClusterReadEndpoint}:${DBClusterEndpoint.Port}/${DatabaseName}
```

---

## Multi-Region Replication Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Cross-region read replica for disaster recovery

Parameters:
  SourceDBInstanceIdentifier:
    Type: String
    Description: Source RDS instance ARN or identifier

  SourceRegion:
    Type: String
    Default: us-east-1
    Description: Source region

  TargetRegion:
    Type: String
    Default: us-west-2
    Description: Target region

  DBInstanceClass:
    Type: String
    Default: db.t3.medium

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Cross-region replica subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Cross-region replica security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          CidrIp: 10.0.0.0/16

  CrossRegionReadReplica:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub ${AWS::StackName}-replica
      SourceDBInstanceIdentifier: !Sub arn:aws:rds:${SourceRegion}:${AWS::AccountId}:db:${SourceDBInstanceIdentifier}
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      MultiAZ: false
      PubliclyAccessible: false

Outputs:
  ReplicaInstanceId:
    Description: Cross-region replica instance ID
    Value: !Ref CrossRegionReadReplica

  ReplicaEndpoint:
    Description: Cross-region replica endpoint
    Value: !GetAtt CrossRegionReadReplica.Endpoint.Address
```

---

## Serverless Aurora Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Aurora Serverless MySQL cluster

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  DBClusterIdentifier:
    Type: String
    Default: my-aurora-serverless

  MasterUsername:
    Type: String
    Default: admin

  MasterUserPassword:
    Type: String
    NoEcho: true
    MinLength: 8

  DatabaseName:
    Type: String
    Default: mydb

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
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Serverless Aurora subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
        - !Ref PrivateSubnet3Id

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Serverless Aurora security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroupId

  ServerlessCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      DBClusterIdentifier: !Ref DBClusterIdentifier
      Engine: aurora-mysql
      EngineVersion: "5.6.mysql_aurora.2.12.0"
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DatabaseName: !Ref DatabaseName
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      EngineMode: serverless
      ScalingConfiguration:
        AutoPause: true
        MinCapacity: 2
        MaxCapacity: 16
        SecondsUntilAutoPause: 300
      EnableIAMDatabaseAuthentication: true
      BackupRetentionPeriod: 35
      DeletionProtection: true

Outputs:
  ClusterEndpoint:
    Description: Serverless cluster endpoint
    Value: !GetAtt ServerlessCluster.Endpoint

  ClusterReadEndpoint:
    Description: Serverless cluster reader endpoint
    Value: !GetAtt ServerlessCluster.ReadEndpoint
```

---

## MariaDB with Read Replicas Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: MariaDB with read replicas for scaling

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  MasterInstanceIdentifier:
    Type: String
    Default: mariadb-master

  MasterUsername:
    Type: String
    Default: admin

  MasterUserPassword:
    Type: String
    NoEcho: true

  MasterInstanceClass:
    Type: String
    Default: db.t3.medium

  ReplicaInstanceClass:
    Type: String
    Default: db.t3.medium

  ReplicaCount:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 5

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: MariaDB subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: MariaDB security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          CidrIp: 10.0.0.0/16

  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: MariaDB parameter group
      Family: mariadb10.6
      Parameters:
        max_connections: 300
        innodb_buffer_pool_size: 1073741824

  MasterDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Ref MasterInstanceIdentifier
      DBInstanceClass: !Ref MasterInstanceClass
      Engine: mariadb
      EngineVersion: "10.6.14"
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      MultiAZ: true
      StorageEncrypted: true

  # Read Replica 1
  ReadReplica1:
    Type: AWS::RDS::DBInstance
    DependsOn: MasterDBInstance
    Properties:
      DBInstanceIdentifier: !Sub ${MasterInstanceIdentifier}-replica-1
      SourceDBInstanceIdentifier: !Ref MasterDBInstance
      DBInstanceClass: !Ref ReplicaInstanceClass
      VPCSecurityGroups:
        - !Ref DBSecurityGroup

  # Read Replica 2 (conditional)
  ReadReplica2:
    Type: AWS::RDS::DBInstance
    DependsOn: MasterDBInstance
    Condition: CreateSecondReplica
    Properties:
      DBInstanceIdentifier: !Sub ${MasterInstanceIdentifier}-replica-2
      SourceDBInstanceIdentifier: !Ref MasterDBInstance
      DBInstanceClass: !Ref ReplicaInstanceClass
      VPCSecurityGroups:
        - !Ref DBSecurityGroup

Conditions:
  CreateSecondReplica: !Not [!Equals [!Ref ReplicaCount, 1]]

Outputs:
  MasterEndpoint:
    Description: Master database endpoint
    Value: !GetAtt MasterDBInstance.Endpoint.Address

  Replica1Endpoint:
    Description: Read replica 1 endpoint
    Value: !GetAtt ReadReplica1.Endpoint.Address

  Replica2Endpoint:
    Condition: CreateSecondReplica
    Description: Read replica 2 endpoint
    Value: !GetAtt ReadReplica2.Endpoint.Address
```

---

## Oracle with Option Group Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Oracle RDS with custom option group and parameter group

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  DBInstanceIdentifier:
    Type: String
    Default: oracle-db

  MasterUsername:
    Type: String
    Default: admin

  MasterUserPassword:
    Type: String
    NoEcho: true
    MinLength: 8

  DBInstanceClass:
    Type: String
    Default: db.t3.medium

  EngineVersion:
    Type: String
    Default: "19.0.0.0.ru-2023-10.rur-2023-10.r1"

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Oracle subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id

  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Oracle parameter group
      Family: oracle-ee-19
      Parameters:
        processes: 300
        sessions: 380
        timed_statistics: "TRUE"

  DBOptionGroup:
    Type: AWS::RDS::DBOptionGroup
    Properties:
      EngineName: oracle-ee
      MajorEngineVersion: "19"
      OptionGroupDescription: Oracle 19c option group
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
            - Name: SQLNET.CIPHER_SUITE
              Value: "SSL_RSA_WITH_AES_256_CBC_SHA"
        - OptionName: APEX
          OptionVersion: "22.1.0"
          OptionSettings:
            - Name: APEX_LISTENER_PORT
              Value: "8080"

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Oracle RDS security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 1521
          ToPort: 1521
          CidrIp: 10.0.0.0/16

  OEMSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: OEM management security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5500
          ToPort: 5500
          CidrIp: 10.0.0.0/16

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Ref DBInstanceIdentifier
      DBInstanceClass: !Ref DBInstanceClass
      Engine: oracle-ee
      EngineVersion: !Ref EngineVersion
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      AllocatedStorage: 200
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      DBOptionGroupName: !Ref DBOptionGroup
      StorageEncrypted: true
      MultiAZ: true
      BackupRetentionPeriod: 35

Outputs:
  DBInstanceEndpoint:
    Description: Oracle endpoint
    Value: !GetAtt DBInstance.Endpoint.Address

  DBInstancePort:
    Description: Oracle port
    Value: !GetAtt DBInstance.Endpoint.Port

  OEMEndpoint:
    Description: OEM Express endpoint
    Value: !Sub "${DBInstanceEndpoint}:5500/dbcars"
```

---

## SQL Server Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: SQL Server RDS instance

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  DBInstanceIdentifier:
    Type: String
    Default: sqlserver-db

  MasterUsername:
    Type: String
    Default: admin

  MasterUserPassword:
    Type: String
    NoEcho: true
    MinLength: 8

  DBInstanceClass:
    Type: String
    Default: db.t3.medium

  EngineEdition:
    Type: String
    Default: sqlserver-ex
    AllowedValues:
      - sqlserver-ex
      - sqlserver-se
      - sqlserver-web
      - sqlserver-ee

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id

Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: SQL Server subnet group
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: SQL Server security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 1433
          ToPort: 1433
          CidrIp: 10.0.0.0/16

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Ref DBInstanceIdentifier
      DBInstanceClass: !Ref DBInstanceClass
      Engine: !Ref EngineEdition
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      AllocatedStorage: 200
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      StorageEncrypted: true
      MultiAZ: true
      BackupRetentionPeriod: 35

Outputs:
  DBInstanceEndpoint:
    Description: SQL Server endpoint
    Value: !GetAtt DBInstance.Endpoint.Address

  DBInstancePort:
    Description: SQL Server port
    Value: !GetAtt DBInstance.Endpoint.Port

  ConnectionString:
    Description: JDBC connection string
    Value: !Sub jdbc:sqlserver://${DBInstanceEndpoint}:${DBInstancePort};databaseName=master
```

---

## Complete Network Stack for RDS

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Network infrastructure for RDS deployment

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

  # Public Subnets
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
        - Key: SubnetType
          Value: Public

  # Private Subnets (for RDS)
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

  PublicSubnetIds:
    Description: Public subnet IDs
    Value: !Join [",", [!Ref PublicSubnet1, !Ref PublicSubnet2]]

  PrivateSubnetIds:
    Description: Private subnet IDs for RDS
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

  NatGatewayId:
    Description: NAT Gateway ID
    Value: !Ref NatGateway
```
