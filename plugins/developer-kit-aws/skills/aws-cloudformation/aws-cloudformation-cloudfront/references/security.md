# CloudFront Security Configuration

## Security Headers

### Complete Security Headers Policy

```yaml
Resources:
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
```

### CORS Configuration

```yaml
Resources:
  CorsHeadersPolicy:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: !Sub "${AWS::StackName}-cors-headers"
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
              - POST
              - PUT
              - DELETE
          AccessControlAllowOrigins:
            Items:
              - https://example.com
              - https://www.example.com
          AccessControlExposeHeaders:
            Items:
              - Content-Length
              - Content-Type
              - X-Custom-Header
          AccessControlMaxAgeSec: 600
          OriginOverride: true
```

### Custom Security Headers

```yaml
Resources:
  CustomSecurityPolicy:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: !Sub "${AWS::StackName}-custom-security"
        CustomHeadersConfig:
          Items:
            - Header: X-Frame-Options
              Value: DENY
              Override: true
            - Header: X-Content-Type-Options
              Value: nosniff
              Override: true
            - Header: X-XSS-Protection
              Value: "1; mode=block"
              Override: true
            - Header: Permissions-Policy
              Value: "geolocation=(), microphone=(), camera=()"
              Override: true
```

## WAF Integration

### WAF Web ACL with Managed Rules

```yaml
Resources:
  CloudFrontWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: !Sub "${AWS::StackName}-waf-acl"
      Scope: CLOUDFRONT
      DefaultAction:
        Allow: {}
      Rules:
        # AWS Managed Rule - Common
        - Name: AWSCommonRule
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
            MetricName: AWSCommonRule

        # Rate-based rule
        - Name: RateLimitRule
          Priority: 2
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

        # SQL Injection protection
        - Name: SQLInjectionRule
          Priority: 3
          Statement:
            SqliMatchStatement:
              FieldToMatch:
                QueryString: {}
                UriPath: {}
              TextTransformations:
                - Priority: 1
                  Type: URL_DECODE
                - Priority: 2
                  Type: LOWERCASE
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: SQLInjectionRule

        # XSS protection
        - Name: XSSRule
          Priority: 4
          Statement:
            XssMatchStatement:
              FieldToMatch:
                QueryString: {}
                UriPath: {}
              TextTransformations:
                - Priority: 1
                  Type: URL_DECODE
                - Priority: 2
                  Type: LOWERCASE
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: XSSRule

      VisibilityConfig:
        SampledRequestsEnabled: true
        CloudWatchMetricsEnabled: true
        MetricName: CloudFrontWAFACL

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        WebACLId: !GetAtt CloudFrontWebACL.Arn
```

### WAF with Custom Rules

```yaml
Resources:
  CustomWAFWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: !Sub "${AWS::StackName}-custom-waf"
      Scope: CLOUDFRONT
      DefaultAction:
        Block: {}
      Rules:
        # Block specific user agents
        - Name: BlockBadBots
          Priority: 1
          Statement:
            ByteMatchStatement:
              FieldToMatch:
                HeaderName: User-Agent
              SearchString: "BadBot"
              PositionalConstraint: CONTAINS
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: BlockBadBots

        # Rate limit per IP
        - Name: PerIPRateLimit
          Priority: 2
          Statement:
            RateBasedStatementKey:
              ForwardedIP:
                AggregateKeyType: IP
                Limit: 500
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: PerIPRateLimit

        # Allow specific IP ranges
        - Name: AllowOfficeIPs
          Priority: 3
          Statement:
            IpSetReferenceStatement:
              Arn: !GetAtt OfficeIPSet.IPSetArn
          Action:
            Allow: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AllowOfficeIPs

  OfficeIPSet:
    Type: AWS::WAFv2::IPSet
    Properties:
      Name: office-ips
      Scope: CLOUDFRONT
      Addresses:
        - Address: 192.0.2.0/24
        - Address: 203.0.113.0/24
```

## Origin Access Control

### OAI (Legacy)

```yaml
Resources:
  # S3 Bucket
  StaticBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "static-assets-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # CloudFront OAI
  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${StaticBucket}"

  # S3 Bucket Policy - Allow CloudFront OAI
  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref StaticBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              CanonicalUser: !GetAtt CloudFrontOAI.S3CanonicalUserId
            Action: s3:GetObject
            Resource: !Sub "${StaticBucket.Arn}/*"
          - Effect: Deny
            Principal: "*"
            Action: s3:GetObject
            Resource: !Sub "${StaticBucket.Arn}/*"
            Condition:
              Bool:
                aws:SecureTransport: false

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt StaticBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
```

