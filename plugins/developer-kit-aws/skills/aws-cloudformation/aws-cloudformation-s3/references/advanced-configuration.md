# S3 CloudFormation - Advanced Properties

## Parameters

### AWS-Specific Parameter Types

```yaml
Parameters:
  # AWS-specific types
  BucketName:
    Type: String
    Description: S3 bucket name
    Default: my-default-bucket
    MinLength: 3
    MaxLength: 63
    AllowedPattern: '^[a-z0-9-]+$'

  Environment:
    Type: String
    Description: Deployment environment
    AllowedValues: [dev, staging, prod]
    ConstraintDescription: Must be dev, staging, or prod

  EnableVersioning:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']
    Description: Enable S3 versioning

  # List type
  TagsList:
    Type: CommaDelimitedList
    Description: List of tags to apply

  # AWS-specific types
  KMSKeyId:
    Type: AWS::SSM::Parameter::Value<String>
    Description: KMS key ID from SSM Parameter Store
```

### SSM Parameter Lookup

```yaml
Parameters:
  DatabaseEndpoint:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /myapp/database/endpoint

Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref DatabaseEndpoint
```

## Mappings

### Environment Configuration

```yaml
Mappings:
  EnvironmentConfig:
    dev:
      LifecycleDays: 30
      RetentionDays: 90
      StorageClass: STANDARD
    staging:
      LifecycleDays: 90
      RetentionDays: 365
      StorageClass: STANDARD_IA
    prod:
      LifecycleDays: 365
      RetentionDays: 2555
      StorageClass: GLACIER

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      LifecycleConfiguration:
        Rules:
          - Id: LifecycleRule
            Status: Enabled
            ExpirationInDays: !FindInMap [EnvironmentConfig, !Ref Environment, RetentionDays]
```

### Region Configuration

```yaml
Mappings:
  RegionToSecondaryRegion:
    us-east-1:
      Secondary: us-west-2
    us-west-2:
      Secondary: us-east-1
    eu-west-1:
      Secondary: eu-central-1

Resources:
  SecondaryBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'secondary-${AWS::Region}-${AWS::StackName}'
```

## Conditions

### Conditional Resource Creation

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, prod]
  IsDevelopment: !Equals [!Ref Environment, dev]
  ShouldEnableVersioning: !Equals [!Ref EnableVersioning, 'true']

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-data"
      VersioningConfiguration:
        Status: !If [ShouldEnableVersioning, Enabled, Suspended]
      LifecycleConfiguration:
        !If
          - IsProduction
          - Rules:
              - Id: ProdLifecycle
                Status: Enabled
                ExpirationInDays: 2555
          - !Ref AWS::NoValue
```

### Conditional Properties

```yaml
Conditions:
  UseKMS: !Not [!Equals [!Ref KMSKeyId, '']]

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
      BucketEncryption:
        !If
          - UseKMS
          - ServerSideEncryptionConfiguration:
              - ServerSideEncryptionByDefault:
                  SSEAlgorithm: aws:kms
                  KMSMasterKeyId: !Ref KMSKeyId
          - !Ref AWS::NoValue
```

## Outputs

### Basic Outputs

```yaml
Outputs:
  BucketName:
    Description: Name of the S3 bucket
    Value: !Ref DataBucket

  BucketArn:
    Description: ARN of the S3 bucket
    Value: !GetAtt DataBucket.Arn
```

### Exported Outputs for Cross-Stack References

```yaml
Outputs:
  BucketName:
    Description: Name of the S3 bucket
    Value: !Ref DataBucket
    Export:
      Name: !Sub '${AWS::StackName}-BucketName'

  BucketArn:
    Description: ARN of the S3 bucket
    Value: !GetAtt DataBucket.Arn
    Export:
      Name: !Sub '${AWS::StackName}-BucketArn'
```

### ImportValue in Another Stack

```yaml
Parameters:
  DataBucketName:
    Type: String

Resources:
  # Import value from another stack
  DataBucketLambda:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.9
      Handler: index.lambda_handler
      Environment:
        Variables:
          BUCKET_NAME: !Ref DataBucketName
```

## Metadata

### Template Metadata

```yaml
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          Default Configuration
        Parameters:
          - BucketName
          - EnableVersioning
      - Label:
          Advanced Configuration
        Parameters:
          - KMSKeyId
          - LifecycleRules
    ParameterLabels:
      BucketName:
        default: Bucket Name
      EnableVersioning:
        default: Enable Versioning
```

## Deletion Policy

### Retain Bucket on Stack Delete

```yaml
Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      BucketName: !Sub "${AWS::StackName}-data"
```

### Snapshot on Delete

```yaml
Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
    Properties:
      BucketName: !Sub "${AWS::StackName}-data"
```

## UpdateReplacePolicy

### Prevent Replacement During Update

```yaml
Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    UpdateReplacePolicy: Retain
    Properties:
      BucketName: my-unique-bucket
```

## DependsOn

### Control Resource Creation Order

```yaml
Resources:
  AccessLogBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-logs"

  DataBucket:
    Type: AWS::S3::Bucket
    DependsOn: AccessLogBucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-data"
      LoggingConfiguration:
        DestinationBucketName: !Ref AccessLogBucket
```

## Transform

### Serverless Transform

```yaml
Transform: 'AWS::Serverless-2016-10-31'
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
```

### Language Extensions

```yaml
Transform:
  - Name: 'AWS::LanguageExtensions'
    Version: latest
```
