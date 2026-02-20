# Deployment Strategies for NestJS Lambda

## Overview

This reference covers deployment strategies, CI/CD pipelines, and optimization techniques for NestJS Lambda applications using AWS SAM and Serverless Framework.

## AWS SAM (Serverless Application Model)

### Installation

```bash
# macOS
brew tap aws/tap
brew install aws-sam-cli

# Linux
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install

# Verify installation
sam --version
```

### Project Structure

```
my-nestjs-lambda/
├── src/                      # NestJS source code
├── dist/                     # Compiled output
├── template.yaml             # SAM template
├── samconfig.toml            # SAM configuration
├── lambda.ts                 # Lambda entry point
├── package.json
└── tsconfig.json
```

### SAM Template Reference

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: NestJS Lambda Application

Globals:
  Function:
    Timeout: 29
    MemorySize: 512
    Runtime: nodejs20.x
    Architectures:
      - x86_64
    Environment:
      Variables:
        NODE_ENV: production
        LOG_LEVEL: info
    Tags:
      Application: NestJS API
      Environment: !Ref Environment

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Deployment environment

  DatabaseUrl:
    Type: String
    NoEcho: true
    Description: Database connection string

  AllowedOrigins:
    Type: String
    Default: ""
    Description: Comma-separated list of allowed CORS origins (leave empty to disable CORS)

Conditions:
  IsProduction: !Equals [!Ref Environment, prod]

