# AWS CloudFormation Lambda - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for Lambda serverless infrastructure.

## AWS::Lambda::Function

Creates a Lambda function.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Code | Code | Yes | The code for the function |
| Handler | String | Yes | The function that Lambda calls to begin execution |
| Role | String | Yes | The ARN of the IAM role that Lambda assumes |
| Runtime | String | Yes | The runtime environment for the function |
| FunctionName | String | No | The name of the function |
| Description | String | No | A description of the function |
| MemorySize | Integer | No | The amount of memory available to the function (128-10240 MB) |
| Timeout | Integer | No | The function execution timeout in seconds (1-900) |
| VpcConfig | VpcConfig | No | The VPC configuration for the function |
| Environment | Environment | No | Environment variables for the function |
| TracingConfig | TracingConfig | No | AWS X-Ray tracing configuration |
| Tags | List of Tag | No | Tags for the function |
| Layers | List of String | No | The layers for the function |
| ReservedConcurrentExecutions | Integer | No | Reserved concurrent executions for the function |
| EphemeralStorage | EphemeralStorage | No | The size of the function's /tmp directory (512-10240 MB) |
| FileSystemConfigs | List of FileSystemConfig | No | The EFS file system connections |
| ImageConfig | ImageConfig | No | The image configuration for container images |
| PackageType | String | No | The package type (Zip or Image) |
| SigningProfileVersionArn | String | No | The ARN of the signing profile |
| SigningJobArn | String | No | The ARN of the signing job |

### Code Structure

```yaml
Code:
  S3Bucket: !Ref CodeBucket
  S3Key: lambda/function.zip
  S3ObjectVersion: version-id

# Or for inline code
ZipFile: |
  def handler(event, context):
      return {"statusCode": 200, "body": "Hello"}
```

### Example

```yaml
Resources:
  MyLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-processor"
      Runtime: python3.11
      Handler: index.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/function.zip
      MemorySize: 256
      Timeout: 60
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the function |
| FunctionName | The name of the function |
| Runtime | The runtime of the function |
| Handler | The handler of the function |
| MemorySize | The memory size of the function |
| Timeout | The timeout of the function |
| Role | The role ARN of the function |

## AWS::Lambda::LayerVersion

Creates a Lambda layer.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| LayerName | String | No | The name of the layer |
| Description | String | No | A description of the layer |
| Content | Content | Yes | The content of the layer |
| CompatibleRuntimes | List of String | No | Compatible runtimes |
| CompatibleArchitectures | List of String | No | Compatible architectures (x86_64, arm64) |
| LicenseInfo | String | No | The layer's license information |

### Example

```yaml
Resources:
  CommonLibraryLayer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: !Sub "${AWS::StackName}-common-lib"
      Description: Common utilities for Lambda functions
      Content:
        S3Bucket: !Ref LayersBucket
        S3Key: layers/common-lib.zip
      CompatibleRuntimes:
        - python3.9
        - python3.10
        - python3.11
      CompatibleArchitectures:
        - x86_64
        - arm64
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| LayerVersionArn | The ARN of the layer version |
| LayerArn | The ARN of the layer |

## AWS::Lambda::EventSourceMapping

Creates an event source mapping between an event source and a Lambda function.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| FunctionName | String | Yes | The name of the Lambda function |
| EventSourceArn | String | Cond | The ARN of the event source (SQS, Kafka, MQ) |
| BatchSize | Integer | No | The maximum number of records in each batch (1-10000) |
| MaximumBatchingWindowInSeconds | Integer | No | The maximum time to gather records (0-300) |
| ParallelizationFactor | Integer | No | The number of batches to process concurrently (1-10) |
| StartingPosition | String | Cond | The position to start reading (AT_TIMESTAMP, LATEST, TRIM_HORIZON) |
| StartingPositionTimestamp | Integer | Cond | The timestamp to start reading (Unix seconds) |
| FilterCriteria | FilterCriteria | No | Criteria to filter events |
| MaximumRecordAgeInSeconds | Integer | No | Maximum age of records (60-604800) |
| MaximumRetryAttempts | Integer | No | Maximum retry attempts (0-10000) |
| BisectBatchOnFunctionError | Boolean | No | Split batch on function error |
| DestinationConfig | DestinationConfig | No | Destination for failed records |
| Enabled | Boolean | No | Whether the mapping is enabled |
| SourceAccessConfigurations | List of SourceAccessConfiguration | No | Credentials for Kafka and MQ sources |
| Topics | List of String | No | Kafka topics |
| Queues | List of String | No | SQS queue names |

