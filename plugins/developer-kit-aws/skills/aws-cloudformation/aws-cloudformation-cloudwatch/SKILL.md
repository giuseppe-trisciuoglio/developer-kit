---
name: aws-cloudformation-cloudwatch
description: Provides AWS CloudFormation patterns for CloudWatch monitoring, metrics, alarms, dashboards, logs, and observability. Use when creating CloudWatch metrics, alarms, dashboards, log groups, log subscriptions, anomaly detection, synthesized canaries, Application Signals, and implementing template structure with Parameters, Outputs, Mappings, Conditions, cross-stack references, and CloudWatch best practices for monitoring production infrastructure.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation CloudWatch Monitoring

## Overview

Create production-ready monitoring and observability infrastructure using AWS CloudFormation templates. This skill covers CloudWatch metrics, alarms, dashboards, log groups, log insights, anomaly detection, synthesized canaries, Application Signals, and best practices for parameters, outputs, and cross-stack references.

## When to Use

Use this skill when:
- Creating custom CloudWatch metrics
- Configuring CloudWatch alarms for thresholds and anomaly detection
- Creating CloudWatch dashboards for multi-region visualization
- Implementing log groups with retention and encryption
- Configuring log subscriptions and cross-account log aggregation
- Implementing synthesized canaries for synthetic monitoring
- Enabling Application Signals for application performance monitoring
- Organizing templates with Parameters, Outputs, Mappings, Conditions
- Implementing cross-stack references with export/import
- Using Transform for macros and reuse

## Instructions

Follow these steps to create CloudWatch monitoring infrastructure with CloudFormation:

### 1. Define Alarm Parameters

Specify metric namespaces, dimensions, and threshold values:

```yaml
Parameters:
  ErrorRateThreshold:
    Type: Number
    Default: 5
    Description: Error rate threshold for alarms (percentage)

  LatencyThreshold:
    Type: Number
    Default: 1000
    Description: Latency threshold in milliseconds

  CpuUtilizationThreshold:
    Type: Number
    Default: 80
    Description: CPU utilization threshold (percentage)

  LogRetentionDays:
    Type: Number
    Default: 30
    AllowedValues:
      - 1
      - 3
      - 7
      - 14
      - 30
      - 60
      - 90
      - 120
      - 365
    Description: Number of days to retain log events
```

### 2. Create CloudWatch Alarms

Set up alarms for CPU, memory, disk, and custom metrics:

```yaml
Resources:
  HighCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cpu"
      AlarmDescription: Trigger when CPU utilization exceeds threshold
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      Statistic: Average
      Period: 60
      EvaluationPeriods: 3
      Threshold: !Ref CpuUtilizationThreshold
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopic

  ErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-error-rate"
      MetricName: ErrorRate
      Namespace: !Ref CustomNamespace
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
      Statistic: Average
      Period: 60
      EvaluationPeriods: 5
      Threshold: !Ref ErrorRateThreshold
      ComparisonOperator: GreaterThanThreshold
```

### 3. Configure Alarm Actions

Define SNS topics for notification delivery:

```yaml
Resources:
  AlarmNotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !Sub "${AWS::StackName}-alarms"
      TopicName: !Sub "${AWS::StackName}-alarms"

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
```

### 4. Create Dashboards

Build visualization widgets for metrics across resources:

```yaml
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
              "x": 0,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "CPU Utilization",
                "metrics": [["AWS/EC2", "CPUUtilization", "InstanceId", "${InstanceId}"]],
                "period": 300,
                "stat": "Average",
                "region": "${AWS::Region}"
              }
            }
          ]
        }
```

### 5. Set Up Log Groups

Configure retention policies and encryption settings:

```yaml
Resources:
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/applications/${Environment}/${ApplicationName}"
      RetentionInDays: !Ref LogRetentionDays
      KmsKeyId: !Ref LogEncryptionKey
```

### 6. Implement Metric Filters

Create metrics from log data:

```yaml
Resources:
  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: '[level="ERROR", msg]'
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${AWS::StackName}/Application"
          MetricName: ErrorCount
```

### 7. Add Composite Alarms

Build multi-condition alarm logic:

```yaml
Resources:
  SystemHealthComposite:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-system-health"
      AlarmRule: !Or
        - !Ref HighCpuAlarm
        - !Ref ErrorRateAlarm
      AlarmActions:
        - !Ref AlarmTopic
```

