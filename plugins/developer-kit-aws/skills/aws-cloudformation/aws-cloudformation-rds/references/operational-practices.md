# RDS Operational Best Practices

## Stack Policies

Stack policies protect critical RDS resources from unintended updates during stack operations.

### Basic Stack Policy

```json
{
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : "Update:*",
      "Principal": "*",
      "Resource" : "*"
    },
    {
      "Effect" : "Deny",
      "Action" : "Update:*",
      "Principal": "*",
      "Resource" : "LogicalResourceId/DBInstance"
    },
    {
      "Effect" : "Deny",
      "Action" : "Update:*",
      "Principal": "*",
      "Resource" : "LogicalResourceId/DBCluster"
    }
  ]
}
```

### Stack Policy for Production RDS

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "Update:*",
      "Principal": "*",
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "Update:Replace",
        "Update:Delete"
      ],
      "Principal": "*",
      "Resource": "LogicalResourceId/DBInstance"
    },
    {
      "Effect": "Deny",
      "Action": [
        "Update:Replace",
        "Update:Delete"
      ],
      "Principal": "*",
      "Resource": "LogicalResourceId/DBCluster"
    },
    {
      "Effect": "Deny",
      "Action": "Update:Delete",
      "Principal": "*",
      "Resource": "LogicalResourceId/DBSubnetGroup"
    },
    {
      "Effect": "Allow",
      "Action": "Update:Modify",
      "Principal": "*",
      "Resource": "LogicalResourceId/DBInstance",
      "Condition": {
        "StringEquals": {
          "ResourceAttribute/StorageEncrypted": "true"
        }
      }
    }
  ]
}
```

### Setting Stack Policy

```bash
# Set stack policy during creation
aws cloudformation create-stack \
  --stack-name my-rds-stack \
  --template-body file://template.yaml \
  --stack-policy-body file://stack-policy.json

# Set stack policy on existing stack
aws cloudformation set-stack-policy \
  --stack-name my-rds-stack \
  --stack-policy-body file://stack-policy.json

# View current stack policy
aws cloudformation get-stack-policy \
  --stack-name my-rds-stack \
  --query StackPolicyBody \
  --output text
```

## Termination Protection

Termination protection is **critical for RDS databases** as it prevents accidental deletion.

### Enabling Termination Protection

```bash
# Enable termination protection on stack creation
aws cloudformation create-stack \
  --stack-name production-rds \
  --template-body file://template.yaml \
  --enable-termination-protection

# Enable termination protection on existing stack
aws cloudformation update-termination-protection \
  --stack-name production-rds \
  --enable-termination-protection

# Check if termination protection is enabled
aws cloudformation describe-stacks \
  --stack-name production-rds \
  --query 'Stacks[0].EnableTerminationProtection' \
  --output boolean

# Disable termination protection (requires confirmation)
aws cloudformation update-termination-protection \
  --stack-name production-rds \
  --no-enable-termination-protection
```

### Deletion Protection vs Termination Protection

| Feature | DeletionProtection | Termination Protection |
|---------|-------------------|------------------------|
| **Level** | Resource level (DBInstance) | Stack level |
| **Prevents** | DELETE_DB_INSTANCE API call | CloudFormation stack deletion |
| **Console UI** | Instance settings | Stack settings |
| **Override** | Cannot be overridden | Can be disabled with confirmation |
| **Recommended for** | All production RDS instances | All production stacks with RDS |

### Deletion Protection Best Practice

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      # Always enable deletion protection
      DeletionProtection: !If [IsProduction, true, false]
      # Additional production safeguards
      MultiAZ: !If [IsProduction, true, false]
      BackupRetentionPeriod: !If [IsProduction, 35, 7]
```

## Drift Detection

Drift detection identifies when the actual infrastructure configuration differs from the CloudFormation template.

### Detecting Drift

```bash
# Detect drift on entire stack
aws cloudformation detect-stack-drift \
  --stack-name production-rds

# Detect drift on specific resources
aws cloudformation detect-stack-drift \
  --stack-name production-rds \
  --logical-resource-ids DBInstance,DBParameterGroup

# Get drift detection status
aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id <detection-id>

# Check drift status for all resources
aws cloudformation describe-stack-resource-drifts \
  --stack-name production-rds
```

### Drift Detection Status Response

```json
{
  "StackResourceDrifts": [
    {
      "LogicalResourceId": "DBInstance",
      "PhysicalResourceId": "production-db-instance-id",
      "ResourceType": "AWS::RDS::DBInstance",
      "DriftStatus": "MODIFIED",
      "PropertyDifferences": [
        {
          "PropertyPath": "MultiAZ",
          "ExpectedValue": "true",
          "ActualValue": "false"
        },
        {
          "PropertyPath": "BackupRetentionPeriod",
          "ExpectedValue": "35",
          "ActualValue": "7"
        }
      ]
    }
  ]
}
```

### Automated Drift Detection Schedule

```bash
# Create EventBridge rule for weekly drift detection
aws events put-rule \
  --name rds-drift-detection \
  --schedule-expression "rate(7 days)"

# Add Lambda target for drift detection
aws events put-targets \
  --rule rds-drift-detection \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789:function/drift-checker"
```

### Drift Detection Script