Resources:
  # API Gateway
  ApiGatewayApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
        AllowOrigin: !Sub "'${AllowedOrigins}'"
        MaxAge: "'600'"
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
            Identity:
              Header: Authorization
              ValidationExpression: ^Bearer [-0-9a-zA-Z\._]*$

  # Lambda Function
  NestJSApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub '${AWS::StackName}-api'
      Handler: dist/lambda.handler
      CodeUri: ./
      Description: NestJS API Lambda function
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseUrl
          JWT_SECRET: !Sub '{{resolve:secretsmanager:${JWTSecret}:SecretString:jwt}}'
          COGNITO_USER_POOL_ID: !Ref UserPool
          COGNITO_CLIENT_ID: !Ref UserPoolClient
      Events:
        ApiRoot:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGatewayApi
            Path: /
            Method: ANY
        ApiProxy:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGatewayApi
            Path: /{proxy+}
            Method: ANY
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: !If [IsProduction, 5, 0]
      AutoPublishAlias: live
      DeploymentPreference:
        Type: Canary10Percent5Minutes
        Alarms:
          - !Ref ErrorAlarm
          - !Ref LatencyAlarm
        Hooks:
          PreTraffic: !Ref PreTrafficHookFunction
          PostTraffic: !Ref PostTrafficHookFunction

  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
      Policies:
        - PolicyName: CloudWatchLogsPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogStreams
                Resource: !Sub 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/*'

        - PolicyName: SecretsManagerPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref JWTSecret

        - PolicyName: DynamoDBPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource: !GetAtt DynamoDBTable.Arn

        - PolicyName: S3Policy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                Resource: !Sub '${S3Bucket.Arn}/*'

  # VPC Configuration for RDS access
  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Lambda functions
      VpcId: !Ref VPC
      SecurityGroupIngress: []
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          CidrIp: !Ref VPCCidr

  # DynamoDB Table
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub '${AWS::StackName}-data'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
        - AttributeName: GSI1SK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: GSI1SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: !If [IsProduction, true, false]

  # S3 Bucket
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-assets-${AWS::AccountId}'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      LifecycleConfiguration:
        Rules:
          - Id: ExpireOldVersions
            Status: Enabled
            NoncurrentVersionExpirationInDays: 30

  # Secrets Manager
  JWTSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '${AWS::StackName}/jwt-secret'
      Description: JWT signing secret
      GenerateSecretString:
        SecretStringTemplate: '{"jwt":""}'
        GenerateStringKey: jwt
        PasswordLength: 32
        ExcludeCharacters: '"@/\'

  # CloudWatch Alarms
  ErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-errors'
      AlarmDescription: Lambda error rate alarm
      MetricName: Errors
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref NestJSApiFunction

  LatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-latency'
      AlarmDescription: Lambda duration alarm
      MetricName: Duration
      Namespace: AWS/Lambda
      Statistic: p99
      Period: 60
      EvaluationPeriods: 2
      Threshold: 5000
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref NestJSApiFunction

  # CloudWatch Log Group
  LambdaLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/lambda/${NestJSApiFunction}'
      RetentionInDays: !If [IsProduction, 30, 7]

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${ApiGatewayApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}/'
    Export:
      Name: !Sub '${AWS::StackName}-api-url'

  FunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt NestJSApiFunction.Arn
    Export:
      Name: !Sub '${AWS::StackName}-function-arn'
```

### SAM Configuration (samconfig.toml)

```toml
version = 0.1

[default]
[default.global.parameters]
stack_name = "nestjs-lambda-api"

[default.build.parameters]
cached = true
parallel = true

[default.validate.parameters]
lint = true

[default.deploy.parameters]
capabilities = "CAPABILITY_IAM CAPABILITY_AUTO_EXPAND"
confirm_changeset = true
resolve_s3 = true
s3_prefix = "nestjs-lambda-api"
region = "us-east-1"
image_repositories = []
parameter_overrides = [
    "Environment=dev"
]

[default.deploy.parameters.globals]
[default.deploy.parameters.globals.parameters]
parallel = true

[dev.deploy.parameters]
stack_name = "nestjs-lambda-api-dev"
parameter_overrides = [
    "Environment=dev",
    "DatabaseUrl=postgres://..."
]

[staging.deploy.parameters]
stack_name = "nestjs-lambda-api-staging"
parameter_overrides = [
    "Environment=staging",
    "DatabaseUrl=postgres://..."
]

[prod.deploy.parameters]
stack_name = "nestjs-lambda-api-prod"
parameter_overrides = [
    "Environment=prod",
    "DatabaseUrl=postgres://..."
]

[default.sync.parameters]
watch = true

[default.local_start_api.parameters]
warm_containers = "EAGER"

[default.local_start_lambda.parameters]
warm_containers = "EAGER"
```

### SAM Commands

```bash
# Initialize SAM project
sam init --runtime nodejs20.x --dependency-manager npm --app-template hello-world

# Validate template
sam validate --lint

# Build application
sam build

# Local development
sam local invoke NestJSApiFunction -e events/api-event.json
sam local start-api --warm-containers EAGER

# Deploy
sam deploy --guided
sam deploy --config-env prod

# Sync (for development)
sam sync --watch

# Logs
sam logs -n NestJSApiFunction --tail

# Delete stack
sam delete
```

### SAM Policy Templates

```yaml
# Inline policy for specific AWS services
Policies:
  - S3ReadPolicy:
      BucketName: !Ref S3Bucket
  - S3WritePolicy:
      BucketName: !Ref S3Bucket
  - DynamoDBReadPolicy:
      TableName: !Ref DynamoDBTable
  - DynamoDBCrudPolicy:
      TableName: !Ref DynamoDBTable
  - SESBulkTemplatedCrudPolicy:
      IdentityName: !Ref SESIdentity
  - SQSSendMessagePolicy:
      QueueName: !GetAtt SQSQueue.QueueName
  - SNSPublishMessagePolicy:
      TopicName: !GetAtt SNSTopic.TopicName
  - CloudWatchPutMetricPolicy: {}
  - VPCAccessPolicy: {}
```

## Serverless Framework

### Installation

```bash
# Install Serverless Framework
npm install -g serverless

# Or use npx
npx serverless

# Verify installation
serverless --version
```

### Project Structure

```
my-nestjs-lambda/
├── src/                      # NestJS source code
├── dist/                     # Compiled output
├── serverless.yml            # Serverless configuration
├── serverless.ts             # TypeScript config (optional)
├── lambda.ts                 # Lambda entry point
├── package.json
└── webpack.config.js
```

### Serverless Configuration Reference

```yaml
service: nestjs-lambda-api

frameworkVersion: '3'

provider:
  name: aws
  runtime: nodejs20.x
  stage: ${opt:stage, 'dev'}
  region: ${opt:region, 'us-east-1'}
  memorySize: 512
  timeout: 29
  logRetentionInDays: 14
  versionFunctions: true

  # Environment variables
  environment:
    NODE_ENV: production
    STAGE: ${self:provider.stage}
    SERVICE_NAME: ${self:service}
    DATABASE_URL: ${ssm:/${self:service}/${self:provider.stage}/database-url}
    JWT_SECRET: ${ssm:/${self:service}/${self:provider.stage}/jwt-secret~true}
    SENTRY_DSN: ${ssm:/${self:service}/${self:provider.stage}/sentry-dsn~true}

  # IAM role statements
  iam:
    role:
      name: ${self:service}-${self:provider.stage}-lambda-role
      statements:
        # CloudWatch Logs
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource:
            - 'arn:aws:logs:${aws:region}:${aws:accountId}:log-group:/aws/lambda/*:*:*'

        # X-Ray Tracing
        - Effect: Allow
          Action:
            - xray:PutTraceSegments
            - xray:PutTelemetryRecords
          Resource:
            - !Sub 'arn:aws:xray:${aws:region}:${aws:accountId}:*'

        # SSM Parameter Store
        - Effect: Allow
          Action:
            - ssm:GetParameter
            - ssm:GetParameters
          Resource:
            - 'arn:aws:ssm:${aws:region}:${aws:accountId}:parameter/${self:service}/*'

        # DynamoDB
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
            - dynamodb:Query
            - dynamodb:Scan
            - dynamodb:BatchGetItem
            - dynamodb:BatchWriteItem
          Resource:
            - !GetAtt DynamoDBTable.Arn
            - !Sub '${DynamoDBTable.Arn}/index/*'

        # S3
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:PutObject
            - s3:DeleteObject
            - s3:ListBucket
          Resource:
            - !GetAtt S3Bucket.Arn
            - !Sub '${S3Bucket.Arn}/*'

        # SQS
        - Effect: Allow
          Action:
            - sqs:SendMessage
            - sqs:SendMessageBatch
            - sqs:ReceiveMessage
            - sqs:DeleteMessage
            - sqs:GetQueueAttributes
          Resource:
            - !GetAtt SQSQueue.Arn

        # SNS
        - Effect: Allow
          Action:
            - sns:Publish
          Resource:
            - !Ref SNSTopic

        # SES
        - Effect: Allow
          Action:
            - ses:SendEmail
            - ses:SendRawEmail
            - ses:SendTemplatedEmail
          Resource:
            - !Sub 'arn:aws:ses:${aws:region}:${aws:accountId}:identity/${self:custom.email.from}'
          Condition:
            StringEquals:
              ses:FromAddress: ${self:custom.email.from}

        # Secrets Manager
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource:
            - 'arn:aws:secretsmanager:${aws:region}:${aws:accountId}:secret:${self:service}/*'

  # VPC configuration
  vpc:
    securityGroupIds:
      - !Ref LambdaSecurityGroup
    subnetIds:
      - !Ref PrivateSubnet1
      - !Ref PrivateSubnet2

  # API Gateway
  apiGateway:
    binaryMediaTypes:
      - '*/*'
    minimumCompressionSize: 1024

  # Tracing
  tracing:
    lambda: true
    apiGateway: true

  # Tags
  tags:
    Service: ${self:service}
    Stage: ${self:provider.stage}
    ManagedBy: serverless

  # Stack tags
  stackTags:
    Service: ${self:service}
    Stage: ${self:provider.stage}

