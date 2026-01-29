# AWS CloudFormation CloudFront - Examples

Questo file contiene esempi completi e production-ready per pattern CloudFront con CloudFormation.

## Esempio 1: Static Website Hosting con S3

Configurazione completa per un sito web statico su S3 con CloudFront, OAI e certificato ACM.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Static website hosting with CloudFront and S3

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  DomainName:
    Type: String
    Default: cdn.example.com
    Description: Custom domain name

  CertificateArn:
    Type: AWS::ACM::Certificate::Arn
    Description: ACM certificate ARN for the domain

  HostedZoneId:
    Type: AWS::Route53::HostedZone::Id
    Description: Route53 hosted zone ID

Mappings:
  EnvironmentConfig:
    dev:
      PriceClass: PriceClass_100
      Compress: false
    staging:
      PriceClass: PriceClass_100
      Compress: true
    production:
      PriceClass: PriceClass_All
      Compress: true

Resources:
  # S3 Bucket per contenuti statici
  StaticAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "static-assets-${AWS::AccountId}-${AWS::Region}"
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
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: static-website

  # CloudFront Origin Access Identity
  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${StaticAssetsBucket}"

  # S3 Bucket Policy - Permetti accesso solo da CloudFront
  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref StaticAssetsBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              CanonicalUser: !GetAtt CloudFrontOAI.S3CanonicalUserId
            Action: s3:GetObject
            Resource: !Sub "${StaticAssetsBucket.Arn}/*"
          - Effect: Deny
            Principal: "*"
            Action: s3:GetObject
            Resource: !Sub "${StaticAssetsBucket.Arn}/*"
            Condition:
              Bool:
                aws:SecureTransport: false

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "Static assets CDN for ${Environment}"
        Enabled: true
        IPV6Enabled: true
        PriceClass: !FindInMap [EnvironmentConfig, !Ref Environment, PriceClass]
        DefaultRootObject: index.html
        Origins:
          - Id: StaticAssetsOrigin
            DomainName: !GetAtt StaticAssetsBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
        DefaultCacheBehavior:
          TargetOriginId: StaticAssetsOrigin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          Compress: !FindInMap [EnvironmentConfig, !Ref Environment, Compress]
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
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: static-website
        - Key: ManagedBy
          Value: CloudFormation

  # Route53 Record Set
  CloudFrontDNSRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      Name: !Ref DomainName
      Type: A
      HostedZoneId: !Ref HostedZoneId
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        EvaluateTargetHealth: false
        HostedZoneId: Z2FDTNDATAQYW2

  # Route53 AAAA Record per IPv6
  CloudFrontDNSRecordAAAA:
    Type: AWS::Route53::RecordSet
    Properties:
      Name: !Ref DomainName
      Type: AAAA
      HostedZoneId: !Ref HostedZoneId
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        EvaluateTargetHealth: false
        HostedZoneId: Z2FDTNDATAQYW2

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

  StaticAssetsBucketName:
    Description: S3 bucket name
    Value: !Ref StaticAssetsBucket
    Export:
      Name: !Sub "${AWS::StackName}-StaticAssetsBucketName"
