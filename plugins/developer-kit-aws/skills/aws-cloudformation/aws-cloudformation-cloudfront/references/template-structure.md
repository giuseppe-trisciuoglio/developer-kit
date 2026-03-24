# CloudFormation Template Structure for CloudFront

## Standard Format Base Template

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront distribution with multiple origins

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: Distribution Configuration
        Parameters:
          - DomainName
          - CertificateArn
          - PriceClass
      - Label:
          default: Origin Settings
        Parameters:
          - OriginDomainName
          - OriginPath
          - OriginProtocolPolicy

Parameters:
  DomainName:
    Type: String
    Default: cdn.example.com
    Description: Custom domain name for CloudFront distribution

  CertificateArn:
    Type: AWS::ACM::Certificate::Arn
    Description: ACM certificate ARN for HTTPS

  PriceClass:
    Type: String
    Default: PriceClass_All
    AllowedValues:
      - PriceClass_All
      - PriceClass_100
      - PriceClass_200
    Description: CloudFront price class

  OriginDomainName:
    Type: String
    Description: Domain name of the origin (ALB or S3)

  OriginPath:
    Type: String
    Default: ""
    Description: Optional origin path

Mappings:
  EnvironmentConfig:
    us-east-1:
      CertificateRegion: us-east-1
    other:
      CertificateRegion: us-east-1

Conditions:
  IsUsEast1: !Equals [!Ref AWS::Region, us-east-1]
  HasOriginPath: !Not [!Equals [!Ref OriginPath, ""]]

Transform:
  - AWS::Serverless-2016-10-31

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront distribution for ${DomainName}"
        DomainNames:
          - !Ref DomainName
        Enabled: true
        PriceClass: !Ref PriceClass
        IPV6Enabled: true
        DefaultRootObject: index.html
        Origins:
          - Id: !Sub "${DomainName}-origin"
            DomainName: !Ref OriginDomainName
            OriginPath: !If [HasOriginPath, !Ref OriginPath, !Ref AWS::NoValue]
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
              OriginSSLProtocols:
                - TLSv1.2
        DefaultCacheBehavior:
          TargetOriginId: !Sub "${DomainName}-origin"
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only

Outputs:
  DistributionDomainName:
    Description: CloudFront distribution domain name
    Value: !GetAtt CloudFrontDistribution.DomainName
    Export:
      Name: !Sub "${AWS::StackName}-DistributionDomainName"

  DistributionId:
    Description: CloudFront distribution ID
    Value: !Ref CloudFrontDistribution
    Export:
      Name: !Sub "${AWS::StackName}-DistributionId"
```

## AWS-Specific Parameter Types

```yaml
Parameters:
  # ACM Certificate for domain
  CertificateArn:
    Type: AWS::ACM::Certificate::Arn
    Description: ACM certificate for the domain

  # S3 Bucket origins
  StaticAssetsBucket:
    Type: AWS::S3::Bucket
    Description: S3 bucket for static assets

  StaticAssetsBucketDomainName:
    Type: AWS::S3::Bucket::RegionalDomainName
    Description: Regional domain name of the S3 bucket

  # ALB origins
  LoadBalancerArn:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer::Arn
    Description: ARN of the Application Load Balancer

  LoadBalancerDNSName:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer::DnsName
    Description: DNS name of the ALB

  # Lambda function origins
  LambdaFunctionArn:
    Type: AWS::Lambda::Function::Arn
    Description: ARN of the Lambda function for Lambda@Edge

  # VPC Origin
  VPCOriginEndpoint:
    Type: AWS::GlobalAccelerator::Endpoint::EndpointId
    Description: VPC Origin endpoint ID

  # IAM Role for Lambda@Edge
  LambdaEdgeRoleArn:
    Type: AWS::IAM::Role::Arn
    Description: IAM role for Lambda@Edge execution
```

## Parameter Constraints

```yaml
Parameters:
  DomainName:
    Type: String
    Default: cdn.example.com
    Description: Custom domain name for CloudFront
    ConstraintDescription: Must be a valid domain name
    MinLength: 4
    MaxLength: 253
    AllowedPattern: "[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*"

  PriceClass:
    Type: String
    Default: PriceClass_All
    Description: CloudFront price class
    AllowedValues:
      - PriceClass_All
      - PriceClass_100
      - PriceClass_200

  DefaultTTL:
    Type: Number
    Default: 86400
    Description: Default cache TTL in seconds
    MinValue: 0
    MaxValue: 31536000
    ConstraintDescription: Must be between 0 and 31536000 seconds

  MaxTTL:
    Type: Number
    Default: 31536000
    Description: Maximum cache TTL in seconds
    MinValue: 0
    MaxValue: 31536000

  MinTTL:
    Type: Number
    Default: 0
    Description: Minimum cache TTL in seconds
    MinValue: 0
    MaxValue: 31536000
