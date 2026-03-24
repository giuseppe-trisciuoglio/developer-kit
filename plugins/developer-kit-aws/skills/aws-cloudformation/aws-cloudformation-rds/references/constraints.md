# RDS Constraints and Warnings

## Resource Limits

### Instance Storage Limits

Maximum storage size varies by instance class and engine:
- **MySQL/PostgreSQL**: Up to 64 TB with gp3 storage
- **Oracle**: Up to 64 TB with gp3 storage
- **SQL Server**: Up to 16 TB with gp3 storage
- **Aurora**: Up to 128 TB (automatically grows)

```yaml
# Storage configuration
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      AllocatedStorage: 100  # GB
      MaxAllocatedStorage: 1000  # GB for autoscaling
      StorageType: gp3
      Iops: 3000  # For io1/io2
      StorageThroughput: 500  # MB/s for gp3
```

### Database Name Limits

- **Identifier Length**: 1-63 characters for MySQL, 1-63 for PostgreSQL, 1-8 for Oracle
- **Allowed Characters**: Letters, numbers, underscores (must start with letter)
- **Reserved Words**: Cannot use database engine reserved words

```yaml
Parameters:
  DatabaseName:
    Type: String
    Description: Database name
    Default: myappdb
    AllowedPattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
    MinLength: 1
    MaxLength: 63
    ConstraintDescription: Must begin with letter; contain only letters, numbers, underscores
```

### Parameter Groups Limits

- **Maximum parameter groups**: Varies by account/region (typically 50)
- **Parameters per group**: Up to 150 parameters per group
- **Dynamic vs Static**: Some parameters require restart

```yaml
Resources:
  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Custom parameter group
      Family: mysql8.0
      Parameters:
        max_connections: 200  # Dynamic (no restart)
        innodb_buffer_pool_size: 1073741824  # Static (requires restart)
```

### Option Groups Limits

- **Compatibility**: Some options are not compatible with specific database engines
- **Port Conflicts**: Options may require specific ports
- **Permanent Options**: Some options cannot be removed once added

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
          Port: 5500  # Ensure port availability
```

## Operational Constraints

### Instance Replacement

Certain modifications require instance replacement with **downtime**:
- **Engine Version Change**: Major version upgrades require replacement
- **Storage Type Change**: gp3 → io1 or vice versa
- **Instance Class Change**: Burstable classes → memory optimized classes
- **License Model**: Changes require replacement

```yaml
# CAUTION: These changes cause replacement and downtime
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      # Engine version change triggers replacement
      EngineVersion: "16.1"  # From 15.x causes replacement
      # Storage type change triggers replacement
      StorageType: io1  # From gp3 causes replacement
```

### Snapshot Storage Costs

Manual snapshots incur storage costs even after instance deletion:

```bash
# List manual snapshots
aws rds describe-db-snapshots \
  --snapshot-type manual \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime,SnapshotStorageSize]'

# Delete old manual snapshots to save costs
aws rds delete-db-snapshot \
  --db-snapshot-identifier old-snapshot-20240101
```

### Multi-AZ Deployment Costs

Multi-AZ deployments double compute costs:

```yaml
Resources:
  SingleAZInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      MultiAZ: false  # Single cost

  MultiAZInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      MultiAZ: true  # ~2x cost for standby replica
```

**Cost Comparison**:
- Single-AZ db.t3.medium: ~$0.08/hour = ~$58/month
- Multi-AZ db.t3.medium: ~$0.16/hour = ~$116/month

### Backup Retention Costs

Changing backup retention period affects storage costs:

```yaml
Resources:
  DevelopmentDB:
    Type: AWS::RDS::DBInstance
    Properties:
      BackupRetentionPeriod: 7  # Minimal backup costs

  ProductionDB:
    Type: AWS::RDS::DBInstance
    Properties:
      BackupRetentionPeriod: 35  # Higher backup storage costs
```

## Security Constraints

### Master Credentials

Master user password cannot be retrieved after creation:

```yaml
# ❌ WRONG: Password cannot be retrieved
Outputs:
  MasterPassword:
    Value: !Ref MasterUserPassword  # This will be masked

# ✅ CORRECT: Store in Secrets Manager
Resources:
  DBCredentials:
    Type: AWS::SecretsManager::Secret
    Properties:
      SecretString: !Sub '{"username":"${MasterUsername}","password":"${MasterUserPassword}"}'
```

**Recovery Process**:
```bash
# If master password is lost, reset it
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --master-user-password new-password-123
  --apply-immediately
```

### Encryption at Rest

Once enabled, encryption cannot be disabled for RDS storage:

```yaml
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      StorageEncrypted: true  # Cannot be disabled later
      KmsKeyId: !Ref EncryptionKey
```

**Migration to Encrypted Storage**:
1. Create snapshot of unencrypted instance
2. Copy snapshot with encryption
3. Restore from encrypted snapshot
4. Update application to use new instance
5. Delete old unencrypted instance

### VPC Access Requirements

RDS instances must be in VPC; public access not recommended:

```yaml
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      PubliclyAccessible: false  # Recommended for security
      DBSubnetGroupName: !Ref DBSubnetGroup  # Required for VPC
```

**Network Isolation Best Practices**:
- Deploy in private subnets only
- Use VPC endpoints for AWS services
- Restrict security group rules to specific sources
- Enable VPC flow logs for monitoring

### Security Group Rules

Security group rules must allow traffic from application tier only:

```yaml
Resources:
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Database security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        # ✅ CORRECT: Specific source
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroup

        # ❌ WRONG: Too permissive
        # - IpProtocol: tcp
        #   FromPort: 5432
        #   ToPort: 5432
        #   CidrIp: 0.0.0.0/0
