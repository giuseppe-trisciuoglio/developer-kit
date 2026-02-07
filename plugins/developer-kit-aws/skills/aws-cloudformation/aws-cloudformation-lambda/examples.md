# AWS CloudFormation Lambda - Examples

This file contains comprehensive examples for Lambda serverless patterns with CloudFormation.

## Example 1: Lambda with API Gateway REST and Cognito Authorization

Complete API with Lambda backend and Cognito user pool authorization.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda API with API Gateway REST and Cognito authorization

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  FunctionName:
    Type: String
    Default: api-function

  Runtime:
    Type: String
    Default: python3.11

  Handler:
    Type: String
    Default: app.handler

  CodeBucket:
    Type: String
    Description: S3 bucket containing Lambda code

  CognitoUserPoolId:
    Type: AWS::Cognito::UserPool::Id
    Description: Cognito User Pool ID

  DomainName:
    Type: String
    Default: api.example.com

Mappings:
  EnvironmentConfig:
    dev:
      MemorySize: 256
      Timeout: 30
      ThrottlingRateLimit: 100
      ThrottlingBurstLimit: 200
    staging:
      MemorySize: 512
      Timeout: 60
      ThrottlingRateLimit: 500
      ThrottlingBurstLimit: 1000
    production:
      MemorySize: 1024
      Timeout: 120
      ThrottlingRateLimit: 1000
      ThrottlingBurstLimit: 2000

Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  # IAM Role for Lambda
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        - arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-dynamodb-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:Query
                  - dynamodb:Scan
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                Resource: !GetAtt DataTable.Arn
        - PolicyName: !Sub "${AWS::StackName}-secrets-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref SecretsArn

  # Lambda Function
  ApiFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${FunctionName}-${Environment}"
      Runtime: !Ref Runtime
      Handler: !Ref Handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Sub "lambda/${Environment}/api.zip"
      MemorySize: !FindInMap [EnvironmentConfig, !Ref Environment, MemorySize]
      Timeout: !FindInMap [EnvironmentConfig, !Ref Environment, Timeout]
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: !If [IsProduction, INFO, DEBUG]
          TABLE_NAME: !Ref DataTable
      TracingConfig:
        Mode: !If [IsProduction, Active, PassThrough]
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  # DynamoDB Table
  DataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
        - AttributeName: gsi1pk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: gsi1
          KeySchema:
            - AttributeName: gsi1pk
              KeyType: HASH
            - AttributeName: pk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

  # API Gateway REST API
  ApiGatewayRestApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "${AWS::StackName}-api-${Environment}"
      Description: REST API for Lambda backend
      EndpointConfiguration:
        Types:
          - REGIONAL
      MinimumCompressionSize: 1024

  # API Gateway Resources
  ApiGatewayResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      ParentId: !GetAtt ApiGatewayRestApi.RootResourceId
      PathPart: items

  ApiGatewayItemIdResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      ParentId: !Ref ApiGatewayResource
      PathPart: "{id}"

  # API Gateway Methods
  ApiGatewayMethodGet:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      ResourceId: !Ref ApiGatewayResource
      HttpMethod: GET
      AuthorizationType: COGNITO_USER_POOLS
      AuthorizerId: !Ref ApiGatewayAuthorizer
      RequestParameters:
        method.request.querystring.limit: false
        method.request.querystring.startkey: false
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations"
        IntegrationResponses:
          - StatusCode: 200
            ResponseParameters:
              method.response.header.Access-Control-Allow-Origin: "'*'"
              method.response.header.Content-Type: "'application/json'"
          - StatusCode: 400
            ResponseParameters:
              method.response.header.Access-Control-Allow-Origin: "'*'"
        PassthroughBehavior: WHEN_NO_MATCH
      MethodResponses:
        - StatusCode: 200
          ResponseModels:
            application/json: Empty
          ResponseParameters:
            method.response.header.Access-Control-Allow-Origin: true
            method.response.header.Content-Type: true

  ApiGatewayMethodPost:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      ResourceId: !Ref ApiGatewayResource
      HttpMethod: POST
      AuthorizationType: COGNITO_USER_POOLS
      AuthorizerId: !Ref ApiGatewayAuthorizer
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations"
        IntegrationResponses:
          - StatusCode: 201
          - StatusCode: 400
      MethodResponses:
        - StatusCode: 201
          ResponseModels:
            application/json: Empty
        - StatusCode: 400
          ResponseModels:
            application/json: Empty

  ApiGatewayMethodGetById:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      ResourceId: !Ref ApiGatewayItemIdResource
      HttpMethod: GET
      AuthorizationType: COGNITO_USER_POOLS
      AuthorizerId: !Ref ApiGatewayAuthorizer
      RequestParameters:
        method.request.path.id: true
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations"

  # API Gateway Authorizer
  ApiGatewayAuthorizer:
    Type: AWS::ApiGateway::Authorizer
    Properties:
      Name: !Sub "${AWS::StackName}-authorizer"
      Type: COGNITO_USER_POOLS
      RestApiId: !Ref ApiGatewayRestApi
      ProviderARNs:
        - !Sub "arn:aws:cognito-idp:${AWS::Region}:${AWS::AccountId}:userpool/${CognitoUserPoolId}"
      IdentitySource: method.request.header.Authorization
      AuthorizerResultTtlInSeconds: 300

  # API Gateway Deployment
  ApiGatewayDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn:
      - ApiGatewayMethodGet
      - ApiGatewayMethodPost
      - ApiGatewayMethodGetById
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      StageName: !Ref Environment
      StageDescription:
        LoggingLevel: !If [IsProduction, INFO, ERROR]
        DataTraceEnabled: !If [IsProduction, false, true]
        MetricsEnabled: true
        ThrottlingRateLimit: !FindInMap [EnvironmentConfig, !Ref Environment, ThrottlingRateLimit]
        ThrottlingBurstLimit: !FindInMap [EnvironmentConfig, !Ref Environment, ThrottlingBurstLimit]

  # Lambda Permissions
  LambdaPermissionForApiGateway:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ApiFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ApiGatewayRestApi}/*/*/*"

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ApiGatewayRestApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"

  ApiFunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt ApiFunction.Arn

  TableName:
    Description: DynamoDB table name
    Value: !Ref DataTable
