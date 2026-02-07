# AWS CloudFormation Skills Guide

This guide covers the comprehensive AWS CloudFormation patterns and best practices available in the Developer Kit for building infrastructure as code solutions.

## Overview

AWS CloudFormation is a service that helps you model and set up your Amazon Web Services resources so you can spend less time managing those resources and more time focusing on your applications. You create a template that describes all the AWS resources you want, and CloudFormation takes care of provisioning and configuring those resources for you.

## Available Skills

### Core Infrastructure

| Skill | Description |
|-------|-------------|
| `aws-cloudformation-vpc` | Virtual Private Cloud, subnets, route tables, NAT Gateway, Internet Gateway |
| `aws-cloudformation-ec2` | EC2 instances, launch templates, Auto Scaling Groups |
| `aws-cloudformation-ecs` | ECS clusters, task definitions, services, load balancing |
| `aws-cloudformation-lambda` | Lambda functions, layers, event sources, integrations |

### Data & Storage

| Skill | Description |
|-------|-------------|
| `aws-cloudformation-rds` | RDS instances, Aurora, read replicas |
| `aws-cloudformation-dynamodb` | DynamoDB tables, GSIs, LSIs, streams |
| `aws-cloudformation-elasticache` | Redis/Memcached clusters, replica groups |
| `aws-cloudformation-s3` | S3 buckets, policies, lifecycle rules |

### Security & Monitoring

| Skill | Description |
|-------|-------------|
| `aws-cloudformation-iam` | IAM roles, policies, users, groups |
| `aws-cloudformation-security` | KMS, Secrets Manager, TLS/SSL, security |
| `aws-cloudformation-cloudwatch` | Metrics, alarms, dashboards, logs |
| `aws-cloudformation-cloudfront` | CloudFront distributions, origins, caching |

### Advanced & AI

| Skill | Description |
|-------|-------------|
| `aws-cloudformation-auto-scaling` | Auto-scaling policies and targets |
| `aws-cloudformation-bedrock` | Bedrock agents, knowledge base, RAG, guardrails |
| `aws-cloudformation-task-ecs-deploy-gh` | CI/CD GitHub Actions for ECS deployment |

## Core Template Structure

Every CloudFormation template follows this basic structure:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Clear description of what this template creates

Parameters:
  # Input values for your template

Mappings:
  # Environment-specific configurations

Conditions:
  # Conditional logic

Resources:
  # AWS resource definitions

Outputs:
  # Values to export or display
```

### Minimal Example

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: S3 bucket for static website hosting

Resources:
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-website-bucket

Outputs:
  WebsiteURL:
    Description: URL of the website
    Value: !GetAtt WebsiteBucket.WebsiteURL
```

## Parameters

Parameters let you customize your templates at runtime.

### AWS-Specific Types

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: Select a VPC

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small, t3.medium]

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: SSH key pair name

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: List of subnets
```

### Secure Parameters

```yaml
Parameters:
  DatabasePassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Database password (will not be shown in console)
```

## Mappings & Conditions

### Environment Configurations

```yaml
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
    us-west-2:
      AMI: ami-0d1cd67c26f5bca7d

  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
      MaxSize: 1
    prod:
      InstanceType: t3.medium
      MaxSize: 3

Conditions:
  IsProduction: !Equals [!Ref Environment, prod]
  HasSpotPrice: !Not [!Equals [!Ref SpotPrice, '']]
```

### Using Conditions

```yaml
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
      InstanceType: !FindInMap [EnvironmentConfig, !Ref Environment, InstanceType]
      SpotPrice: !If [HasSpotPrice, !Ref SpotPrice, !Ref "AWS::NoValue"]
```

## Intrinsic Functions

### Reference & GetAtt

```yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Cidr [!GetAtt VPC.CidrBlock, 4, 8]]
```

### Sub & Join

```yaml
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-logs-${AWS::AccountId}"

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: !Join ['.', ['0', '0', '0', '0/0']]
```

## Cross-Stack References

### Export Values

```yaml
# network-stack.yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub "${AWS::StackName}-VPCId"

  PublicSubnetIds:
    Description: Public subnet IDs
    Value: !Join [',', !Ref PublicSubnets]
    Export:
      Name: !Sub "${AWS::StackName}-PublicSubnetIds"
