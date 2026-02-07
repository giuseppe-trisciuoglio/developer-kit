# AWS CloudFormation CloudWatch - Esempi Completi

## Indice

- [Esempio 1: Stack di Monitoring Completo](#esempio-1-stack-di-monitoring-completo)
- [Esempio 2: Multi-Region Dashboard](#esempio-2-multi-region-dashboard)
- [Esempio 3: Application Performance Monitoring](#esempio-3-application-performance-monitoring)
- [Esempio 4: Cross-Account Log Aggregation](#esempio-4-cross-account-log-aggregation)
- [Esempio 5: Synthesized Canary Monitoring](#esempio-5-synthesized-canary-monitoring)
- [Esempio 6: SLO/SLI Configuration](#esempio-6-slosli-configuration)

---

## Esempio 1: Stack di Monitoring Completo

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Complete CloudWatch monitoring stack for production application

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: Environment Settings
        Parameters:
          - Environment
          - ApplicationName
      - Label:
          default: Alarm Thresholds
        Parameters:
          - ErrorRateThreshold
          - LatencyThresholdMs
          - CpuUtilizationThreshold
      - Label:
          default: Notification Settings
        Parameters:
          - AlarmTopicArn
          - SeverityLevel

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production
    Description: Deployment environment

  ApplicationName:
    Type: String
    Default: my-application
    Description: Application name for resource naming

  ErrorRateThreshold:
    Type: Number
    Default: 5
    Description: Error rate threshold percentage
    MinValue: 1
    MaxValue: 100

  LatencyThresholdMs:
    Type: Number
    Default: 1000
    Description: P99 latency threshold in milliseconds
    MinValue: 100
    MaxValue: 60000

  CpuUtilizationThreshold:
    Type: Number
    Default: 80
    Description: CPU utilization threshold percentage
    MinValue: 10
    MaxValue: 100

  AlarmTopicArn:
    Type: String
    Description: SNS topic ARN for alarm notifications
    ConstraintDescription: Must be a valid SNS topic ARN

  SeverityLevel:
    Type: String
    Default: high
    AllowedValues:
      - low
      - medium
      - high
      - critical

Mappings:
  EnvironmentSettings:
    dev:
      LogRetentionDays: 7
      EvaluationPeriods: 3
      DatapointsToAlarm: 2
      AnomalyDetectionEnabled: false
    staging:
      LogRetentionDays: 14
      EvaluationPeriods: 5
      DatapointsToAlarm: 3
      AnomalyDetectionEnabled: true
    production:
      LogRetentionDays: 30
      EvaluationPeriods: 5
      DatapointsToAlarm: 3
      AnomalyDetectionEnabled: true

Resources:
  # ==================== LOG GROUPS ====================

  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/applications/${Environment}/${ApplicationName}"
      RetentionInDays: !FindInMap [EnvironmentSettings, !Ref Environment, LogRetentionDays]
      KmsKeyId: !Ref LogEncryptionKey

  LambdaLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/lambda/${ApplicationName}"
      RetentionInDays: !FindInMap [EnvironmentSettings, !Ref Environment, LogRetentionDays]
      KmsKeyId: !Ref LogEncryptionKey

  ApiLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/api-gateway/${ApplicationName}"
      RetentionInDays: !FindInMap [EnvironmentSettings, !Ref Environment, LogRetentionDays]
      KmsKeyId: !Ref LogEncryptionKey

  # ==================== METRIC FILTERS ====================

  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: '[level="ERROR" || level="error" || level="Error"]'
      LogGroupName: !Ref ApplicationLogGroup
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${ApplicationName}/${Environment}"
          MetricName: LogErrorCount

  WarningMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: '[level="WARN" || level="warning" || level="Warning"]'
      LogGroupName: !Ref ApplicationLogGroup
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${ApplicationName}/${Environment}"
          MetricName: LogWarningCount

  # ==================== LAMBDA ALARMS ====================

  LambdaErrorsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ApplicationName}-${Environment}-lambda-errors"
      AlarmDescription: !Sub "Alert when Lambda errors exceed ${ErrorRateThreshold}% threshold"
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunctionName
      Statistic: Sum
      Period: 60
      EvaluationPeriods: !FindInMap [EnvironmentSettings, !Ref Environment, EvaluationPeriods]
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn
      InsufficientDataActions:
        - !Ref AlarmTopicArn

  LambdaLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ApplicationName}-${Environment}-lambda-latency"
      AlarmDescription: !Sub "Alert when Lambda P99 latency exceeds ${LatencyThresholdMs}ms"
      MetricName: Duration
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunctionName
      Statistic: p99
      Period: 60
      EvaluationPeriods: !FindInMap [EnvironmentSettings, !Ref Environment, EvaluationPeriods]
      Threshold: !Ref LatencyThresholdMs
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  LambdaThrottlesAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ApplicationName}-${Environment}-lambda-throttles"
      AlarmDescription: Alert when Lambda throttling occurs
      MetricName: Throttles
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunctionName
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 3
      Threshold: 2
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  # ==================== API GATEWAY ALARMS ====================

  Api5xxErrorsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ApplicationName}-${Environment}-api-5xx"
      AlarmDescription: Alert on API Gateway 5xx errors
      MetricName: 5XXError
      Namespace: AWS/ApiGateway
      Dimensions:
        - Name: ApiName
          Value: !Ref ApiName
        - Name: Stage
          Value: !Ref ApiStage
      Statistic: Sum
      Period: 60
      EvaluationPeriods: !FindInMap [EnvironmentSettings, !Ref Environment, EvaluationPeriods]
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  ApiLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ApplicationName}-${Environment}-api-latency"
      AlarmDescription: Alert on API Gateway high latency
      MetricName: Latency
      Namespace: AWS/ApiGateway
      Dimensions:
        - Name: ApiName
          Value: !Ref ApiName
        - Name: Stage
          Value: !Ref ApiStage
      Statistic: p99
      Period: 60
      EvaluationPeriods: 3
      Threshold: 3000
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  # ==================== COMPOSITE ALARMS ====================

  ApplicationHealthAlarm:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: !Sub "${ApplicationName}-${Environment}-health"
      AlarmDescription: Composite alarm for overall application health
      AlarmRule: !Or
        - !Ref LambdaErrorsAlarm
        - !Ref LambdaThrottlesAlarm
        - !Ref Api5xxErrorsAlarm
      ActionsEnabled: true
      AlarmActions:
        - !Ref AlarmTopicArn
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Application
          Value: !Ref ApplicationName
        - Key: Severity
          Value: !Ref SeverityLevel

  # ==================== ANOMALY DETECTION ====================

  RequestRateAnomalyDetector:
    Type: AWS::CloudWatch::AnomalyDetector
    Condition: EnableAnomalyDetection
    Properties:
      MetricName: Invocations
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunctionName
      Statistic: Sum
      Configuration:
        MetricTimeZone: UTC

  AnomalyAlarm:
    Type: AWS::CloudWatch::Alarm
    Condition: EnableAnomalyDetection
    Properties:
      AlarmName: !Sub "${ApplicationName}-${Environment}-anomaly"
      AlarmDescription: Alert on anomalous metric behavior
      MetricName: Invocations
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunctionName
      AnomalyDetectorConfiguration:
        ExcludeTimeRange:
          StartTime: "2023-12-25T00:00:00Z"
          EndTime: "2023-12-26T00:00:00Z"
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 2
      ComparisonOperator: GreaterThanUpperThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  # ==================== DASHBOARD ====================

  MainDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${ApplicationName}-${Environment}-dashboard"
      DashboardBody: !Sub |
        {
          "start": "-PT6H",
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 2,
              "properties": {
                "markdown": "# ${ApplicationName} - ${Environment} Dashboard\n## Last Updated: `date`"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Lambda Invocations",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "${LambdaFunctionName}"],
                  ["AWS/Lambda", "Errors", ".", "."],
                  ["AWS/Lambda", "Throttles", ".", "."]
                ],
                "period": 60,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Lambda Duration (P99)",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/Lambda", "Duration", "FunctionName", "${LambdaFunctionName}", {"stat": "p99"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "API Gateway Requests",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/ApiGateway", "Count", "ApiName", "${ApiName}", "Stage", "${ApiStage}"],
                  ["AWS/ApiGateway", "4XXError", ".", ".", ".", "."],
                  ["AWS/ApiGateway", "5XXError", ".", ".", ".", "."]
                ],
                "period": 300,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "API Gateway Latency",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/ApiGateway", "Latency", "ApiName", "${ApiName}", "Stage", "${ApiStage}", {"stat": "p99"}]
                ],
                "period": 300
              }
            },
            {
              "type": "log",
              "x": 0,
              "y": 14,
              "width": 24,
              "height": 6,
              "properties": {
                "title": "Application Errors",
                "view": "table",
                "region": "${AWS::Region}",
                "logGroupName": "${ApplicationLogGroup}",
                "timeRange": {
                  "type": "relative",
                  "from": 3600
                },
                "filterPattern": "ERROR",
                "columns": ["@timestamp", "@message", "@logStream"]
              }
            },
            {
              "type": "alarm",
              "x": 0,
              "y": 20,
              "width": 24,
              "height": 4,
              "properties": {
                "title": "Alarm Status",
                "alarms": [
                  "${LambdaErrorsAlarm.Arn}",
                  "${LambdaLatencyAlarm.Arn}",
                  "${Api5xxErrorsAlarm.Arn}",
                  "${ApplicationHealthAlarm.Arn}"
                ]
              }
            }
          ]
        }

  # ==================== KMS KEY ====================

  LogEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: !Sub "KMS key for ${ApplicationName} log encryption"
      EnableKeyRotation: true
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: Enable CloudWatch Logs access
            Effect: Allow
            Principal:
              Service: !Sub "logs.${AWS::Region}.amazonaws.com"
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

  LogEncryptionKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub "alias/${ApplicationName}-${Environment}-log-key"
      TargetKeyId: !Ref LogEncryptionKey