```

## Example 2: Lambda with SQS Event Source and DLQ

Lambda function processing messages from SQS queue with dead letter queue.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda function with SQS event source and DLQ

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Execution Role
  LambdaExecutionRole:
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
        - arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: SqsProcessingPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - sqs:DeleteMessage
                  - sqs:ReceiveMessage
                  - sqs:GetQueueAttributes
                Resource: !GetAtt ProcessingQueue.Arn
              - Effect: Allow
                Action:
                  - sqs:DeleteMessage
                  - sqs:SendMessage
                Resource: !GetAtt DeadLetterQueue.Arn

  # Lambda Function
  SqsProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-sqs-processor"
      Runtime: python3.11
      Handler: sqs_handler.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/sqs-processor.zip
      Timeout: 300
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          DLQ_URL: !Ref DeadLetterQueue

  # Main Queue
  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-processing-${Environment}"
      VisibilityTimeout: 360
      MessageRetentionPeriod: 1209600
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
        maxReceiveCount: 5
      KmsMasterKeyId: !Ref QueueKmsKey
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Dead Letter Queue
  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-dlq-${Environment}"
      MessageRetentionPeriod: 604800
      KmsMasterKeyId: !Ref QueueKmsKey

  # Event Source Mapping
  EventSourceMapping:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      FunctionName: !Ref SqsProcessorFunction
      EventSourceArn: !GetAtt ProcessingQueue.Arn
      BatchSize: 10
      MaximumBatchingWindowInSeconds: 60
      ScalingConfig:
        MaximumConcurrency: 10
      FilterCriteria:
        Filters:
          - Pattern: '{"body": {"messageType": ["order", "notification"]}}'
      Enabled: true

Outputs:
  QueueUrl:
    Description: SQS Queue URL
    Value: !Ref ProcessingQueue

  QueueArn:
    Description: SQS Queue ARN
    Value: !GetAtt ProcessingQueue.Arn

  DlqUrl:
    Description: Dead Letter Queue URL
    Value: !Ref DeadLetterQueue
```