```bash
#!/bin/bash
# check-rds-drift.sh

STACK_NAME=$1
if [ -z "$STACK_NAME" ]; then
    echo "Usage: $0 <stack-name>"
    exit 1
fi

# Start drift detection
DETECTION_ID=$(aws cloudformation detect-stack-drift \
  --stack-name $STACK_NAME \
  --query 'StackId' \
  --output text)

echo "Drift detection started: $DETECTION_ID"

# Wait for completion
STATUS="DETECTION_IN_PROGRESS"
while [ "$STATUS" = "DETECTION_IN_PROGRESS" ]; do
    sleep 10
    STATUS=$(aws cloudformation describe-stack-drift-detection-status \
      --stack-drift-detection-id $DETECTION_ID \
      --query 'DetectionStatus' \
      --output text)
    echo "Status: $STATUS"
done

# Get drift status
DRIFT_STATUS=$(aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id $DETECTION_ID \
  --query 'DriftStatus' \
  --output text)

if [ "$DRIFT_STATUS" = "DRIFTED" ]; then
    echo "Drift detected!"
    aws cloudformation describe-stack-resource-drifts \
      --stack-name $STACK_NAME \
      --query 'StackResourceDrifts[].{LogicalId:LogicalResourceId,Status:ResourceDriftStatus}'
else
    echo "No drift detected"
fi
```

## Change Sets

Change sets allow you to preview how proposed changes will affect your stack before execution.

### Creating and Viewing a Change Set

```bash
# Create change set for stack update
aws cloudformation create-change-set \
  --stack-name production-rds \
  --change-set-name preview-changes \
  --template-body file://updated-template.yaml \
  --capabilities CAPABILITY_IAM \
  --change-set-type UPDATE

# List change sets for a stack
aws cloudformation list-change-sets \
  --stack-name production-rds

# Describe change set
aws cloudformation describe-change-set \
  --stack-name production-rds \
  --change-set-name preview-changes

# Execute change set
aws cloudformation execute-change-set \
  --stack-name production-rds \
  --change-set-name preview-changes

# Delete change set (if not executing)
aws cloudformation delete-change-set \
  --stack-name production-rds \
  --change-set-name preview-changes
```

### Change Set Response Example

```json
{
  "ChangeSetName": "preview-changes",
  "Status": "CREATE_COMPLETE",
  "Changes": [
    {
      "Type": "Resource",
      "ResourceChange": {
        "Action": "Modify",
        "LogicalResourceId": "DBInstance",
        "PhysicalResourceId": "production-db",
        "ResourceType": "AWS::RDS::DBInstance",
        "Replacement": "False",
        "Details": [
          {
            "Target": {
              "Attribute": "Properties",
              "Name": "MultiAZ"
            },
            "BeforeValue": "false",
            "AfterValue": "true"
          }
        ]
      }
    }
  ]
}
```

### Change Set Types

| Change Set Type | Description | Use Case |
|----------------|-------------|----------|
| `UPDATE` | Creates changes for existing stack | Modifying existing resources |
| `CREATE` | Simulates stack creation | Validating new templates |
| `IMPORT` | Imports existing resources | Moving resources to CloudFormation |

### Change Set Best Practices for RDS

```bash
# Always create change set before updating RDS
aws cloudformation create-change-set \
  --stack-name production-rds \
  --change-set-name pre-update-preview \
  --template-body file://updated-template.yaml

# Review changes carefully
aws cloudformation describe-change-set \
  --stack-name production-rds \
  --change-set-name pre-update-preview \
  --query 'Changes[].ResourceChange'

# Check for replacement operations
aws cloudformation describe-change-set \
  --stack-name production-rds \
  --change-set-name pre-update-preview \
  --query 'Changes[?ResourceChange.Replacement==`True`]'

# Only execute if changes are acceptable
aws cloudformation execute-change-set \
  --stack-name production-rds \
  --change-set-name pre-update-preview
```

## Backup and Recovery

### Automated Backup Strategy

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
```

### Manual Snapshot Creation

```bash
# Create manual snapshot before major changes
aws rds create-db-snapshot \
  --db-instance-identifier production-db \
  --db-snapshot-identifier pre-migration-snapshot-$(date +%Y%m%d)

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier production-db

# Copy snapshot to different region
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier pre-migration-snapshot \
  --target-db-snapshot-identifier dr-snapshot-copy \
  --source-region us-east-1 \
  --kms-key-id alias/dr-key
```

### Restore from Snapshot

```yaml
Resources:
  # Restore from snapshot
  RestoredDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: postgres
      DBInstanceIdentifier: restored-db
      DBSnapshotIdentifier: !Ref DBSnapshot
      MultiAZ: false

  # Point-in-time restore
  PITRRestoredInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: postgres
      DBInstanceIdentifier: pitr-restored
      SourceDBInstanceIdentifier: !Ref OriginalDBInstance
      RestoreTime: '2024-01-15T12:00:00Z'
```

## Monitoring and Alerting

### CloudWatch Alarms

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

  # Free storage space alarm
  StorageAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: Alarm if free storage < 10GB
      MetricName: FreeStorageSpace
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 10737418240
      ComparisonOperator: LessThanThreshold
```

### SNS Notifications

```yaml
Resources:
  # SNS topic for alerts
  DBAlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: RDS Alerts

  # Subscribe email to alerts
  EmailSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      Protocol: email
      TopicArn: !Ref DBAlertsTopic
      Endpoint: dba@company.com

  # Alarms send to SNS
  CPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmActions:
        - !Ref DBAlertsTopic
      # ... other properties
```

## Maintenance Windows

```yaml
Resources:
  ProductionDBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: postgres
      # Maintenance window (Sunday 3-4 AM UTC)
      PreferredMaintenanceWindow: sun:03:00-sun:04:00
      # Auto minor version upgrade disabled for manual control
      AutoMinorVersionUpgrade: false
      # Major version upgrade requires manual intervention
      AllowMajorVersionUpgrade: false
```

### Maintenance Scheduling

```bash
# View pending maintenance
aws rds describe-pending-maintenance-actions \
  --filters Name=resource-type,Values=DBInstance

# Apply maintenance immediately (emergency)
aws rds apply-pending-maintenance-action \
  --resource-id production-db \
  --apply-action system-update \
  --opt-in-type immediate
```