Conditions:
  EnableAnomalyDetection: !Equals [!Ref Environment, production]

Outputs:
  LogGroupNames:
    Description: Names of created log groups
    Value: !Sub "${ApplicationLogGroup},${LambdaLogGroup},${ApiLogGroup}"
    Export:
      Name: !Sub "${AWS::StackName}-LogGroupNames"

  DashboardUrl:
    Description: URL to the CloudWatch dashboard
    Value: !Sub "https://${AWS::Region}.console.aws.amazon.com/cloudwatch/home?region=${AWS::Region}#dashboards:name=${ApplicationName}-${Environment}-dashboard"
```

---

## Esempio 2: Multi-Region Dashboard

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Multi-region CloudWatch dashboard for global applications

Parameters:
  ApplicationName:
    Type: String
    Default: global-application
    Description: Application name

  PrimaryRegion:
    Type: String
    Default: us-east-1
    Description: Primary region

  SecondaryRegion:
    Type: String
    Default: eu-west-1
    Description: Secondary region

Resources:
  MultiRegionDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${ApplicationName}-global"
      DashboardBody: !Sub |
        {
          "start": "-PT4H",
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 2,
              "properties": {
                "markdown": "# Global Application Dashboard\n## Multi-Region Monitoring"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "US-East-1 Request Rate",
                "view": "timeSeries",
                "region": "${PrimaryRegion}",
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "us-function"],
                  ["AWS/Lambda", "Errors", ".", "."]
                ],
                "period": 60,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "EU-West-1 Request Rate",
                "view": "timeSeries",
                "region": "${SecondaryRegion}",
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "eu-function"],
                  ["AWS/Lambda", "Errors", ".", "."]
                ],
                "period": 60,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "US-East-1 Latency P99",
                "view": "timeSeries",
                "region": "${PrimaryRegion}",
                "metrics": [
                  ["AWS/Lambda", "Duration", "FunctionName", "us-function", {"stat": "p99"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "EU-West-1 Latency P99",
                "view": "timeSeries",
                "region": "${SecondaryRegion}",
                "metrics": [
                  ["AWS/Lambda", "Duration", "FunctionName", "eu-function", {"stat": "p99"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 14,
              "width": 24,
              "height": 6,
              "properties": {
                "title": "Combined Error Rate",
                "view": "timeSeries",
                "region": "${PrimaryRegion}",
                "metrics": [
                  ["AWS/Lambda", "Errors", "FunctionName", "us-function"],
                  ["AWS/Lambda", "Invocations", "FunctionName", "us-function"],
                  {
                    "expression": "m1 / m2 * 100",
                    "label": "US Error Rate %",
                    "id": "usErrorRate"
                  },
                  ["AWS/Lambda", "Errors", "FunctionName", "eu-function"],
                  ["AWS/Lambda", "Invocations", "FunctionName", "eu-function"],
                  {
                    "expression": "m4 / m5 * 100",
                    "label": "EU Error Rate %",
                    "id": "euErrorRate"
                  }
                ],
                "period": 60
              }
            }
          ]
        }
```

