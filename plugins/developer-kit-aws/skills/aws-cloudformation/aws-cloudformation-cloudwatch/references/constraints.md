# CloudWatch Constraints and Limitations

## Resource Limits

### Alarm Limits

```yaml
# Maximum 5000 alarms per AWS account per region
Parameters:
  ExpectedAlarms:
    Type: Number
    Default: 100
    MinValue: 1
    MaxValue: 5000
    Description: Expected number of CloudWatch alarms
    ConstraintDescription: Cannot exceed 5000 alarms per region

# Request quota increase if needed
Resources:
  AlarmQuotaRequest:
    Type: AWS::SupportApp::SlackChannelConfiguration
    Properties:
      # Notify when approaching quota limits
      SlackChannelId: !Ref SlackChannelId
      SlackWorkspaceId: !Ref SlackWorkspaceId
```

### Dashboard Limits

```yaml
# Maximum 500 dashboards per account per region
# Maximum 500 widgets per dashboard
# Maximum 100 metrics per dashboard

Parameters:
  MaxDashboards:
    Type: Number
    Default: 10
    MaxValue: 500
    Description: Maximum number of dashboards

  MaxWidgetsPerDashboard:
    Type: Number
    Default: 50
    MaxValue: 500
    Description: Maximum widgets per dashboard

Resources:
  MonitoringDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${AWS::StackName}-dashboard"
      DashboardBody: !Sub |
        {
          "widgets": [
            # Maximum 500 widgets allowed
            # Each widget can contain multiple metrics
            # Maximum 100 metrics per dashboard recommended
          ]
        }
```

### Metrics Limits

```yaml
# Metric resolution and retention constraints
Parameters:
  MetricResolution:
    Type: String
    Default: Standard
    AllowedValues:
      - Standard    # 1-minute resolution, 15-month retention
      - High        # 1-second resolution (Stateful), 3-month retention
      - VeryHigh    # 1-second resolution (Stateless), 3-hour retention
    Description: Metric resolution affects retention and cost

# Custom metrics limits
Resources:
  CustomMetric:
    Type: AWS::CloudWatch::Metric
    Properties:
      # Custom metrics count against account limits
      Namespace: !Sub "${AWS::StackName}/custom"
      MetricData:
        - MetricName: CustomMetric
          # Dimensions and values
```

### Log Groups Limits

```yaml
# Unlimited log groups but retention has cost implications
Parameters:
  LogRetentionDays:
    Type: Number
    Default: 30
    AllowedValues:
      - 1          # 1 day
      - 3          # 3 days
      - 5          # 5 days
      - 7          # 1 week
      - 14         # 2 weeks
      - 30         # 1 month
      - 60         # 2 months
      - 90         # 3 months
      - 120        # 4 months
      - 150        # 5 months
      - 180        # 6 months
      - 365        # 1 year
      - 400        # 400 days
      - 545        # 18 months
      - 731        # 2 years
      - 1827       # 5 years
      - 3653       # 10 years
    Description: Log retention period (longer = higher cost)

Resources:
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/application/${AWS::StackName}"
      RetentionInDays: !Ref LogRetentionDays
```

## Operational Constraints

### Metric Resolution Constraints

```yaml
# Higher resolution metrics cost more and have shorter retention
Parameters:
  MetricResolution:
    Type: String
    Default: Standard
    AllowedValues:
      - Standard    # 1-minute minimum, 15-month retention
      - High        # 1-second minimum, 3-month retention
      - VeryHigh    # 1-second minimum, 3-hour retention

Resources:
  HighResolutionAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      # High-resolution metrics
      Period: 1  # 1 second (requires high-resolution metrics)
      EvaluationPeriods: 3
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
```

### Alarm Evaluation Constraints

```yaml
# Alarms with too few evaluation periods may trigger false positives
Parameters:
  EvaluationPeriods:
    Type: Number
    Default: 3
    MinValue: 1
    MaxValue: 100  # Practical limit
    Description: Number of periods to evaluate

  AlarmPeriod:
    Type: Number
    Default: 60
    AllowedValues:
      - 10       # 10 seconds (high-resolution only)
      - 30       # 30 seconds (high-resolution only)
      - 60       # 1 minute
      - 300      # 5 minutes
      - 900      # 15 minutes
      - 3600     # 1 hour
      - 86400    # 1 day
    Description: Time period for each evaluation

Resources:
  CpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-cpu-alarm"
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: !Ref AlarmPeriod
      EvaluationPeriods: !Ref EvaluationPeriods
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
```

### Cross-Account Metrics Constraints

```yaml
# Cross-account sharing requires explicit resource policies
Resources:
  # Account A - Source account with metrics
  MetricSinkPolicy:
    Type: AWS::CloudWatch::MetricSinkPolicy
    Properties:
      MetricSinkPolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${TargetAccountId}:root"
            Action:
              - cloudwatch:PutMetricData
              - cloudwatch:GetMetricData
              - cloudwatch:ListMetrics
            Resource: "*"

  # Account B - Destination account
  CrossAccountAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: cross-account-alarm
      # Must have permission to access source account metrics
```

