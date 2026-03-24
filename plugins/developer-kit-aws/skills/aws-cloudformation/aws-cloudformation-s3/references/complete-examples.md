# S3 CloudFormation - Complete Examples

## Basic S3 Bucket

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Simple S3 bucket with default settings

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-data-bucket
      Tags:
        - Key: Environment
          Value: production
        - Key: Project
          Value: my-project
```

## Bucket with Versioning and Encryption

```yaml
DataBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub "${AWS::StackName}-data"
    VersioningConfiguration:
      Status: Enabled
    BucketEncryption:
      ServerSideEncryptionConfiguration:
        - ServerSideEncryptionByDefault:
            SSEAlgorithm: AES256
    PublicAccessBlockConfiguration:
      BlockPublicAcls: true
      BlockPublicPolicy: true
      IgnorePublicAcls: true
      RestrictPublicBuckets: true
```

## Bucket with Lifecycle Rules

```yaml
DataBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub "${AWS::StackName}-data"
    LifecycleConfiguration:
      Rules:
        - Id: ArchiveOldData
          Status: Enabled
          Transitions:
            - StorageClass: INTELLIGENT_TIERING
              TransitionInDays: 90
            - StorageClass: GLACIER
              TransitionInDays: 365
          ExpirationInDays: 2555
```

## Bucket with CORS Configuration

```yaml
DataBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub "${AWS::StackName}-data"
    CorsConfiguration:
      CorsRules:
        - AllowedHeaders:
            - '*'
          AllowedMethods:
            - GET
            - PUT
            - POST
            - DELETE
          AllowedOrigins:
            - https://example.com
          ExposedHeaders:
            - ETag
```

## Bucket Policy for IAM Role Access

```yaml
BucketPolicy:
  Type: AWS::S3::BucketPolicy
  Properties:
    Bucket: !Ref DataBucket
    PolicyDocument:
      Statement:
        - Effect: Allow
          Principal:
            AWS: !Ref RoleArn
          Action:
            - s3:GetObject
            - s3:PutObject
            - s3:DeleteObject
          Resource: !Sub "${DataBucket.Arn}/*"
```

## Complete Production S3 Stack

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production S3 bucket with all features

Parameters:
  BucketName:
    Type: String
    Description: Name of the S3 bucket
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
  EnableVersioning:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
      VersioningConfiguration:
        Status: !Ref EnableVersioning
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldVersions
            Status: Enabled
            NoncurrentVersionExpirationInDays: 90
          - Id: ArchiveToGlacier
            Status: Enabled
            Transitions:
              - StorageClass: INTELLIGENT_TIERING
                TransitionInDays: 90
              - StorageClass: GLACIER
                TransitionInDays: 365
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref DataBucket
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Ref DataAccessRole
            Action:
              - s3:GetObject
              - s3:PutObject
              - s3:DeleteObject
            Resource: !Sub "${DataBucket.Arn}/*"

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

## S3 Event Notifications

```yaml
DataBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub "${AWS::StackName}-data"
    NotificationConfiguration:
      LambdaConfigurations:
        - Event: s3:ObjectCreated:*
          Function: !GetAtt LambdaFunction.Arn
        - Event: s3:ObjectRemoved:*
          Function: !GetAtt LambdaFunction.Arn
      QueueConfigurations:
        - Event: s3:ObjectCreated:*
          Queue: !GetAtt Queue.Arn
      TopicConfigurations:
        - Event: s3:ObjectCreated:*
          Topic: !Ref SNSTopic
```

## Static Website Hosting

```yaml
WebsiteBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub "${AWS::StackName}-website"
    WebsiteConfiguration:
      IndexDocument: index.html
      ErrorDocument: error.html
    PublicAccessBlockConfiguration:
      BlockPublicAcls: false
      BlockPublicPolicy: false

BucketPolicy:
  Type: AWS::S3::BucketPolicy
  Properties:
    Bucket: !Ref WebsiteBucket
    PolicyDocument:
      Statement:
        - Effect: Allow
          Principal: '*'
          Action: s3:GetObject
          Resource: !Sub '${WebsiteBucket.Arn}/*'

Outputs:
  WebsiteURL:
    Description: S3 Website URL
    Value: !GetAtt WebsiteBucket.WebsiteURL
```

## Cross-Region Replication

```yaml
SourceBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: source-bucket
    VersioningConfiguration:
      Status: Enabled

ReplicationBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub 'destination-bucket-${AWS::Region}'
    VersioningConfiguration:
      Status: Enabled

ReplicationConfiguration:
  Type: AWS::S3::BucketReplication
  Properties:
    Role: !GetAtt ReplicationRole.Arn
    Bucket: !Ref SourceBucket
    ReplicationConfiguration:
      Rules:
        - Destination:
            Bucket: !Ref ReplicationBucket
            Account: !Ref DestinationAccountId
          Status: Enabled
          Prefix: data/
```