plugins:
  - serverless-esbuild
  - serverless-offline
  - serverless-plugin-aws-alerts
  - serverless-plugin-warmup

custom:
  # esbuild configuration
  esbuild:
    bundle: true
    minify: ${self:custom.isProduction}
    sourcemap: true
    target: node20
    platform: node
    format: cjs
    mainFields:
      - main
      - module
    external:
      - '@nestjs/microservices'
      - '@nestjs/websockets'
      - 'class-transformer/storage'
      - 'aws-sdk'
    keepNames: true
    splitting: false
    concurrency: 10
    packager: npm
    installExtraArgs: ['--legacy-peer-deps']

  # Offline configuration
  serverless-offline:
    httpPort: 3000
    host: 0.0.0.0
    lambdaPort: 3002
    noPrependStageInUrl: true

  # Warming configuration
  warmup:
    warmer:
      enabled: ${self:custom.isProduction}
      events:
        - schedule: rate(5 minutes)
      concurrency: 2

  # Alerts configuration
  alerts:
    stages:
      - prod
    dashboards: true
    topics:
      alarm:
        - !Ref AlarmTopic
    alarms:
      - functionErrors
      - functionThrottles
      - functionInvocations
      - functionDuration
    definitions:
      functionErrors:
        threshold: 1
        statistic: Sum
        period: 60
        evaluationPeriods: 1
        comparisonOperator: GreaterThanOrEqualToThreshold
      functionDuration:
        threshold: 5000
        statistic: p99
        period: 60
        evaluationPeriods: 2
        comparisonOperator: GreaterThanThreshold

  # Custom variables
  isProduction: !Equals ['${self:provider.stage}', 'prod']
  email:
    from: noreply@example.com

package:
  individually: false
  patterns:
    - '!**/*'
    - 'dist/**'
    - '!dist/**/*.map'
    - '!dist/**/*.spec.js'
    - '!dist/**/*.test.js'
    - '!dist/**/__tests__/**'
    - 'package.json'