## Security Constraints

### Log Data Access

```yaml
# CloudWatch Logs may contain sensitive information
# Implement appropriate access controls

Resources:
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/application/${AWS::StackName}"
      RetentionInDays: 30

  # Restrict log access with IAM policies
  LogGroupPolicy:
    Type: AWS::Logs::ResourcePolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-log-policy"
      PolicyDocument: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": "es.amazonaws.com"
              },
              "Action": [
                "logs:PutLogEvents",
                "logs:CreateLogStream"
              ],
              "Resource": !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/application/${AWS::StackName}"
            }
          ]
        }
```

### Encryption Constraints

```yaml
# KMS keys required for encrypted log groups incur additional costs
Parameters:
  EnableLogEncryption:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false

Conditions:
  EncryptLogs: !Equals [!Ref EnableLogEncryption, true]

Resources:
  LogEncryptionKey:
    Type: AWS::KMS::Key
    Condition: EncryptLogs
    Properties:
      Description: KMS key for log encryption
      KeyPolicy:
        Statement:
          - Effect: Allow
            Principal:
              Service: logs.amazonaws.com
            Action:
              - kms:Decrypt
              - kms:GenerateDataKey
            Resource: "*"

  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/application/${AWS::StackName}"
      RetentionInDays: 30
      KmsKeyId: !If [EncryptLogs, !GetAtt LogEncryptionKey.Arn, !Ref AWS::NoValue]
```

### Metric Filter Constraints

```yaml
# Metric filters count as separate billable operations
Parameters:
  MaxMetricFilters:
    Type: Number
    Default: 10
    MaxValue: 100  # Practical limit per log group
    Description: Maximum number of metric filters

Resources:
  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: "[timestamp, request_id, event_type=ERROR, ...]"
      MetricTransformations:
        - MetricName: ErrorCount
          MetricNamespace: !Sub "${AWS::StackName}/application"
          MetricValue: "1"
          Unit: Count

  # Multiple filters increase costs
  WarningMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: "[..., event_type=WARNING]"
      MetricTransformations:
        - MetricName: WarningCount
          MetricNamespace: !Sub "${AWS::StackName}/application"
```

### Alarm Actions Security

```yaml
# SNS topics used for alarm actions must have appropriate permissions
Resources:
  AlarmNotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !Sub "${AWS::StackName}-alarms"
      TopicName: !Sub "${AWS::StackName}-alarms"

  # Topic policy for CloudWatch
  AlarmTopicPolicy:
    Type: AWS::SNS::TopicPolicy
    Properties:
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudwatch.amazonaws.com
            Action: sns:Publish
            Resource: !Ref AlarmNotificationTopic
      Topics:
        - !Ref AlarmNotificationTopic

  CriticalAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-critical-alarm"
      AlarmActions:
        - !Ref AlarmNotificationTopic
      OKActions:
        - !Ref AlarmNotificationTopic
```

## Cost Considerations

### Detailed Monitoring Costs

```yaml
# Enabling detailed monitoring doubles metrics for EC2
Parameters:
  EnableDetailedMonitoring:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false
    Description: Enable detailed monitoring (doubles metric cost)

Resources:
  # Standard monitoring (free, 5-minute intervals)
  InstanceWithStandardMonitoring:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref ImageId
      InstanceType: !Ref InstanceType
      Monitoring: false  # Standard monitoring

  # Detailed monitoring (extra cost, 1-minute intervals)
  InstanceWithDetailedMonitoring:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref ImageId
      InstanceType: !Ref InstanceType
      Monitoring: true  # Detailed monitoring

  DetailedMonitoringAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      # 1-minute period requires detailed monitoring
      Period: 60
      EvaluationPeriods: 3
```

### Custom Metric Costs

```yaml
# Custom metrics stored in CloudWatch incur costs
# Based on resolution and retention

Parameters:
  CustomMetricResolution:
    Type: String
    Default: Standard
    AllowedValues:
      - Standard    # $0.30 per metric (us-east-1)
      - High        # $0.60 per metric
      - VeryHigh    # $0.90 per metric
    Description: Custom metric resolution (affects cost)

Resources:
  # Budget for custom metrics
  MetricsBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetLimit:
          Amount: 50  # Monthly budget for metrics
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          Service:
            - Amazon CloudWatch
          MetricType:
            - CustomMetrics
```

### Log Retention Costs

```yaml
# Longer retention periods significantly increase costs
Parameters:
  LogRetentionDays:
    Type: Number
    Default: 30
    Description: Longer retention = higher storage cost

# Calculate estimated monthly log costs
Conditions:
  UseLongRetention: !Not [!Equals [!Ref LogRetentionDays, 30]]

Resources:
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/application/${AWS::StackName}"
      RetentionInDays: !Ref LogRetentionDays

Outputs:
  EstimatedLogCost:
    Description: Estimated monthly log storage cost
    Value: !Sub
      - "${CostPerGB} GB"
      - CostPerGB: !If [UseLongRetention, "Higher ($0.50/GB)", "Standard ($0.50/GB)"]
```