```

## Cost Considerations

### Instance Class Costs

Larger instance classes significantly increase hourly costs:

```yaml
# Cost comparison (us-east-1, on-demand, Linux/Unix)
Resources:
  MicroInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro  # ~$0.013/hour = ~$9.50/month

  MediumInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium  # ~$0.052/hour = ~$38/month

  LargeInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.m5.large  # ~$0.135/hour = ~$99/month
```

### IOPS Costs

Provisioned IOPS (io1/io2) storage type significantly increases costs:

```yaml
Resources:
  # gp3 storage (cost-effective)
  GP3Instance:
    Type: AWS::RDS::DBInstance
    Properties:
      StorageType: gp3
      AllocatedStorage: 100
      Iops: 3000  # Free with gp3
      StorageThroughput: 125  # Free with gp3 up to 125 MB/s

  # io1 storage (expensive for high IOPS)
  IO1Instance:
    Type: AWS::RDS::DBInstance
    Properties:
      StorageType: io1
      AllocatedStorage: 100
      Iops: 3000  # $0.125 per IOPS-month = $375/month additional
```

### Backup Storage Costs

Automated backups beyond free tier incur monthly GB storage costs:

```yaml
Resources:
  DevelopmentDB:
    Type: AWS::RDS::DBInstance
    Properties:
      AllocatedStorage: 100  # GB
      BackupRetentionPeriod: 7  # Minimal backup cost
      # Free tier: 100% of DB storage for 7-day retention

  ProductionDB:
    Type: AWS::RDS::DBInstance
    Properties:
      AllocatedStorage: 1000  # GB
      BackupRetentionPeriod: 35  # Higher backup costs
      # Cost: (1000 GB × (35 - 7) days) × $0.095/GB-month
```

### Data Transfer Costs

Inter-AZ data transfer for Multi-AZ replication incurs costs:

```yaml
Resources:
  MultiAZDB:
    Type: AWS::RDS::DBInstance
    Properties:
      MultiAZ: true  # Inter-AZ data transfer: $0.01/GB
      # Example: 100 GB/day replication = $3/day = $90/month
```

## Performance Constraints

### Storage Autoscaling

Storage autoscaling has minimum and maximum increments:

```yaml
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      AllocatedStorage: 100  # Starting size
      MaxAllocatedStorage: 1000  # Maximum autoscaling limit
      StorageType: gp3  # Required for autoscaling
```

**Autoscaling Behavior**:
- Triggers when free storage < 10%
- Increments in 10% chunks
- Maximum limit prevents runaway costs

### Connection Limits

Maximum connections vary by instance class and database engine:

```yaml
Resources:
  # MySQL connection limits
  MySQLInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro  # max_connections: ~40
      # db.t3.medium: ~200 connections
      # db.m5.large: ~500-1000 connections

  # PostgreSQL connection limits
  PostgreSQLInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro  # max_connections: ~40
      # Can be configured via parameter group
```

**Connection Pooling**:
```yaml
Resources:
  # Increase connection limits via parameter group
  HighConnectionParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Family: mysql8.0
      Parameters:
        max_connections: 1000  # Increase for high-traffic apps
```

### Maintenance Windows

Maintenance windows may cause brief service interruptions:

```yaml
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      PreferredMaintenanceWindow: sun:03:00-sun:04:00  # Low-traffic time
      # Expect ~30 seconds downtime for patches
```

### Read Replica Lag

Read replicas may lag behind primary by seconds to minutes:

```yaml
Resources:
  # Monitor replication lag
  PrimaryDB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: postgres

  ReadReplica:
    Type: AWS::RDS::DBInstance
    Properties:
      SourceDBInstanceIdentifier: !Ref PrimaryDB
      # Replication lag varies by:
      # - Write workload intensity
      # - Network latency between AZs
      # - Instance class size
```

## Availability Constraints

### Region Availability

Not all database engines are available in all regions:

```yaml
# Check availability before deployment
# Aurora PostgreSQL: Available in us-east-1, us-west-2, eu-west-1, etc.
# Aurora MySQL: Available in all commercial regions
# Oracle: Limited regions due to licensing

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      Engine: aurora-postgresql  # Verify region availability
```

### Version Support

Older database versions may be deprecated and require upgrades:

```yaml
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      Engine: postgres
      EngineVersion: "16.1"  # Use current supported version
      # Avoid deprecated versions like PostgreSQL 10 or 11
```

### Instance Type Availability

Some instance types may not be available in all AZs:

```yaml
Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.x2g.large  # Memory optimized
      # May not be available in all AZs
      # Let AWS select AZ for best availability
```

## Troubleshooting

### Common Issues

**Insufficient Storage**:
```bash
# Check storage usage
aws rds describe-db-instances \
  --db-instance-identifier mydb \
  --query 'DBInstances[0].[AllocatedStorage,FreeStorageSpace]'

# Enable storage autoscaling
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --max-allocated-storage 1000 \
  --apply-immediately
```

**Connection Timeouts**:
```yaml
# Increase max_connections parameter
Resources:
  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Family: postgres16
      Parameters:
        max_connections: 500  # Increase from default
```

**Slow Performance**:
```bash
# Enable Performance Insights
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --enable-performance-insights \
  --performance-insights-retention-period 731 \
  --apply-immediately

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=mydb \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average
```