functions:
  api:
    name: ${self:service}-${self:provider.stage}-api
    handler: dist/lambda.handler
    description: NestJS API Lambda function
    memorySize: 512
    timeout: 29
    reservedConcurrency: 100
    provisionedConcurrency: ${self:custom.isProduction, 0}
    environment:
      FUNCTION_NAME: api
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors:
            origin: ${self:custom.cors.origins}
            headers:
              - Content-Type
              - Authorization
              - X-Amz-Date
              - X-Api-Key
              - X-Amz-Security-Token
              - X-Amz-User-Agent
            allowCredentials: true
      - http:
          path: /
          method: ANY
          cors: true
    iamRoleStatements:
      - Effect: Allow
        Action:
          - execute-api:Invoke
        Resource:
          - !Sub 'arn:aws:execute-api:${aws:region}:${aws:accountId}:${ApiGatewayRestApiId}/*'

  worker:
    name: ${self:service}-${self:provider.stage}-worker
    handler: dist/worker.handler
    description: Background worker Lambda
    memorySize: 256
    timeout: 900
    events:
      - sqs:
          arn:
            Fn::GetAtt:
              - SQSQueue
              - Arn
          batchSize: 10
          maximumBatchingWindowInSeconds: 5
          functionResponseType: ReportBatchItemFailures
          destinationConfig:
            onFailure:
              destination:
                Fn::GetAtt:
                  - DLQ
                  - Arn

  scheduler:
    name: ${self:service}-${self:provider.stage}-scheduler
    handler: dist/scheduler.handler
    description: Scheduled task Lambda
    memorySize: 256
    timeout: 300
    events:
      - schedule:
          rate: rate(1 hour)
          input:
            task: cleanup
      - schedule:
          rate: cron(0 2 * * ? *)
          input:
            task: daily-report

