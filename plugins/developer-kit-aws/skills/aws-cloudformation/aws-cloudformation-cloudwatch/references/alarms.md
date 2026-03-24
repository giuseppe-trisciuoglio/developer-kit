# CloudWatch Metrics and Alarms

## Base Metric Alarms

### Error Rate Alarm

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudWatch metric alarms

Resources:
  # Error rate alarm
  ErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-error-rate"
      AlarmDescription: Alert when error rate exceeds threshold
      MetricName: ErrorRate
      Namespace: !Ref CustomNamespace
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
        - Name: Environment
          Value: !Ref Environment
      Statistic: Average
      Period: 60
      EvaluationPeriods: 5
      DatapointsToAlarm: 3
      Threshold: !Ref ErrorRateThreshold
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopic
      InsufficientDataActions:
        - !Ref AlarmTopic
      OKActions:
        - !Ref AlarmTopic
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Severity
          Value: high
```

### Latency Alarms

```yaml
Resources:
  # P99 latency alarm
  LatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-p99-latency"
      AlarmDescription: Alert when P99 latency exceeds threshold
      MetricName: Latency
      Namespace: !Ref CustomNamespace
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
      Statistic: p99
      ExtendedStatistic: "p99"
      Period: 60
      EvaluationPeriods: 3
      Threshold: !Ref LatencyThreshold
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref AlarmTopic

  # P95 latency alarm
  P95LatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-p95-latency"
      AlarmDescription: Alert when P95 latency exceeds threshold
      MetricName: Latency
      Namespace: !Ref CustomNamespace
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
      ExtendedStatistic: "p95"
      Period: 60
      EvaluationPeriods: 3
      Threshold: 500
      ComparisonOperator: GreaterThanThreshold
```

### API Gateway Error Alarms

```yaml
Resources:
  # 4xx errors alarm
  ClientErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-4xx-errors"
      AlarmDescription: Alert on high 4xx error rate
      MetricName: 4XXError
      Namespace: AWS/ApiGateway
      Dimensions:
        - Name: ApiName
          Value: !Ref ApiName
        - Name: Stage
          Value: !Ref StageName
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 100
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopic

  # 5xx errors alarm
  ServerErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-5xx-errors"
      AlarmDescription: Alert on high 5xx error rate
      MetricName: 5XXError
      Namespace: AWS/ApiGateway
      Dimensions:
        - Name: ApiName
          Value: !Ref ApiName
        - Name: Stage
          Value: !Ref StageName
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopic
```

### EC2 Instance Alarms

```yaml
Resources:
  # CPU utilization alarm
  HighCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cpu"
      AlarmDescription: Alert when CPU utilization exceeds threshold
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopic

  # Memory utilization alarm (requires CW Agent)
  HighMemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-memory"
      AlarmDescription: Alert when memory utilization exceeds threshold
      MetricName: MemoryUtilization
      Namespace: CWAgent
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 85
      ComparisonOperator: GreaterThanThreshold

  # Disk space alarm
  LowDiskSpaceAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-low-disk"
      AlarmDescription: Alert when disk space is low
      MetricName: DiskSpaceUtilization
      Namespace: CWAgent
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
        - Name: MountPath
          Value: /
      Statistic: Average
      Period: 300
      EvaluationPeriods: 1
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
```

### Lambda Function Alarms

```yaml
Resources:
  # Lambda error count alarm
  LambdaErrorsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-lambda-errors"
      AlarmDescription: Alert on Lambda function errors
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlarmTopic

  # Lambda duration alarm
  LambdaDurationAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-lambda-duration"
      AlarmDescription: Alert when Lambda duration exceeds threshold
      MetricName: Duration
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunction
      Statistic: Average
      Period: 300
      EvaluationPeriods: 3
      Threshold: 10000  # 10 seconds in milliseconds
      ComparisonOperator: GreaterThanThreshold

  # Lambda throttle alarm
  LambdaThrottleAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-lambda-throttles"
      AlarmDescription: Alert on Lambda throttles
      MetricName: Throttles
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 3
      ComparisonOperator: GreaterThanThreshold
```

## Composite Alarms

### Basic Composite Alarm

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudWatch composite alarms

Resources:
  # Base alarm for Lambda errors
  LambdaErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-lambda-errors"
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold

  # Base alarm for Lambda throttles
  LambdaThrottleAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-lambda-throttles"
      MetricName: Throttles
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 3
      ComparisonOperator: GreaterThanThreshold

  # Composite alarm combining both
  LambdaHealthCompositeAlarm:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-lambda-health"
      AlarmDescription: Composite alarm for Lambda function health
      AlarmRule: !Or
        - !Ref LambdaErrorAlarm
        - !Ref LambdaThrottleAlarm
      ActionsEnabled: true
      AlarmActions:
        - !Ref AlarmTopic
      Tags:
        - Key: Service
          Value: lambda
        - Key: Tier
          Value: application
```

