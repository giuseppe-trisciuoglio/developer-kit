# AWS CloudFormation DynamoDB Examples

## Example 1: E-Commerce Order Management System

### Complete Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: E-commerce order management system with DynamoDB

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  TableNamePrefix:
    Type: String
    Default: orders
    Description: Prefix for table names

  BillingMode:
    Type: String
    Default: PAY_PER_REQUEST
    AllowedValues:
      - PAY_PER_REQUEST
      - PROVISIONED

Resources:
  # Orders Table
  OrdersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${TableNamePrefix}-${Environment}"
      BillingMode: !Ref BillingMode
      AttributeDefinitions:
        # Primary key
        - AttributeName: order_id
          AttributeType: S
        # Sort key for order items
        - AttributeName: order_date
          AttributeType: S
        # GSI for customer queries
        - AttributeName: customer_id
          AttributeType: S
        - AttributeName: created_at
          AttributeType: S
        # GSI for status queries
        - AttributeName: status
          AttributeType: S
        - AttributeName: order_total
          AttributeType: N
      KeySchema:
        - AttributeName: order_id
          KeyType: HASH
        - AttributeName: order_date
          KeyType: RANGE
      GlobalSecondaryIndexes:
        # Customer orders index
        - IndexName: customer-orders
          KeySchema:
            - AttributeName: customer_id
              KeyType: HASH
            - AttributeName: created_at
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        # Status-based queries index
        - IndexName: status-orders
          KeySchema:
            - AttributeName: status
              KeyType: HASH
            - AttributeName: order_total
              KeyType: RANGE
          Projection:
            ProjectionType: INCLUDE
            NonKeyAttributes:
              - customer_id
              - order_date
      ProvisionedThroughput: !If
        - !Equals [!Ref BillingMode, PROVISIONED]
        - ReadCapacityUnits: 25
          WriteCapacityUnits: 25
        - !Ref AWS::NoValue
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      SSESpecification:
        SSEEnabled: true
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: e-commerce-platform
        - Key: DataClassification
          Value: confidential

  # Auto Scaling Role
  DynamoDBAutoScalingRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-autoscaling"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: application-autoscaling.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/DynamoDBAutoscaleRole

  # Scalable Targets
  ReadScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 200
      MinCapacity: 5
      ResourceId: !Sub "table/${OrdersTable}"
      RoleARN: !GetAtt DynamoDBAutoScalingRole.Arn
      ScalableDimension: dynamodb:table:ReadCapacityUnits
      ServiceNamespace: dynamodb

  WriteScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 200
      MinCapacity: 5
      ResourceId: !Sub "table/${OrdersTable}"
      RoleARN: !GetAtt DynamoDBAutoScalingRole.Arn
      ScalableDimension: dynamodb:table:WriteCapacityUnits
      ServiceNamespace: dynamodb

  # Scaling Policies
  ReadScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-read-policy"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ReadScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: DynamoDBReadCapacityUtilization
        TargetValue: 70
        ScaleInCooldown: 120
        ScaleOutCooldown: 60

  WriteScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-write-policy"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref WriteScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: DynamoDBWriteCapacityUtilization
        TargetValue: 70
        ScaleInCooldown: 120
        ScaleOutCooldown: 60

Outputs:
  TableName:
    Description: Orders table name
    Value: !Ref OrdersTable
    Export:
      Name: !Sub "${AWS::StackName}-OrdersTableName"

  TableArn:
    Description: Orders table ARN
    Value: !GetAtt OrdersTable.Arn
    Export:
      Name: !Sub "${AWS::StackName}-OrdersTableArn"

  StreamArn:
    Description: Orders stream ARN
    Value: !GetAtt OrdersTable.StreamArn
    Export:
      Name: !Sub "${AWS::StackName}-OrdersStreamArn"
```

## Example 2: Multi-Tenant SaaS Application

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Multi-tenant SaaS application with DynamoDB

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  TenantId:
    Type: String
    Default: default
    Description: Tenant identifier for isolation

Resources:
  # Tenant-specific table with item-level tenant isolation
  TenantDataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "tenant-${TenantId}-data-${Environment}"
      BillingMode: PROVISIONED
      AttributeDefinitions:
        # Primary key with tenant isolation
        - AttributeName: tenant_id
          AttributeType: S
        - AttributeName: entity_type
          AttributeType: S
        - AttributeName: entity_id
          AttributeType: S
        - AttributeName: created_at
          AttributeType: S
        # GSI for querying by type
        - AttributeName: type_status
          AttributeType: S
      KeySchema:
        - AttributeName: tenant_id
          KeyType: HASH
        - AttributeName: entity_type
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: entities-by-type
          KeySchema:
            - AttributeName: tenant_id
              KeyType: HASH
            - AttributeName: type_status
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      LocalSecondaryIndexes:
        - IndexName: entities-by-date
          KeySchema:
            - AttributeName: tenant_id
              KeyType: HASH
            - AttributeName: created_at
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      ProvisionedThroughput:
        ReadCapacityUnits: 10
        WriteCapacityUnits: 10
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      SSESpecification:
        SSEEnabled: true

  # Tenant configuration table
  TenantConfigTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "tenant-config-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: tenant_id
          AttributeType: S
      KeySchema:
        - AttributeName: tenant_id
          KeyType: HASH
      SSESpecification:
        SSEEnabled: true

  # IAM Role for tenant access
  TenantAccessRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-tenant-access"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-tenant-data-access"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                  - dynamodb:Query
                Resource: !GetAtt TenantDataTable.Arn
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                Resource: !GetAtt TenantConfigTable.Arn

Outputs:
  TenantDataTableName:
    Description: Tenant data table name
    Value: !Ref TenantDataTable

  TenantDataTableArn:
    Description: Tenant data table ARN
    Value: !GetAtt TenantDataTable.Arn
```

