# CloudWatch Logs Configuration

## Log Group Configurations

### Basic Log Group

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudWatch log groups configuration

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
      - 1095       # 3 years
      - 1827       # 5 years
      - 2190       # 6 years
      - 2555       # 7 years
      - 2922       # 8 years
      - 3285       # 9 years
      - 3650       # 10 years

Resources:
  # Application log group
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/applications/${Environment}/${ApplicationName}"
      RetentionInDays: !Ref LogRetentionDays
      KmsKeyId: !Ref LogKmsKeyArn
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Application
          Value: !Ref ApplicationName
        - Key: Service
          Value: !Ref ServiceName

  # Lambda log group
  LambdaLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/lambda/${LambdaFunctionName}"
      RetentionInDays: !Ref LogRetentionDays
      KmsKeyId: !Ref LogKmsKeyArn

  # Audit log group with longer retention
  AuditLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/audit/${Environment}/${ApplicationName}"
      RetentionInDays: 365
      KmsKeyId: !Ref LogKmsKeyArn
```

## Metric Filters

### Error Metric Filter

```yaml
Resources:
  # Metric filter for errors
  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: '[level="ERROR", msg]'
      LogGroupName: !Ref ApplicationLogGroup
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${AWS::StackName}/Application"
          MetricName: ErrorCount
          Unit: Count
        - MetricValue: "$level"
          MetricNamespace: !Sub "${AWS::StackName}/Application"
          MetricName: LogLevel

  # Metric filter for warnings
  WarningMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: '[level="WARN", msg]'
      LogGroupName: !Ref ApplicationLogGroup
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${AWS::StackName}/Application"
          MetricName: WarningCount
          Unit: Count

  # Metric filter for HTTP status codes
  HttpStatusFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: '[..., http_status > 400]'
      LogGroupName: !Ref ApplicationLogGroup
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${AWS::StackName}/HTTP"
          MetricName: HttpErrorCount
          Unit: Count

  # Metric filter for latency
  LatencyMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      FilterPattern: '[..., latency=duration]'
      LogGroupName: !Ref ApplicationLogGroup
      MetricTransformations:
        - MetricValue: "$latency"
          MetricNamespace: !Sub "${AWS::StackName}/Latency"
          MetricName: AverageLatency
          Unit: Milliseconds
```

## Subscription Filters

### Subscription to Lambda

```yaml
Resources:
  LogSubscriptionFilter:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      DestinationArn: !GetAtt LogProcessingFunction.Arn
      FilterPattern: '[timestamp=*Z, request_id, level, message]'
      LogGroupName: !Ref ApplicationLogGroup
      RoleArn: !GetAtt LogSubscriptionRole.Arn

  # Lambda function for log processing
  LogProcessingFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-log-processor"
      Runtime: nodejs20.x
      Handler: index.handler
      Code:
        ZipFile: |
          exports.handler = async (event) => {
            event.records.forEach(record => {
              const payload = Buffer.from(record.data, 'base64').toString('utf-8');
              // Process log data
            });
          };

  # IAM role for subscription
  LogSubscriptionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: !Sub "logs.${AWS::Region}.amazonaws.com"
            Action: sts:AssumeRole
      Policies:
        - PolicyName: LambdaInvocation
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource: !GetAtt LogProcessingFunction.Arn
```

### Subscription to Kinesis Data Firehose

```yaml
Resources:
  LogSubscriptionFirehose:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      DestinationArn: !GetAtt DeliveryStream.Arn
      FilterPattern: ''
      LogGroupName: !Ref ApplicationLogGroup
      RoleArn: !Ref LogSubscriptionRole

  # Kinesis Data Firehose delivery stream
  DeliveryStream:
    Type: AWS::KinesisFirehose::DeliveryStream
    Properties:
      DeliveryStreamName: !Sub "${AWS::StackName}-logs"
      DeliveryStreamType: DirectPut
      ExtendedS3DestinationConfiguration:
        BucketARN: !GetAtt LogsBucket.Arn
        BufferingHints:
          IntervalInSeconds: 300
          SizeInMBs: 5
        CompressionFormat: UNCOMPRESSED
        Prefix: logs/
        RoleARN: !GetAtt FirehoseRole.Arn

  LogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-logs-${AWS::AccountId}-${AWS::Region}"

  FirehoseRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: firehose.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSKinesisFirehoseServiceRole
```

### Cross-Account Log Aggregation

```yaml
Resources:
  # Central log aggregation destination
  CentralLogDestination:
    Type: AWS::Logs::Destination
    Properties:
      DestinationName: !Sub "${AWS::StackName}-central-logs"
      RoleArn: !Ref DestinationRole
      TargetArn: !GetAtt CentralKinesisStream.Arn
      Tags:
        - Key: Purpose
          Value: LogAggregation

  # Destination policy
  DestinationPolicy:
    Type: AWS::Logs::DestinationPolicy
    Properties:
      DestinationName: !Ref CentralLogDestination
      AccessPolicy: !Sub |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "AWS": "arn:aws:iam::${SourceAccountId}:root"
              },
              "Action": "logs:PutSubscriptionFilter",
              "Resource": !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:destination:${CentralLogDestination}"
            }
          ]
        }

  # Source account subscription
  SourceAccountSubscription:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      DestinationArn: !Sub "arn:aws:logs:${DestinationRegion}:${DestinationAccountId}:destination:${CentralLogDestinationName}"
      FilterPattern: '[timestamp, request_id, level, message]'
      LogGroupName: !Ref ApplicationLogGroup
      RoleArn: !Ref SourceSubscriptionRole
```

## Log Insights Queries

### Saved Query Definitions

```yaml
Resources:
  # Query definition for recent errors
  RecentErrorsQuery:
    Type: AWS::Logs::QueryDefinition
    Properties:
      Name: !Sub "${AWS::StackName}-recent-errors"
      LogGroupNames:
        - !Ref ApplicationLogGroup
      QueryString: |
        fields @timestamp, @message
        | sort @timestamp desc
        | limit 100
        | filter @message like /ERROR/
        | display @timestamp, @message, @logStream

  # Query for performance analysis
  PerformanceQuery:
    Type: AWS::Logs::QueryDefinition
    Properties:
      Name: !Sub "${AWS::StackName}-performance"
      LogGroupNames:
        - !Ref ApplicationLogGroup
      QueryString: |
        fields @timestamp, @message, @duration
        | filter @duration > 1000
        | sort @duration desc
        | limit 50
        | display @timestamp, @duration, @message

  # Query for statistics
  StatisticsQuery:
    Type: AWS::Logs::QueryDefinition
    Properties:
      Name: !Sub "${AWS::StackName}-stats"
      LogGroupNames:
        - !Ref ApplicationLogGroup
      QueryString: |
        stats count(*) as requestCount,
              avg(@duration) as avgDuration,
              max(@duration) as maxDuration
        | filter @message like /REQUEST/
        | sort requestCount desc
```

## Log Resource Policies

### Cross-Account Log Access

```yaml
Resources:
  LogGroupPolicy:
    Type: AWS::Logs::ResourcePolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-log-policy"
      PolicyDocument: !Sub |
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
              "Resource": !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:${ApplicationLogGroup}*"
            }
          ]
        }
```

### S3 Bucket Access for Logs

```yaml
Resources:
  S3AccessPolicy:
    Type: AWS::Logs::ResourcePolicy
    Properties:
      PolicyName: s3-access-policy
      PolicyDocument: !Sub |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": "delivery.logs.amazonaws.com"
              },
              "Action": "s3:PutObject",
              "Resource": !Sub "${LogsBucket.Arn}/*"
            }
          ]
        }
```

## Export and Archive Tasks

### Export Task to S3

```yaml
Resources:
  LogExportTask:
    Type: Custom::LogExportTask
    Properties:
      ServiceToken: !GetAtt ExportFunction.Arn
      LogGroupName: !Ref ApplicationLogGroup
      DestinationBucket: !Ref ArchiveBucket
      DestinationPrefix: !Sub "logs/${ApplicationLogGroup}/"
      From: !Ref ExportStartTime
      To: !Ref ExportEndTime

  ExportFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: nodejs20.x
      Handler: index.handler
      Timeout: 300
      Code:
        ZipFile: |
          const AWS = require('aws-sdk');
          const logs = new AWS.CloudWatchLogs();

          exports.handler = async (event) => {
            await logs.createExportTask({
              logGroupName: event.LogGroupName,
              from: event.From,
              to: event.To,
              destination: event.DestinationBucket,
              destinationPrefix: event.DestinationPrefix
            }).promise();
          };
```

### Log Stream Configuration

```yaml
Resources:
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/applications/${ApplicationName}"

  # Log stream (created automatically by application)
  # This is for reference - log streams are typically created by the logging library
```

## CloudWatch Logs Agent

### EC2 Instance with CloudWatch Agent

```yaml
Resources:
  # IAM role for CloudWatch agent
  CloudWatchAgentRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref CloudWatchAgentRole

  # EC2 instance with agent
  ApplicationInstance:
    Type: AWS::EC2::Instance
    Properties:
      IamInstanceProfile: !Ref InstanceProfile
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum install -y amazon-cloudwatch-agent
          /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
            -a fetch-config \
            -m ec2 \
            -s \
            -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### CloudWatch Agent Configuration