resources:
  Resources:
    # DynamoDB Table
    DynamoDBTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-${self:provider.stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: PK
            AttributeType: S
          - AttributeName: SK
            AttributeType: S
        KeySchema:
          - AttributeName: PK
            KeyType: HASH
          - AttributeName: SK
            KeyType: RANGE
        PointInTimeRecoverySpecification:
          PointInTimeRecoveryEnabled: ${self:custom.isProduction}
        SSESpecification:
          SSEEnabled: true
        Tags:
          - Key: Service
            Value: ${self:service}
          - Key: Stage
            Value: ${self:provider.stage}

    # S3 Bucket
    S3Bucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: ${self:service}-${self:provider.stage}-assets-${aws:accountId}
        PublicAccessBlockConfiguration:
          BlockPublicAcls: true
          BlockPublicPolicy: true
          IgnorePublicAcls: true
          RestrictPublicBuckets: true
        BucketEncryption:
          ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SSEAlgorithm: AES256
        LifecycleConfiguration:
          Rules:
            - Id: TransitionToIA
              Status: Enabled
              TransitionInDays: 30
              StorageClass: STANDARD_IA
            - Id: DeleteOldVersions
              Status: Enabled
              NoncurrentVersionExpirationInDays: 30

    # SQS Queue
    SQSQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-${self:provider.stage}-queue
        VisibilityTimeout: 960
        MessageRetentionPeriod: 1209600
        RedrivePolicy:
          deadLetterTargetArn:
            Fn::GetAtt:
              - DLQ
              - Arn
          maxReceiveCount: 3

    # Dead Letter Queue
    DLQ:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-${self:provider.stage}-dlq
        MessageRetentionPeriod: 1209600

    # SNS Topic
    SNSTopic:
      Type: AWS::SNS::Topic
      Properties:
        TopicName: ${self:service}-${self:provider.stage}-topic

    # Alarm Topic
    AlarmTopic:
      Type: AWS::SNS::Topic
      Properties:
        TopicName: ${self:service}-${self:provider.stage}-alarms

    # Security Group
    LambdaSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupName: ${self:service}-${self:provider.stage}-lambda-sg
        GroupDescription: Security group for Lambda functions
        VpcId:
          Ref: VPC
        SecurityGroupEgress:
          - IpProtocol: tcp
            FromPort: 443
            ToPort: 443
            CidrIp: 0.0.0.0/0
          - IpProtocol: tcp
            FromPort: 5432
            ToPort: 5432
            CidrIp:
              Ref: VPCCidr

  Outputs:
    ApiGatewayRestApiId:
      Value:
        Ref: ApiGatewayRestApi
      Export:
        Name: ${self:service}-${self:provider.stage}-restApiId

    ApiGatewayRestApiRootResourceId:
      Value:
        Fn::GetAtt:
          - ApiGatewayRestApi
          - RootResourceId
      Export:
        Name: ${self:service}-${self:provider.stage}-rootResourceId
```

### Serverless TypeScript Configuration

```typescript
// serverless.ts
import type { AWS } from '@serverless/typescript';

const serverlessConfiguration: AWS = {
  service: 'nestjs-lambda-api',
  frameworkVersion: '3',
  plugins: [
    'serverless-esbuild',
    'serverless-offline',
    'serverless-plugin-aws-alerts',
  ],
  provider: {
    name: 'aws',
    runtime: 'nodejs20.x',
    stage: '${opt:stage, "dev"}',
    region: '${opt:region, "us-east-1"}',
    memorySize: 512,
    timeout: 29,
    environment: {
      NODE_ENV: 'production',
      DATABASE_URL: '${ssm:/${self:service}/${self:provider.stage}/database-url}',
    },
    iam: {
      role: {
        statements: [
          {
            Effect: 'Allow',
            Action: ['logs:*'],
            Resource: {
              'Fn::Sub': 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${self:service}-*',
            },
          },
        ],
      },
    },
  },
  functions: {
    api: {
      handler: 'dist/lambda.handler',
      events: [
        {
          http: {
            path: '/{proxy+}',
            method: 'ANY',
            cors: true,
          },
        },
      ],
    },
  },
  custom: {
    esbuild: {
      bundle: true,
      minify: true,
      target: 'node20',
    },
  },
};

module.exports = serverlessConfiguration;
```

### Serverless Commands

```bash
# Deploy
serverless deploy
serverless deploy --stage prod --region eu-west-1
serverless deploy function -f api

# Offline development
serverless offline
serverless offline start --reloadHandler

# Logs
serverless logs -f api -t
serverless logs -f api --startTime 5m

# Info
serverless info
serverless info --stage prod

# Remove
serverless remove
serverless remove --stage dev

# Print compiled config
serverless print

# Invoke function
serverless invoke -f api -p event.json
serverless invoke local -f api -p event.json

# Metrics
serverless metrics
serverless metrics -f api --startTime 1h

# Plugins
serverless plugin install -n serverless-esbuild
serverless plugin uninstall -n serverless-esbuild
serverless plugin list
serverless plugin search esbuild
```

## CI/CD Pipeline

### GitHub Actions with SAM

```yaml
# .github/workflows/sam-deploy.yml
name: SAM Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  NODE_VERSION: '20'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run lint
        run: npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup SAM
        uses: aws-actions/setup-sam@v2

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: SAM Build
        run: sam build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: sam-build
          path: |
            .aws-sam/
            dist/

  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: development
    steps:
      - uses: actions/checkout@v4

      - name: Setup SAM
        uses: aws-actions/setup-sam@v2

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: sam-build

      - name: SAM Deploy (Dev)
        run: |
          sam deploy --config-env dev \
                     --no-confirm-changeset \
                     --no-fail-on-empty-changeset

  deploy-prod:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Setup SAM
        uses: aws-actions/setup-sam@v2

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: sam-build

      - name: SAM Deploy (Prod)
        run: |
          sam deploy --config-env prod \
                     --no-confirm-changeset \
                     --no-fail-on-empty-changeset
```

### GitHub Actions with Serverless Framework

```yaml
# .github/workflows/serverless-deploy.yml
name: Serverless Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  NODE_VERSION: '20'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run lint
        run: npm run lint

  deploy-dev:
    needs: test
    runs-on: ubuntu-latest
    environment: development
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install Serverless
        run: npm install -g serverless

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to dev
        run: serverless deploy --stage dev

  deploy-prod:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install Serverless
        run: npm install -g serverless

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to production
        run: serverless deploy --stage prod
```

## Build Optimization

### Webpack Configuration

```javascript
// webpack.config.js
const path = require('path');
const nodeExternals = require('webpack-node-externals');
const TerserPlugin = require('terser-webpack-plugin');
const { IgnorePlugin } = require('webpack');

module.exports = {
  entry: './lambda.ts',
  target: 'node',
  mode: 'production',
  externals: [nodeExternals()],
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: {
          loader: 'ts-loader',
          options: {
            transpileOnly: true,
            experimentalWatchApi: true,
          },
        },
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.ts', '.js'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  output: {
    filename: 'lambda.js',
    path: path.resolve(__dirname, 'dist'),
    libraryTarget: 'commonjs2',
    clean: true,
  },
  optimization: {
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          keep_classnames: true,
          keep_fnames: true,
          compress: {
            drop_console: true,
            drop_debugger: true,
          },
        },
      }),
    ],
  },
  plugins: [
    // Ignore optional dependencies that aren't needed in Lambda
    new IgnorePlugin({
      resourceRegExp: /^@nestjs\/microservices$/,
    }),
    new IgnorePlugin({
      resourceRegExp: /^@nestjs\/websockets$/,
    }),
  ],
  stats: {
    modules: true,
    warnings: false,
  },
};
```

### esbuild Configuration

```javascript
// esbuild.config.js
const esbuild = require('esbuild');
const { nodeExternalsPlugin } = require('esbuild-node-externals');

