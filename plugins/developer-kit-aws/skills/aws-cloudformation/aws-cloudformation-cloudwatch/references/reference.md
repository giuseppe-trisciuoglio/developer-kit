# AWS CloudFormation CloudWatch - Detailed Reference

## Table of Contents

- [CloudWatch Resources](#cloudwatch-resources)
- [Common Properties](#common-properties)
- [Alarm Configuration](#alarm-configuration)
- [Dashboard Widgets](#dashboard-widgets)
- [Log Group Configuration](#log-group-configuration)
- [Metric Properties](#metric-properties)

---

## CloudWatch Resources

### AWS::CloudWatch::Alarm

Main resource for creating CloudWatch alarms.

#### Main Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| AlarmName | String | No | Unique alarm name (max 255 chars) |
| AlarmDescription | String | No | Alarm description |
| MetricName | String | Yes | Metric name |
| Namespace | String | No | Metric namespace |
| Dimensions | List | No | Dimensions for the metric |
| Statistic | String | No | Statistic (SampleCount, Average, Sum, Minimum, Maximum) |
| ExtendedStatistic | String | No | Percentile statistic (e.g., p99) |
| Period | Number | No | Period in seconds (default: 300) |
| EvaluationPeriods | Number | Yes | Number of evaluation periods |
| Threshold | Number | Yes | Threshold for the alarm |
| ComparisonOperator | String | Yes | Comparison operator |
| TreatMissingData | String | No | How to treat missing data |
| AlarmActions | List | No | ARNs of actions to execute |
| InsufficientDataActions | List | No | Actions for insufficient data |
| OKActions | List | No | Actions when alarm returns to OK |

#### ComparisonOperator Values

```yaml
ComparisonOperator:
  - GreaterThanThreshold
  - GreaterThanOrEqualToThreshold
  - LessThanThreshold
  - LessThanOrEqualToThreshold
  - GreaterThanUpperBound
  - LessThanLowerBound
```

#### TreatMissingData Values

```yaml
TreatMissingData:
  # Treat as breaching (alarm goes to ALARM)
  - breaching
  # Treat as not breaching (alarm goes to OK)
  - notBreaching
  # Treat as missing (alarm goes to INSUFFICIENT_DATA)
  - missing
  # Maintain current state
  - ignore
```

#### Complete Example

```yaml
Resources:
  CompleteAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: production-error-alarm
      AlarmDescription: Alert on production errors exceeding threshold
      MetricName: Errors
      Namespace: MyApplication/Production
      Dimensions:
        - Name: Service
          Value: api-service
        - Name: Region
          Value: us-east-1
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      DatapointsToAlarm: 3
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref AlarmTopic
        - !Ref PagerDutyTopic
      InsufficientDataActions:
        - !Ref AlarmTopic
      OKActions:
        - !Ref RecoveryTopic
      Tags:
        - Key: Environment
          Value: production
        - Key: Severity
          Value: critical
```

---

### AWS::CloudWatch::CompositeAlarm

Combines multiple alarms into a single logical expression.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| AlarmName | String | Yes | Composite alarm name |
| AlarmDescription | String | No | Description |
| AlarmRule | String | Yes | Rule that combines other alarms |
| ActionsEnabled | Boolean | No | Whether actions are enabled |
| AlarmActions | List | No | Actions to execute |
| OKActions | List | No | Actions when OK |

#### AlarmRule Operators

```yaml
AlarmRule: !Or
  - !Ref Alarm1
  - !Ref Alarm2
  - !And
    - !Ref Alarm3
    - !Ref Alarm4
  - !Not
    - !Ref Alarm5
```

---

### AWS::CloudWatch::AnomalyDetector

Configures anomaly detection for metrics.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| MetricName | String | Yes | Metric name |
| Namespace | String | Yes | Metric namespace |
| Dimensions | List | No | Dimensions |
| Statistic | String | Yes | Statistic |
| Configuration | Configuration | No | Anomaly detector configuration |

#### Configuration

```yaml
Configuration:
  ExcludedTimeRanges:
    - StartTime: "2023-12-25T00:00:00"
      EndTime: "2023-12-26T00:00:00"
  MetricTimeZone: UTC
```

---

### AWS::CloudWatch::Dashboard

Creates CloudWatch dashboards for metric visualization.

#### DashboardBody Structure

```yaml
DashboardBody:
  "start": "-PT6H"
  "end": "P0D"
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Widget Title",
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "metrics": [
          ["Namespace", "MetricName", "Dimension1", "Value1"],
          [".", ".", ".", "."]
        ],
        "period": 300,
        "stat": "Sum",
        "annotations": {
          "horizontal": [
            {
              "value": 100,
              "label": "Threshold",
              "color": "#ff7f0e"
            }
          ]
        }
      }
    }
  ]
```

#### View Types

```yaml
view:
  - timeSeries    # Line chart
  - bar           # Bar chart
  - pie           # Pie chart
  - singleValue   # Single value display
  - table         # Tabular view
```

---

### AWS::Logs::LogGroup

Creates CloudWatch log groups.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| LogGroupName | String | Yes | Log group name |
| RetentionInDays | Number | No | Retention days (1-3650) |
| KmsKeyId | String | No | KMS key ARN for encryption |
| Tags | List | No | Tags for the log group |

#### Retention Values

```yaml
RetentionInDays:
  - 1        # 1 day
  - 3        # 3 days
  - 5        # 5 days
  - 7        # 1 week
  - 14       # 2 weeks
  - 30       # 1 month
  - 60       # 2 months
  - 90       # 3 months
  - 120      # 4 months
  - 150      # 5 months
  - 180      # 6 months
  - 365      # 1 year
  - 400      # 13 months
  - 545      # 18 months
  - 731      # 2 years
  - 1095     # 3 years
  - 1827     # 5 years
  - 2190     # 6 years
  - 2555     # 7 years
  - 2922     # 8 years
  - 3285     # 9 years
  - 3650     # 10 years
```

---

### AWS::Logs::MetricFilter

Extracts metrics from log patterns.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| FilterPattern | String | Yes | Pattern to filter logs |
| LogGroupName | String | Yes | Log group name |
| MetricTransformations | List | Yes | Metric transformations |

#### MetricTransformation

```yaml
MetricTransformations:
  - MetricValue: "1"
    MetricNamespace: MyApp/Logs
    MetricName: ErrorCount
    DefaultValue: 0.0
```

---

### AWS::Logs::SubscriptionFilter

Sends logs to external destinations (Kinesis, Lambda, ES).

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| DestinationArn | String | Yes | Destination ARN |
| FilterPattern | String | Yes | Pattern to filter logs |
| LogGroupName | String | Yes | Log group name |
| RoleArn | String | Yes | Role ARN for access |

---

### AWS::Logs::QueryDefinition

Saves Log Insights queries.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| Name | String | Yes | Query name |
| QueryString | String | Yes | Log Insights query |

---

### AWS::Synthetics::Canary

Creates synthesized canaries for synthetic monitoring.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| Name | String | Yes | Canary name |
| ArtifactS3Location | String | Yes | S3 location for artifacts |
| Code | Code | Yes | Code configuration |
| ExecutionRoleArn | String | Yes | Role ARN |
| RuntimeVersion | String | Yes | Runtime version |
| Schedule | Schedule | Yes | Execution schedule |
| SuccessRetentionPeriodInDays | Number | No | Retention for successes |
| FailureRetentionPeriodInDays | Number | No | Retention for failures |

#### Runtime Versions

```yaml
RuntimeVersion:
  - syn-python-selenium-1.1
  - syn-python-selenium-1.0
  - syn-nodejs-puppeteer-6.0
  - syn-nodejs-puppeteer-5.0
  - syn-nodejs-puppeteer-4.0
```

#### Schedule Expression

```yaml
Schedule:
  Expression: "rate(5 minutes)"
  DurationInSeconds: 120
```

---

### AWS::CloudWatch::ServiceLevelIndicator

Defines SLI for service health.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| Name | String | Yes | SLI name |
| Monitor | Monitor | Yes | Reference monitor |
| Metric | Metric | Yes | Metric configuration |
| OperationName | String | No | Operation name |

---

### AWS::CloudWatch::ServiceLevelObjective

Defines SLO based on SLI.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| Name | String | Yes | SLO name |
| Description | String | No | Description |
| Monitor | Monitor | Yes | Reference monitor |
| SliMetric | SliMetric | Yes | SLI metric |
| Target | Target | Yes | Objective target |
| Goal | Goal | No | Goal configuration |

---

### AWS::CloudWatch::ApplicationMonitor

Configures Application Signals for APM.

#### Properties

| Property | Type | Required | Description |
|-----------|------|-----------|-------------|
| MonitorName | String | Yes | Monitor name |
| MonitorType | String | Yes | Type (CW_MONITOR) |
| Telemetry | List | No | Telemetry configuration |

---

## Common Properties

### Dimensions

```yaml
Dimensions:
  - Name: DimensionName1
    Value: DimensionValue1
  - Name: DimensionName2
    Value: DimensionValue2
```

### Tags

```yaml
Tags:
  - Key: Environment
    Value: production
  - Key: Service
    Value: api
  - Key: CostCenter
    Value: engineering
```

---

## Alarm Configuration

### Statistic Types

```yaml
Statistic:
  - SampleCount    # Number of datapoints
  - Average        # Average
  - Sum            # Sum
  - Minimum        # Minimum
  - Maximum        # Maximum
```

### Extended Statistics

```yaml
ExtendedStatistic: "p99"        # 99th percentile
ExtendedStatistic: "p95"        # 95th percentile
ExtendedStatistic: "p50"        # Median
ExtendedStatistic: "tc99"       # Trimmed mean 99%
ExtendedStatistic: "wm99"       # Winsorized mean 99%
```

### Metric Selectors

```yaml
# Single metric
MetricName: Errors
Namespace: AWS/Lambda

# Multiple metrics with dimensions
metrics:
  - ["AWS/Lambda", "Invocations", "FunctionName", "MyFunction"]
  - [".", "Errors", ".", "."]
  - [".", "Duration", ".", ".", {"stat": "p99"}]

# Math expression
metrics:
  - ["AWS/Lambda", "Errors", "FunctionName", "MyFunction"]
  - [".", "Invocations", ".", "."]
  - expression: Errors / Invocations * 100
    label: Error Rate (%)
    id: errorRate
```

---

## Dashboard Widgets

### Metric Widget

```yaml
{
  "type": "metric",
  "x": 0,
  "y": 0,
  "width": 12,
  "height": 6,
  "properties": {
    "title": "API Gateway Metrics",
    "view": "timeSeries",
    "stacked": false,
    "region": "us-east-1",
    "metrics": [
      ["AWS/ApiGateway", "Count", "ApiName", "MyApi", "Stage", "prod"]
    ],
    "period": 300,
    "stat": "Sum",
    "legend": {
      "position": "bottom"
    },
    "liveData": true,
    "annotations": {
      "horizontal": [
        {
          "value": 1000,
          "label": "Warning Threshold",
          "color": "#ff7f0e"
        }
      ],
      "vertical": [
        {
          "value": "2023-12-31T00:00:00Z",
          "label": "Deployment",
          "color": "#2ca02c"
        }
      ]
    }
  }
}
```

### Text Widget

```yaml
{
  "type": "text",
  "x": 0,
  "y": 0,
  "width": 12,
  "height": 3,
  "properties": {
    "markdown": "# Production Dashboard\nLast updated: `date`"
  }
}
```

### Log Widget

```yaml
{
  "type": "log",
  "x": 0,
  "y": 12,
  "width": 24,
  "height": 6,
  "properties": {
    "title": "Application Errors",
    "view": "table",
    "region": "us-east-1",
    "logGroupName": "/aws/applications/prod/app",
    "timeRange": {
      "type": "relative",
      "from": 3600
    },
    "filterPattern": "ERROR | WARN",
    "columns": ["@timestamp", "@message", "@logStream"]
  }
}
```

### Alarm Status Widget

```yaml
{
  "type": "alarm",
  "x": 0,
  "y": 0,
  "width": 6,
  "height": 6,
  "properties": {
    "title": "Alarm Status",
    "alarms": [
      "arn:aws:cloudwatch:us-east-1:123456789:alarm:ErrorAlarm",
      "arn:aws:cloudwatch:us-east-1:123456789:alarm:LatencyAlarm"
    ]
  }
}
```

---

## Log Group Configuration

### Retention Policy Examples

```yaml
# Development - short retention
DevLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /aws/applications/dev/app
    RetentionInDays: 7

# Production - long retention
ProdLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /aws/applications/prod/app
    RetentionInDays: 90
    KmsKeyId: !Ref ProdLogKmsKey
```

### Encryption Configuration

```yaml
Resources:
  EncryptedLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/applications/prod/encrypted
      RetentionInDays: 30
      KmsKeyId: !Ref LogEncryptionKey

  LogEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Key for log encryption
      EnableKeyRotation: true
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: logs.us-east-1.amazonaws.com
            Action:
              - kms:Encrypt*
              - kms:Decrypt*
              - kms:ReEncrypt*
              - kms:GenerateDataKey*
              - kms:Describe*
            Resource: "*"
            Condition:
              ArnEquals:
                aws:SourceArn: !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:*"
```

---

## Metric Properties

### Common Namespace Patterns

```yaml
Namespace:
  # AWS services
  - AWS/Lambda
  - AWS/ApiGateway
  - AWS/EC2
  - AWS/RDS
  - AWS/ECS
  - AWS/EKS
  - AWS/DynamoDB
  - AWS/S3
  - AWS/SNS
  - AWS/SQS
  - AWS/ElastiCache
  - AWS/ElasticLoadBalancing

  # Custom namespaces
  - MyApplication/Production
  - MyService/Metrics
  - CustomMetrics/Business
```

### Common Metric Names

```yaml
MetricName:
  # Lambda
  - Invocations
  - Errors
  - Throttles
  - Duration
  - ConcurrentExecutions
  - UnreservedConcurrentExecutions

  # API Gateway
  - Count
  - Latency
  - 4XXError
  - 5XXError
  - IntegrationLatency
  - CacheHitCount
  - CacheMissCount

  # EC2
  - CPUUtilization
  - NetworkIn
  - NetworkOut
  - DiskReadOps
  - DiskWriteOps
  - StatusCheckFailed

  # RDS
  - DatabaseConnections
  - ReadLatency
  - WriteLatency
  - ReadIOPS
  - WriteIOPS
  - FreeStorageSpace
  - CPUUtilization

  # Custom
  - RequestCount
  - ErrorCount
  - SuccessCount
  - Latency
  - ResponseSize
  - QueueSize
  - ProcessingTime
```

---

## Nested Stack References

### Cross-Stack Import

```yaml
# Import from network stack
Parameters:
  NetworkStackName:
    Type: String
    Description: Network stack name

Resources:
  # Import VPC ID
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      VpcId: !ImportValue
        !Sub "${NetworkStackName}-VPCId"
      GroupDescription: Security group for monitoring

# Import log group name
LogGroupName:
  Fn::ImportValue:
    !Sub "${MonitoringStackName}-LogGroupName"
```

---

## Condition Functions

### Intrinsic Functions

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  IsStaging: !Equals [!Ref Environment, staging]
  EnableAnomaly: !Not [!Equals [!Ref Environment, dev]]
  CreateAlarms: !Or [!Equals [!Ref Environment, staging], !Equals [!Ref Environment, production]]

Resources:
  ProdAlarm:
    Condition: IsProduction
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: prod-errors
      MetricName: Errors
      Namespace: MyApp
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 3
      Threshold: 1
      ComparisonOperator: GreaterThanThreshold
```

---

## Best Practices Summary

### Alarm Configuration

| Scenario | Period | EvaluationPeriods | DatapointsToAlarm |
|----------|--------|-------------------|-------------------|
| High traffic metrics | 60s | 5 | 3 |
| Latency (P99) | 60s | 3 | 2 |
| Error rate | 60s | 5 | 3 |
| Resource utilization | 300s | 3 | 2 |
| Cost metrics | 3600s | 2 | 1 |

### Log Retention

| Log Type | Retention | Encryption |
|----------|-----------|------------|
| Application logs | 30 days | Required |
| Audit logs | 365 days | Required |
| Lambda logs | 30 days | Optional |
| VPC flow logs | 90 days | Recommended |
| Security logs | 365+ days | Required |

### Dashboard Design

- Use 6-hour default time range for operational dashboards
- Group related metrics in widgets
- Add threshold annotations for critical values
- Use alarm status widgets for quick health check
- Limit widgets per dashboard for performance