## Example 3: Lambda with SNS Topic Subscription

Lambda function subscribed to SNS topic for event processing.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda function with SNS topic subscription

Parameters:
  Environment:
    Type: String
    Default: prod

Resources:
  # Execution Role
  LambdaExecutionRole:
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

  # Lambda Function
  SnsProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-sns-processor"
      Runtime: python3.11
      Handler: sns_handler.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/sns-processor.zip
      Timeout: 60
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment

  # SNS Topic
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-notifications-${Environment}"
      DisplayName: !Sub "${AWS::StackName} Notifications"
      Subscription:
        - Endpoint: !GetAtt SnsProcessorFunction.Arn
          Protocol: lambda
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Topic Policy to allow SNS to invoke Lambda
  TopicPolicy:
    Type: AWS::SNS::TopicPolicy
    Properties:
      Topics:
        - !Ref NotificationTopic
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: sns.amazonaws.com
            Action: sns:Publish
            Resource: !Ref NotificationTopic
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sns:Subscribe
            Resource: !Ref NotificationTopic

  # Lambda Permission for SNS
  LambdaPermissionForSns:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref SnsProcessorFunction
      Action: lambda:InvokeFunction
      Principal: sns.amazonaws.com
      SourceArn: !Ref NotificationTopic

Outputs:
  TopicArn:
    Description: SNS Topic ARN
    Value: !Ref NotificationTopic

  TopicName:
    Description: SNS Topic Name
    Value: !GetAtt NotificationTopic.TopicName
```

## Example 4: Lambda with EventBridge (CloudWatch Events)

Scheduled Lambda function with EventBridge rule.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda function with EventBridge scheduled execution

Parameters:
  Environment:
    Type: String
    Default: production

  ScheduleExpression:
    Type: String
    Default: "rate(5 minutes)"

Resources:
  # Execution Role
  LambdaExecutionRole:
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
        - PolicyName: CloudWatchPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - cloudwatch:PutMetricData
                Resource: "*"

  # Lambda Function
  ScheduledFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-scheduler-${Environment}"
      Runtime: python3.11
      Handler: scheduler.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/scheduler.zip
      Timeout: 300
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment

  # EventBridge Rule
  ScheduledRule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub "${AWS::StackName}-scheduled-rule-${Environment}"
      Description: Triggers Lambda function on schedule
      ScheduleExpression: !Ref ScheduleExpression
      State: ENABLED
      Targets:
        - Id: ScheduledFunction
          Arn: !GetAtt ScheduledFunction.Arn
          RetryPolicy:
            MaximumEventAgeInSeconds: 86400
            MaximumRetryAttempts: 3

  # Lambda Permission for EventBridge
  LambdaPermissionForEventBridge:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ScheduledFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt ScheduledRule.Arn

Outputs:
  RuleArn:
    Description: EventBridge Rule ARN
    Value: !GetAtt ScheduledRule.Arn
```

## Example 5: Lambda with S3 Event Notification

