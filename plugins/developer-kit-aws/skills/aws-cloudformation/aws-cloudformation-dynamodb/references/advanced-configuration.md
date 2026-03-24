# DynamoDB CloudFormation - Advanced Configuration

## Parameters

### AWS-Specific Parameter Types

```yaml
Parameters:
  TableName:
    Type: String
    Default: my-dynamodb-table
    Description: DynamoDB table name
    MinLength: 3
    MaxLength: 255
    AllowedPattern: '^[a-zA-Z0-9_.-]+$'

  BillingMode:
    Type: String
    Default: PAY_PER_REQUEST
    AllowedValues:
      - PAY_PER_REQUEST
      - PROVISIONED
    Description: DynamoDB billing mode

  ReadCapacityUnits:
    Type: Number
    Default: 5
    MinValue: 5
    Description: Read capacity units

  WriteCapacityUnits:
    Type: Number
    Default: 5
    MinValue: 5
    Description: Write capacity units

  EnableEncryption:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']

  KMSKeyId:
    Type: AWS::SSM::Parameter::Value<String>
    Description: KMS key ID from SSM

  Tags:
    Type: CommaDelimitedList
    Description: Tags to apply to resources
```

## Mappings

### Capacity Configuration by Environment

```yaml
Mappings:
  EnvironmentCapacity:
    dev:
      ReadCapacity: 5
      WriteCapacity: 5
    staging:
      ReadCapacity: 10
      WriteCapacity: 10
    prod:
      ReadCapacity: 50
      WriteCapacity: 50

Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      ProvisionedThroughput:
        ReadCapacityUnits: !FindInMap [EnvironmentCapacity, !Ref Environment, ReadCapacity]
        WriteCapacityUnits: !FindInMap [EnvironmentCapacity, !Ref Environment, WriteCapacity]
```

## Conditions

### Conditional Resource Creation

```yaml
Conditions:
  IsProd: !Equals [!Ref Environment, prod]
  UseEncryption: !Equals [!Ref EnableEncryption, 'true']
  EnableAutoScaling: !Equals [!Ref BillingMode, PROVISIONED]

Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Ref TableName
      BillingMode: !Ref BillingMode
      SSESpecification:
        !If
          - UseEncryption
          - SSEEnabled: true
          - !Ref AWS::NoValue

  AutoScalingTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Condition: EnableAutoScaling
    Properties:
      ResourceId: !Sub "table/${DynamoDBTable}"
```

## Auto Scaling Configuration

### Target Tracking Policy

```yaml
Resources:
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 100
      MinCapacity: 5
      ResourceId: !Sub "table/${DynamoDBTable}"
      RoleARN: !GetAtt AutoScalingRole.Arn
      ScalableDimension: dynamodb:table:ReadCapacityUnits
      ServiceNamespace: dynamodb

  ScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: TargetTrackingPolicy
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingConfig:
        TargetValue: 70.0
        ScaleInCooldown: 300
        ScaleOutCooldown: 60
```

### Scheduled Scaling

```yaml
ScheduledAction:
  Type: AWS::ApplicationAutoScaling::ScheduledAction
  Properties:
    ScheduledActionName: scale-up-during-business-hours
    Schedule: 'cron(0 8 * * ? *)'
    ScalableTargetAction:
      MinCapacity: 20
      MaxCapacity: 50
```

## DynamoDB Streams

### Stream Configuration

```yaml
Resources:
  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES

  StreamProcessor:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      EventSourceArn: !GetAtt DynamoDBTable.StreamArn
      FunctionName: !Ref LambdaFunction
      StartingPosition: TRIM_HORIZON
```

## TTL Configuration

### Multiple TTL Attributes

```yaml
Resources:
  SessionTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-sessions"
      TimeToLiveSpecification:
        AttributeName: expiresAt
        Enabled: true

  CacheTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-cache"
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true
```

## Global Tables

### Replica Configuration

```yaml
Resources:
  ReplicaTable:
    Type: AWS::DynamoDB::GlobalTable
    Properties:
      TableName: global-table
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
      Replicas:
        - Region: us-east-1
        - Region: us-west-2
        - Region: eu-west-1
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
```

## Outputs

### Exported Outputs

```yaml
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

  StreamArn:
    Description: DynamoDB stream ARN
    Value: !GetAtt DynamoDBTable.StreamArn
    Export:
      Name: !Sub '${AWS::StackName}-StreamArn'
```

## Cross-Stack References

### Import Value in Another Stack

```yaml
Parameters:
  DataTableArn:
    Type: String

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.9
      Handler: index.lambda_handler
      Environment:
        Variables:
          TABLE_ARN: !Ref DataTableArn
      Policies:
        - DynamoDBCrudPolicy:
            PolicyName: DynamoDBCrudPolicy
            PolicyDocument:
              Version: '2012-10-17'
              Statement:
                - Effect: Allow
                  Action:
                    - dynamodb:GetItem
                    - dynamodb:PutItem
                    - dynamodb:UpdateItem
                    - dynamodb:Query
                    - dynamodb:Scan
                  Resource: !Sub '${DataTableArn}/*'
```

## IAM Roles

### Auto Scaling Role

```yaml
AutoScalingRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: autoscaling.amazonaws.com
          Action: 'sts:AssumeRole'
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSApplicationAutoScalingDynamoDBTablePolicy
```

### DynamoDB Access Role

```yaml
DynamoDBAccessRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: 'sts:AssumeRole'
    Policies:
      - PolicyName: DynamoDBCrudPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - dynamodb:GetItem
                - dynamodb:PutItem
                - dynamodb:UpdateItem
                - dynamodb:Query
                - dynamodb:Scan
                - dynamodb:DescribeTable
              Resource: !Sub 'arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${TableName}/*'
```

## Deletion Policy

### Retain Table on Stack Delete

```yaml
Resources:
  ImportantTable:
    Type: AWS::DynamoDB::Table
    DeletionPolicy: Retain
    Properties:
      TableName: critical-data-table
```

## UpdateReplacePolicy

### Snapshot on Replace

```yaml
Resources:
  ImportantTable:
    Type: AWS::DynamoDB::Table
    UpdateReplacePolicy: Snapshot
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
```