async function build() {
  try {
    await esbuild.build({
      entryPoints: ['lambda.ts', 'worker.ts', 'scheduler.ts'],
      bundle: true,
      platform: 'node',
      target: 'node20',
      outdir: 'dist',
      minify: process.env.NODE_ENV === 'production',
      sourcemap: true,
      splitting: false,
      format: 'cjs',
      metafile: true,
      external: [
        '@nestjs/microservices',
        '@nestjs/websockets',
        'class-transformer/storage',
        'aws-sdk', // Provided by Lambda runtime
      ],
      define: {
        'process.env.NODE_ENV': '"production"',
      },
      plugins: [
        nodeExternalsPlugin({
          allowList: ['@nestjs/core', '@nestjs/common', '@nestjs/platform-express'],
        }),
      ],
    });

    console.log('Build completed successfully');
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

build();
```

### esbuild with Serverless

```yaml
# serverless.yml with esbuild
custom:
  esbuild:
    bundle: true
    minify: ${self:custom.isProduction}
    sourcemap: true
    target: node20
    platform: node
    format: cjs
    mainFields:
      - main
      - module
    external:
      - '@nestjs/microservices'
      - '@nestjs/websockets'
      - 'class-transformer/storage'
      - 'aws-sdk'
    keepNames: true
    splitting: false
    concurrency: 10
    packager: npm
    installExtraArgs:
      - '--legacy-peer-deps'
    # Exclude specific paths from bundling
    exclude:
      - './test/**'
      - './**/*.spec.ts'
      - './**/*.test.ts'
```

## Package Optimization

### Dependencies to Exclude

```json
{
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@codegenie/serverless-express": "^4.0.0",
    "aws-lambda": "^1.0.0",
    "express": "^4.18.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.0"
  },
  "devDependencies": {
    "@nestjs/testing": "^10.0.0",
    "@types/aws-lambda": "^8.10.0",
    "@types/express": "^4.17.0",
    "@types/node": "^20.0.0",
    "esbuild": "^0.20.0",
    "serverless": "^3.0.0",
    "serverless-esbuild": "^1.0.0",
    "serverless-offline": "^13.0.0",
    "ts-loader": "^9.0.0",
    "typescript": "^5.0.0",
    "webpack": "^5.0.0",
    "webpack-node-externals": "^3.0.0"
  }
}
```

### SAM Package Configuration

```yaml
# template.yaml - package optimization
Globals:
  Function:
    CodeUri: ./
    Runtime: nodejs20.x
    Architectures:
      - x86_64
    # Exclude dev dependencies
    Environment:
      Variables:
        NODE_ENV: production

Resources:
  NestJSApiFunction:
    Type: AWS::Serverless::Function
    Metadata:
      BuildMethod: esbuild
      BuildProperties:
        Minify: true
        Target: es2020
        Sourcemap: true
        EntryPoints:
          - lambda.ts
        External:
          - '@nestjs/microservices'
          - '@nestjs/websockets'
    Properties:
      Handler: dist/lambda.handler
```

## Environment Management

### SAM Environment Variables

```yaml
# Using parameter overrides
Parameters:
  Environment:
    Type: String
    Default: dev

  # Secure parameters
  DatabaseUrl:
    Type: String
    NoEcho: true

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          STAGE: !Ref Environment
          DATABASE_URL: !Ref DatabaseUrl
          SECRET_VALUE: !Sub '{{resolve:secretsmanager:${MySecret}:SecretString:value}}'
          SSM_VALUE: !Sub '{{resolve:ssm-secure:/${Environment}/my-param}}'
```

### SSM Parameter Store

```yaml
# serverless.yml - SSM integration
provider:
  environment:
    # Standard parameters
    API_URL: ${ssm:/${self:service}/${self:provider.stage}/api-url}

    # Secure parameters (encrypted)
    DATABASE_URL: ${ssm:/${self:service}/${self:provider.stage}/database-url~true}

    # Reference by ARN
    EXTERNAL_API_KEY: ${ssm:arn:aws:ssm:${aws:region}:${aws:accountId}:parameter/external/api-key}

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - ssm:GetParameter
            - ssm:GetParameters
          Resource:
            - arn:aws:ssm:${aws:region}:${aws:accountId}:parameter/${self:service}/*
```

### Secrets Manager

```yaml
# SAM with Secrets Manager
Resources:
  MySecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '${AWS::StackName}/my-secret'
      GenerateSecretString:
        SecretStringTemplate: '{"username":"admin"}'
        GenerateStringKey: password
        PasswordLength: 32
        ExcludeCharacters: '"@/\'

  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          DB_SECRET: !Sub '{{resolve:secretsmanager:${MySecret}:SecretString}}'
```

```yaml
# Serverless with Secrets Manager
provider:
  environment:
    # Full secret JSON
    DB_SECRET: ${secrets:${self:service}/${self:provider.stage}/database}

    # Specific key from secret
    DB_PASSWORD: ${secrets:${self:service}/${self:provider.stage}/database:password}

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource:
            - arn:aws:secretsmanager:${aws:region}:${aws:accountId}:secret:${self:service}/*
```

## Monitoring

### SAM CloudWatch Dashboard

```yaml
Resources:
  MonitoringDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub '${AWS::StackName}-dashboard'
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "title": "Invocations",
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "${NestJSApiFunction}", { "stat": "Sum" }]
                ],
                "period": 300,
                "region": "${AWS::Region}",
                "yAxis": { "left": { "min": 0 } }
              }
            },
            {
              "type": "metric",
              "properties": {
                "title": "Errors",
                "metrics": [
                  ["AWS/Lambda", "Errors", "FunctionName", "${NestJSApiFunction}", { "stat": "Sum" }],
                  [".", "Throttles", ".", ".", { "stat": "Sum" }]
                ],
                "period": 300,
                "region": "${AWS::Region}"
              }
            },
            {
              "type": "metric",
              "properties": {
                "title": "Duration",
                "metrics": [
                  ["AWS/Lambda", "Duration", "FunctionName", "${NestJSApiFunction}", { "stat": "p99" }],
                  ["...", { "stat": "Average" }]
                ],
                "period": 300,
                "region": "${AWS::Region}"
              }
            }
          ]
        }
```

### Serverless CloudWatch Alarms

```yaml
custom:
  alerts:
    stages:
      - prod
      - staging
    dashboards: true
    topics:
      alarm:
        - !Ref AlarmTopic
      ok:
        - !Ref OkTopic

    alarms:
      - functionErrors
      - functionThrottles
      - functionInvocations
      - functionDuration

    definitions:
      functionErrors:
        description: 'Function errors exceeded threshold'
        threshold: 1
        statistic: Sum
        period: 60
        evaluationPeriods: 1
        comparisonOperator: GreaterThanOrEqualToThreshold
        treatMissingData: notBreaching

      functionThrottles:
        description: 'Function throttled'
        threshold: 1
        statistic: Sum
        period: 60
        evaluationPeriods: 1
        comparisonOperator: GreaterThanOrEqualToThreshold

      functionDuration:
        description: 'Function duration exceeded threshold'
        threshold: 5000
        statistic: p99
        period: 60
        evaluationPeriods: 2
        comparisonOperator: GreaterThanThreshold

      customAlarm:
        description: 'Custom business metric'
        metric: CustomMetric
        namespace: MyNamespace
        threshold: 100
        statistic: Average
        period: 300
        evaluationPeriods: 1
```

### X-Ray Tracing

```yaml
# SAM - Enable tracing
Globals:
  Function:
    Tracing: Active

Resources:
  ApiGatewayApi:
    Type: AWS::Serverless::Api
    Properties:
      TracingEnabled: true
```

```yaml
# Serverless - Enable tracing
provider:
  tracing:
    lambda: true
    apiGateway: true
```

```typescript
// X-Ray instrumentation
import * as AWSXRay from 'aws-xray-sdk-core';
import * as AWS from 'aws-sdk';

// Capture AWS SDK calls
const tracedAWS = AWSXRay.captureAWS(AWS);

// Capture HTTP requests
import http from 'http';
import https from 'https';
AWSXRay.captureHTTPsGlobal(http);
AWSXRay.captureHTTPsGlobal(https);

// Custom subsegment
const segment = AWSXRay.getSegment();
const subsegment = segment?.addNewSubsegment('custom-operation');
try {
  // Your code
  subsegment?.close();
} catch (error) {
  subsegment?.close(error);
}
```

## Performance Tuning

### Memory Configuration

```yaml
# SAM - Memory and CPU tuning
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 512
      # Memory impacts CPU proportionally
      # 1769MB = 1 vCPU
      # 3008MB = ~1.7 vCPU

  ComputeIntensiveFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 3008
```

```yaml
# Serverless - Memory per function
functions:
  api:
    memorySize: 512

  compute:
    memorySize: 1024

  health:
    memorySize: 256
```

### Provisioned Concurrency

```yaml
# SAM - Provisioned Concurrency
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 10
      AutoPublishAlias: live
```

```yaml
# Serverless - Provisioned Concurrency
functions:
  api:
    provisionedConcurrency: 10
```

### Reserved Concurrency

```yaml
# SAM - Reserved Concurrency
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      ReservedConcurrentExecutions: 100
```

```yaml
# Serverless - Reserved Concurrency
functions:
  api:
    reservedConcurrency: 100
```

## Rollback Strategy

### SAM Auto-Rollback

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      AutoPublishAlias: live
      DeploymentPreference:
        Type: Canary10Percent5Minutes
        Alarms:
          - !Ref ErrorAlarm
          - !Ref LatencyAlarm
        Hooks:
          PreTraffic: !Ref PreTrafficHook
          PostTraffic: !Ref PostTrafficHook

  PreTrafficHook:
    Type: AWS::Serverless::Function
    Properties:
      Handler: hooks.preTraffic
      Runtime: nodejs20.x
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - codedeploy:PutLifecycleEventHookExecutionStatus
              Resource:
                - !Sub 'arn:aws:codedeploy:${aws:region}:${aws:accountId}:deploymentgroup:${AWS::StackName}/*'

  PostTrafficHook:
    Type: AWS::Serverless::Function
    Properties:
      Handler: hooks.postTraffic
      Runtime: nodejs20.x
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - codedeploy:PutLifecycleEventHookExecutionStatus
              Resource:
                - !Sub 'arn:aws:codedeploy:${aws:region}:${aws:accountId}:deploymentgroup:${AWS::StackName}/*'
```

### Serverless Canary

```yaml
custom:
  canary:
    type: LinearCanary
    alias: Live
    linearTrafficShifting:
      - intervalMinutes: 10
        percentage: 10
      - intervalMinutes: 10
        percentage: 50
      - intervalMinutes: 10
        percentage: 100
    alarms:
      - functionErrors
      - functionDuration
```

## Security Best Practices

### SAM VPC Configuration

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      VpcConfig:
        SecurityGroupIds:
          - !Ref LambdaSecurityGroup
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
      Policies:
        - VPCAccessPolicy: {}
```

### Serverless VPC

```yaml
provider:
  vpc:
    securityGroupIds:
      - !Ref LambdaSecurityGroup
    subnetIds:
      - !Ref PrivateSubnet1
      - !Ref PrivateSubnet2
```

### IAM Least Privilege

```yaml
# SAM - Granular IAM
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - dynamodb:GetItem
                - dynamodb:PutItem
              Resource:
                - !GetAtt MyTable.Arn
              Condition:
                ForAllValues:StringEquals:
                  dynamodb:LeadingKeys:
                    - 'USER#${cognito-identity.amazonaws.com:sub}'
```

```yaml
# Serverless - Granular IAM
provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
          Resource:
            - !GetAtt MyTable.Arn
          Condition:
            ForAllValues:StringEquals:
              dynamodb:LeadingKeys:
                - 'USER#${cognito-identity.amazonaws.com:sub}'
```

## Cost Optimization

### Graviton2 (ARM64)

```yaml
# SAM - ARM64
Globals:
  Function:
    Architectures:
      - arm64
```

```yaml
# Serverless - ARM64
provider:
  architecture: arm64
```

### SAM Lambda Layers

```yaml
Resources:
  CommonLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: common-dependencies
      ContentUri: layers/common/
      CompatibleRuntimes:
        - nodejs20.x
      RetentionPolicy: Retain

  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Layers:
        - !Ref CommonLayer
```

### Serverless Lambda Layers

```yaml
layers:
  common:
    path: layers/common
    compatibleRuntimes:
      - nodejs20.x
    package:
      patterns:
        - 'node_modules/**'

functions:
  api:
    layers:
      - { Ref: CommonLambdaLayer }
```

## SAM vs Serverless Framework

| Feature | SAM | Serverless Framework |
|---------|-----|---------------------|
| Native AWS | Yes | No (uses CloudFormation) |
| Local testing | `sam local` | `serverless-offline` |
| CI/CD integration | AWS-native | Multi-cloud support |
| Syntax | YAML/JSON | YAML/TypeScript/JavaScript |
| Extensions | SAR, nested stacks | Plugins ecosystem |
| Debugging | SAM CLI | Serverless console |

### When to Choose SAM

- Native AWS environment
- Team familiar with CloudFormation
- Need deep AWS service integration
- Want to use AWS CodePipeline/CodeBuild

### When to Choose Serverless Framework

- Multi-cloud requirements
- Large plugin ecosystem needed
- Prefer TypeScript/JavaScript config
- Want easier local development

## Complete Example Project

```
nestjs-lambda-sam/
├── src/
│   ├── app.module.ts
│   ├── main.ts
│   ├── lambda.ts
│   └── modules/
│       └── users/
├── dist/
├── template.yaml
├── samconfig.toml
├── package.json
└── tsconfig.json
```

```
nestjs-lambda-serverless/
├── src/
│   ├── app.module.ts
│   ├── main.ts
│   ├── lambda.ts
│   └── modules/
│       └── users/
├── dist/
├── serverless.yml
├── package.json
└── tsconfig.json
```
