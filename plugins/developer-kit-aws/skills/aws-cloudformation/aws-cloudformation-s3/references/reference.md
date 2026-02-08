# AWS CloudFormation S3 - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for S3 infrastructure.

## AWS::S3::Bucket

Creates an Amazon S3 bucket.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AccelerateConfiguration | AccelerateConfiguration | No | Configures bucket acceleration |
| AccessControl | String | No | A canned ACL (Private, PublicRead, etc.) |
| AnalyticsConfigurations | List | No | Analytics configurations for inventory reports |
| BucketEncryption | BucketEncryption | No | Server-side encryption configuration |
| BucketName | String | No | Name of the bucket |
| CorsConfiguration | CorsConfiguration | No | CORS rules for cross-origin requests |
| EventBridgeConfiguration | EventBridgeConfiguration | No | EventBridge configuration |
| IntelligentTieringConfiguration | IntelligentTieringConfiguration | No | S3 Intelligent-Tiering configuration |
| InventoryConfigurations | List | No | Inventory configurations |
| LifecycleConfiguration | LifecycleConfiguration | No | Lifecycle rules for object management |
| LoggingConfiguration | LoggingConfiguration | No | Server access logging configuration |
| MetricsConfiguration | MetricsConfiguration | No | CloudWatch metrics configuration |
| NotificationConfiguration | NotificationConfiguration | No | Event notification configuration |
| ObjectLockConfiguration | ObjectLockConfiguration | No | Object Lock configuration |
| ObjectLockEnabled | Boolean | No | Whether Object Lock is enabled |
| OwnershipControls | OwnershipControls | No | Bucket ownership controls |
| PublicAccessBlockConfiguration | PublicAccessBlockConfiguration | No | Block public access settings |
| ReplicationConfiguration | ReplicationConfiguration | No | Cross-region replication rules |
| Tags | List | No | Tags assigned to the bucket |
| VersioningConfiguration | VersioningConfiguration | No | Versioning status |
| WebsiteConfiguration | WebsiteConfiguration | No | Static website hosting configuration |

### VersioningConfiguration

```yaml
VersioningConfiguration:
  Status: Enabled | Suspended
  MFADelete: Enabled | Disabled  # Optional
```

### CorsConfiguration

```yaml
CorsConfiguration:
  CorsRules:
    - AllowedHeaders:
        - "*"
      AllowedMethods:
        - GET
        - PUT
        - POST
        - DELETE
        - HEAD
      AllowedOrigins:
        - "https://example.com"
      ExposedHeaders:
        - ContentLength
        - Date
      MaxAge: 3600
```

### LifecycleConfiguration

```yaml
LifecycleConfiguration:
  Rules:
    - ID: string
      Status: Enabled | Disabled
      PrefixFilter:
        Prefix: logs/
      TagFilter:
        - Key: Environment
          Value: production
      ExpirationInDays: 30
      ExpirationDate: "2024-12-31T00:00:00.000Z"
      Transitions:
        - Days: 30
          StorageClass: STANDARD_IA | GLACIER | DEEP_ARCHIVE
        - Days: 90
          StorageClass: GLACIER
      NoncurrentVersionExpirationInDays: 7
      NoncurrentVersionTransitions:
        - NoncurrentDays: 30
          StorageClass: STANDARD_IA
```

### LoggingConfiguration

```yaml
LoggingConfiguration:
  DestinationBucketName: !Ref LogBucket
  LogFilePrefix: logs/
  LogFilePrefix: !Sub ${AWS::StackName}/logs/
```

### BucketEncryption

```yaml
BucketEncryption:
  ServerSideEncryptionConfiguration:
    - ServerSideEncryptionByDefault:
        SSEAlgorithm: AES256 | aws:kms | aws:kms:dsse
        KMSMasterKeyID: !Ref KMSKeyArn
    BucketKeyEnabled: true
```

### PublicAccessBlockConfiguration

```yaml
PublicAccessBlockConfiguration:
  BlockPublicAcls: true
  BlockPublicPolicy: true
  IgnorePublicAcls: true
  RestrictPublicBuckets: true
```

### NotificationConfiguration

```yaml
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
  QueueConfigurations:
    - Event: s3:ObjectCreated:*
      Queue: !Ref EventQueue
      Filter:
        S3Key:
          Rules:
            - Name: suffix
              Value: .log
  TopicConfigurations:
    - Event: s3:ObjectCreated:*
      Topic: !Ref EventTopic
```

### ReplicationConfiguration