```

## SSM Parameter References

```yaml
Parameters:
  WafWebAclArn:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /cloudfront/waf-webacl-arn
    Description: WAF Web ACL ARN from Parameter Store

  CloudFrontKeyId:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /cloudfront/keys/cloudfront-key-id
    Description: CloudFront key pair ID for signed URLs
```

## Metadata for Parameter Grouping

```yaml
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: Distribution Configuration
        Parameters:
          - DomainName
          - CertificateArn
          - PriceClass
      - Label:
          default: Origin Settings
        Parameters:
          - OriginDomainName
          - OriginPath
          - OriginProtocolPolicy
      - Label:
          default: Cache Settings
        Parameters:
          - DefaultTTL
          - MinTTL
          - MaxTTL
          - PriceClass
    ParameterLabels:
      DomainName:
        default: Custom Domain Name
      CertificateArn:
        default: SSL Certificate
      PriceClass:
        default: Price Class for Cost Optimization
```

## Transform for Macros

```yaml
Transform:
  - AWS::Serverless-2016-10-31
  - AWS::LanguageExtensions
  - Name: MyCustomMacro
```

## Conditions for Environment-Specific Configuration

```yaml
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production
    Description: Deployment environment

  EnableWAF:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false
    Description: Enable WAF protection

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  IsStaging: !Equals [!Ref Environment, staging]
  EnableWAFProtection: !And
    - !Equals [!Ref EnableWAF, true]
    - !Or
      - [!Equals [!Ref Environment, staging]]
      - [!Equals [!Ref Environment, production]]
```

## Nested Stacks for Modularity

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Main stack with nested CloudFront stacks

Resources:
  # Nested stack for static assets distribution
  StaticAssetsDistributionStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/bucket/cloudfront-static.yaml
      TimeoutInMinutes: 15
      Parameters:
        DomainName: !Ref DomainName
        CertificateArn: !Ref CertificateArn
        StaticAssetsBucketName: !Ref StaticAssetsBucketName
        Environment: !Ref Environment

  # Nested stack for API distribution
  ApiDistributionStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/bucket/cloudfront-api.yaml
      TimeoutInMinutes: 15
      Parameters:
        DomainName: !Ref ApiDomainName
        CertificateArn: !Ref CertificateArn
        LoadBalancerDnsName: !Ref LoadBalancerDnsName
        Environment: !Ref Environment
```

## Outputs and Cross-Stack References

### Export/Import Patterns

```yaml
# Stack A - Infrastructure Stack
AWSTemplateFormatVersion: 2010-09-09
Description: Infrastructure stack exporting CloudFront resources

Resources:
  # S3 Bucket for static content
  StaticAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "static-assets-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled
      CorsConfiguration:
        CorsRules:
          - AllowedHeaders:
              - "*"
            AllowedMethods:
              - GET
              - HEAD
            AllowedOrigins:
              - "*"
            MaxAge: 3600

  # OAI for CloudFront access
  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${StaticAssetsBucket}"

Outputs:
  StaticAssetsBucketName:
    Description: S3 bucket name for static assets
    Value: !Ref StaticAssetsBucket
    Export:
      Name: !Sub "${AWS::StackName}-StaticAssetsBucketName"

  StaticAssetsBucketRegionalDomainName:
    Description: Regional domain name of the S3 bucket
    Value: !GetAtt StaticAssetsBucket.RegionalDomainName
    Export:
      Name: !Sub "${AWS::StackName}-StaticAssetsBucketRegionalDomainName"

  CloudFrontOAIId:
    Description: CloudFront OAI ID
    Value: !Ref CloudFrontOAI
    Export:
      Name: !Sub "${AWS::StackName}-CloudFrontOAIId"
```

```yaml
# Stack B - Application Stack (imports from Infrastructure Stack)
AWSTemplateFormatVersion: 2010-09-09
Description: Application stack importing from infrastructure stack

Parameters:
  InfrastructureStackName:
    Type: String
    Default: infrastructure-stack
    Description: Name of the infrastructure stack

  DomainName:
    Type: String
    Default: cdn.example.com
    Description: Custom domain name

  CertificateArn:
    Type: AWS::ACM::Certificate::Arn
    Description: ACM certificate ARN

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront for ${DomainName}"
        Enabled: true
        IPV6Enabled: true
        DefaultRootObject: index.html
        Origins:
          - Id: StaticAssetsOrigin
            DomainName: !ImportValue
              !Sub "${InfrastructureStackName}-StaticAssetsBucketRegionalDomainName"
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${InfrastructureStackName}-CloudFrontOAIId"
        DefaultCacheBehavior:
          TargetOriginId: StaticAssetsOrigin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only
```