```

## Esempio 2: Multi-Origin con API, S3 e Lambda@Edge

Configurazione avanzata con origini multiple per contenuti statici, API e funzioni Lambda@Edge.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Multi-origin CloudFront distribution with S3, ALB and Lambda@Edge

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  DomainName:
    Type: String
    Default: example.com
    Description: Custom domain name

  CertificateArn:
    Type: AWS::ACM::Certificate::Arn
    Description: ACM certificate ARN

  StaticBucketName:
    Type: String
    Description: S3 bucket for static assets

  StaticBucketRegionalDomainName:
    Type: AWS::S3::Bucket::RegionalDomainName
    Description: Regional domain name of S3 bucket

  CloudFrontOAIId:
    Type: String
    Description: CloudFront OAI ID

  LoadBalancerDnsName:
    Type: String
    Description: DNS name of the Application Load Balancer

  LambdaEdgeFunctionArn:
    Type: AWS::Lambda::Function::Arn
    Description: ARN of Lambda@Edge function

  LambdaEdgeFunctionVersion:
    Type: String
    Description: Version of Lambda@Edge function

Mappings:
  EnvironmentConfig:
    dev:
      PriceClass: PriceClass_100
      ApiCacheTTL: 0
      StaticCacheTTL: 3600
    staging:
      PriceClass: PriceClass_100
      ApiCacheTTL: 300
      StaticCacheTTL: 86400
    production:
      PriceClass: PriceClass_All
      ApiCacheTTL: 300
      StaticCacheTTL: 31536000

Resources:
  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "Multi-origin CDN for ${DomainName}"
        Enabled: true
        IPV6Enabled: true
        PriceClass: !FindInMap [EnvironmentConfig, !Ref Environment, PriceClass]
        DefaultRootObject: index.html
        Origins:
          # Static assets origin (S3)
          - Id: StaticAssetsOrigin
            DomainName: !Ref StaticBucketRegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAIId}"

          # API origin (ALB)
          - Id: ApiOrigin
            DomainName: !Ref LoadBalancerDnsName
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
              OriginSSLProtocols:
                - TLSv1.2
            ConnectionAttempts: 3
            ConnectionTimeout: 10
            OriginReadTimeout: 30
            OriginKeepaliveTimeout: 5

          # Lambda@Edge origin
          - Id: LambdaOrigin
            DomainName: !Sub "${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com"
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only

        # Default cache behavior - Static assets
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
          DefaultTTL: !FindInMap [EnvironmentConfig, !Ref Environment, StaticCacheTTL]
          MaxTTL: 31536000
          LambdaFunctionAssociations:
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${LambdaEdgeFunctionArn}:${LambdaEdgeFunctionVersion}"
              EventType: viewer-request

        # API cache behavior
        CacheBehaviors:
          - PathPattern: "/api/*"
            TargetOriginId: ApiOrigin
            ViewerProtocolPolicy: redirect-to-https
            AllowedMethods:
              - GET
              - HEAD
              - OPTIONS
              - PUT
              - POST
              - PATCH
              - DELETE
            CachedMethods:
              - GET
              - HEAD
            Compress: true
            ForwardedValues:
              QueryString: true
              Headers:
                - Accept
                - Accept-Language
                - Authorization
                - Content-Type
              Cookies:
                Forward: all
              QueryStringCacheKeys:
                - version
                - lang
            MinTTL: 0
            DefaultTTL: !FindInMap [EnvironmentConfig, !Ref Environment, ApiCacheTTL]
            MaxTTL: 600
            LambdaFunctionAssociations:
              - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${LambdaEdgeFunctionArn}:${LambdaEdgeFunctionVersion}"
                EventType: origin-request

          # Static assets with longer cache
          - PathPattern: "/static/*"
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
            DefaultTTL: 31536000
            MaxTTL: 31536000

          # Lambda function path
          - PathPattern: "/lambda/*"
            TargetOriginId: LambdaOrigin
            ViewerProtocolPolicy: redirect-to-https
            AllowedMethods:
              - GET
              - HEAD
              - OPTIONS
            CachedMethods:
              - GET
              - HEAD
            Compress: true
            ForwardedValues:
              QueryString: true
              Cookies:
                Forward: none
            MinTTL: 0
            DefaultTTL: 0
            MaxTTL: 0

        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only

Outputs:
  DistributionDomainName:
    Value: !GetAtt CloudFrontDistribution.DomainName

  DistributionId:
    Value: !Ref CloudFrontDistribution
```

## Esempio 3: CloudFront con WAF e Security Headers

Configurazione completa con WAF, security headers e monitoring.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with WAF, security headers and monitoring

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  DomainName:
    Type: String
    Default: secure.example.com

  CertificateArn:
    Type: AWS::ACM::Certificate::Arn

  AlertEmail:
    Type: String
    Description: Email per alert SNS

Mappings:
  EnvironmentConfig:
    dev:
      EnableWAF: false
    staging:
      EnableWAF: true
    production:
      EnableWAF: true