```yaml
ReplicationConfiguration:
  Role: !GetAtt ReplicationRole.Arn
  Rules:
    - ID: string
      Status: Enabled | Disabled
      Priority: 1
      Filter:
        Prefix: ""
        And:
          Prefix: ""
          Tags:
            - Key: Key
              Value: Value
      Destination:
        Bucket: arn:aws:s3:::destination-bucket
        Account: destination-account-id
        StorageClass: STANDARD | STANDARD_IA | INTELLIGENT_TIERING
        EncryptionConfiguration:
          ReplicaKmsKeyID: kms-key-arn
        AccessControlTranslation:
          Owner: Destination
        Account: account-id
        Metrics:
          Status: Enabled
          EventThreshold:
            Minutes: 15
        ReplicationTime:
          Status: Enabled
          Time:
            Minutes: 15
      SourceSelectionCriteria:
        SseKmsEncryptedObjects:
          Status: Enabled
```

### WebsiteConfiguration

```yaml
WebsiteConfiguration:
  IndexDocument: index.html
  ErrorDocument: error.html
  RoutingRules:
    - Condition:
        KeyPrefixEquals: docs/
      Redirect:
        ReplaceKeyWith: documents/index.html
    - Condition:
        HttpErrorCodeReturnedEquals: 404
      Redirect:
        Protocol: https
        HostName: example.com
        ReplaceKeyWith: 404.html
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The Amazon Resource Name (ARN) of the bucket |
| DomainName | The DNS name of the bucket |
| DualStackDomainName | The DNS name of the bucket when using IPv6 |
| RegionalDomainName | The regional domain name of the bucket |
| WebsiteURL | URL of the website endpoint |
| S3CanonicalUserId | The canonical user ID for the bucket owner |

### Examples

#### Basic Bucket

```yaml
Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-data-bucket
```

#### Bucket with Versioning and Logging

```yaml
Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-data-bucket
      VersioningConfiguration:
        Status: Enabled
      LoggingConfiguration:
        DestinationBucketName: !Ref LogBucket
        LogFilePrefix: logs/
      Tags:
        - Key: Environment
          Value: production
```

#### Bucket with Lifecycle Rules

```yaml
Resources:
  LifecycleBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-lifecycle-bucket
      LifecycleConfiguration:
        Rules:
          - Id: ArchiveOldData
            Status: Enabled
            PrefixFilter:
              Prefix: archive/
            Transitions:
              - Days: 30
                StorageClass: GLACIER
            ExpirationInDays: 365
```

#### Bucket with CORS

```yaml
Resources:
  CorsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-cors-bucket
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders:
              - Authorization
              - Content-Type
            AllowedMethods:
              - GET
              - PUT
              - POST
            AllowedOrigins:
              - "https://example.com"
              - "https://*.example.com"
            MaxAge: 3600