Lambda function triggered by S3 object creation events.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda function with S3 event triggers

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Execution Role
  LambdaExecutionRole:
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
        - PolicyName: S3AccessPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                Resource: !Sub "${UploadBucket.Arn}/*"
              - Effect: Allow
                Action:
                  - s3:GetBucketNotification
                  - s3:PutBucketNotification
                Resource: !Ref UploadBucket

  # Lambda Function
  S3ProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-s3-processor"
      Runtime: python3.11
      Handler: s3_handler.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/s3-processor.zip
      Timeout: 300
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          OUTPUT_BUCKET: !Ref ProcessedBucket

  # Upload Bucket with Lambda notification configuration
  UploadBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-uploads-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      VersioningConfiguration:
        Status: Enabled
      NotificationConfiguration:
        LambdaConfigurations:
          - Event: s3:ObjectCreated:*
            Filter:
              S3Key:
                Rules:
                  - Name: suffix
                    Value: .csv
            Function: !GetAtt S3ProcessorFunction.Arn
          - Event: s3:ObjectCreated:*
            Filter:
              S3Key:
                Rules:
                  - Name: prefix
                    Value: incoming/
            Function: !GetAtt S3ProcessorFunction.Arn
          - Event: s3:ObjectRemoved:*
            Function: !GetAtt S3ProcessorFunction.Arn
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders:
              - "*"
            AllowedMethods:
              - GET
              - PUT
              - POST
            AllowedOrigins:
              - "*"
            MaxAge: 3600
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Processed Bucket
  ProcessedBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-processed-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

  # Lambda Permission for S3
  LambdaPermissionForS3:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref S3ProcessorFunction
      Action: lambda:InvokeFunction
      Principal: s3.amazonaws.com
      SourceArn: !GetAtt UploadBucket.Arn

Outputs:
  UploadBucketName:
    Description: Upload bucket name
    Value: !Ref UploadBucket

  UploadBucketArn:
    Description: Upload bucket ARN
    Value: !GetAtt UploadBucket.Arn
```

## Example 6: Lambda with Step Functions Workflow

Lambda functions orchestrated by Step Functions state machine.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda functions with Step Functions workflow orchestration

Parameters:
  Environment:
    Type: String
    Default: prod

Resources:
  # Lambda Functions
  ValidateItemFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-validate"
      Runtime: python3.11
      Handler: validate.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/validate.zip
      Timeout: 60
      Role: !GetAtt LambdaExecutionRole.Arn

  ProcessItemFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-process"
      Runtime: python3.11
      Handler: process.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/process.zip
      Timeout: 300
      Role: !GetAtt LambdaExecutionRole.Arn

  EnrichItemFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-enrich"
      Runtime: python3.11
      Handler: enrich.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/enrich.zip
      Timeout: 120
      Role: !GetAtt LambdaExecutionRole.Arn

  NotifyCompletionFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-notify"
      Runtime: python3.11
      Handler: notify.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/notify.zip
      Timeout: 60
      Role: !GetAtt LambdaExecutionRole.Arn

  # Execution Role
  LambdaExecutionRole:
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

  # Step Functions Execution Role
  StepFunctionsExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-sfn-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: states.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: LambdaInvokePolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource:
                  - !GetAtt ValidateItemFunction.Arn
                  - !GetAtt ProcessItemFunction.Arn
                  - !GetAtt EnrichItemFunction.Arn
                  - !GetAtt NotifyCompletionFunction.Arn
        - PolicyName: CloudWatchLogsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: !Sub "${StateMachineLogGroup.Arn}:*"

  # State Machine Log Group
  StateMachineLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/state-machine/${AWS::StackName}"
      RetentionInDays: 30

  # Step Functions State Machine
  ProcessingStateMachine:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      StateMachineName: !Sub "${AWS::StackName}-processor-${Environment}"
      StateMachineType: STANDARD
      DefinitionString: !Sub |
        {
          "Comment": "Item processing state machine",
          "StartAt": "ValidateItem",
          "States": {
            "ValidateItem": {
              "Type": "Task",
              "Resource": "${ValidateItemFunction.Arn}",
              "Retry": [
                {
                  "ErrorEquals": ["States.TaskFailed"],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 3,
                  "BackoffRate": 2
                }
              ],
              "Next": "ProcessItem"
            },
            "ProcessItem": {
              "Type": "Task",
              "Resource": "${ProcessItemFunction.Arn}",
              "Retry": [
                {
                  "ErrorEquals": ["States.TaskFailed"],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 2,
                  "BackoffRate": 2
                }
              ],
              "Next": "EnrichItem"
            },
            "EnrichItem": {
              "Type": "Task",
              "Resource": "${EnrichItemFunction.Arn}",
              "Retry": [
                {
                  "ErrorEquals": ["States.TaskFailed"],
                  "IntervalSeconds": 3,
                  "MaxAttempts": 3,
                  "BackoffRate": 1.5
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": ["States.ALL"],
                  "Next": "HandleEnrichmentFailure"
                }
              ],
              "Next": "NotifyCompletion"
            },
            "NotifyCompletion": {
              "Type": "Task",
              "Resource": "${NotifyCompletionFunction.Arn}",
              "End": true
            },
            "HandleEnrichmentFailure": {
              "Type": "Pass",
              "ResultPath": "$.error",
              "Next": "NotifyCompletion"
            }
          }
        }
      RoleArn: !GetAtt StepFunctionsExecutionRole.Arn
      LoggingConfiguration:
        Level: ALL
        IncludeExecutionData: true
        Destinations:
          - CloudWatchLogsLogGroup: !Ref StateMachineLogGroup
      Tags:
        - Key: Environment
          Value: !Ref Environment

Outputs:
  StateMachineArn:
    Description: Step Functions State Machine ARN
    Value: !Ref ProcessingStateMachine
```