### 8. Configure Log Insights Queries

Create saved queries for log analysis:

```yaml
Resources:
  ErrorAnalysisQuery:
    Type: AWS::Logs::QueryDefinition
    Properties:
      Name: !Sub "${AWS::StackName}-errors"
      LogGroupNames:
        - !Ref ApplicationLogGroup
      QueryString: |
        fields @timestamp, @message
        | filter @message like /ERROR/
        | sort @timestamp desc
        | limit 100
```

## Best Practices

### Monitoring Strategy

- Use composite alarms to reduce alarm noise
- Configure appropriate evaluation periods to avoid false positives
- Set up anomaly detection for metrics with variable patterns
- Use metric math for derived metrics (error rates, averages)
- Implement high-resolution alarms for critical metrics
- Create separate dashboards for different audiences (ops, dev, management)

### Log Management

- Use appropriate retention periods based on compliance requirements
- Encrypt log groups containing sensitive data
- Implement metric filters for critical log patterns
- Set up cross-account log aggregation for centralized analysis
- Use CloudWatch Logs Insights for troubleshooting
- Configure log subscriptions to Lambda/Kinesis for real-time processing

### Cost Optimization

- Use standard resolution metrics when possible (not high-resolution)
- Set appropriate log retention periods (longer = more expensive)
- Limit metric filters to essential patterns
- Use composite alarms to reduce total alarm count
- Monitor CloudWatch usage with budgets and alarms
- Consider using CloudWatch Logs Insights instead of frequent metric filters

### Alarm Configuration

- Set meaningful thresholds based on baseline metrics
- Use datapoints-to-alarm for reliability
- Configure OK actions to reset notifications
- Treat missing data appropriately (breaching, not breaching, ignore)
- Test alarm actions regularly
- Document alarm runbooks and escalation procedures

### Template Structure

- Use AWS-specific parameter types for resources
- Implement parameter constraints for validation
- Use Conditions for environment-specific configuration
- Leverage Mappings for region-specific settings
- Apply Metadata for parameter grouping
- Use nested stacks for large monitoring setups

### Dashboard Design

- Organize dashboards by service or application tier
- Use consistent widget layouts and sizing
- Include text widgets for context and documentation
- Set appropriate time ranges for data visualization
- Use variables for dynamic dashboard filtering
- Limit metrics per dashboard to avoid performance issues

## References

For detailed implementation guidance, see:

- **[alarms.md](references/alarms.md)** - CloudWatch metrics and alarms including base metric alarms, latency alarms, API Gateway errors, EC2 instance alarms, Lambda function alarms, composite alarms, anomaly detection, metric math, alarm actions (SNS, Auto Scaling, EC2), missing data treatment, custom metrics, metric filters, and high-resolution alarms

- **[dashboards.md](references/dashboards.md)** - CloudWatch dashboards including base template, service-specific dashboards, widget types (metric, log, text, single value, alarm status), multi-region dashboards, stacked metrics, anomaly detection widgets, math expressions, layout patterns (grid, row, column), dynamic variables, cross-account sharing, and dashboard automation

- **[logs.md](references/logs.md)** - CloudWatch logs including log group configurations, metric filters, subscription filters (Lambda, Kinesis Firehose), cross-account log aggregation, log insights queries, resource policies, export and archive tasks, CloudWatch agent configuration, log encryption with KMS, lifecycle management, centralized logging, and search patterns

- **[constraints.md](references/constraints.md)** - Resource limits (5000 alarms max, 500 dashboards max), operational constraints (metric resolution, evaluation periods, dashboard widgets, cross-account), security constraints (log data access, encryption, metric filters, alarm actions), cost considerations (detailed monitoring, custom metrics, log retention, dashboard queries), and data constraints (metric age, log ingestion, filter limits)

## Related Resources

- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [AWS CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/)
- [CloudWatch Alarms Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/UserGuide/AlarmThatSendsEmail.html)
- [CloudWatch Dashboards Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/UserGuide/CloudWatch_Dashboards.html)
- [CloudWatch Logs Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/UserGuide/WhatIsCloudWatchLogs.html)
- [CloudWatch Logs Insights Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/UserGuide/CloudWatch-Logs-Insights-Syntax.html)
- [CloudWatch Anomaly Detection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/UserGuide/CloudWatch_Anomaly_Detection.html)