Resources:
  # WAF Web ACL
  CloudFrontWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: !Sub "${AWS::StackName}-waf-acl"
      Scope: CLOUDFRONT
      DefaultAction:
        Allow: {}
      Rules:
        # AWS Managed - Common Rule Set
        - Name: AWSManagedRulesCommonRuleSet
          Priority: 1
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
              ExcludedRules:
                - Name: SizeRestrictions_BODY
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AWSManagedRulesCommonRuleSet

        # AWS Managed - Known Bad Inputs
        - Name: AWSManagedRulesKnownBadInputsRuleSet
          Priority: 2
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesKnownBadInputsRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AWSKnownBadInputs

        # AWS Managed - SQL Database
        - Name: AWSManagedRulesSQLiRuleSet
          Priority: 3
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesSQLiRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AWSSQLi

        # Rate-based rule per protezione DDoS
        - Name: RateLimitRule
          Priority: 4
          Statement:
            RateBasedStatementKey:
              SingleHeader:
                Name: ip
            AggregateKeyType: IP
            Limit: 1000
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: RateLimitRule

        # Geographic restriction
        - Name: GeoBlockRule
          Priority: 5
          Statement:
            NotStatement:
              Statement:
                GeoMatchStatement:
                  CountryCodes:
                    - US
                    - CA
                    - GB
                    - DE
                    - FR
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: GeoBlockRule

      VisibilityConfig:
        SampledRequestsEnabled: true
        CloudWatchMetricsEnabled: true
        MetricName: CloudFrontWAFACL

  # Security Headers Policy
  SecurityHeadersPolicy:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: !Sub "${AWS::StackName}-security-headers"
        SecurityHeadersConfig:
          ContentTypeOptions:
            Override: true
          FrameOptions:
            FrameOption: DENY
            Override: true
          ReferrerPolicy:
            ReferrerPolicy: strict-origin-when-cross-origin
            Override: true
          StrictTransportSecurity:
            AccessControlMaxAgeSec: 31536000
            IncludeSubdomains: true
            Override: true
            Preload: true
          XSSProtection:
            ModeBlock: true
            Override: true
            Protection: true
        CorsConfig:
          AccessControlAllowCredentials: false
          AccessControlAllowHeaders:
            Items:
              - "*"
          AccessControlAllowMethods:
            Items:
              - GET
              - HEAD
              - OPTIONS
          AccessControlAllowOrigins:
            Items:
              - https://example.com
              - https://www.example.com
          AccessControlMaxAgeSec: 600
          OriginOverride: true

  # Origin Domain
  OriginDomainName:
    Type: String
    Default: origin.example.com

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "Secure CDN with WAF for ${Environment}"
        Enabled: true
        IPV6Enabled: true
        PriceClass: PriceClass_All
        WebACLId: !GetAtt CloudFrontWebACL.Arn
        Origins:
          - Id: Origin
            DomainName: !Ref OriginDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
            - OPTIONS
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          ForwardedValues:
            QueryString: true
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000
          ResponseHeadersPolicyId: !GetAtt SecurityHeadersPolicy.Id
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only

  # CloudWatch Alarms
  WAFBlockedRequestsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-waf-blocked-requests"
      AlarmDescription: Alert when WAF blocks requests
      MetricName: BlockedRequests
      Namespace: AWS/WAFV2
      Dimensions:
        - Name: WebACL
          Value: !Sub "${AWS::StackName}-waf-acl"
        - Name: Region
          Value: Global
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 100
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic
      OKActions:
        - !Ref AlertTopic

  High5XXErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-5xx-errors"
      AlarmDescription: Alert when 5XX error rate exceeds threshold
      MetricName: 5xxErrorRate
      Namespace: AWS/CloudFront
      Dimensions:
        - Name: DistributionId
          Value: !Ref CloudFrontDistribution
        - Name: Region
          Value: Global
      Statistic: Average
      Period: 60
      EvaluationPeriods: 5
      Threshold: 1
      ComparisonOperator: GreaterThanThreshold

  HighCacheMissRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cache-miss"
      AlarmDescription: Alert when cache miss rate is high
      MetricName: CacheMissRate
      Namespace: AWS/CloudFront
      Dimensions:
        - Name: DistributionId
          Value: !Ref CloudFrontDistribution
        - Name: Region
          Value: Global
      Statistic: Average
      Period: 300
      EvaluationPeriods: 3
      Threshold: 0.1
      ComparisonOperator: GreaterThanThreshold

  # SNS Topic per Alert
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-alerts-${Environment}"
      Subscription:
        - Endpoint: !Ref AlertEmail
          Protocol: email

Outputs:
  DistributionDomainName:
    Value: !GetAtt CloudFrontDistribution.DomainName

  WebACLArn:
    Value: !GetAtt CloudFrontWebACL.Arn
