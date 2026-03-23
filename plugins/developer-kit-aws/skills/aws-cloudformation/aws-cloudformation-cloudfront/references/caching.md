# CloudFront Caching Configuration

## Cache Policies

### Managed Cache Policy

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CacheBehaviors:
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
            CachePolicyId: !Ref ManagedCachingOptimizedPolicyId
            FunctionAssociations:
              - FunctionARN: !GetAtt CloudFrontFunction.FunctionARN
                EventType: viewer-request

          - PathPattern: "/api/*"
            TargetOriginId: ApiOrigin
            ViewerProtocolPolicy: redirect-to-https
            AllowedMethods:
              - GET
              - HEAD
              - OPTIONS
            CachedMethods:
              - GET
              - HEAD
            Compress: true
            CachePolicyId: !Ref ManagedSecurityHeadersPolicyId
```

### Custom Cache Policy

```yaml
Resources:
  # Custom Cache Policy for Static Assets
  StaticAssetsCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-static-assets-policy"
        DefaultTTL: 86400
        MaxTTL: 31536000
        MinTTL: 0
        ParametersInCacheKeyAndForwardedToOrigin:
          CookiesConfig:
            CookieBehavior: none
          HeadersConfig:
            HeaderBehavior: none
          QueryStringsConfig:
            QueryStringBehavior: none
          EnableAcceptEncodingBrotli: true
          EnableAcceptEncodingGzip: true

  # Custom Cache Policy for API
  ApiCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-api-cache-policy"
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
              - Accept
          QueryStringsConfig:
            QueryStringBehavior: all
          EnableAcceptEncodingBrotli: true
          EnableAcceptEncodingGzip: true

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: StaticAssetsOrigin
            DomainName: !GetAtt StaticAssetsBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
        CacheBehaviors:
          - PathPattern: "/static/*"
            TargetOriginId: StaticAssetsOrigin
            CachePolicyId: !GetAtt StaticAssetsCachePolicy.Id
```

### Cache Policy for Images

```yaml
Resources:
  ImageCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-images-policy"
        DefaultTTL: 86400
        MaxTTL: 31536000
        MinTTL: 86400
        ParametersInCacheKeyAndForwardedToOrigin:
          CookiesConfig:
            CookieBehavior: none
          HeadersConfig:
            HeaderBehavior: whitelist
            Headers:
              - Accept
              - Accept-Encoding
          QueryStringsConfig:
            QueryStringBehavior: none
          EnableAcceptEncodingBrotli: true
          EnableAcceptEncodingGzip: true
```

### Cache Policy for Videos

```yaml
Resources:
  VideoCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-videos-policy"
        DefaultTTL: 31536000
        MaxTTL: 31536000
        MinTTL: 86400
        ParametersInCacheKeyAndForwardedToOrigin:
          CookiesConfig:
            CookieBehavior: none
          HeadersConfig:
            HeaderBehavior: none
          QueryStringsConfig:
            QueryStringBehavior: none
          EnableAcceptEncodingBrotli: false
          EnableAcceptEncodingGzip: false
```

## Origin Request Policies

### Origin Request Policy for Static Assets

```yaml
Resources:
  StaticAssetsOriginRequestPolicy:
    Type: AWS::CloudFront::OriginRequestPolicy
    Properties:
      OriginRequestPolicyConfig:
        Name: !Sub "${AWS::StackName}-static-assets-origin-request"
        CookiesConfig:
          CookieBehavior: none
        HeadersConfig:
          HeaderBehavior: none
        QueryStringsConfig:
          QueryStringBehavior: none
```

### Origin Request Policy for API

```yaml
Resources:
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
            - X-Request-ID
        QueryStringsConfig:
          QueryStringBehavior: all
```

### Origin Request Policy with CORS Headers

```yaml
Resources:
  CorsOriginRequestPolicy:
    Type: AWS::CloudFront::OriginRequestPolicy
    Properties:
      OriginRequestPolicyConfig:
        Name: !Sub "${AWS::StackName}-cors-origin-request"
        CookiesConfig:
          CookieBehavior: none
        HeadersConfig:
          HeaderBehavior: whitelist
          Headers:
            - Origin
            - Access-Control-Request-Method
            - Access-Control-Request-Headers
        QueryStringsConfig:
          QueryStringBehavior: none
```

## Cache Behaviors

### Multiple Cache Behaviors

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: StaticAssetsOrigin
            DomainName: !GetAtt StaticAssetsBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
          - Id: ApiOrigin
            DomainName: !GetAtt ApplicationLoadBalancer.DNSName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
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
          CachePolicyId: !GetAtt StaticAssetsCachePolicy.Id
          OriginRequestPolicyId: !GetAtt StaticAssetsOriginRequestPolicy.Id
        CacheBehaviors:
          # API cache behavior
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
              - OPTIONS
            Compress: true
            CachePolicyId: !GetAtt ApiCachePolicy.Id
            OriginRequestPolicyId: !GetAtt ApiOriginRequestPolicy.Id
            ForwardedValues:
              QueryString: true
              Headers:
                - Authorization
                - Content-Type
              Cookies:
                Forward: all
            MinTTL: 0
            DefaultTTL: 0
            MaxTTL: 0
          # Images cache behavior
          - PathPattern: "/images/*"
            TargetOriginId: StaticAssetsOrigin
            ViewerProtocolPolicy: redirect-to-https
            AllowedMethods:
              - GET
              - HEAD
            CachedMethods:
              - GET
              - HEAD
            Compress: true
            CachePolicyId: !GetAtt ImageCachePolicy.Id
            MinTTL: 86400
            DefaultTTL: 86400
            MaxTTL: 31536000
```