### Complex Composite Alarm Logic

```yaml
Resources:
  # Multiple condition alarm
  SystemHealthyComposite:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: system-healthy
      AlarmDescription: System is healthy when all conditions are met
      AlarmRule: !Sub
        - "(ALARM(${AlarmA}) OR ALARM(${AlarmB})) AND NOT MISSING(${AlarmC})"
        - AlarmA: !Ref AlarmA
          AlarmB: !Ref AlarmB
          AlarmC: !Ref AlarmC
      ActionsEnabled: true

  # Nested composite alarms
  CriticalServiceAlarm:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: critical-service-alarm
      AlarmRule: !Ref ParentCompositeAlarm
      AlarmActions:
        - !Ref CriticalNotificationTopic
```

## Anomaly Detection Alarms

### Anomaly Detector Configuration

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudWatch anomaly detection

Resources:
  # Anomaly detector for metric
  RequestRateAnomalyDetector:
    Type: AWS::CloudWatch::AnomalyDetector
    Properties:
      MetricName: RequestCount
      Namespace: !Ref CustomNamespace
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
        - Name: Environment
          Value: !Ref Environment
      Statistic: Sum
      Configuration:
        ExcludedTimeRanges:
          - StartTime: "2023-12-25T00:00:00"
            EndTime: "2023-12-26T00:00:00"
        MetricTimeZone: UTC

  # Alarm based on anomaly detection
  AnomalyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-anomaly-detection"
      AlarmDescription: Alert on anomalous metric behavior
      Metrics:
        - Id: e1
          Expression: "ANOMALY_DETECTION_BAND(m1, 2)"
          Label: "RequestCount (expected)"
        - Id: m1
          MetricStat:
            Metric:
              MetricName: RequestCount
              Namespace: !Ref CustomNamespace
              Dimensions:
                - Name: Service
                  Value: !Ref ServiceName
            Period: 300
            Statistic: Sum
          ReturnData: false
      EvaluationPeriods: 2
      AlarmActions:
        - !Ref AlarmTopic

  # Alarm for high anomalous value
  HighTrafficAnomalyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-traffic-anomaly"
      AlarmDescription: Alert on unusually high traffic
      MetricName: RequestCount
      Namespace: !Ref CustomNamespace
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
      AnomalyDetectorConfiguration:
        ExcludeTimeRange:
          StartTime: "2023-12-25T00:00:00"
          EndTime: "2023-12-26T00:00:00"
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 2
      ComparisonOperator: GreaterThanUpperThreshold
      AlarmActions:
        - !Ref AlarmTopic

  # Alarm for low anomalous value
  LowTrafficAnomalyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-low-traffic"
      AlarmDescription: Alert on unusually low traffic
      MetricName: RequestCount
      Namespace: !Ref CustomNamespace
      Dimensions:
        - Name: Service
          Value: !Ref ServiceName
      AnomalyDetectorConfiguration:
        Bound: Lower
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 3
      Threshold: 0.5
      ComparisonOperator: LessThanLowerThreshold
      AlarmActions:
        - !Ref AlarmTopic
```

## Metric Math Alarms

### Metric Math Expression

```yaml
Resources:
  # CPU utilization percentage
  CpuUtilizationAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: cpu-utilization-alarm
      Metrics:
        - Id: m1
          MetricStat:
            Metric:
              Namespace: AWS/EC2
              MetricName: CPUUtilization
              Dimensions:
                - Name: InstanceId
                  Value: !Ref InstanceId
            Period: 300
            Stat: Average
        - Id: e1
          Expression: "m1"
          Label: CPU Utilization
          ReturnData: true
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold

  # Error rate calculation
  ErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: error-rate-alarm
      Metrics:
        - Id: errors
          MetricStat:
            Metric:
              Namespace: MyApplication
              MetricName: Errors
              Dimensions:
                - Name: Service
                  Value: !Ref ServiceName
            Period: 60
            Stat: Sum
        - Id: requests
          MetricStat:
            Metric:
              Namespace: MyApplication
              MetricName: Requests
              Dimensions:
                - Name: Service
                  Value: !Ref ServiceName
            Period: 60
            Stat: Sum
        - Id: e1
          Expression: "100 * (errors / requests)"
          Label: Error Rate %
      EvaluationPeriods: 5
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
```

## Alarm Actions

### SNS Notification Actions

```yaml
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
      AlarmName: critical-alarm
      AlarmActions:
        - !Ref AlarmNotificationTopic
      OKActions:
        - !Ref AlarmNotificationTopic
      InsufficientDataActions:
        - !Ref AlarmNotificationTopic