## Example 7: Lambda with Layers

Lambda function using shared layers for dependencies.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda function with shared layers

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Common Library Layer
  CommonLibraryLayer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: !Sub "${AWS::StackName}-common-lib"
      Description: Common utilities, logger, and validators
      Content:
        S3Bucket: !Ref LayersBucket
        S3Key: layers/common-lib.zip
      CompatibleRuntimes:
        - python3.9
        - python3.10
        - python3.11
        - python3.12
      CompatibleArchitectures:
        - x86_64
        - arm64

  # Data Processing Layer
  DataProcessingLayer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: !Sub "${AWS::StackName}-data-processing"
      Description: Data processing utilities (pandas, numpy)
      Content:
        S3Bucket: !Ref LayersBucket
        S3Key: layers/data-processing.zip
      CompatibleRuntimes:
        - python3.11
        - python3.12
      CompatibleArchitectures:
        - x86_64

  # ML Utilities Layer
  MlUtilitiesLayer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: !Sub "${AWS::StackName}-ml-utilities"
      Description: ML utilities (scikit-learn, torch)
      Content:
        S3Bucket: !Ref LayersBucket
        S3Key: layers/ml-utilities.zip
      CompatibleRuntimes:
        - python3.11
        - python3.12
      CompatibleArchitectures:
        - x86_64

  # Lambda Function using layers
  DataProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-data-processor"
      Runtime: python3.11
      Handler: processor.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/data-processor.zip
      MemorySize: 2048
      Timeout: 900
      Role: !GetAtt LambdaExecutionRole.Arn
      Layers:
        - !Ref CommonLibraryLayer
        - !Ref DataProcessingLayer
      Environment:
        Variables:
          PYTHONPATH: "/var/task:/opt"
          ENVIRONMENT: !Ref Environment

  # Lambda Execution Role
  LambdaExecutionRole:
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

Outputs:
  CommonLibraryLayerArn:
    Description: Common library layer ARN
    Value: !Ref CommonLibraryLayer

  DataProcessingLayerArn:
    Description: Data processing layer ARN
    Value: !Ref DataProcessingLayer
