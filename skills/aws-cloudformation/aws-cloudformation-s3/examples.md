# AWS CloudFormation S3 - Examples

This file contains comprehensive examples for Amazon S3 patterns with CloudFormation.

## Example 1: Static Website Hosting

Complete static website with custom domain and CloudFront.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Static website hosting on S3 with CloudFront distribution

Parameters:
  DomainName:
    Type: String
    Description: Your domain name (e.g., example.com)
    AllowedPattern: "[a-z0-9-]+\\.[a-z]+"

  HostedZoneName:
    Type: String
    Description: Route 53 hosted zone name
    Default: example.com

  CertificateArn:
    Type: String
    Description: ACM certificate ARN for HTTPS

Conditions:
  IsRootDomain: !Equals [!Ref DomainName, !Ref HostedZoneName]

Resources:
  # S3 Buckets
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref DomainName
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: error.html
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders:
              - "*"
            AllowedMethods:
              - GET
            AllowedOrigins:
              - "*"
            MaxAge: 3600
      Tags:
        - Key: Website
          Value: !Ref DomainName

  WWWRedirectBucket:
    Type: AWS::S3::Bucket
    Condition: IsRootDomain
    Properties:
      BucketName: !Sub www.${DomainName}
      AccessControl: Private
      WebsiteConfiguration:
        RedirectAllRequestsTo:
          HostName: !Ref DomainName
          Protocol: https

  # Bucket Policies
  WebsiteBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref WebsiteBucket
      PolicyDocument:
        Statement:
          - Sid: CloudFrontOAI
            Effect: Allow
            Principal:
              CanonicalUser: !GetAtt CloudFrontOAI.S3CanonicalUserId
            Action: s3:GetObject
            Resource: !Sub ${WebsiteBucket.Arn}/*

  # CloudFront
  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub OAI for ${DomainName}

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !GetAtt WebsiteBucket.RegionalDomainName
            Id: S3Origin
            S3OriginConfig:
              OriginAccessIdentity: !Sub origin-access-identity/cloudfront/${CloudFrontOAI}
        Enabled: true
        IPV6Enabled: true
        DefaultRootObject: index.html
        DefaultCacheBehavior:
          AllowedMethods:
            - GET
            - HEAD
          TargetOriginId: S3Origin
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          ViewerProtocolPolicy: redirect-to-https
          Compress: true
        CustomErrorResponses:
          - ErrorCode: 404
            ResponseCode: 200
            ResponsePagePath: /error.html
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /error.html
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only

  # Route 53 Records
  DNSRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneName: !Sub ${HostedZoneName}.
      Name: !Ref DomainName
      Type: A
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        EvaluateTargetHealth: false
        HostedZoneId: !GetAtt CloudFrontDistribution.HostedZoneId

  DNSRecordIPv6:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneName: !Sub ${HostedZoneName}.
      Name: !Ref DomainName
      Type: AAAA
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        EvaluateTargetHealth: false
        HostedZoneId: !GetAtt CloudFrontDistribution.HostedZoneId

Outputs:
  WebsiteURL:
    Description: URL of the website
    Value: !Sub https://${DomainName}
    Export:
      Name: !Sub ${AWS::StackName}-WebsiteURL

  DistributionID:
    Description: CloudFront distribution ID
    Value: !Ref CloudFrontDistribution
    Export:
      Name: !Sub ${AWS::StackName}-DistributionID
```

## Example 2: Data Lake with Lifecycle Management

S3 bucket configured for data lake storage with tiered lifecycle.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: S3 bucket for data lake with tiered lifecycle management

Parameters:
  BucketName:
    Type: String
    Description: Name of the data lake bucket
    Default: my-data-lake

  RawDataRetention:
    Type: Number
    Description: Days to retain raw data
    Default: 90

  ProcessedDataRetention:
    Type: Number
    Description: Days to retain processed data
    Default: 365

  ArchiveDataRetention:
    Type: Number
    Description: Days before archiving to Glacier
    Default: 30

Resources:
  DataLakeBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !Ref DataLakeKey
            BucketKeyEnabled: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          # Raw data: move to Glacier after 30 days, delete after 90
          - Id: RawDataLifecycle
            Status: Enabled
            PrefixFilter:
              Prefix: raw/
            Transitions:
              - Days: !Ref ArchiveDataRetention
                StorageClass: GLACIER
              - Days: !Ref RawDataRetention
                StorageClass: DEEP_ARCHIVE
            NoncurrentVersionExpirationInDays: 30
            NoncurrentVersionTransitions:
              - NoncurrentDays: 7
                StorageClass: GLACIER
          # Processed data: move to IA after 30 days, archive after 180
          - Id: ProcessedDataLifecycle
            Status: Enabled
            PrefixFilter:
              Prefix: processed/
            Transitions:
              - Days: 30
                StorageClass: STANDARD_IA
              - Days: 180
                StorageClass: GLACIER
            ExpirationInDays: !Ref ProcessedDataRetention
          # Analytics output: delete after 90 days
          - Id: AnalyticsOutputLifecycle
            Status: Enabled
            PrefixFilter:
              Prefix: analytics/
            ExpirationInDays: 90
          # Incomplete multipart uploads cleanup
          - Id: AbortIncompleteUploads
            Status: Enabled
            AbortIncompleteMultipartUpload:
              DaysAfterInitiation: 7
      Tags:
        - Key: DataClassification
          Value: confidential
        - Key: Environment
          Value: production

  DataLakeKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for data lake encryption
      EnableKeyRotation: true
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: Enable IAM policies
            Effect: Allow
            Principal:
              AWS: !Sub arn:aws:iam::${AWS::AccountId}:root
            Action: kms:*
            Resource: "*"
          - Sid: Allow data lake access
            Effect: Allow
            Principal:
              AWS: !Ref DataLakeRole
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey
            Resource: "*"

  DataLakeRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: glue.amazonaws.com
            Action: sts:AssumeRole

Outputs:
  BucketName:
    Description: Name of the data lake bucket
    Value: !Ref DataLakeBucket
    Export:
      Name: !Sub ${AWS::StackName}-BucketName

  BucketArn:
    Description: ARN of the data lake bucket
    Value: !GetAtt DataLakeBucket.Arn
    Export:
      Name: !Sub ${AWS::StackName}-BucketArn
```

## Example 3: Event-Driven Processing Pipeline

S3 bucket with event notifications triggering Lambda functions.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: S3 bucket with Lambda processing pipeline

Parameters:
  BucketName:
    Type: String
    Description: Name of the processing bucket
    Default: my-processing-bucket

  ProcessingFunctionName:
    Type: String
    Description: Name of the Lambda function
    Default: process-data

Resources:
  ProcessingBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      NotificationConfiguration:
        LambdaConfigurations:
          - Event: s3:ObjectCreated:*
            Function: !GetAtt ProcessingFunction.Arn
            Filter:
              S3Key:
                Rules:
                  - Name: prefix
                    Value: uploads/
          - Event: s3:ObjectRemoved:*
            Function: !GetAtt CleanupFunction.Arn
            Filter:
              S3Key:
                Rules:
                  - Name: suffix
                    Value: .tmp
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders:
              - "*"
            AllowedMethods:
              - PUT
              - POST
            AllowedOrigins:
              - "*"
            MaxAge: 3600

  ProcessingFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Ref ProcessingFunctionName
      Handler: index.handler
      Runtime: python3.9
      Code:
        S3Bucket: !Ref ProcessingBucket
        S3Key: functions/process.zip
      Timeout: 300
      Role: !GetAtt LambdaRole.Arn
      Environment:
        Variables:
          OUTPUT_BUCKET: !Ref OutputBucket

  CleanupFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub ${ProcessingFunctionName}-cleanup
      Handler: cleanup.handler
      Runtime: python3.9
      Code:
        S3Bucket: !Ref ProcessingBucket
        S3Key: functions/cleanup.zip
      Timeout: 60
      Role: !GetAtt LambdaRole.Arn

  OutputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${BucketName}-output
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LifecycleConfiguration:
        Rules:
          - Id: CleanOldOutput
            Status: Enabled
            ExpirationInDays: 7

  LambdaRole:
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
        - PolicyName: S3Access
          PolicyDocument:
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                Resource:
                  - !Sub ${ProcessingBucket.Arn}
                  - !Sub ${ProcessingBucket.Arn}/*
                  - !Sub ${OutputBucket.Arn}
                  - !Sub ${OutputBucket.Arn}/*

  BucketPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ProcessingFunction
      Action: lambda:InvokeFunction
      Principal: s3.amazonaws.com
      SourceArn: !GetAtt ProcessingBucket.Arn

Outputs:
  ProcessingBucketName:
    Description: Name of the processing bucket
    Value: !Ref ProcessingBucket
    Export:
      Name: !Sub ${AWS::StackName}-ProcessingBucketName
```

## Example 4: Multi-Environment S3 Configuration

Template with conditions for different environments.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Multi-environment S3 bucket configuration

Parameters:
  Environment:
    Type: String
    Description: Deployment environment
    Default: development
    AllowedValues:
      - development
      - staging
      - production

  BucketSuffix:
    Type: String
    Description: Optional suffix for bucket name
    Default: ""

  EnableVersioning:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false

  EnableLogging:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false

  RetentionDays:
    Type: Number
    Description: Data retention period in days
    Default: 30

Mappings:
  EnvironmentConfig:
    development:
      EnableVersioning: false
      EnableLogging: false
      RetentionDays: 7
      AccessLevel: private
    staging:
      EnableVersioning: true
      EnableLogging: true
      RetentionDays: 30
      AccessLevel: private
    production:
      EnableVersioning: true
      EnableLogging: true
      RetentionDays: 90
      AccessLevel: private-log-delivery

Conditions:
  ShouldEnableVersioning: !Equals [!Ref EnableVersioning, true]
  ShouldEnableLogging: !Equals [!Ref EnableLogging, true]
  HasBucketSuffix: !Not [!Equals [!Ref BucketSuffix, ""]]
  IsDevelopment: !Equals [!Ref Environment, development]

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !If
        - HasBucketSuffix
        - !Sub ${Environment}-${BucketSuffix}
        - !Sub ${Environment}-data
      VersioningConfiguration:
        Status: !If [ShouldEnableVersioning, Enabled, Suspended]
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LoggingConfiguration: !If
        - ShouldEnableLogging
        - DestinationBucketName: !Ref AccessLogBucket
          LogFilePrefix: !Sub ${Environment}/
        - !Ref AWS::NoValue
      LifecycleConfiguration:
        Rules:
          - Id: DataRetention
            Status: Enabled
            ExpirationInDays: !Ref RetentionDays
            NoncurrentVersionExpirationInDays: 7
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  AccessLogBucket:
    Type: AWS::S3::Bucket
    Condition: ShouldEnableLogging
    Properties:
      BucketName: !Sub ${Environment}-access-logs
      AccessControl: LogDeliveryWrite
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LifecycleConfiguration:
        Rules:
          - Id: CleanLogs
            Status: Enabled
            ExpirationInDays: 30

Outputs:
  BucketName:
    Description: Name of the data bucket
    Value: !Ref DataBucket
    Export:
      Name: !Sub ${AWS::StackName}-BucketName

  Environment:
    Description: Deployment environment
    Value: !Ref Environment
```

## Example 5: S3 Bucket with Object Lock

Bucket configured for compliance with Object Lock.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: S3 bucket with Object Lock for compliance

Parameters:
  BucketName:
    Type: String
    Description: Name of the bucket with Object Lock

  RetentionPeriodDays:
    Type: Number
    Description: Default retention period in days
    Default: 365

Resources:
  ObjectLockBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
      ObjectLockEnabled: true
      ObjectLockConfiguration:
        ObjectLockEnabled: Enabled
        Rule:
          DefaultRetention:
            Mode: COMPLIANCE
            Days: !Ref RetentionPeriodDays
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
      Tags:
        - Key: Compliance
          Value: enabled
        - Key: RetentionPeriod
          Value: !Ref RetentionPeriodDays

Outputs:
  BucketName:
    Description: Name of the Object Lock bucket
    Value: !Ref ObjectLockBucket
    Export:
      Name: !Sub ${AWS::StackName}-BucketName

  BucketArn:
    Description: ARN of the Object Lock bucket
    Value: !GetAtt ObjectLockBucket.Arn
    Export:
      Name: !Sub ${AWS::StackName}-BucketArn
```

## Example 6: Cross-Region Replication

S3 bucket with cross-region replication configuration.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: S3 bucket with cross-region replication

Parameters:
  SourceBucketName:
    Type: String
    Description: Name of the source bucket

  DestinationBucketName:
    Type: String
    Description: Name of the destination bucket

  DestinationRegion:
    Type: String
    Description: Destination region
    Default: us-west-2

Resources:
  SourceBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref SourceBucketName
      VersioningConfiguration:
        Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      ReplicationConfiguration:
        Role: !GetAtt ReplicationRole.Arn
        Rules:
          - Id: ReplicateToDestRegion
            Status: Enabled
            Priority: 1
            Filter:
              Prefix: ""
            Destination:
              Bucket: !Sub arn:aws:s3:::${DestinationBucketName}
              StorageClass: STANDARD_IA
              EncryptionConfiguration:
                ReplicaKmsKeyID: !Ref DestKMSKey
              Account: !Ref DestinationAccountId

  ReplicationRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: s3.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: ReplicationPolicy
          PolicyDocument:
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetReplicationConfiguration
                  - s3:GetObjectVersion
                  - s3:GetObjectVersionAcl
                  - s3:GetObjectVersionTagging
                Resource:
                  - !Sub ${SourceBucket.Arn}
                  - !Sub ${SourceBucket.Arn}/*
              - Effect: Allow
                Action:
                  - s3:ReplicateObject
                  - s3:ReplicateDelete
                  - s3:ObjectOwnerOverrideToBucketOwner
                  - s3:ReplicateTags
                Resource:
                  - !Sub arn:aws:s3:::${DestinationBucketName}
                  - !Sub arn:aws:s3:::${DestinationBucketName}/*
              - Effect: Allow
                Action:
                  - kms:Decrypt
                  - kms:Encrypt
                  - kms:GenerateDataKey
                Resource: !Ref SourceKMSKey
                Condition:
                  StringEquals:
                    kms:ViaService: !Sub s3.${AWS::Region}.amazonaws.com
              - Effect: Allow
                Action:
                  - kms:Decrypt
                  - kms:Encrypt
                  - kms:GenerateDataKey
                Resource: !Ref DestKMSKey
                Condition:
                  StringEquals:
                    kms:ViaService: !Sub s3.${DestinationRegion}.amazonaws.com

  SourceKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for source bucket encryption

  DestKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for destination bucket encryption

Outputs:
  SourceBucketName:
    Description: Name of the source bucket
    Value: !Ref SourceBucket
    Export:
      Name: !Sub ${AWS::StackName}-SourceBucketName

  DestinationBucketName:
    Description: Name of the destination bucket
    Value: !Ref DestinationBucketName
```

## Example 7: S3 Inventory and Analytics

Bucket with analytics and inventory configurations.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: S3 bucket with analytics and inventory configurations

Parameters:
  BucketName:
    Type: String
    Description: Name of the bucket

Resources:
  AnalyticsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      AnalyticsConfigurations:
        - Id: AnalyticsConfig
          StorageClassAnalysis:
            DataExport:
              Destination:
                S3BucketDestination:
                  Bucket: !Ref AnalyticsReportBucket
                  BucketAccountId: !Ref AWS::AccountId
                  Format: CSV
                  Prefix: analytics/
      InventoryConfigurations:
        - Id: DailyInventory
          IncludedObjectVersions: Current
          Schedule:
            Frequency: Daily
          Destination:
            S3BucketDestination:
              Bucket: !Ref InventoryReportBucket
              BucketAccountId: !Ref AWS::AccountId
              Format: CSV
              Prefix: inventory/
          Filter:
            Prefix: data/
          OptionalFields:
            - Size
            - LastModifiedDate
            - StorageClass
            - ETag
            - IsMultipartUploaded

  AnalyticsReportBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${BucketName}-analytics-reports
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  InventoryReportBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${BucketName}-inventory-reports
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      LifecycleConfiguration:
        Rules:
          - Id: CleanOldReports
            Status: Enabled
            ExpirationInDays: 90

Outputs:
  BucketName:
    Description: Name of the analytics bucket
    Value: !Ref AnalyticsBucket
```