```

## Esempio 4: CloudFront Functions per URL Rewrite

CloudFront Functions per operazioni edge leggere come URL rewrite e header management.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront distribution with CloudFront Functions

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  OriginDomainName:
    Type: String
    Description: Origin domain name

Resources:
  # CloudFront Function - URL Rewrite
  UrlRewriteFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-url-rewrite"
      FunctionCode: |
        function handler(event) {
          var request = event.request;
          var uri = request.uri;

          // Remove trailing slash
          if (uri.endsWith('/') && uri.length > 1) {
            request.uri = uri.substring(0, uri.length - 1);
          }

          // Add .html extension for HTML pages
          if (!uri.includes('.') && !uri !== '/') {
            request.uri = uri + '.html';
          }

          // Rewrite /home to /index.html
          if (uri === '/home' || uri === '/home/') {
            request.uri = '/index.html';
          }

          // Rewrite /about to /about.html
          if (uri === '/about' || uri === '/about/') {
            request.uri = '/about.html';
          }

          return request;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true

  # CloudFront Function - Add Security Headers
  SecurityHeadersFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-security-headers"
      FunctionCode: |
        function handler(event) {
          var response = event.response;

          // Add security headers
          response.headers['x-content-type-options'] = { value: 'nosniff' };
          response.headers['x-frame-options'] = { value: 'DENY' };
          response.headers['x-xss-protection'] = { value: '1; mode=block' };
          response.headers['referrer-policy'] = { value: 'strict-origin-when-cross-origin' };

          return response;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true

  # CloudFront Function - A/B Testing
  ABTestingFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-ab-testing"
      FunctionCode: |
        function handler(event) {
          var request = event.request;
          var response = event.response;

          // Check for existing cookie
          var cookieName = 'ab-test-variant';
          var cookieValue = request.cookies[cookieName];

          if (!cookieValue) {
            // Randomly assign variant (50/50 split)
            var variants = ['A', 'B'];
            var variant = variants[Math.floor(Math.random() * variants.length)];

            // Set cookie
            response.headers['set-cookie'] = {
              value: cookieName + '=' + variant + '; Path=/; Max-Age=2592000'
            };
          } else {
            // Preserve existing variant
            response.headers['set-cookie'] = {
              value: cookieName + '=' + cookieValue + '; Path=/; Max-Age=2592000'
            };
          }

          return response;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront with Functions for ${Environment}"
        Enabled: true
        Origins:
          - Id: Origin
            DomainName: !Ref OriginDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: Origin
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
          FunctionAssociations:
            - FunctionARN: !GetAtt UrlRewriteFunction.FunctionARN
              EventType: viewer-request
            - FunctionARN: !GetAtt SecurityHeadersFunction.FunctionARN
              EventType: viewer-response
```

## Esempio 5: Real-Time Logs con Kinesis

Configurazione CloudFront con real-time logs verso Kinesis Data Stream.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with real-time logs to Kinesis

Parameters:
  Environment:
    Type: String
    Default: production

  OriginDomainName:
    Type: String
    Description: Origin domain name

Resources:
  # Kinesis Data Stream
  CloudFrontLogsStream:
    Type: AWS::Kinesis::Stream
    Properties:
      Name: !Sub "${AWS::StackName}-cloudfront-logs"
      ShardCount: 2
      RetentionPeriodHours: 24
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Kinesis Data Stream - Enhanced Monitoring (optional)
  CloudFrontLogsStreamConsumer:
    Type: AWS::Kinesis::StreamConsumer
    Properties:
      ConsumerName: !Sub "${AWS::StackName}-logs-consumer"
      StreamARN: !GetAtt CloudFrontLogsStream.Arn

  # IAM Role for CloudFront
  CloudFrontLoggingRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-cloudfront-logging"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: KinesisPutRecord
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - kinesis:PutRecord
                  - kinesis:PutRecords
                Resource: !GetAtt CloudFrontLogsStream.Arn

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront with real-time logs"
        Enabled: true
        IPV6Enabled: true
        RealTimeConfig:
          Endpoint: !GetAtt CloudFrontLogsStream.Arn
          RoleArn: !GetAtt CloudFrontLoggingRole.Arn
          Fields:
            - timestamp
            - c-ip
            - cs-method
            - cs-uri
            - sc-status
            - time-taken
            - cs(Referer)
            - cs(User-Agent)
            - cs(Cookie)
            - cs(Host)
        Origins:
          - Id: Origin
            DomainName: !Ref OriginDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000

Outputs:
  StreamArn:
    Description: Kinesis stream ARN
    Value: !GetAtt CloudFrontLogsStream.Arn

  StreamName:
    Description: Kinesis stream name
    Value: !Ref CloudFrontLogsStream
```

## Esempio 6: Cross-Stack References

Pattern per organizzare CloudFront in stack separati con cross-stack references.

```yaml
# Stack A - Network/Infrastructure
AWSTemplateFormatVersion: 2010-09-09
Description: Infrastructure stack - exports for CloudFront