```

## Example 8: Lambda with Provisioned Concurrency

Lambda function with provisioned concurrency for predictable latency.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda function with provisioned concurrency for low latency

Parameters:
  Environment:
    Type: String
    Default: prod

  ProvisionedConcurrentExecutions:
    Type: Number
    Default: 10
    Description: Number of provisioned concurrent executions

Resources:
  # Lambda Function
  LowLatencyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-low-latency"
      Runtime: python3.11
      Handler: app.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/low-latency.zip
      MemorySize: 1024
      Timeout: 30
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment

  # Lambda Execution Role
  LambdaExecutionRole:
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

  # Provisioned Concurrency Configuration
  ProvisionedConcurrencyConfig:
    Type: AWS::Lambda::ProvisionedConcurrencyConfig
    Properties:
      FunctionName: !Ref LowLatencyFunction
      ProvisionedConcurrentExecutions: !Ref ProvisionedConcurrentExecutions
      Qualifier: $LATEST
      ProvisionedExecutionTarget:
        AllocationStrategy: PRICE_OPTIMIZED

  # Auto Alias
  LambdaVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref LowLatencyFunction
      Description: Version with provisioned concurrency

Outputs:
  ProvisionedConcurrencyArn:
    Description: Provisioned concurrency configuration ARN
    Value: !Ref ProvisionedConcurrencyConfig

  FunctionVersion:
    Description: Lambda function version
    Value: !Ref LambdaVersion
```

## Example 9: Complete Production Lambda with Monitoring

Complete production-ready Lambda with CloudWatch monitoring, alarms, and logging.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production Lambda with comprehensive monitoring

Parameters:
  Environment:
    Type: String
    Default: production

  FunctionName:
    Type: String
    Default: api-function

  Runtime:
    Type: String
    Default: python3.11

  AlertEmail:
    Type: String
    Description: Email for alert notifications

Mappings:
  EnvironmentConfig:
    dev:
      MemorySize: 256
      Timeout: 30
      ReservedConcurrency: 10
    staging:
      MemorySize: 512
      Timeout: 60
      ReservedConcurrency: 50
    production:
      MemorySize: 1024
      Timeout: 120
      ReservedConcurrency: 100

Resources:
  # IAM Role with CloudWatch full access
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        - arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
      Policies:
        - PolicyName: CloudWatchMetricsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - cloudwatch:PutMetricData
                Resource: "*"

  # Lambda Function
  ProductionFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${FunctionName}-${Environment}"
      Runtime: !Ref Runtime
      Handler: app.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Sub "lambda/${Environment}/function.zip"
      MemorySize: !FindInMap [EnvironmentConfig, !Ref Environment, MemorySize]
      Timeout: !FindInMap [EnvironmentConfig, !Ref Environment, Timeout]
      Role: !GetAtt LambdaExecutionRole.Arn
      ReservedConcurrentExecutions: !FindInMap [EnvironmentConfig, !Ref Environment, ReservedConcurrency]
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO
      TracingConfig:
        Mode: Active

  # Log Group with encryption
  LambdaLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/lambda/${ProductionFunction}"
      RetentionInDays: 30
      KmsKeyId: !Ref LogKmsKey

  # Metric Filter for Errors
  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref LambdaLogGroup
      FilterPattern: 'ERROR'
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${AWS::StackName}/Lambda"
          MetricName: ErrorCount

  # Metric Filter for Warnings
  WarningMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref LambdaLogGroup
      FilterPattern: 'WARNING'
      MetricTransformations:
        - MetricValue: "1"
          MetricNamespace: !Sub "${AWS::StackName}/Lambda"
          MetricName: WarningCount

  # CloudWatch Alarms
  HighErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-error-rate"
      AlarmDescription: Alert when error rate exceeds 1%
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref ProductionFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic
      OKActions:
        - !Ref AlertTopic

  HighLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-latency"
      AlarmDescription: Alert when p99 latency exceeds 5 seconds
      MetricName: Duration
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref ProductionFunction
      Statistic: p99
      Period: 60
      EvaluationPeriods: 3
      Threshold: 5000
      ComparisonOperator: GreaterThanThreshold

  HighThrottlesAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-throttles"
      AlarmDescription: Alert when throttling occurs
      MetricName: Throttles
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref ProductionFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 3
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold

  HighInvocationAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-invocations"
      AlarmDescription: Alert on unusual high invocation count
      MetricName: Invocations
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref ProductionFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 10000
      ComparisonOperator: GreaterThanThreshold

  # SNS Topic for Alerts
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-alerts-${Environment}"
      Subscription:
        - Endpoint: !Ref AlertEmail
          Protocol: email

  # Lambda Event Invoke Config
  EventInvokeConfig:
    Type: AWS::Lambda::EventInvokeConfig
    Properties:
      FunctionName: !Ref ProductionFunction
      MaximumEventAgeInSeconds: 3600
      MaximumRetryAttempts: 2
      Qualifier: $LATEST

  # Lambda URL for direct invocation
  LambdaFunctionUrl:
    Type: AWS::Lambda::Url
    Properties:
      AuthType: AWS_IAM
      TargetFunctionArn: !GetAtt ProductionFunction.Arn
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

  # Lambda Permission for URL
  LambdaPermissionForUrl:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ProductionFunction
      Action: lambda:InvokeFunctionUrl
      Principal: "*"