### Example

```yaml
Resources:
  EventSourceMapping:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      FunctionName: !Ref MyLambdaFunction
      EventSourceArn: !GetAtt Queue.Arn
      BatchSize: 10
      MaximumBatchingWindowInSeconds: 60
      MaximumRecordAgeInSeconds: 604800
      MaximumRetryAttempts: 3
      Enabled: true
```

## AWS::Lambda::Permission

Grants an AWS service or another account permission to use a function.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| FunctionName | String | Yes | The name or ARN of the Lambda function |
| Action | String | Yes | The action Lambda should perform (lambda:InvokeFunction) |
| Principal | String | Yes | The principal to grant permission to |
| SourceArn | String | Cond | The ARN of the source triggering the function |
| SourceAccount | String | Cond | The AWS account ID of the source |
| EventSourceToken | String | Cond | The event source token for Alexa Smart Home |
| Qualifier | String | Cond | The version or alias of the function |

### Example

```yaml
Resources:
  LambdaPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref MyLambdaFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${MyLambdaFunction.Arn}/invocations"
```

## AWS::Lambda::ProvisionedConcurrencyConfig

Configures provisioned concurrency for a Lambda function alias or version.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| FunctionName | String | Yes | The name of the Lambda function |
| ProvisionedConcurrentExecutions | Integer | Yes | The amount of provisioned concurrency |
| Qualifier | String | Yes | The alias or version of the function |
| ProvisionedExecutionTarget | ProvisionedExecutionTarget | No | Target allocation strategy |

### Example

```yaml
Resources:
  ProvisionedConcurrencyConfig:
    Type: AWS::Lambda::ProvisionedConcurrencyConfig
    Properties:
      FunctionName: !Ref MyLambdaFunction
      ProvisionedConcurrentExecutions: 5
      Qualifier: $LATEST
      ProvisionedExecutionTarget:
        AllocationStrategy: PRICE_OPTIMIZED
```

## AWS::Lambda::EventInvokeConfig

Configures options for asynchronous invocation on a Lambda function.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| FunctionName | String | Yes | The name of the Lambda function |
| MaximumEventAgeInSeconds | Integer | No | Maximum age of events (60-21600) |
| MaximumRetryAttempts | Integer | No | Maximum retry attempts (0-2) |
| Qualifier | String | No | The alias or version of the function |
| DestinationConfig | DestinationConfig | No | Destination for successful/failed invocations |

### Example

```yaml
Resources:
  EventInvokeConfig:
    Type: AWS::Lambda::EventInvokeConfig
    Properties:
      FunctionName: !Ref MyLambdaFunction
      MaximumEventAgeInSeconds: 3600
      MaximumRetryAttempts: 2
      DestinationConfig:
        OnSuccess:
          Destination: !Ref SuccessQueue
        OnFailure:
          Destination: !Ref DeadLetterQueue
```

## AWS::Lambda::Url

Creates a function URL for a Lambda function.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AuthType | String | Yes | The authentication type (AWS_IAM, NONE) |
| TargetFunctionArn | String | Yes | The ARN of the Lambda function |
| Cors | Cors | No | CORS configuration |
| InvokeMode | String | No | The invocation mode (BUFFERED, RESPONSE_STREAM) |
| Qualifier | String | No | The alias or version of the function |