---

## Esempio 3: Application Performance Monitoring

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Application Performance Monitoring with CloudWatch

Parameters:
  ServiceName:
    Type: String
    Default: api-service
    Description: Name of the service

  Environment:
    Type: String
    Default: production
    Description: Environment name

Resources:
  # Custom metrics for APM
  ApiGatewayMetricAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ServiceName}-${Environment}-apm-errors"
      AlarmDescription: APM - High error rate detected
      MetricName: RequestErrors
      Namespace: !Sub "APM/${ServiceName}"
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
        - Name: Environment
          Value: !Ref Environment
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 3
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold

  LatencyPercentileAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ServiceName}-${Environment}-apm-latency-p99"
      AlarmDescription: APM - P99 latency exceeds threshold
      MetricName: RequestLatency
      Namespace: !Sub "APM/${ServiceName}"
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
      ExtendedStatistic: "p99"
      Period: 60
      EvaluationPeriods: 3
      Threshold: 2000
      ComparisonOperator: GreaterThanThreshold

  ThroughputAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ServiceName}-${Environment}-apm-throughput"
      AlarmDescription: APM - Low throughput detected
      MetricName: RequestCount
      Namespace: !Sub "APM/${ServiceName}"
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 4
      Threshold: 100
      ComparisonOperator: LessThanThreshold

  ApmDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${ServiceName}-${Environment}-apm"
      DashboardBody: !Sub |
        {
          "start": "-PT1H",
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 8,
              "height": 6,
              "properties": {
                "title": "Request Count",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["APM/${ServiceName}", "RequestCount", "Service", "${ServiceName}", "Environment", "${Environment}"]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 8,
              "y": 0,
              "width": 8,
              "height": 6,
              "properties": {
                "title": "Error Count",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["APM/${ServiceName}", "RequestErrors", "Service", "${ServiceName}"]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 16,
              "y": 0,
              "width": 8,
              "height": 6,
              "properties": {
                "title": "Error Rate %",
                "view": "singleValue",
                "region": "${AWS::Region}",
                "metrics": [
                  ["APM/${ServiceName}", "RequestErrors", "Service", "${ServiceName}"],
                  ["APM/${ServiceName}", "RequestCount", "Service", "${ServiceName}"]
                ],
                "period": 300,
                "stat": "Average"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 6,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Latency Distribution",
                "view": "bar",
                "region": "${AWS::Region}",
                "metrics": [
                  ["APM/${ServiceName}", "RequestLatency", "Service", "${ServiceName}", {"stat": "p50"}],
                  [".", ".", ".", ".", {"stat": "p90"}],
                  [".", ".", ".", ".", {"stat": "p95"}],
                  [".", ".", ".", ".", {"stat": "p99"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 6,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Latency Over Time",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["APM/${ServiceName}", "RequestLatency", "Service", "${ServiceName}", {"stat": "p50"}],
                  [".", ".", ".", ".", {"stat": "p99"}]
                ],
                "period": 60
              }
            }
          ]
        }
```

---

## Esempio 4: Cross-Account Log Aggregation

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Cross-account log aggregation setup

Parameters:
  SourceAccountId:
    Type: String
    Description: Source AWS account ID for log aggregation

  SourceRoleArn:
    Type: String
    Description: IAM role ARN in source account for log access

  DestinationLogGroupPrefix:
    Type: String
    Default: /aws/applications
    Description: Prefix for destination log groups

Resources:
  # Destination log group
  AggregatedLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "${DestinationLogGroupPrefix}/aggregated"
      RetentionInDays: 30
      KmsKeyId: !Ref LogEncryptionKey

  # Subscription filter to Kinesis Data Stream
  LogSubscriptionKinesis:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      DestinationArn: !GetAtt KinesisStream.Arn
      FilterPattern: '[timestamp=*Z, level, message]'
      LogGroupName: !Ref AggregatedLogGroup
      RoleArn: !GetAtt SubscriptionRole.Arn

  # Kinesis Data Stream for log processing
  KinesisStream:
    Type: AWS::Kinesis::Stream
    Properties:
      Name: !Sub "${AWS::StackName}-log-stream"
      ShardCount: 1
      StreamEncryption:
        EncryptionType: KMS
        KeyId: !Ref StreamEncryptionKey

  # IAM role for subscription
  SubscriptionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-log-subscription-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: logs.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-kinesis-write"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - kinesis:PutRecord
                  - kinesis:PutRecords
                Resource: !GetAtt KinesisStream.Arn

  # Cross-account permission
  CrossAccountPermission:
    Type: AWS::Logs::ResourcePolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-cross-account-policy"
      PolicyDocument: !Sub |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "AWS": "${SourceAccountId}"
              },
              "Action": [
                "logs:CreateExportTask",
                "logs:PutResourcePolicy",
                "logs:DescribeResourcePolicies",
                "logs:DescribeLogGroups"
              ],
              "Resource": "*"
            },
            {
              "Effect": "Allow",
              "Principal": {
                "AWS": "${SourceAccountId}"
              },
              "Action": [
                "logs:DescribeLogStreams",
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
              ],
              "Resource": "${AggregatedLogGroup.Arn}"
            }
          ]
        }

  # Metric filter for aggregated logs
  AggregatedErrorFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: 'ERROR'
      LogGroupName: !Ref AggregatedLogGroup
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "CrossAccount/${AWS::StackName}"
          MetricName: AggregatedErrors

  # Dashboard for aggregated logs
  AggregatedDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${AWS::StackName}-aggregated"
      DashboardBody: |
        {
          "start": "-PT1H",
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Aggregated Error Count",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["CrossAccount/${AWS::StackName}", "AggregatedErrors"]
                ],
                "period": 60,
                "stat": "Sum"
              }
            },
            {
              "type": "log",
              "x": 12,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Recent Errors",
                "view": "table",
                "region": "${AWS::Region}",
                "logGroupName": "${AggregatedLogGroup}",
                "timeRange": {
                  "type": "relative",
                  "from": 3600
                },
                "filterPattern": "ERROR"
              }
            }
          ]
        }

  LogEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for aggregated log encryption
      EnableKeyRotation: true
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: logs.amazonaws.com
            Action:
              - kms:Encrypt*
              - kms:Decrypt*
              - kms:GenerateDataKey*
            Resource: "*"

  StreamEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for Kinesis stream encryption
      EnableKeyRotation: true
```

---

## Esempio 5: Synthesized Canary Monitoring

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Synthesized canary monitoring for API endpoints

Parameters:
  EndpointUrl:
    Type: String
    Description: URL to monitor
    Default: https://api.example.com/health

  CanarySchedule:
    Type: String
    Default: rate(5 minutes)
    Description: Schedule expression

  CanaryName:
    Type: String
    Default: api-health-check
    Description: Name for the canary

Resources:
  # Canary execution role
  CanaryRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${CanaryName}-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: synthetics.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchSyntheticsFullAccess

  # S3 bucket for canary artifacts
  CanaryArtifactsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${CanaryName}-artifacts-${AWS::AccountId}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

  # Health check canary
  HealthCanary:
    Type: AWS::Synthetics::Canary
    Properties:
      Name: !Sub "${CanaryName}-health"
      ArtifactS3Location: !Sub "s3://${CanaryArtifactsBucket}/${CanaryName}"
      Code:
        S3Bucket: !Ref CanaryCodeBucket
        S3Key: canary/health-check.zip
        Handler: healthCheck.handler
      ExecutionRoleArn: !GetAtt CanaryRole.Arn
      RuntimeVersion: syn-python-selenium-1.1
      Schedule:
        Expression: !Ref CanarySchedule
        DurationInSeconds: 60
      SuccessRetentionPeriodInDays: 31
      FailureRetentionPeriodInDays: 31
      Tags:
        - Key: Environment
          Value: production
        - Key: MonitoringType
          Value: health-check

  # API endpoint canary
  ApiCanary:
    Type: AWS::Synthetics::Canary
    Properties:
      Name: !Sub "${CanaryName}-api"
      ArtifactS3Location: !Sub "s3://${CanaryArtifactsBucket}/${CanaryName}-api"
      Code:
        S3Bucket: !Ref CanaryCodeBucket
        S3Key: canary/api-check.zip
        Handler: apiCheck.handler
      ExecutionRoleArn: !GetAtt CanaryRole.Arn
      RuntimeVersion: syn-python-selenium-1.1
      Schedule:
        Expression: "rate(1 minute)"
        DurationInSeconds: 120
      SuccessRetentionPeriodInDays: 31
      FailureRetentionPeriodInDays: 31
      Tags:
        - Key: Environment
          Value: production
        - Key: MonitoringType
          Value: api-check

  # Canary failure alarm
  CanaryFailureAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${CanaryName}-failed"
      AlarmDescription: Alert when canary health check fails
      MetricName: Failed
      Namespace: AWS/Synthetics
      Dimensions:
        - Name: CanaryName
          Value: !Ref HealthCanary
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  # Canary latency alarm
  CanaryLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${CanaryName}-slow"
      AlarmDescription: Alert when canary latency is high
      MetricName: Duration
      Namespace: AWS/Synthetics
      Dimensions:
        - Name: CanaryName
          Value: !Ref HealthCanary
      Statistic: p99
      Period: 300
      EvaluationPeriods: 3
      Threshold: 5000
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  # Canary availability alarm
  CanaryAvailabilityAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${CanaryName}-availability"
      AlarmDescription: Alert on low canary availability
      MetricName: SuccessPercent
      Namespace: AWS/Synthetics
      Dimensions:
        - Name: CanaryName
          Value: !Ref HealthCanary
      Statistic: Average
      Period: 300
      EvaluationPeriods: 12
      Threshold: 95
      ComparisonOperator: LessThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  # Dashboard for canaries
  CanaryDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${CanaryName}-dashboard"
      DashboardBody: !Sub |
        {
          "start": "-PT24H",
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 2,
              "properties": {
                "markdown": "# Synthesized Canaries Dashboard\n## ${EndpointUrl}"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Canary Success/Failures",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/Synthetics", "Success", "CanaryName", "${HealthCanary}"],
                  ["AWS/Synthetics", "Failed", ".", "."]
                ],
                "period": 60,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Canary Latency",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/Synthetics", "Duration", "CanaryName", "${HealthCanary}", {"stat": "p99"}],
                  [".", ".", ".", ".", {"stat": "Average"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Availability %",
                "view": "singleValue",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/Synthetics", "SuccessPercent", "CanaryName", "${HealthCanary}"]
                ],
                "period": 300,
                "stat": "Average"
              }
            },
            {
              "type": "alarm",
              "x": 12,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Alarm Status",
                "alarms": [
                  "${CanaryFailureAlarm.Arn}",
                  "${CanaryLatencyAlarm.Arn}",
                  "${CanaryAvailabilityAlarm.Arn}"
                ]
              }
            }
          ]
        }