## Example 3: Real-Time Analytics Pipeline

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Real-time analytics pipeline with DynamoDB

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Raw events table
  EventsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "analytics-events-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: event_id
          AttributeType: S
        - AttributeName: event_type
          AttributeType: S
        - AttributeName: timestamp
          AttributeType: S
        - AttributeName: user_id
          AttributeType: S
        - AttributeName: session_id
          AttributeType: S
      KeySchema:
        - AttributeName: event_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: events-by-type
          KeySchema:
            - AttributeName: event_type
              KeyType: HASH
            - AttributeName: timestamp
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: events-by-user
          KeySchema:
            - AttributeName: user_id
              KeyType: HASH
            - AttributeName: timestamp
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      SSESpecification:
        SSEEnabled: true
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # Aggregated metrics table
  MetricsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "analytics-metrics-${Environment}"
      BillingMode: PROVISIONED
      AttributeDefinitions:
        - AttributeName: metric_id
          AttributeType: S
        - AttributeName: metric_date
          AttributeType: S
        - AttributeName: metric_type
          AttributeType: S
      KeySchema:
        - AttributeName: metric_id
          KeyType: HASH
        - AttributeName: metric_date
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: metrics-by-type
          KeySchema:
            - AttributeName: metric_type
              KeyType: HASH
            - AttributeName: metric_date
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      ProvisionedThroughput:
        ReadCapacityUnits: 10
        WriteCapacityUnits: 10
      SSESpecification:
        SSEEnabled: true

  # Lambda function for processing events
  EventProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-event-processor"
      Runtime: python3.11
      Handler: handler.process
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/event-processor.zip
      Timeout: 300
      Role: !GetAtt LambdaExecutionRole.Arn

  # Event source mapping
  EventSourceMapping:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      EventSourceArn: !GetAtt EventsTable.StreamArn
      FunctionName: !Ref EventProcessorFunction
      StartingPosition: LATEST
      BatchSize: 100
      MaximumBatchingWindowInSeconds: 60
      Enabled: true

  # Lambda function for aggregation
  MetricAggregatorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-metric-aggregator"
      Runtime: python3.11
      Handler: handler.aggregate
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/metric-aggregator.zip
      Timeout: 300
      Role: !GetAtt LambdaExecutionRole.Arn

  # Scheduled rule for aggregation
  AggregationSchedule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub "${AWS::StackName}-aggregation"
      ScheduleExpression: "rate(5 minutes)"
      State: ENABLED
      Targets:
        - Id: !Ref MetricAggregatorFunction
          Arn: !GetAtt MetricAggregatorFunction.Arn

  # Lambda execution role
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
        - arn:aws:iam::aws:policy/service-role/AWSLambdaDynamoDBExecutionRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-write-metrics"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                Resource: !GetAtt MetricsTable.Arn

Outputs:
  EventsTableName:
    Description: Events table name
    Value: !Ref EventsTable
    Export:
      Name: !Sub "${AWS::StackName}-EventsTableName"

  EventsStreamArn:
    Description: Events stream ARN
    Value: !GetAtt EventsTable.StreamArn
    Export:
      Name: !Sub "${AWS::StackName}-EventsStreamArn"

  MetricsTableName:
    Description: Metrics table name
    Value: !Ref MetricsTable
```

## Example 4: Gaming Leaderboard System

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Gaming leaderboard with DynamoDB

Resources:
  # Leaderboard table with GSI for scores
  LeaderboardTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-leaderboard"
      BillingMode: PROVISIONED
      AttributeDefinitions:
        - AttributeName: game_id
          AttributeType: S
        - AttributeName: player_id
          AttributeType: S
        - AttributeName: score
          AttributeType: N
        - AttributeName: score_date
          AttributeType: S
      KeySchema:
        - AttributeName: game_id
          KeyType: HASH
        - AttributeName: player_id
          KeyType: RANGE
      GlobalSecondaryIndexes:
        # Descending sort key for top scores
        - IndexName: top-scores
          KeySchema:
            - AttributeName: game_id
              KeyType: HASH
            - AttributeName: score
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      ProvisionedThroughput:
        ReadCapacityUnits: 10
        WriteCapacityUnits: 20
      StreamSpecification:
        StreamViewType: NEW_IMAGE
      SSESpecification:
        SSEEnabled: true

  # Player stats table
  PlayerStatsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-player-stats"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: player_id
          AttributeType: S
        - AttributeName: game_id
          AttributeType: S
      KeySchema:
        - AttributeName: player_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: games-index
          KeySchema:
            - AttributeName: player_id
              KeyType: HASH
            - AttributeName: game_id
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      SSESpecification:
        SSEEnabled: true

  # IAM Role for game backend
  GameBackendRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-game-backend"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-leaderboard-access"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:Query
                Resource: !GetAtt LeaderboardTable.Arn
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                Resource: !GetAtt PlayerStatsTable.Arn

Outputs:
  LeaderboardTableName:
    Description: Leaderboard table name
    Value: !Ref LeaderboardTable
```