Resources:
  # S3 Bucket
  StaticAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "static-assets-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # OAI
  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${StaticAssetsBucket}"

  # Bucket Policy
  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref StaticAssetsBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              CanonicalUser: !GetAtt CloudFrontOAI.S3CanonicalUserId
            Action: s3:GetObject
            Resource: !Sub "${StaticAssetsBucket.Arn}/*"

Outputs:
  StaticAssetsBucketName:
    Description: S3 bucket name
    Value: !Ref StaticAssetsBucket
    Export:
      Name: !Sub "${AWS::StackName}-StaticAssetsBucketName"

  StaticAssetsBucketArn:
    Description: S3 bucket ARN
    Value: !GetAtt StaticAssetsBucket.Arn
    Export:
      Name: !Sub "${AWS::StackName}-StaticAssetsBucketArn"

  StaticAssetsBucketRegionalDomainName:
    Description: Regional domain name
    Value: !GetAtt StaticAssetsBucket.RegionalDomainName
    Export:
      Name: !Sub "${AWS::StackName}-StaticAssetsBucketRegionalDomainName"

  CloudFrontOAIId:
    Description: CloudFront OAI ID
    Value: !Ref CloudFrontOAI
    Export:
      Name: !Sub "${AWS::StackName}-CloudFrontOAIId"

  CloudFrontOAIArn:
    Description: CloudFront OAI ARN
    Value: !GetAtt CloudFrontOAI.Arn
    Export:
      Name: !Sub "${AWS::StackName}-CloudFrontOAIArn"
```

```yaml
# Stack B - Application
AWSTemplateFormatVersion: 2010-09-09
Description: Application stack - imports from infrastructure stack

Parameters:
  InfrastructureStackName:
    Type: String
    Default: infrastructure-stack
    Description: Name of infrastructure stack

  DomainName:
    Type: String
    Default: cdn.example.com

  CertificateArn:
    Type: AWS::ACM::Certificate::Arn

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront distribution"
        Enabled: true
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
    Value: !GetAtt CloudFrontDistribution.DomainName
    Export:
      Name: !Sub "${AWS::StackName}-DistributionDomainName"

  DistributionId:
    Value: !Ref CloudFrontDistribution
    Export:
      Name: !Sub "${AWS::StackName}-DistributionId"
```

## Esempio 7: CloudFront per API Gateway

Configurazione CloudFront davanti a API Gateway con caching e throttling.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront distribution for API Gateway

Parameters:
  Environment:
    Type: String
    Default: production

  ApiGatewayDomainName:
    Type: String
    Description: API Gateway domain name

  CertificateArn:
    Type: AWS::ACM::Certificate::Arn

  CustomDomainName:
    Type: String
    Default: api.example.com

Resources:
  # Origin Request Policy per API
  ApiOriginRequestPolicy:
    Type: AWS::CloudFront::OriginRequestPolicy
    Properties:
      OriginRequestPolicyConfig:
        Name: !Sub "${AWS::StackName}-api-origin-request"
        CookiesConfig:
          CookieBehavior: all
        HeadersConfig:
          HeaderBehavior: whitelist
          Headers:
            - Authorization
            - Content-Type
            - Accept
            - Accept-Language
            - X-Request-ID
        QueryStringsConfig:
          QueryStringBehavior: all

  # Cache Policy per API
  ApiCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-api-cache"
        DefaultTTL: 300
        MaxTTL: 600
        MinTTL: 60
        ParametersInCacheKeyAndForwardedToOrigin:
          CookiesConfig:
            CookieBehavior: all
          HeadersConfig:
            HeaderBehavior: whitelist
            Headers:
              - Authorization
              - Content-Type
          QueryStringsConfig:
            QueryStringBehavior: all

  # CloudFront Distribution
  ApiCloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront for API Gateway - ${Environment}"
        Enabled: true
        IPV6Enabled: true
        PriceClass: PriceClass_All
        DomainNames:
          - !Ref CustomDomainName
        Origins:
          - Id: ApiGatewayOrigin
            DomainName: !Ref ApiGatewayDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
              OriginReadTimeout: 30
        DefaultCacheBehavior:
          TargetOriginId: ApiGatewayOrigin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
            - OPTIONS
            - PUT
            - POST
            - PATCH
            - DELETE
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          CachePolicyId: !GetAtt ApiCachePolicy.Id
          OriginRequestPolicyId: !GetAtt ApiOriginRequestPolicy.Id
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only

Outputs:
  ApiDistributionDomainName:
    Value: !GetAtt ApiCloudFrontDistribution.DomainName

  ApiDistributionId:
    Value: !Ref ApiCloudFrontDistribution
```