```

## AWS::S3::BucketPolicy

Applies a bucket policy to an Amazon S3 bucket.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Bucket | String | Yes | Name of the bucket to apply the policy to |
| PolicyDocument | PolicyDocument | Yes | Policy to apply |

### PolicyDocument Structure

```yaml
PolicyDocument:
  Version: "2012-10-17" | "2008-10-17"
  Id: policy-id
  Statement:
    - Sid: statement-id
      Effect: Allow | Deny
      Principal:
        AWS: arn:aws:iam::account-id:user/user-name
        Service: service-name.amazonaws.com
        CanonicalUser: canonical-user-id
        "*":  # All principals
      Action:
        - s3:GetObject
        - s3:PutObject
        - s3:DeleteObject
      NotAction:
        - s3:*
      Resource:
        - arn:aws:s3:::bucket-name
        - arn:aws:s3:::bucket-name/*
      NotResource:
        - arn:aws:s3:::bucket-name/secret/*
      Condition:
        ConditionOperator:
          ConditionKey: condition-value
```

### Condition Operators

| Operator | Description |
|----------|-------------|
| StringEquals | Exact string match |
| StringNotEquals | Negated string match |
| StringLike | String with wildcards |
| StringNotLike | Negated string with wildcards |
| NumericEquals | Exact number match |
| NumericNotEquals | Negated number match |
| NumericLessThan | Less than comparison |
| NumericLessThanEquals | Less than or equal |
| NumericGreaterThan | Greater than comparison |
| NumericGreaterThanEquals | Greater than or equal |
| Bool | Boolean comparison |
| IpAddress | IP address range |
| NotIpAddress | Excluded IP address |
| ArnEquals | ARN match |
| ArnLike | ARN with wildcards |

### Common Condition Keys

| Key | Description |
|-----|-------------|
| aws:sourceVpce | VPC endpoint ID |
| aws:sourceVpc | VPC ID |
| aws:PrincipalAccount | Principal's account ID |
| aws:PrincipalArn | Principal's ARN |
| aws:SecureTransport | Whether request uses HTTPS |
| s3:prefix | Object key prefix |
| s3:Delimiter | Delimiter for listing |
| s3:max-keys | Max keys in listing |

### Examples

#### Allow Access from VPC Endpoint

```yaml
Resources:
  PrivateBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-private-bucket

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref PrivateBucket
      PolicyDocument:
        Statement:
          - Sid: AllowVPCEndpoint
            Effect: Allow
            Principal: "*"
            Action: s3:GetObject
            Resource: !Sub ${PrivateBucket.Arn}/*
            Condition:
              StringEquals:
                aws:sourceVpce: !Ref VPCEndpointId
```

#### Deny Unencrypted Uploads

```yaml
Resources:
  SecureBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-secure-bucket

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref SecureBucket
      PolicyDocument:
        Statement:
          - Sid: DenyUnencryptedUploads
            Effect: Deny
            Principal: "*"
            Action: s3:PutObject
            Resource: !Sub ${SecureBucket.Arn}/*
            Condition:
              StringNotEquals:
                s3:x-amz-server-side-encryption: AES256
          - Sid: DenyKMSUnencryptedUploads
            Effect: Deny
            Principal: "*"
            Action: s3:PutObject
            Resource: !Sub ${SecureBucket.Arn}/*
            Condition:
              StringNotEquals:
                s3:x-amz-server-side-encryption: aws:kms
              Null:
                s3:x-amz-server-side-encryption-aws-kms-key-id: false
```

#### Allow CloudFront OAI Access

```yaml
Resources:
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-website-bucket
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: error.html

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref WebsiteBucket
      PolicyDocument:
        Statement:
          - Sid: CloudFrontReadAccess
            Effect: Allow
            Principal:
              CanonicalUser: !GetAtt CloudFrontOAI.S3CanonicalUserId
            Action: s3:GetObject
            Resource: !Sub ${WebsiteBucket.Arn}/*

  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: Website OAI
```

#### Cross-Account Access

```yaml
Resources:
  SharedBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-shared-bucket

  BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref SharedBucket
      PolicyDocument:
        Statement:
          - Sid: CrossAccountRead
            Effect: Allow
            Principal:
              AWS:
                - arn:aws:iam::123456789012:role/ReadRole
                - arn:aws:iam::123456789012:user/ReadUser
            Action:
              - s3:GetObject
              - s3:GetObjectVersion
            Resource: !Sub ${SharedBucket.Arn}/*
          - Sid: CrossAccountWrite
            Effect: Allow
            Principal:
              AWS: arn:aws:iam::123456789012:role/WriteRole
            Action:
              - s3:PutObject
            Resource: !Sub ${SharedBucket.Arn}/*
```

## Intrinsic Functions

### Fn::Ref

Returns the bucket name.

```yaml
BucketName: !Ref DataBucket
```

### Fn::GetAtt

Returns bucket attributes.

```yaml
BucketArn: !GetAtt DataBucket.Arn
BucketDomainName: !GetAtt DataBucket.DomainName
WebsiteURL: !GetAtt DataBucket.WebsiteURL
S3CanonicalUserId: !GetAtt DataBucket.S3CanonicalUserId
```

### Fn::Sub

Substitutes variables in an input string with values.

```yaml
BucketArn: !Sub "arn:aws:s3:::${BucketName}"
```

### Fn::Join

Appends a set of values into a single value.

```yaml
Resource: !Join
  - ""
  - - "arn:aws:s3:::"
    - !Ref BucketName
    - "/*"
```

### Fn::ImportValue

Imports an output value exported by another stack.

```yaml
BucketArn: !ImportValue storage-stack-BucketArn
```

## Best Practices

### Security

1. **Block Public Access**: Always enable block public access settings
2. **Use Bucket Policies**: Define explicit access controls
3. **Enable Versioning**: Protect against accidental deletion
4. **Use Encryption**: Enable server-side encryption
5. **Use VPC Endpoints**: Keep traffic within AWS network

### Cost Optimization

1. **Lifecycle Rules**: Move data to cheaper storage classes
2. **Intelligent-Tiering**: Use for unpredictable access patterns
3. **Delete Old Versions**: Clean up noncurrent versions
4. **Monitor with Metrics**: Track storage usage

### Performance

1. **Use Prefixes**: Distribute objects across prefixes for parallelism
2. **Enable Transfer Acceleration**: For faster global uploads
3. **Use Multi-Region Access Points**: For low-latency access