```

### Auto Scaling Actions

```yaml
Resources:
  ScaleUpAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: scale-up-alarm
      AlarmDescription: Scale up when CPU is high
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 70
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref ScaleUpPolicy

  ScaleDownAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: scale-down-alarm
      AlarmDescription: Scale down when CPU is low
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup
      Statistic: Average
      Period: 300
      EvaluationPeriods: 5
      Threshold: 30
      ComparisonOperator: LessThanThreshold
      AlarmActions:
        - !Ref ScaleDownPolicy
```

### EC2 Actions

```yaml
Resources:
  RebootInstanceAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: reboot-instance-alarm
      AlarmDescription: Reboot instance when status check fails
      MetricName: StatusCheckFailed
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      AlarmActions:
        - !Ref RebootPolicy

  RecoverInstanceAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: recover-instance-alarm
      AlarmDescription: Recover instance when system check fails
      MetricName: StatusCheckFailed_System
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      Statistic: Average
      Period: 60
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      AlarmActions:
        - !Ref RecoverPolicy

  StopInstanceAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: stop-instance-alarm
      AlarmDescription: Stop instance when CPU is too low
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      Statistic: Average
      Period: 900
      EvaluationPeriods: 10
      Threshold: 5
      ComparisonOperator: LessThanThreshold
      AlarmActions:
        - !Ref StopPolicy
```

## Missing Data Treatment

```yaml
Resources:
  # Treat missing data as breaching
  BreachingAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: breaching-on-missing
      MetricName: Heartbeat
      Namespace: Custom
      TreatMissingData: breaching

  # Treat missing data as not breaching
  NotBreachingAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: not-breaching-on-missing
      MetricName: StatusMetric
      Namespace: Custom
      TreatMissingData: notBreaching

  # Ignore missing data (maintain current state)
  IgnoreAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: ignore-missing
      MetricName: OptionalMetric
      Namespace: Custom
      TreatMissingData: ignore

  # Go to INSUFFICIENT_DATA state
  InsufficientDataAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: insufficient-on-missing
      MetricName: CriticalMetric
      Namespace: Custom
      TreatMissingData: missing
```

## Custom Metrics

### PutMetricData API Pattern

```yaml
Resources:
  # Custom metric via Lambda or API
  CustomMetricPublisher:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-metric-publisher"
      Runtime: nodejs20.x
      Handler: index.handler
      Code:
        ZipFile: |
          const AWS = require('aws-sdk');
          const cloudwatch = new AWS.CloudWatch();

          exports.handler = async (event) => {
            await cloudwatch.putMetricData({
              Namespace: 'MyApplication',
              MetricData: [{
                MetricName: 'CustomMetric',
                Dimensions: [{
                  Name: 'Service',
                  Value: 'MyService'
                }],
                Value: 100,
                Unit: 'Count',
                Timestamp: new Date()
              }]
            }).promise();
          };
      Role: !Ref LambdaExecutionRole

  # CloudWatch IAM permissions for custom metrics
  MetricPublishRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CloudWatchMetrics
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - cloudwatch:PutMetricData
                  - cloudwatch:GetMetricStatistics
                  - cloudwatch:ListMetrics
                Resource: "*"
```

### Metric Filters for Logs

```yaml
Resources:
  # Metric filter for error logs
  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: "[timestamp, request_id, event_type=ERROR, ...]"
      MetricTransformations:
        - MetricName: ErrorCount
          MetricNamespace: !Sub "${AWS::StackName}/errors"
          MetricValue: "1"
          Unit: Count

  # Metric filter for HTTP status codes
  HttpStatusMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: "[..., http_status > 400]"
      MetricTransformations:
        - MetricName: HttpErrorCount
          MetricNamespace: !Sub "${AWS::StackName}/http"
          MetricValue: "1"
          Unit: Count

  # Metric filter with pattern extraction
  LatencyMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: "[..., latency=duration]"
      MetricTransformations:
        - MetricName: AverageLatency
          MetricNamespace: !Sub "${AWS::StackName}/latency"
          MetricValue: "$latency"
          Unit: Milliseconds
```

## High-Resolution Alarms

```yaml
Resources:
  # High-resolution metric alarm (1-second)
  HighResolutionAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: high-resolution-alarm
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      Statistic: Average
      # High resolution period
      Period: 1  # 1 second
      EvaluationPeriods: 3
      Threshold: 90
      ComparisonOperator: GreaterThanThreshold
      # Extended statistics for high-resolution
      ExtendedStatistic: p90
```