```

### Import Values

```yaml
# app-stack.yaml
Resources:
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Subnets: !Split [',', !ImportValue NetworkStack-PublicSubnetIds]
      SecurityGroups:
        - !Ref SecurityGroup
```

## Common Patterns

### VPC Pattern

```yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-vpc"

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  VPCGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC

  PublicRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Cidr [!GetAtt VPC.CidrBlock, 4, 8]]
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PublicSubnetAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable
```

### Lambda Function Pattern

```yaml
Resources:
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
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-function"
      Runtime: python3.11
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          def handler(event, context):
              return {'statusCode': 200, 'body': 'Hello World'}
      Timeout: 30
      MemorySize: 256

  LambdaLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/lambda/${LambdaFunction}"
      RetentionInDays: 7
```

### Lambda with API Gateway

```yaml
Resources:
  LambdaApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: !Sub "${AWS::StackName}-api"
      ProtocolType: HTTP
      Description: HTTP API for Lambda

  LambdaIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref LambdaApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${LambdaFunction.Arn}/invocations"

  ApiRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref LambdaApi
      RouteKey: GET /hello
      Target: !Join ['/', ['integrations', !Ref LambdaIntegration]]

  ApiDeployment:
    Type: AWS::ApiGatewayV2::Deployment
    DependsOn: ApiRoute
    Properties:
      ApiId: !Ref LambdaApi

  ApiStage:
    Type: AWS::ApiGatewayV2::Stage
    Properties:
      StageName: $default
      DeploymentId: !Ref ApiDeployment
      ApiId: !Ref LambdaApi

  LambdaPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref LambdaFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${LambdaApi}/*/*"

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub "https://${LambdaApi}.execute-api.${AWS::Region}.amazonaws.com/"
```

### ECS Fargate Pattern

```yaml
Resources:
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-cluster"

  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-task"
      Cpu: 512
      Memory: 1024
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        - Name: app
          Image: nginx:latest
          PortMappings:
            - ContainerPort: 80
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  ECSService:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref SubnetIds
          SecurityGroups:
            - !Ref SecurityGroup
          AssignPublicIp: ENABLED

  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      RetentionInDays: 7
```

### RDS Database Pattern

```yaml
Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnets for RDS
      SubnetIds: !Ref PrivateSubnetIds

  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub "${AWS::StackName}-db"
      DBInstanceClass: db.t3.micro
      Engine: postgres
      EngineVersion: 15.4
      AllocatedStorage: 20
      StorageType: gp2
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: 7
      MultiAZ: false
      PubliclyAccessible: false

Parameters:
  DBUsername:
    Type: String
    Default: dbadmin

  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
```

### DynamoDB Table Pattern

```yaml
Resources:
  Table:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
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
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true
```

### S3 Bucket Pattern

```yaml
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-bucket"
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
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldVersions
            Status: Enabled
            NoncurrentVersionExpirationInDays: 30

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref Bucket
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: EnforceTLS
            Effect: Deny
            Principal: '*'
            Action: s3:*
            Resource:
              - !GetAtt Bucket.Arn
              - !Sub "${Bucket.Arn}/*"
            Condition:
              Bool:
                aws:SecureTransport: false
```

## Security Patterns

### KMS Encryption

```yaml
Resources:
  Key:
    Type: AWS::KMS::Key
    Properties:
      Description: Encryption key for application
      KeyUsage: ENCRYPT_DECRYPT
      KeySpec: SYMMETRIC_DEFAULT
      Enabled: true
      PendingWindowInDays: 7
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Action: kms:*
            Resource: '*'

  KeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: alias/app-key
      TargetKeyId: !Ref Key
```

### Secrets Manager

```yaml
Resources:
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/db-credentials"
      Description: Database credentials
      GenerateSecretString:
        SecretStringTemplate: '{"username": "admin"}'
        GenerateStringKey: "password"
        PasswordLength: 32
        ExcludeCharacters: '"@/\'
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

### Security Group

```yaml
Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for application
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - Description: HTTP from ALB
          IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
        - Description: HTTPS from ALB
          IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref ALBSecurityGroup
      SecurityGroupEgress:
        - Description: All outbound traffic
          IpProtocol: -1
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-sg"
```

## Update Policies

### Auto Scaling Update Policy

```yaml
Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      # ... other properties ...
    UpdatePolicy:
      AutoScalingRollingUpdate:
        PauseTime: PT10M
        MinInstancesInService: 1
        MaxBatchSize: 2
        WaitOnResourceSignals: true
```

### Creation Policy

```yaml
Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      # ... properties ...
    CreationPolicy:
      ResourceSignal:
        Count: 2
        Timeout: PT15M
```

### Deletion Policy

```yaml
Resources:
  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      # ... properties ...

  S3Bucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      # ... properties ...
```

## Monitoring & Alarms

### CloudWatch Alarms

```yaml
Resources:
  CPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cpu"
      AlarmDescription: Alert when CPU exceeds 80%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup

  ErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-lambda-errors"
      MetricName: Errors
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref LambdaFunction
```

### Log Groups

```yaml
Resources:
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/lambda/${LambdaFunction}"
      RetentionInDays: 7

  MetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref LogGroup
      FilterPattern: "[timestamp, request_id, status_code > 400]"
      MetricTransformations:
        - MetricValue: 1
          MetricNamespace: Application
          MetricName: ErrorCount
```

## Nested Stacks

### Nested Stack Pattern

```yaml
Resources:
  NetworkLayer:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub "s3://${Bucket}/templates/network.yaml"
      Parameters:
        VpcCidr: 10.0.0.0/16
        Environment: !Ref Environment

  DataLayer:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub "s3://${Bucket}/templates/database.yaml"
      Parameters:
        VpcId: !GetAtt NetworkLayer.Outputs.VPCId
        SubnetIds: !GetAtt NetworkLayer.Outputs.PrivateSubnetIds
    DependsOn: NetworkLayer

Outputs:
  DatabaseEndpoint:
    Value: !GetAtt DataLayer.Outputs.DatabaseEndpoint
```

## Best Practices

### 1. Naming Conventions
```yaml
# Use consistent, descriptive names
Resources:
  AppLoadBalancer:  # Good: clear and descriptive
  ALB:              # Good: common abbreviation
  LB1:              # Bad: not descriptive

# Use tags for all resources
Properties:
  Tags:
    - Key: Name
      Value: !Sub "${AWS::StackName}-resource"
    - Key: Environment
      Value: !Ref Environment
    - Key: Project
      Value: MyProject
    - Key: CostCenter
      Value: Engineering
```

### 2. Template Organization
```
templates/
├── core/
│   ├── vpc.yaml
│   ├── security-groups.yaml
│   └── iam-roles.yaml
├── services/
│   ├── ecs-service.yaml
│   ├── lambda-function.yaml
│   └── rds-database.yaml
├── stacks/
│   ├── dev-stack.yaml
│   ├── staging-stack.yaml
│   └── prod-stack.yaml
└── lambda/
    └── source/
```

### 3. Parameter Design
```yaml
# Provide sensible defaults
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]
    Description: Deployment environment

  # Use AWS-specific types when possible
  VpcId:
    Type: AWS::EC2::VPC::Id

  # Add constraints
  MaxSize:
    Type: Number
    MinValue: 1
    MaxValue: 10
    Default: 2
```

### 4. Output Design
```yaml
# Always export useful values
Outputs:
  # Export for cross-stack references
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub "${AWS::StackName}-VPCId"

  # Include important endpoints
  ApiEndpoint:
    Description: API endpoint URL
    Value: !Sub "https://${Api}.execute-api.${AWS::Region}.amazonaws.com/"

  # Include connection strings
  DatabaseConnectionString:
    Description: Database connection string
    Value: !Sub "postgresql://${DBUsername}:${DBPassword}@${DatabaseInstance.Endpoint.Address}/mydb"
```

### 5. Security Best Practices
```yaml
# Enable encryption by default
Properties:
  BucketEncryption:
    ServerSideEncryptionConfiguration:
      - ServerSideEncryptionByDefault:
          SSEAlgorithm: AES256

# Block public access
PublicAccessBlockConfiguration:
  BlockPublicAcls: true
  BlockPublicPolicy: true

# Use least privilege IAM policies
Policies:
  - PolicyName: SpecificAccess
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - s3:GetObject
          Resource: !Sub "${Bucket.Arn}/*"
```

### 6. Cost Optimization
```yaml
# Use appropriate instance types
InstanceType: !FindInMap [EnvironmentConfig, !Ref Environment, InstanceType]

# Consider spot instances
SpotPrice: !If [IsProduction, !Ref "AWS::NoValue", "0.005"]

# Enable S3 lifecycle
LifecycleConfiguration:
  Rules:
    - Id: ArchiveOldObjects
      Status: Enabled
      Transitions:
        - TransitionInDays: 30
          StorageClass: STANDARD_IA
        - TransitionInDays: 90
          StorageClass: GLACIER
```

### 7. Change Management
```yaml
# Use DeletionPolicy for important data
DeletionPolicy: Snapshot  # For RDS
DeletionPolicy: Retain    # For S3, DynamoDB

# Use UpdatePolicy for smooth updates
UpdatePolicy:
  AutoScalingRollingUpdate:
    MinInstancesInService: 1
    PauseTime: PT5M

# Use DependsOn for explicit dependencies
DependsOn: [NetworkLayer, DatabaseLayer]
```

## CI/CD Integration

### GitHub Actions for Deployment

```yaml
# .github/workflows/deploy-cloudformation.yml
name: Deploy CloudFormation

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy CloudFormation Stack
        run: |
          aws cloudformation deploy \
            --stack-name my-app-${{ github.ref_name }} \
            --template-file templates/main.yaml \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides \
              Environment=${{ github.ref_name }} \
              Branch=${{ github.sha }}
```

## Testing & Validation

### cfn-lint

```bash
# Install
pip install cfn-lint

# Validate template
cfn-lint templates/app.yaml

# Validate with specific rules
cfn-lint -i templates/app.yaml
```

### CloudFormation Validation

```bash
# Validate template syntax
aws cloudformation validate-template \
  --template-body file://templates/app.yaml

# Create change set for preview
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name my-change-set \
  --template-body file://templates/app.yaml
```

## Troubleshooting

### Common Issues

**Stack rollback failed:**
```bash
# Continue rolling back
aws cloudformation continue-rollback-stack \
  --stack-name my-stack

# Or skip rollback and delete
aws cloudformation delete-stack \
  --stack-name my-stack \
  --retain-resources [Resource1,Resource2]
```

**Resource creation timeout:**
- Add `CreationPolicy` with `WaitOnResourceSignals`
- Increase timeout in `DependsOn` resources
- Check CloudWatch logs for errors

**Parameter validation failed:**
- Verify `AllowedValues` match input
- Check AWS-specific types are valid IDs
- Ensure `NoEcho` parameters are correct

### Useful Commands

```bash
# Describe stack events
aws cloudformation describe-stack-events \
  --stack-name my-stack

# Get stack resources
aws cloudformation list-stack-resources \
  --stack-name my-stack

# Export stack outputs
aws cloudformation describe-stacks \
  --stack-name my-stack \
  --query 'Stacks[0].Outputs'

# Detect drift
aws cloudformation detect-stack-drift \
  --stack-name my-stack
```

## Conclusion

This guide provides practical CloudFormation patterns for building infrastructure as code. The key is to start simple, use nested stacks for complexity, and always follow AWS best practices for security and cost optimization.

For specific service patterns, refer to individual skill documentation and the official [AWS CloudFormation documentation](https://docs.aws.amazon.com/cloudformation/).
