# AWS Lambda Constraints and Limitations

## Resource Limits

### Function and Concurrency Limits

```yaml
# Maximum number of Lambda functions per region: account-dependent
# Default concurrent execution limit: 1000 per region (soft limit)

Parameters:
  ReservedConcurrentExecutions:
    Type: Number
    Default: 100
    MaxValue: 1000  # Account limit
    Description: Reserved concurrent executions
    ConstraintDescription: Cannot exceed account concurrent execution limit

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-function"
      Runtime: nodejs20.x
      Handler: index.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Ref CodeKey
      Role: !Ref ExecutionRole
      ReservedConcurrentExecutions: !Ref ReservedConcurrentExecutions
```

### Timeout and Memory Limits

```yaml
# Maximum timeout: 15 minutes (900 seconds)
# Maximum memory: 10,240 MB (10 GB)

Parameters:
  FunctionTimeout:
    Type: Number
    Default: 30
    MinValue: 1
    MaxValue: 900
    Description: Function timeout in seconds

  FunctionMemory:
    Type: Number
    Default: 256
    MinValue: 128
    MaxValue: 10240
    Description: Function memory in MB

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Timeout: !Ref FunctionTimeout
      MemorySize: !Ref FunctionMemory
```

## Deployment Constraints

### Function and Layer Size Limits

```yaml
# Maximum deployment package: 50 MB (zipped), 250 MB (unzipped)
# Maximum layer size: 250 MB (unzipped)
# Maximum environment variables: 4 KB

Parameters:
  CodeSize:
    Type: Number
    Description: Deployment package size in bytes
    # Validate before deployment

Conditions:
  PackageTooLarge: !Not [!Equals [!Ref CodeSize, 0]]

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Ref CodeKey
      # Ensure package size < 50 MB zipped
```

### Environment Variable Constraints

```yaml
# Environment variables limited to 4 KB total

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseUrl
          API_KEY: !Ref ApiKey
          # Total size must be < 4 KB
```

## Operational Constraints

### Cold Start Considerations

```yaml
# Cold starts add latency to first invocation
# Use provisioned concurrency to eliminate cold starts

Parameters:
  EnableProvisionedConcurrency:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false

Conditions:
  UseProvisionedConcurrency: !Equals [!Ref EnableProvisionedConcurrency, true]

Resources:
  ProvisionedConcurrency:
    Type: AWS::Lambda::ProvisionedConcurrencyConfiguration
    Condition: UseProvisionedConcurrency
    Properties:
      FunctionName: !Ref LambdaFunction
      ProvisionedConcurrentExecutions: 10

  # Or use Lambda PowerTuning for cost optimization
  PowerTuningState:
    Type: AWS::Lambda::EventInvokeConfig
    Properties:
      FunctionName: !Ref LambdaFunction
      Qualifier: $LATEST
      MaximumRetryAttempts: 2
```

### VPC Networking Constraints

```yaml
# Lambda in VPC has ENI limits and cold start delays
# Consider networking requirements when using VPC

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      VpcConfig:
        SecurityGroupIds:
          - !Ref SecurityGroup
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2

  # ENI creation takes time
  # Plan for additional cold start latency
```

### Event Source Limits

```yaml
# Event sources have rate limits
# Configure Dead Letter Queue for failed invocations

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      DeadLetterConfig:
        TargetArn: !Ref DeadLetterQueue

  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-dlq"
```

## Security Constraints

### Execution Role Requirements

```yaml
# Lambda functions require IAM execution roles
# Grant minimum required permissions

Resources:
  ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: SpecificPermissions
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "${DataBucket.Arn}/*"
```

### Resource-Based Policies

```yaml
# Resource-based policies required for cross-account access

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-function"

  LambdaResourcePolicy:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref LambdaFunction
      Action: lambda:InvokeFunction
      Principal: !Ref SourceAccount
      SourceAccount: !Ref SourceAccount
```

## Cost Considerations

### Provisioned Concurrency Costs

```yaml
# Provisioned concurrency incurs costs even when unused
# Calculate costs: memory allocation × duration × concurrency

Parameters:
  ProvisionedConcurrency:
    Type: Number
    Default: 10
    Description: Number of provisioned concurrent instances

# Cost estimation (US-East-1):
# 256 MB × $0.0000002083/GB-second = $0.053/second
# With provisioned concurrency: charged per provisioned instance
```

### Duration and Memory Costs

```yaml
# Longer duration directly increases costs
# Higher memory costs more even if not utilized

Parameters:
  FunctionTimeout:
    Type: Number
    Default: 30
    Description: Longer timeout = higher potential cost

  FunctionMemory:
    Type: Number
    Default: 256
    AllowedValues:
      - 128   # $0.0000002083/GB-second
      - 256   # $0.0000002083/GB-second
      - 512   # $0.0000002083/GB-second
      - 1024  # $0.0000002083/GB-second
      - 2048  # $0.0000002083/GB-second
    Description: Higher memory = higher cost per GB-second
```

## Performance Constraints

### SnapStart Limitations

```yaml
# SnapStart only available for specific runtimes and versions
# Java 11, Java 17 on AL2

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: java17
      SnapStart:
        SnapStartType: SnapStart  # Available for Java 11/17 on AL2
```

### X-Ray Tracing Constraints

```yaml
# X-Ray tracing adds latency and costs
# Use selectively for debugging

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      TracingConfig:
        Mode: Active  # Adds latency, use Passives for production
```

## Best Practices to Avoid Constraints

### Use Provisioned Concurrency Strategically

```yaml
# Use for critical functions requiring low latency
# Combine with reserved concurrency

Resources:
  CriticalFunction:
    Type: AWS::Lambda::Function
    Properties:
      ReservedConcurrentExecutions: 50
      MemorySize: 512
      Timeout: 30
```

### Optimize Cold Starts

```yaml
# Use SnapStart for Java functions
# Keep deployment packages small
# Use provisioned concurrency for critical paths

Resources:
  OptimizedLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: nodejs20.x
      MemorySize: 256
      Timeout: 30
      Code:
        ZipFile: |
          // Minimal code size
          exports.handler = async (event) => {
            return { statusCode: 200, body: "OK" };
          };
```

### Implement DLQ for Reliability

```yaml
# Always configure DLQ for async invocations
# Monitor DLQ for errors

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      DeadLetterConfig:
        TargetArn: !GetAtt DeadLetterQueue.Arn

  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-dlq"
      MessageRetentionPeriod: 1209600  # 14 days

  # Alarm for DLQ messages
  DLQAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: dlq-messages-alarm
      MetricName: ApproximateNumberOfMessagesVisible
      Namespace: AWS/SQS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanThreshold
```

## Quota Management

### Request Quota Increases

```yaml
# Concurrent execution limits can be increased
# Document quota requirements in stack outputs

Parameters:
  RequestedConcurrencyQuota:
    Type: Number
    Default: 1000
    Description: Requested concurrent execution quota

Outputs:
  QuotaIncreaseRequest:
    Description: Link to request quota increase
    Value: !Sub "https://console.aws.amazon.com/support/home#/case/create?issueType=service-limit-increase&serviceCode=aws-lambda"
```