### Example

```yaml
Resources:
  LambdaFunctionUrl:
    Type: AWS::Lambda::Url
    Properties:
      AuthType: AWS_IAM
      TargetFunctionArn: !GetAtt MyLambdaFunction.Arn
      Cors:
        AllowCredentials: true
        AllowHeaders:
          - "*"
        AllowMethods:
          - GET
          - POST
        AllowOrigins:
          - "*"
        MaxAge: 86400
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Url | The function URL |

## AWS::Serverless::Function

Creates a Lambda function with SAM simplifications.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CodeUri | String | Yes | The location of the code |
| Handler | String | Yes | The function handler |
| Runtime | String | Yes | The runtime environment |
| Code | Code | No | Inline code (alternative to CodeUri) |
| InlineCode | String | No | Inline code (alternative to CodeUri) |
| Description | String | No | A description of the function |
| MemorySize | Integer | No | The memory allocation (128-10240) |
| Timeout | Integer | No | The function timeout (1-900) |
| Role | String | No | The IAM role ARN |
| Policies | List or Policy | No | IAM policies to attach |
| Environment | Environment | No | Environment variables |
| VpcConfig | VpcConfig | No | The VPC configuration |
| Events | Map of Event | No | Event sources |
| Tags | Map of String | No | Tags |
| Layers | List of String | No | Layers |
| Tracing | String | No | X-Ray tracing (Active or PassThrough) |
| ReservedConcurrentExecutions | Integer | No | Reserved concurrent executions |
| PermissionsBoundary | String | No | Permissions boundary policy |
| EventInvokeConfig | EventInvokeConfig | No | Async invocation config |
| ProvisionedConcurrencyConfig | ProvisionedConcurrencyConfig | No | Provisioned concurrency |
| AutoPublishAlias | String | No | Auto-publish alias on update |
| AutoPublishCodeSha256 | String | No | Code hash for alias update |
| DeploymentPreference | DeploymentPreference | No | Deployment configuration |
| FunctionName | String | No | The function name |
| FileSystemConfigs | List of FileSystemConfig | No | EFS configurations |
| ImageConfig | ImageConfig | No | Image configuration |
| PackageType | String | No | Package type (Zip or Image) |
| Metadata | Metadata | No | Build metadata |
| SnapStart | SnapStart | No | SnapStart configuration |

### Example

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-api"
      CodeUri: lambda_function/
      Handler: app.handler
      Runtime: python3.11
      MemorySize: 512
      Timeout: 30
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref DataBucket
        - DynamoDBReadPolicy:
            TableName: !Ref DataTable
      Environment:
        Variables:
          LOG_LEVEL: INFO
      Events:
        Api:
          Type: Api
          Properties:
            Path: /items
            Method: get
        SqsQueue:
          Type: SQS
          Properties:
            Queue: !GetAtt Queue.Arn
            BatchSize: 10
      AutoPublishAlias: !Ref Environment
```

## AWS::Serverless::LayerVersion

Creates a Lambda layer with SAM simplifications.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| LayerName | String | No | The name of the layer |
| Description | String | No | A description of the layer |
| ContentUri | String | Yes | The location of the layer content |
| CompatibleRuntimes | List of String | No | Compatible runtimes |
| CompatibleArchitectures | List of String | No | Compatible architectures |
| LicenseInfo | String | No | The layer license |
| RetentionPolicy | String | No | Retention policy (Retain or Delete) |

### Example

```yaml
Resources:
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: !Sub "${AWS::StackName}-dependencies"
      Description: Python dependencies
      ContentUri: layers/dependencies.zip
      CompatibleRuntimes:
        - python3.11
      RetentionPolicy: Retain
```

## AWS::ApiGateway::RestApi

