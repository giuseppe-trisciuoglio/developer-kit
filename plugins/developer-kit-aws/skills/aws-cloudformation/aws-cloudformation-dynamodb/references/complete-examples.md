# DynamoDB CloudFormation - Complete Examples

## Basic Table with On-Demand Capacity

```yaml
Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
```

## Table with Global Secondary Index

```yaml
Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
        - AttributeName: gsi-pk
          AttributeType: S
        - AttributeName: gsi-sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: gsi-index
          KeySchema:
            - AttributeName: gsi-pk
              KeyType: HASH
            - AttributeName: gsi-sk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
          ProvisionedThroughput:
            ReadCapacityUnits: 5
            WriteCapacityUnits: 5
```

## Table with TTL

```yaml
Resources:
  SessionTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-sessions"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: sessionId
          AttributeType: S
      KeySchema:
        - AttributeName: sessionId
          KeyType: HASH
      TimeToLiveSpecification:
        AttributeName: expiresAt
        Enabled: true
```

## Table with Encryption

```yaml
Parameters:
  KMSKeyId:
    Type: String
    Default: alias/dynamodb

Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
      SSESpecification:
        SSEEnabled: true
        SSEType: KMS
        KMSMasterKeyId: !Ref KMSKeyId
```

## Table with Point-In-Time Recovery

```yaml
Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
```

## Table with Auto Scaling

```yaml
Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PROVISIONED
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
      ProvisionedThroughput:
        ReadCapacityUnits: 5
        WriteCapacityUnits: 5

  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 100
      MinCapacity: 5
      ResourceId: !Sub "table/${DynamoDBTable}"
      RoleARN: !GetAtt AutoScalingRole.Arn
      ScalableDimension: dynamodb:table:ReadCapacityUnits
      ServiceNamespace: dynamodb

  ReadScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: ReadAutoScalingPolicy
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingConfig:
        TargetValue: 50.0
        ScaleInCooldown: 300
        ScaleOutCooldown: 60

  WriteScalingTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 50
      MinCapacity: 5
      ResourceId: !Sub "table/${DynamoDBTable}"
      RoleARN: !GetAtt AutoScalingRole.Arn
      ScalableDimension: dynamodb:table:WriteCapacityUnits
      ServiceNamespace: dynamodb
```

## Complete Production Table

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production DynamoDB table

Parameters:
  TableName:
    Type: String
    Default: my-table
  ReadCapacityUnits:
    Type: Number
    Default: 5
    MinValue: 5
  WriteCapacityUnits:
    Type: Number
    Default: 5
    MinValue: 5
  EnableEncryption:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']
  EnableStreams:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']

Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Ref TableName
      BillingMode: PROVISIONED
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
        - AttributeName: gsi1-pk
          AttributeType: S
        - AttributeName: gsi1-sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: gsi1
          KeySchema:
            - AttributeName: gsi1-pk
              KeyType: HASH
            - AttributeName: gsi1-sk
              KeyType: RANGE
          Projection:
            ProjectionType: INCLUDE
            NonKeyAttributes:
              - data
              - timestamp
          ProvisionedThroughput:
            ReadCapacityUnits: 5
            WriteCapacityUnits: 5
      ProvisionedThroughput:
        ReadCapacityUnits: !Ref ReadCapacityUnits
        WriteCapacityUnits: !Ref WriteCapacityUnits
      SSESpecification:
        !If
          - EnableEncryption
          - SSEEnabled: true
            SSEType: KMS
            KMSMasterKeyId: !Ref KMSKey
          - !Ref AWS::NoValue
      StreamSpecification:
        !If
          - EnableStreams
          - StreamViewType: NEW_AND_OLD_IMAGES
          - !Ref AWS::NoValue
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      Tags:
        - Key: Environment
          Value: production

  KMSKey:
    Type: AWS::KMS::Key
    Condition: EnableEncryption
    Properties:
      Description: KMS key for DynamoDB encryption
      KeyPolicy:
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:role/DynamoDBAutoscalingRole'
            Action:
              - kms:Decrypt
              - kms:GenerateDataKey
            Resource: '*'

Outputs:
  TableName:
    Description: DynamoDB table name
    Value: !Ref DynamoDBTable
    Export:
      Name: !Sub '${AWS::StackName}-TableName'

  TableArn:
    Description: DynamoDB table ARN
    Value: !GetAtt DynamoDBTable.Arn
    Export:
      Name: !Sub '${AWS::StackName}-TableArn'
```

## Local Secondary Index

```yaml
Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PROVISIONED
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
        - AttributeName: lsi-sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      LocalSecondaryIndexes:
        - IndexName: lsi-index
          KeySchema:
            - AttributeName: pk
              KeyType: HASH
            - AttributeName: lsi-sk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
```