Outputs:
  FunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt ProductionFunction.Arn

  FunctionUrl:
    Description: Lambda function URL
    Value: !GetAtt LambdaFunctionUrl.Url

  LogGroupName:
    Description: CloudWatch log group name
    Value: !Ref LambdaLogGroup
```

## Example 10: Lambda with SAM Globals

Using SAM Globals to reduce template repetition.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31
Description: Lambda functions with SAM Globals for configuration reuse

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    Tracing: Active
    Environment:
      Variables:
        LOG_LEVEL: INFO
        ENVIRONMENT: !Ref Environment
    Metadata:
      DockerBuild: true
      Dockerfile: Dockerfile
      DockerContext: lambda_functions/
    VpcConfig:
      SecurityGroupIds: !Ref SecurityGroupIds
      SubnetIds: !Ref SubnetIds

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  SecurityGroupIds:
    Type: List<AWS::EC2::SecurityGroup::Id>

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  # API Function
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-api"
      Handler: api.handler
      CodeUri: lambda_functions/api/
      MemorySize: 512
      Timeout: 60
      Policies:
        - DynamoDBWritePolicy:
            TableName: !Ref DataTable
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /api/{proxy+}
            Method: ANY
            RestApiId: !Ref ApiGateway

  # Data Processing Function
  DataFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-data"
      Handler: data.handler
      CodeUri: lambda_functions/data/
      MemorySize: 2048
      Timeout: 300
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref InputBucket
        - S3WritePolicy:
            BucketName: !Ref OutputBucket
      Events:
        S3Upload:
          Type: S3
          Properties:
            Bucket: !Ref InputBucket
            Events: s3:ObjectCreated:*

  # Background Job Function
  JobFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-jobs"
      Handler: jobs.handler
      CodeUri: lambda_functions/jobs/
      MemorySize: 256
      Policies:
        - SQSReadPolicy:
            QueueName: !Ref JobQueue
      Events:
        SqsQueue:
          Type: SQS
          Properties:
            Queue: !GetAtt JobQueue.Arn
            BatchSize: 10

  # DynamoDB Table
  DataTable:
    Type: AWS::Serverless::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-data"
      PrimaryKey:
        Name: id
        Type: String
      BillingMode: PAY_PER_REQUEST

  # API Gateway
  ApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      Name: !Sub "${AWS::StackName}-api"
      StageName: !Ref Environment
      Cors:
        AllowOrigin: "*"
        AllowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

  # S3 Buckets
  InputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-input-${AWS::AccountId}-${AWS::Region}"

  OutputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-output-${AWS::AccountId}-${AWS::Region}"

  # SQS Queue
  JobQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-jobs"
      VisibilityTimeout: 360
      MessageRetentionPeriod: 1209600

Outputs:
  ApiEndpoint:
    Value: !Sub "https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"
```