Creates a REST API in API Gateway.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | The name of the REST API |
| Description | String | No | A description of the API |
| EndpointConfiguration | EndpointConfiguration | No | The endpoint configuration |
| Policy | Json | No | The resource policy |
| MinimumCompressionSize | Integer | No | Minimum compression size (0-10485760) |
| DisableExecuteApiEndpoint | Boolean | No | Disable the execute API endpoint |
| BinaryMediaTypes | List of String | No | Binary media types |
| CorsConfiguration | CorsConfiguration | No | CORS configuration |

### Example

```yaml
Resources:
  ApiGatewayRestApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "${AWS::StackName}-api"
      Description: REST API for Lambda backend
      EndpointConfiguration:
        Types:
          - REGIONAL
      MinimumCompressionSize: 1024
```

## AWS::ApiGatewayV2::Api

Creates an HTTP API in API Gateway V2.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | The name of the API |
| ProtocolType | String | Yes | The protocol type (HTTP) |
| Description | String | No | A description of the API |
| CorsConfiguration | CorsConfiguration | No | CORS configuration |
| DisableExecuteApiEndpoint | Boolean | No | Disable the execute API endpoint |
| RouteSelectionExpression | String | No | The route selection expression |
| Body | Json | No | OpenAPI definition |
| BodyS3Location | S3Location | No | S3 location of OpenAPI definition |

### Example

```yaml
Resources:
  HttpApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: !Sub "${AWS::StackName}-http-api"
      ProtocolType: HTTP
      CorsConfiguration:
        AllowOrigins:
          - "*"
        AllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
```

## AWS::StepFunctions::StateMachine

Creates a Step Functions state machine.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| StateMachineName | String | No | The name of the state machine |
| StateMachineType | String | No | The type (STANDARD or EXPRESS) |
| DefinitionString | Json | Yes | The state machine definition |
| DefinitionS3Location | S3Location | No | S3 location of definition |
| RoleArn | String | Yes | The IAM role ARN |
| LoggingConfiguration | LoggingConfiguration | No | CloudWatch Logs configuration |
| TracingConfiguration | TracingConfiguration | No | X-Ray tracing |
| Tags | List of Tag | No | Tags |

### State Types Reference

| Type | Description |
|------|-------------|
| Task | Execute work using Lambda or other service |
| Choice | Branch based on data |
| Wait | Pause execution |
| Pass | Pass data to next state |
| Parallel | Execute branches in parallel |
| Map | Iterate over items |
| Succeed | End execution successfully |
| Fail | End execution in failure |

### Example

```yaml
Resources:
  ProcessingStateMachine:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      StateMachineName: !Sub "${AWS::StackName}-processor"
      StateMachineType: STANDARD
      DefinitionString: !Sub |
        {
          "Comment": "Item processing workflow",
          "StartAt": "ValidateItem",
          "States": {
            "ValidateItem": {
              "Type": "Task",
              "Resource": "${ValidateItemFunction.Arn}",
              "Next": "ProcessItem"
            },
            "ProcessItem": {
              "Type": "Task",
              "Resource": "${ProcessItemFunction.Arn}",
              "End": true
            }
          }
        }
      RoleArn: !GetAtt StepFunctionsExecutionRole.Arn
      LoggingConfiguration:
        Level: ALL
        IncludeExecutionData: true
```

## AWS::SQS::Queue

Creates an SQS queue.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| QueueName | String | No | The name of the queue |
| DelaySeconds | Integer | No | Delivery delay in seconds (0-900) |
| MaximumMessageSize | Integer | No | Max message size (1024-262144) |
| MessageRetentionPeriod | Integer | No | Retention period (60-1209600) |
| ReceiveMessageWaitTimeSeconds | Integer | No | Polling wait time (0-20) |
| VisibilityTimeout | Integer | No | Visibility timeout (0-43200) |
| RedrivePolicy | RedrivePolicy | No | Dead letter queue configuration |
| FifoQueue | Boolean | No | Whether this is a FIFO queue |
| ContentBasedDeduplication | Boolean | No | Content-based deduplication for FIFO |
| KmsMasterKeyId | String | No | KMS key for encryption |
| KmsDataKeyReusePeriodSeconds | Integer | No | KMS key reuse period (60-86400) |
| Tags | List of Tag | No | Tags |