## Esempio 8: CloudFront con Custom Error Responses

Configurazione per pagine di errore personalizzate e redirect.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with custom error responses

Resources:
  # S3 Bucket per error pages
  ErrorPagesBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "error-pages-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${ErrorPagesBucket}"

  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref ErrorPagesBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              CanonicalUser: !GetAtt CloudFrontOAI.S3CanonicalUserId
            Action: s3:GetObject
            Resource: !Sub "${ErrorPagesBucket.Arn}/*"

  # Origin per error pages
  ErrorPagesOrigin:
    Type: String
    Description: Origin domain name

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Enabled: true
        CustomErrorResponses:
          # Custom 404 page
          - ErrorCode: 404
            ResponseCode: 404
            ResponsePagePath: /404.html
            ErrorCachingMinTTL: 300

          # Custom 403 page
          - ErrorCode: 403
            ResponseCode: 403
            ResponsePagePath: /403.html
            ErrorCachingMinTTL: 300

          # Custom 500 page
          - ErrorCode: 500
            ResponseCode: 500
            ResponsePagePath: /500.html
            ErrorCachingMinTTL: 60

          # Custom 502 page
          - ErrorCode: 502
            ResponseCode: 502
            ResponsePagePath: /502.html
            ErrorCachingMinTTL: 60

          # Redirect 404 to /not-found
          - ErrorCode: 404
            ResponseCode: 404
            ResponsePagePath: /not-found/
            ErrorCachingMinTTL: 0

        Origins:
          - Id: MainOrigin
            DomainName: !Ref ErrorPagesOrigin
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: MainOrigin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000
```

## Esempio 9: CloudFront con Lambda@Edge per A/B Testing

Configurazione completa per A/B testing con Lambda@Edge.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with Lambda@Edge for A/B testing

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  # Lambda@Edge Function per A/B Testing
  ABTestingLambdaEdge:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-ab-testing"
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/ab-testing.zip
      Handler: index.handler
      Runtime: nodejs20.x
      Role: !GetAtt LambdaEdgeRole.Arn
      MemorySize: 128
      Timeout: 5

  # Lambda Version
  ABTestingLambdaVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref ABTestingLambdaEdge
      Description: Lambda@Edge version for A/B testing

  # Lambda@Edge Role
  LambdaEdgeRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-edge-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
                - edgelambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  # Origin
  OriginDomainName:
    Type: String
    Description: Origin domain name

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront with A/B testing - ${Environment}"
        Enabled: true
        Origins:
          - Id: OriginA
            DomainName: !Ref OriginDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: OriginA
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          ForwardedValues:
            QueryString: true
            Cookies:
              Forward: all
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000
          LambdaFunctionAssociations:
            # Viewer request - A/B testing logic
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${ABTestingLambdaEdge}:${ABTestingLambdaVersion}"
              EventType: viewer-request
            # Origin response - Set variant cookie
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${ABTestingLambdaEdge}:${ABTestingLambdaVersion}"
              EventType: origin-response
```

## Esempio 10: CloudFront Distribution con Geo-Restrictions

Configurazione per limitare l'accesso geograficamente.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with geo restrictions

Parameters:
  Environment:
    Type: String
    Default: production

  AllowedCountries:
    Type: CommaDelimitedList
    Default: US,CA,GB,DE,FR,IT,JP,AU
    Description: List of allowed country codes

Resources:
  OriginDomainName:
    Type: String
    Description: Origin domain name

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront with geo restrictions - ${Environment}"
        Enabled: true
        IPV6Enabled: true

        # Geo restrictions
        GeoRestriction:
          RestrictionType: whitelist
          !If
            - HasAllowedCountries
            - Locations: !Ref AllowedCountries
            - !Ref AWS::NoValue

        Origins:
          - Id: Origin
            DomainName: !Ref OriginDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only

        DefaultCacheBehavior:
          TargetOriginId: Origin
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

Conditions:
  HasAllowedCountries: !Not [!Equals [!Join ["", !Ref AllowedCountries], ""]]

Outputs:
  DistributionDomainName:
    Value: !GetAtt CloudFrontDistribution.DomainName
```