## Example 5: IoT Device State Management

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: IoT device state management with DynamoDB

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Device state table
  DeviceStateTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "device-state-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: device_id
          AttributeType: S
        - AttributeName: state_timestamp
          AttributeType: S
        - AttributeName: device_type
          AttributeType: S
        - AttributeName: firmware_version
          AttributeType: S
      KeySchema:
        - AttributeName: device_id
          KeyType: HASH
        - AttributeName: state_timestamp
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: devices-by-type
          KeySchema:
            - AttributeName: device_type
              KeyType: HASH
            - AttributeName: firmware_version
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      SSESpecification:
        SSEEnabled: true
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # Device configuration table
  DeviceConfigTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "device-config-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: device_id
          AttributeType: S
        - AttributeName: config_version
          AttributeType: S
      KeySchema:
        - AttributeName: device_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: configs-by-version
          KeySchema:
            - AttributeName: device_id
              KeyType: HASH
            - AttributeName: config_version
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      SSESpecification:
        SSEEnabled: true

  # IoT rule for updating device state
  IoTDeviceStateRule:
    Type: AWS::IoT::TopicRule
    Properties:
      RuleName: !Sub "${AWS::StackName}-device-state"
      TopicRulePayload:
        Sql: "SELECT * FROM 'devices/+/state'"
        Actions:
          - DynamoDBv2Action:
              TableName: !Ref DeviceStateTable
              RoleArn: !GetAtt IoTRole.Arn

  # IAM Role for IoT
  IoTRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-iot-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: iot.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-write-state"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                Resource: !GetAtt DeviceStateTable.Arn

Outputs:
  DeviceStateTableName:
    Description: Device state table name
    Value: !Ref DeviceStateTable

  DeviceConfigTableName:
    Description: Device config table name
    Value: !Ref DeviceConfigTable
```

## Example 6: Chat Message System

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Real-time chat messaging system

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Conversation table
  ConversationsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "conversations-${Environment}"
      BillingMode: PROVISIONED
      AttributeDefinitions:
        - AttributeName: conversation_id
          AttributeType: S
        - AttributeName: last_message_time
          AttributeType: S
        - AttributeName: participant_id
          AttributeType: S
      KeySchema:
        - AttributeName: conversation_id
          KeyType: HASH
      LocalSecondaryIndexes:
        - IndexName: conversations-by-time
          KeySchema:
            - AttributeName: conversation_id
              KeyType: HASH
            - AttributeName: last_message_time
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      ProvisionedThroughput:
        ReadCapacityUnits: 10
        WriteCapacityUnits: 10
      SSESpecification:
        SSEEnabled: true

  # Messages table with conversation-based routing
  MessagesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "messages-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: conversation_id
          AttributeType: S
        - AttributeName: message_time
          AttributeType: S
        - AttributeName: sender_id
          AttributeType: S
        - AttributeName: recipient_id
          AttributeType: S
      KeySchema:
        - AttributeName: conversation_id
          KeyType: HASH
        - AttributeName: message_time
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: messages-by-sender
          KeySchema:
            - AttributeName: sender_id
              KeyType: HASH
            - AttributeName: message_time
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: messages-by-recipient
          KeySchema:
            - AttributeName: recipient_id
              KeyType: HASH
            - AttributeName: message_time
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      SSESpecification:
        SSEEnabled: true

  # Chat Lambda functions
  MessageProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-message-processor"
      Runtime: python3.11
      Handler: handler.process
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/message-processor.zip
      Timeout: 60
      Role: !GetAtt LambdaExecutionRole.Arn

  # Event source for new messages
  MessageEventSource:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      EventSourceArn: !GetAtt MessagesTable.StreamArn
      FunctionName: !Ref MessageProcessorFunction
      StartingPosition: LATEST
      BatchSize: 100
      Enabled: true

  # Lambda execution role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-chat-lambda"
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
        - PolicyName: !Sub "${AWS::StackName}-chat-access"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:Query
                Resource:
                  - !GetAtt ConversationsTable.Arn
                  - !GetAtt MessagesTable.Arn

Outputs:
  ConversationsTableName:
    Description: Conversations table name
    Value: !Ref ConversationsTable

  MessagesTableName:
    Description: Messages table name
    Value: !Ref MessagesTable

  MessagesStreamArn:
    Description: Messages stream ARN
    Value: !GetAtt MessagesTable.StreamArn
```