### Example

```yaml
Resources:
  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-queue"
      VisibilityTimeout: 300
      MessageRetentionPeriod: 86400
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
        maxReceiveCount: 5
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the queue |
| QueueName | The name of the queue |
| QueueUrl | The URL of the queue |

## AWS::SNS::Topic

Creates an SNS topic.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| TopicName | String | No | The name of the topic |
| DisplayName | String | No | The display name for the topic |
| Subscription | List of Subscription | No | The subscriptions |
| Tags | List of Tag | No | Tags |
| FifoTopic | Boolean | No | Whether this is a FIFO topic |
| ContentBasedDeduplication | Boolean | No | Content-based deduplication |
| KmsMasterKeyId | String | No | KMS key for encryption |

### Example

```yaml
Resources:
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-notifications"
      DisplayName: "Notifications"
      Subscription:
        - Endpoint: !GetAtt LambdaFunction.Arn
          Protocol: lambda
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the topic |
| TopicName | The name of the topic |

## AWS::Events::Rule

Creates an EventBridge rule.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | The name of the rule |
| Description | String | No | A description of the rule |
| State | String | No | The state (ENABLED or DISABLED) |
| ScheduleExpression | String | Cond | The schedule expression (rate or cron) |
| EventPattern | Json | Cond | The event pattern |
| EventBusName | String | No | The event bus name |
| RoleArn | String | No | The IAM role ARN |
| Targets | List of Target | No | The targets |

### Example

```yaml
Resources:
  ScheduledRule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub "${AWS::StackName}-scheduler"
      ScheduleExpression: "rate(5 minutes)"
      State: ENABLED
      Targets:
        - Id: LambdaFunction
          Arn: !GetAtt LambdaFunction.Arn
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the rule |

## AWS::CloudWatch::Alarm

Creates a CloudWatch alarm.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AlarmName | String | No | The name of the alarm |
| AlarmDescription | String | No | A description of the alarm |
| MetricName | String | Yes | The name of the metric |
| Namespace | String | Yes | The namespace of the metric |
| Dimensions | List of Dimension | No | The dimensions |
| Period | Integer | No | The period in seconds |
| EvaluationPeriods | Integer | No | Number of evaluation periods |
| Threshold | Double | Yes | The threshold value |
| ComparisonOperator | String | Yes | The comparison operator |
| Statistic | String | No | The statistic |
| ExtendedStatistic | String | Cond | The extended statistic |
| Unit | String | No | The unit |
| EvaluationPeriods | Integer | No | Number of evaluation periods |
| DatapointsToAlarm | Integer | No | Datapoints to trigger alarm |
| TreatMissingData | String | No | How to treat missing data |
| OKActions | List of String | No | Actions on OK state |
| AlarmActions | List of String | No | Actions on ALARM state |
| InsufficientDataActions | List of String | No | Actions on INSUFFICIENT_DATA |

### Lambda Metrics Reference

| Metric | Description |
|--------|-------------|
| Invocations | Number of invocations |
| Errors | Number of errors |
| Throttles | Number of throttles |
| Duration | Execution duration in ms |
| ConcurrentExecutions | Concurrent executions |
| ProvisionedConcurrentExecutions | Provisioned concurrent executions |
| ProvisionedConcurrencyInvocations | Provisioned concurrency invocations |
| ProvisionedConcurrencySpilloverInvocations | Spillover invocations |
| UnreservedConcurrentExecutions | Unreserved concurrent executions |

### Example

```yaml
Resources:
  HighErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-error-rate"
      AlarmDescription: Alert when error rate exceeds threshold
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic
```

## Intrinsic Functions Reference

### !Ref

Returns the value of the specified parameter or resource.

```yaml
# Reference a parameter
FunctionName: !Ref FunctionNameParam

