---
name: aws-cloudformation-cloudwatch
description: Provides AWS CloudFormation patterns for CloudWatch monitoring, metrics, alarms, dashboards, logs, and observability. Use when creating CloudWatch metrics, alarms, dashboards, log groups, log subscriptions, anomaly detection, synthesized canaries, Application Signals, and implementing template structure with Parameters, Outputs, Mappings, Conditions, cross-stack references, and CloudWatch best practices for monitoring production infrastructure.
category: aws
tags: [aws, cloudformation, cloudwatch, monitoring, observability, metrics, alarms, logs, dashboards, infrastructure, iaac]
version: 2.2.0
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation CloudWatch Monitoring

## Overview

Create production-ready monitoring and observability infrastructure using AWS CloudFormation templates. This skill covers CloudWatch metrics, alarms, dashboards, log groups, log insights, anomaly detection, synthesized canaries, Application Signals, and best practices for parameters, outputs, and cross-stack references.

## When to Use

Use this skill when:
- Creating custom CloudWatch metrics and alarms
- Configuring composite alarms and anomaly detection
- Creating CloudWatch dashboards for visualization
- Implementing log groups with retention and encryption
- Configuring metric filters and log subscriptions
- Implementing synthesized canaries for synthetic monitoring
- Enabling Application Signals and SLI/SLO for APM
- Implementing cross-stack references with export/import

## Instructions

1. **Define Alarm Parameters**: Specify metric namespaces, dimensions, thresholds, and evaluation periods
2. **Create CloudWatch Alarms**: Set up alarms for CPU, memory, error rate, latency (use `DatapointsToAlarm` for sensitivity)
3. **Configure Alarm Actions**: Define SNS topics for notifications, use OKActions and InsufficientDataActions
4. **Create Composite Alarms**: Combine multiple alarms with OR/AND logic to reduce alarm fatigue
5. **Configure Anomaly Detection**: Create AnomalyDetector resources with excluded time ranges
6. **Create Dashboards**: Build widgets (metric, log, text) with `!Sub` for dynamic references
7. **Set Up Log Groups**: Configure retention policies (7-3650 days) and KMS encryption
8. **Add Metric Filters**: Extract custom metrics from log patterns
9. **Implement Canaries**: Create Synthetics canaries for endpoint monitoring with failure/latency alarms
10. **Configure Application Signals**: Set up SLI/SLO for service health monitoring

## Best Practices

### Security
- Encrypt log groups with KMS keys
- Implement least privilege IAM for log access
- Configure log retention appropriate for compliance

### Performance
- Use 60s periods for alarms, 300s for dashboards
- Implement composite alarms to reduce alarm fatigue
- Use anomaly detection for non-linear patterns
- Use `TreatMissingData: notBreaching` for intermittent metrics

### Monitoring
- Implement SLI/SLO for service health
- Use multi-region dashboards for global applications
- Configure canaries for synthetic monitoring

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudWatch monitoring stack

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/app/${AWS::StackName}"
      RetentionInDays: 30

  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: "ERROR"
      LogGroupName: !Ref LogGroup
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${AWS::StackName}/App"
          MetricName: ErrorCount

  ErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-errors"
      MetricName: ErrorCount
      Namespace: !Sub "${AWS::StackName}/App"
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      DatapointsToAlarm: 3
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref AlarmTopic

  LatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-latency"
      MetricName: Duration
      Namespace: AWS/Lambda
      Statistic: p99
      Period: 60
      EvaluationPeriods: 3
      Threshold: 5000
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopic

  HealthComposite:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-health"
      AlarmRule: !Sub "ALARM(${ErrorAlarm}) OR ALARM(${LatencyAlarm})"
      AlarmActions:
        - !Ref AlarmTopic

  AlarmTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-alarms"

Outputs:
  AlarmTopicArn:
    Value: !Ref AlarmTopic
    Export:
      Name: !Sub "${AWS::StackName}-AlarmTopicArn"
  LogGroupName:
    Value: !Ref LogGroup
    Export:
      Name: !Sub "${AWS::StackName}-LogGroupName"
```

## Constraints and Warnings

- **Alarms Limits**: Max 5000 CloudWatch alarms per account per region
- **Dashboards Limits**: Max 500 dashboards, 500 widgets per dashboard
- **Metric Resolution**: High-resolution metrics (1s) cost more than standard (60s)
- **Log Retention**: Longer retention periods significantly increase storage costs
- **Detailed Monitoring**: Enabling detailed monitoring doubles EC2 metric count
- **Metric Filters**: Count as separate billable CloudWatch Logs operations
- **Cross-Account Metrics**: Requires explicit resource policies
- **Alarm Evaluation**: Too few evaluation periods may trigger false positives

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