### OAC (Origin Access Control - Recommended)

```yaml
Resources:
  StaticBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "static-assets-oac-${AWS::AccountId}-${AWS::Region}"
      OwnershipControls:
        Rules:
          - ObjectOwnership: BucketOwnerPreferred
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # S3 Bucket Policy for OAC
  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref StaticBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: s3:GetObject
            Resource: !Sub "${StaticBucket.Arn}/*"
            Condition:
              StringEquals:
                AWS:SourceArn: !Sub "arn:aws:cloudfront::${AWS::AccountId}:distribution/${CloudFrontDistribution}"

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt StaticBucket.RegionalDomainName
            AccessControlId: !Ref OriginAccessControl
            S3OriginConfig:
              OriginAccessIdentity: ""
```

### Origin Access Control with OAC

```yaml
Resources:
  OriginAccessControl:
    Type: AWS::CloudFront::OriginAccessControl
    Properties:
      OriginAccessControlConfig:
        Name: !Sub "${AWS::StackName}-oac"
        SigningBehavior: no-origin-access-control
        OriginAccessControlSignatures:
          - # Origin access control not required for this origin
```

## Signed URLs and Signed Cookies

### Key Pair for Signed URLs

```yaml
Resources:
  # CloudFront Key Pair
  CloudFrontKeyPair:
    Type: AWS::CloudFront::PublicKey
    Properties:
      PublicKeyConfig:
        CallerReference: !Sub "${AWS::StackName}-keypair"
        EncodedKey: !Ref PublicKeyEncoded

  # Store encoded key in Parameter Store
  EncodedKeyParameter:
    Type: AWS::SSM::Parameter
    Properties:
      Name: /cloudfront/public-key-encoded
      Type: String
      Value: !Ref PublicKeyEncoded
```

### Trusted Signers

```yaml
Resources:
  TrustedSigners:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: Trusted signers for signed URLs
```

## Geo-Restrictions

### Whitelist Countries

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        GeoRestriction:
          RestrictionType: whitelist
          Locations:
            - US
            - CA
            - GB
            - DE
            - FR
            - IT
            - JP
            - AU
```

### Blacklist Countries

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        GeoRestriction:
          RestrictionType: none
          # To blacklist, use restrictionType: blacklist
          # Locations:
          #   - CN
          #   - RU
```

## HTTPS Only

### Enforce HTTPS

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          ViewerProtocolPolicy: redirect-to-https
        CacheBehaviors:
          - PathPattern: "/api/*"
            ViewerProtocolPolicy: https-only
```

### TLS Configuration

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only
```

## Field-Level Encryption

```yaml
Resources:
  # Encryption configuration
  FieldLevelEncryptionConfig:
    Type: AWS::CloudFront::FieldLevelEncryptionConfig
    Properties:
      Comment: Encrypt sensitive fields
      ContentTypeProfileConfig:
        ContentTypeProfiles:
          - ContentType: application/x-www-form-urlencoded
            Format: JSON
          - ContentType: application/json
            Format: JSON
      FieldLevelEncryptionProfileConfig:
        FieldLevelEncryptionProfile:
          Name: encrypt-fields
          EncryptionEntities:
            FieldPatterns:
              Items:
                - FieldType: QUERY_STRING
                  Value: creditcard
            FieldPatterns:
              Items:
                - FieldType: BODY
                  Value: ssn
          KMSKeyArn: !Ref EncryptionKey
```

## Security Best Practices

### HTTPS Enforcement

```yaml
ViewerCertificate:
  AcmCertificateArn: !Ref CertificateArn
  MinimumProtocolVersion: TLSv1.2_2021
  SslSupportMethod: sni-only
```

### Content Security Policy

```yaml
- Header: Content-Security-Policy
  Value: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';"
  Override: true
```

### Prevent Clickjacking

```yaml
- Header: X-Frame-Options
  Value: DENY
  Override: true
```

### Prevent MIME Sniffing

```yaml
- Header: X-Content-Type-Options
  Value: nosniff
  Override: true
```