# Reference a resource (returns the physical ID)
FunctionArn: !Ref MyLambdaFunction
```

### !GetAtt

Returns the value of an attribute from a Lambda function.

```yaml
# Get the function ARN
FunctionArn: !GetAtt MyLambdaFunction.Arn

# Get layer ARN
LayerArn: !GetAtt CommonLayer.Arn

# Get queue ARN
QueueArn: !GetAtt Queue.Arn
```

### !Sub

Substitutes variables in an input string.

```yaml
# With variable substitution
FunctionName: !Sub ${AWS::StackName}-function

# With multiple variables
RoleArn: !Sub arn:aws:iam::${AWS::AccountId}:role/${RoleName}
```

### !ImportValue

Imports values exported by other stacks.

```yaml
# Import from another stack
LambdaRoleArn: !ImportValue
  Fn::Sub: "${NetworkStackName}-LambdaRoleArn"
```

### !FindInMap

Returns the value from a mapping.

```yaml
# Find in mapping
RuntimeConfig: !FindInMap [RuntimeMap, !Ref Runtime, Config]
```

### !If

Returns one value if condition is true, another if false.

```yaml
# Conditional environment variable
MemorySize: !If [IsProduction, 512, 256]
```

## IAM Policy Templates for Lambda

### AWSLambdaBasicExecutionRole

```yaml
Policies:
  - AWSLambdaBasicExecutionRole
```

### AWSLambdaVPCAccessExecutionRole

```yaml
Policies:
  - AWSLambdaVPCAccessExecutionRole
```

### AWSLambdaSQSQueueExecutionRole

```yaml
Policies:
  - AWSLambdaSQSQueueExecutionRole
```

### Custom Policy Document

```yaml
Policies:
  - PolicyName: LambdaPolicy
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:PutObject
          Resource: !Ref DataBucketArn
        - Effect: Allow
          Action:
            - dynamodb:Query
            - dynamodb:Scan
          Resource: !Ref DataTableArn
```

## Lambda Runtime Versions

| Runtime | Version | Architecture | Status |
|---------|---------|--------------|--------|
| python | 3.13, 3.12, 3.11, 3.10, 3.9, 3.8 | x86_64, arm64 | Supported |
| nodejs | 22.x, 20.x, 18.x | x86_64, arm64 | Supported |
| java | 21, 17, 11 | x86_64, arm64 | Supported |
| go | 1.x | x86_64 | Supported |
| ruby | 3.3, 3.2 | x86_64, arm64 | Supported |
| provided | .al2023, .al2 | x86_64, arm64 | Supported |
| provided.al2 | .arm64 | arm64 | Supported |

## Limits and Quotas

### Lambda Limits

| Resource | Default Limit |
|----------|---------------|
| Concurrent executions per account | 1,000 (configurable) |
| Function memory | 128-10,240 MB |
| Function timeout | 1-900 seconds |
| Deployment package size (zip) | 50 MB (direct), 250 MB (S3) |
| Container image size | 10 GB |
| Ephemeral storage (/tmp) | 512-10,240 MB |
| Layers | 5 layers per function |
| Variables | 4 KB total size |

### API Gateway Limits

| Resource | Default Limit |
|----------|---------------|
| Regional APIs per account | 600 |
| Stage variables per API | 100 |
| Timeout (REST API) | 29 seconds |
| Timeout (HTTP API) | 30 seconds |

### Step Functions Limits

| Resource | Default Limit |
|----------|---------------|
| Execution time | 1 year |
| State payload | 256 KB |
| Execution history | 25,000 events |
| Concurrent executions | 1,000 (standard), unlimited (express) |

## Common Tags for Lambda

```yaml
Resources:
  MyLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: team@example.com
        - Key: ManagedBy
          Value: CloudFormation
        - Key: CostCenter
          Value: "12345"
        - Key: Version
          Value: "1.0.0"
```