```yaml
Resources:
  CloudWatchAgentConfigParameter:
    Type: AWS::SSM::Parameter
    Properties:
      Name: !Sub "/aws/AmazonCloudWatchAgent/${AWS::StackName}"
      Type: String
      Value: !Sub |
        {
          "agent": {
            "metrics_collection_interval": 60,
            "run_as_user": "root"
          },
          "logs": {
            "logs_collected": {
              "files": {
                "collect_list": [
                  {
                    "file_path": "/var/log/application/app.log",
                    "log_group_name": "/aws/applications/${ApplicationName}",
                    "log_stream_name": "{instance_id}"
                  }
                ]
              }
            }
          },
          "metrics": {
            "namespace": "${ApplicationName}",
            "metrics_collected": {
              "cpu": {
                "measurement": ["cpu_usage_active"]
              },
              "mem": {
                "measurement": ["mem_used_percent"]
              },
              "disk": {
                "measurement": ["disk_used_percent"]
              }
            }
          }
        }
```

## Log Encryption

### KMS Encryption for Logs

```yaml
Resources:
  # KMS key for log encryption
  LogEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for CloudWatch Logs encryption
      KeyPolicy:
        Statement:
          - Effect: Allow
            Principal:
              Service: logs.amazonaws.com
            Action:
              - kms:Decrypt
              - kms:GenerateDataKey
            Resource: "*"
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Action:
              - kms:*
            Resource: "*"

  LogKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub "${AWS::StackName}/logs-encryption"
      TargetKeyId: !Ref LogEncryptionKey

  # Encrypted log group
  EncryptedLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/encrypted/${ApplicationName}"
      RetentionInDays: 30
      KmsKeyId: !Ref LogEncryptionKey
```

## Log Lifecycle Management

### Automatic Log Expiration

```yaml
Resources:
  # Short-term logs (7 days)
  ShortTermLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/temp/${ApplicationName}"
      RetentionInDays: 7

  # Medium-term logs (30 days)
  MediumTermLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/applications/${ApplicationName}"
      RetentionInDays: 30

  # Long-term logs (1 year)
  LongTermLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/audit/${ApplicationName}"
      RetentionInDays: 365
```

## Cross-Account Logging

### Centralized Logging Architecture

```yaml
Resources:
  # Central logging account - destination
  CentralLogDestination:
    Type: AWS::Logs::Destination
    Properties:
      DestinationName: central-log-destination
      RoleArn: !Ref CentralDestinationRole
      TargetArn: !GetAtt CentralFirehose.Arn

  CentralDestinationRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: logs.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: PutRecordPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - firehose:PutRecord
                  - firehose:PutRecordBatch
                Resource: !GetAtt CentralFirehose.Arn

  # Source account - subscription
  SourceLogSubscription:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      DestinationArn: !Sub "arn:aws:logs:${CentralRegion}:${CentralAccountId}:destination:${CentralLogDestinationName}"
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: '[timestamp, request_id, level, message]'
      RoleArn: !Ref SourceSubscriptionRole
```

## Log Anomaly Detection

### Anomaly Detection Filter

```yaml
Resources:
  # Metric filter for anomaly detection
  AnomalyMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterPattern: '[..., status]'
      MetricTransformations:
        - MetricName: AnomalousStatus
          MetricNamespace: !Sub "${AWS::StackName}/anomaly"
          MetricValue: "1"
          Unit: Count
```

## CloudWatch Logs Insights Patterns

### Search Patterns

```yaml
Resources:
  ErrorPatternQuery:
    Type: AWS::Logs::QueryDefinition
    Properties:
      Name: error-search
      QueryString: |
        fields @timestamp, @message, level
        | filter level = "ERROR"
        | sort @timestamp desc
        | limit 100

  IPAddressQuery:
    Type: AWS::Logs::QueryDefinition
    Properties:
      Name: ip-address-extract
      QueryString: |
        fields @timestamp, @message
        | parse @message "user_ip=*" as user_ip
        | stats count(*) by user_ip
        | sort count desc

  DurationAnalysisQuery:
    Type: AWS::Logs::QueryDefinition
    Properties:
      Name: duration-analysis
      QueryString: |
        fields @timestamp, @duration
        | filter @duration > 0
        | stats avg(@duration), max(@duration), min(@duration), percentile(@duration, 50)
```

## Live Tail Sessions

### Live Tail Configuration

```yaml
# Note: Live Tail is configured via AWS Console or CLI
# This is for reference - CloudFormation does not directly support Live Tail configuration

Resources:
  LogGroupForLiveTail:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/livetail/${ApplicationName}"
      RetentionInDays: 7
```