### Path Pattern Examples

```yaml
CacheBehaviors:
  # API endpoints
  - PathPattern: "/api/v1/*"
    TargetOriginId: ApiOriginV1
    CachePolicyId: !GetAtt NoCachePolicy.Id

  # Static assets with version
  - PathPattern: "/static/v1/*"
    TargetOriginId: StaticAssetsV1Origin
    CachePolicyId: !GetAtt LongCachePolicy.Id

  # Media files
  - PathPattern: "/media/*"
    TargetOriginId: MediaOrigin
    CachePolicyId: !GetAtt MediaCachePolicy.Id

  # Dynamic content
  - PathPattern: "/dynamic/*"
    TargetOriginId: ApiOrigin
    CachePolicyId: !GetAtt NoCachePolicy.Id
```

## Response Headers Policies

### Security Headers Policy

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

### CORS Headers Policy

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
          AccessControlAllowOrigins:
            Items:
              - !Ref AllowedOrigin
          AccessControlMaxAgeSec: 600
          OriginOverride: true
```

### Custom Headers Policy

```yaml
Resources:
  CustomHeadersPolicy:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: !Sub "${AWS::StackName}-custom-headers"
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
```

## Forwarded Values Configuration

### Query String Forwarding

```yaml
DefaultCacheBehavior:
  TargetOriginId: Origin
  ForwardedValues:
    QueryString: false
    Cookies:
      Forward: none

# Forward all query strings
CacheBehaviors:
  - PathPattern: "/api/*"
    TargetOriginId: ApiOrigin
    ForwardedValues:
      QueryString: true
      QueryStringCacheKeys:
        - version
        - locale
      Cookies:
        Forward: all
```

### Header Forwarding

```yaml
CacheBehaviors:
  - PathPattern: "/api/*"
    TargetOriginId: ApiOrigin
    ForwardedValues:
      QueryString: true
      Headers:
        - Authorization
        - Content-Type
        - Accept
        - Accept-Language
      Cookies:
        Forward: all
```

### Cookie Forwarding

```yaml
# No cookies
DefaultCacheBehavior:
  TargetOriginId: Origin
  ForwardedValues:
    QueryString: false
    Cookies:
      Forward: none

# All cookies
CacheBehaviors:
  - PathPattern: "/api/*"
    TargetOriginId: ApiOrigin
    ForwardedValues:
      QueryString: true
      Cookies:
        Forward: all

# Whitelist cookies
CacheBehaviors:
  - PathPattern: "/api/*"
    TargetOriginId: ApiOrigin
    ForwardedValues:
      QueryString: true
      Cookies:
        Forward: whitelist
        WhitelistedNames:
          - session_id
          - user_token
```

## Cache Key Configuration

### Cache Key with Query Strings

```yaml
CachePolicy:
  Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: query-string-cache-policy
        DefaultTTL: 3600
        MaxTTL: 86400
        MinTTL: 60
        ParametersInCacheKeyAndForwardedToOrigin:
          QueryStringsConfig:
            QueryStringBehavior: whitelist
            QueryStringCacheKeys:
              - version
              - locale
          CookiesConfig:
            CookieBehavior: none
          HeadersConfig:
            HeaderBehavior: none
```

### Cache Key with Headers

```yaml
CachePolicy:
  Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: header-cache-policy
        DefaultTTL: 3600
        MaxTTL: 86400
        MinTTL: 60
        ParametersInCacheKeyAndForwardedToOrigin:
          HeadersConfig:
            HeaderBehavior: whitelist
            Headers:
              - Authorization
              - Accept-Encoding
          CookiesConfig:
            CookieBehavior: none
          QueryStringsConfig:
            QueryStringBehavior: none
```

## TTL Configuration Best Practices

### Static Assets (Long TTL)

```yaml
StaticAssetsCachePolicy:
  Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        DefaultTTL: 86400      # 24 hours
        MaxTTL: 31536000     # 1 year
        MinTTL: 86400        # 24 hours
```

### API Responses (Short TTL)

```yaml
ApiCachePolicy:
  Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        DefaultTTL: 300        # 5 minutes
        MaxTTL: 600          # 10 minutes
        MinTTL: 60           # 1 minute
```

### Dynamic Content (No Caching)

```yaml
NoCachePolicy:
  Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        DefaultTTL: 0
        MaxTTL: 0
        MinTTL: 0
```