### Dashboard Query Costs

```yaml
# Dashboard widgets don't directly cost but each metric queried does
Parameters:
  DashboardRefreshInterval:
    Type: Number
    Default: 15  # 15 seconds
    AllowedValues:
      - 10       # 10 seconds
      - 30       # 30 seconds
      - 1        # 1 minute
      - 5        # 5 minutes
      - 15       # 15 minutes
    Description: Dashboard refresh interval (affects GetMetricData API calls)

Resources:
  MonitoringDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${AWS::StackName}-dashboard"
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "metrics": [["AWS/EC2", "CPUUtilization"]],
                "period": 300,
                "stat": "Average"
              }
            }
            # Each widget metric queries CloudWatch (incurs API costs)
          ]
        }
```

## Data Constraints

### Metric Age and Retention

```yaml
# Metrics are retained for 15 months by default
# High-resolution metrics have shorter retention

Parameters:
  MetricResolution:
    Type: String
    Default: Standard
    AllowedValues:
      - Standard    # 15-month retention
      - High        # 3-month retention
      - VeryHigh    # 3-hour retention

Resources:
  HighResolutionMetric:
    Type: AWS::CloudWatch::Alarm
    Condition: UseStandardResolution
    Properties:
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Period: 60  # 1-minute period
      # High-resolution metrics (1-second) have shorter retention

Conditions:
  UseStandardResolution: !Equals [!Ref MetricResolution, Standard]
```

### Log Ingestion Constraints

```yaml
# Large log volumes can impact ingestion latency and query performance
Parameters:
  ExpectedLogVolumeGB:
    Type: Number
    Default: 10
    Description: Expected daily log volume in GB

  EnableLogCompression:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false
    Description: Enable gzip compression for logs

Resources:
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/application/${AWS::StackName}"
      # Consider volume when setting retention

  # CloudWatch Logs automatically handles large volumes
  # But may experience ingestion delays during spikes
```

### Metric Filter Constraints

```yaml
# Metric filters have limits on number and patterns
Parameters:
  MaxMetricFiltersPerLogGroup:
    Type: Number
    Default: 10
    MaxValue: 100  # AWS limit
    Description: Maximum metric filters per log group

Resources:
  # Complex filter patterns may fail to match
  ErrorFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: "[timestamp, request_id, event_type=ERROR, message]"
      MetricTransformations:
        - MetricName: ErrorCount
          MetricNamespace: !Sub "${AWS::StackName}/errors"

  # Simple filter patterns recommended
  SimpleErrorFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: "[..., event_type=ERROR]"
      MetricTransformations:
        - MetricName: SimpleErrorCount
```

## Best Practices to Avoid Constraints

### Use Composite Alarms

```yaml
# Combine multiple conditions instead of creating many individual alarms
Resources:
  HighCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: high-cpu
      MetricName: CPUUtilization
      Threshold: 80

  HighMemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: high-memory
      MetricName: MemoryUtilization
      Threshold: 80

  # Composite alarm reduces total alarm count
  SystemOverloadedComposite:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: system-overloaded
      AlarmRule: "ALARM(HighCpuAlarm) OR ALARM(HighMemoryAlarm)"
      AlarmActions:
        - !Ref AlarmTopic
```

### Optimize Dashboard Widgets

```yaml
# Combine multiple metrics in single widgets
Resources:
  OptimizedDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: |
        {
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "metrics": [
                  ["AWS/EC2", "CPUUtilization", "InstanceId", "i-123"],
                  [".", "NetworkIn", ".", "."],
                  [".", "NetworkOut", ".", "."]
                ],
                "stat": "Average"
              }
            }
            # 3 metrics in 1 widget instead of 3 widgets
          ]
        }
```

### Use Log Insights Efficiently

```yaml
# CloudWatch Logs Insights queries have costs
# Optimize queries to scan only necessary data

Resources:
  # Create saved queries to avoid repeated full scans
  EfficientQuery:
    Type: AWS::CloudWatch::QueryDefinition
    Properties:
      Name: !Sub "${AWS::StackName}-error-query"
      LogGroupNames:
        - !Ref ApplicationLogGroup
      QueryString: |
        fields @timestamp, @message
        | filter event_type = "ERROR"
        | stats count() by error_code
        | sort @timestamp desc
        | limit 20
```

### Monitor CloudWatch Costs

```yaml
# Set up budget alerts for CloudWatch spending
Resources:
  CloudWatchBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetLimit:
          Amount: 100
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          Service:
            - Amazon CloudWatch
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 80
          Subscribers:
            - SubscriptionType: EMAIL
              Address: !Ref BudgetEmailAddress

  # Alarm for budget threshold
  BudgetAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: cloudwatch-budget-alarm
      MetricName: EstimatedCharges
      Namespace: AWS/Billing
      Statistic: Maximum
      Period: 21600  # 6 hours
      EvaluationPeriods: 1
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
```