```

---

## Esempio 6: SLO/SLI Configuration

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Service Level Objectives configuration with CloudWatch

Parameters:
  ServiceName:
    Type: String
    Default: api-service
    Description: Name of the service

  Environment:
    Type: String
    Default: production
    Description: Environment name

  AvailabilityTarget:
    Type: Number
    Default: 99.9
    Description: Availability target percentage

  LatencyTarget:
    Type: Number
    Default: 500
    Description: Latency target in milliseconds

Resources:
  # SLI for availability
  AvailabilitySLI:
    Type: AWS::CloudWatch::ServiceLevelIndicator
    Properties:
      Name: !Sub "${ServiceName}-${Environment}-availability"
      Monitor:
        MonitorName: !Sub "${ServiceName}-monitor"
      Metric:
        MetricName: Availability
        Namespace: !Sub "SLO/${ServiceName}"
        Dimensions:
          - Name: Service
            Value: !Ref ServiceName
          - Name: Environment
            Value: !Ref Environment
      OperationName: AllOperations

  # SLI for latency
  LatencySLI:
    Type: AWS::CloudWatch::ServiceLevelIndicator
    Properties:
      Name: !Sub "${ServiceName}-${Environment}-latency"
      Monitor:
        MonitorName: !Sub "${ServiceName}-monitor"
      Metric:
        MetricName: Latency
        Namespace: !Sub "SLO/${ServiceName}"
        Dimensions:
          - Name: Service
            Value: !Ref ServiceName
      OperationName: GetItem
      AccountId: !Ref AWS::AccountId

  # SLO for availability
  AvailabilitySLO:
    Type: AWS::CloudWatch::ServiceLevelObjective
    Properties:
      Name: !Sub "${ServiceName}-${Environment}-availability-slo"
      Description: Availability SLO for ${ServiceName}
      Monitor:
        MonitorName: !Sub "${ServiceName}-monitor"
      SliMetric:
        MetricName: Availability
        Namespace: !Sub "SLO/${ServiceName}"
        Dimensions:
          - Name: Service
            Value: !Ref ServiceName
      Target:
        ComparisonOperator: GREATER_THAN_OR_EQUAL
        Threshold: !Ref AvailabilityTarget
        Period:
          RollingInterval:
            Count: 1
            TimeUnit: HOUR
      Goal:
        TargetLevel: !Ref AvailabilityTarget
      Tags:
        - Key: Service
          Value: !Ref ServiceName
        - Key: Environment
          Value: !Ref Environment

  # SLO for latency
  LatencySLO:
    Type: AWS::CloudWatch::ServiceLevelObjective
    Properties:
      Name: !Sub "${ServiceName}-${Environment}-latency-slo"
      Description: Latency SLO for ${ServiceName}
      Monitor:
        MonitorName: !Sub "${ServiceName}-monitor"
      SliMetric:
        MetricName: Latency
        Namespace: !Sub "SLO/${ServiceName}"
        Dimensions:
          - Name: Service
            Value: !Ref ServiceName
      Target:
        ComparisonOperator: LESS_THAN_OR_EQUAL
        Threshold: !Ref LatencyTarget
        Period:
          RollingInterval:
            Count: 1
            TimeUnit: HOUR
      Goal:
        TargetLevel: !Ref LatencyTarget
      Tags:
        - Key: Service
          Value: !Ref ServiceName
        - Key: Environment
          Value: !Ref Environment

  # Burn rate alarm for SLO
  AvailabilityBurnRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${ServiceName}-${Environment}-burn-rate"
      AlarmDescription: Alert on high SLO burn rate for availability
      MetricName: BurnRate
      Namespace: AWS/SLO
      Dimensions:
        - Name: ServiceName
          Value: !Ref ServiceName
      Statistic: Maximum
      Period: 300
      EvaluationPeriods: 12
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopicArn

  # SLO dashboard
  SloDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${ServiceName}-${Environment}-slo"
      DashboardBody: !Sub |
        {
          "start": "-PT24H",
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 2,
              "properties": {
                "markdown": "# SLO Dashboard - ${ServiceName}\n## Environment: ${Environment}"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Availability",
                "view": "singleValue",
                "region": "${AWS::Region}",
                "metrics": [
                  ["SLO/${ServiceName}", "Availability", "Service", "${ServiceName}"]
                ],
                "period": 300,
                "stat": "Average"
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 2,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Latency (P99)",
                "view": "singleValue",
                "region": "${AWS::Region}",
                "metrics": [
                  ["SLO/${ServiceName}", "Latency", "Service", "${ServiceName}", {"stat": "p99"}]
                ],
                "period": 300
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Availability Over Time",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["SLO/${ServiceName}", "Availability", "Service", "${ServiceName}"]
                ],
                "period": 300
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 8,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Burn Rate",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/SLO", "BurnRate", "ServiceName", "${ServiceName}"]
                ],
                "period": 300
              }
            }
          ]
        }
```

---

## Risorse Utili

- [CloudWatch Alarms Documentation](https://docs.aws.amazon.com/cloudwatch/latest/monitoring/AlarmThatSendsEmail.html)
- [CloudWatch Dashboards](https://docs.aws.amazon.com/cloudwatch/latest/monitoring/CloudWatch_Dashboards.html)
- [CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
- [Synthesized Canaries](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries.html)
- [Service Level Indicators](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ServiceLevelIndicators.html)
