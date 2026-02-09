# AWS CloudFormation CloudFront - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for CloudFront CDN infrastructure.

## AWS::CloudFront::Distribution

Creates a CloudFront distribution to serve content from multiple origins.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| DistributionConfig | DistributionConfig | Yes | Distribution configuration |
| Tags | List of Tag | No | Tags for the distribution |

### DistributionConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CallerReference | String | Yes | Unique identifier for the distribution |
| Comment | String | No | Comment for the distribution |
| CustomErrorResponses | List | No | Custom error responses |
| DefaultRootObject | String | No | Default object for root requests |
| Enabled | Boolean | Yes | Whether the distribution is enabled |
| HttpVersion | String | No | Supported HTTP version |
| IPV6Enabled | Boolean | No | Whether IPv6 is enabled |
| Logging | LoggingConfig | No | Logging configuration |
| OriginGroups | List | No | Origin groups for failover |
| Origins | List | Yes | List of origins |
| PriceClass | String | No | Price class (PriceClass_All, PriceClass_100, PriceClass_200) |
| Restrictions | GeoRestriction | No | Geographic restrictions |
| ViewerCertificate | ViewerCertificate | No | Certificate for HTTPS |
| WebACLId | String | No | WAF Web ACL ID |
| DefaultCacheBehavior | CacheBehavior | Yes | Default cache behavior |
| CacheBehaviors | List | No | Additional cache behaviors |
| RealTimeConfig | RealTimeConfig | No | Real-time log configuration |

### Origins Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Id | String | Yes | Unique identifier for the origin |
| DomainName | String | Yes | Domain name of the origin |
| OriginPath | String | No | Optional path in the origin |
| CustomOriginConfig | CustomOrigin | No | Configuration for custom origins |
| S3OriginConfig | S3Origin | No | Configuration for S3 origins |
| ConnectionAttempts | Integer | No | Number of connection attempts |
| ConnectionTimeout | Integer | No | Connection timeout in seconds |
| OriginShield | OriginShield | No | Origin Shield configuration |
| OriginKeepaliveTimeout | Integer | No | Keepalive timeout in seconds |
| OriginReadTimeout | Integer | No | Read timeout in seconds |

### CustomOrigin Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| HTTPPort | Integer | No | HTTP port (default: 80) |
| HTTPSPort | Integer | No | HTTPS port (default: 443) |
| OriginProtocolPolicy | String | Yes | Protocol policy (http-only, https-only, match-viewer) |
| OriginSSLProtocols | List | No | Supported SSL protocols |
| OriginReadTimeout | Integer | No | Read timeout (4-60 seconds) |
| OriginKeepaliveTimeout | Integer | No | Keepalive timeout (1-60 seconds) |

### S3Origin Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| OriginAccessIdentity | String | No | OAI ID for bucket access |

### CacheBehavior Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AllowedMethods | List | Yes | Allowed HTTP methods |
| CachePolicyId | String | No | Cache policy ID |
| Compress | Boolean | No | Whether to enable compression |
| DefaultTTL | Integer | No | Default TTL in seconds |
| FieldLevelEncryptionId | String | No | Field-level encryption ID |
| ForwardedValues | ForwardedValues | Yes | Values forwarded to origin |
| FunctionAssociations | List | No | CloudFront Functions associations |
| LambdaFunctionAssociations | List | No | Lambda@Edge associations |
| MaxTTL | Integer | No | Maximum TTL in seconds |
| MinTTL | Integer | No | Minimum TTL in seconds |
| OriginRequestPolicyId | String | No | Origin request policy ID |
| PathPattern | String | Yes | Path pattern |
| ResponseHeadersPolicyId | String | No | Response headers policy ID |
| TargetOriginId | String | Yes | Target origin ID |
| TrustedSigners | List | No | Authorized AWS accounts |
| ViewerProtocolPolicy | String | Yes | Viewer protocol policy |

### ForwardedValues Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Cookies | Cookies | Yes | Cookie configuration |
| Headers | List | No | List of headers to forward |
| QueryString | Boolean | No | Whether to forward query string |
| QueryStringCacheKeys | List | No | Query string keys to cache |

### Cookies Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Forward | String | Yes | none, whitelist, all |

### ViewerCertificate Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AcmCertificateArn | String | No | ACM certificate ARN |
| CloudFrontDefaultCertificate | Boolean | No | Use default certificate |
| IamCertificateId | String | No | IAM certificate ID |
| MinimumProtocolVersion | String | No | Minimum TLS version |
| SslSupportMethod | String | No | sni-only, vip |

### Example

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront distribution"
        Enabled: true
        IPV6Enabled: true
        PriceClass: PriceClass_All
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt StaticBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
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
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| DomainName | Distribution domain name |
| Id | Distribution ID |
| ARN | Distribution ARN |

## AWS::CloudFront::CloudFrontOriginAccessIdentity

Creates an Origin Access Identity to allow CloudFront to access private S3 buckets.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CloudFrontOriginAccessIdentityConfig | OriginAccessIdentityConfig | Yes | OAI configuration |

### OriginAccessIdentityConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Comment | String | No | Comment for the OAI |

### Example

```yaml
Resources:
  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${StaticBucket}"

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
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| S3CanonicalUserId | S3 canonical user ID |
| Arn | OAI ARN |

## AWS::CloudFront::CachePolicy

Creates a cache policy to configure how CloudFront handles caching.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CachePolicyConfig | CachePolicyConfig | Yes | Policy configuration |

### CachePolicyConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Policy name |
| DefaultTTL | Integer | Yes | Default TTL in seconds |
| MaxTTL | Integer | Yes | Maximum TTL in seconds |
| MinTTL | Integer | Yes | Minimum TTL in seconds |
| ParametersInCacheKeyAndForwardedToOrigin | ParametersInCacheKeyAndForwardedToOrigin | Yes | Parameters included in cache key |

### ParametersInCacheKeyAndForwardedToOrigin Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CookiesConfig | CookiesConfig | Yes | Cookie configuration |
| EnableAcceptEncodingBrotli | Boolean | No | Whether to enable Brotli compression |
| EnableAcceptEncodingGzip | Boolean | No | Whether to enable Gzip compression |
| HeadersConfig | HeadersConfig | Yes | Header configuration |
| QueryStringsConfig | QueryStringsConfig | Yes | Query string configuration |

### CookiesConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CookieBehavior | String | Yes | none, whitelist, all |

### HeadersConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| HeaderBehavior | String | Yes | none, whitelist, all |
| Headers | List | Cond | List of headers (required if whitelist) |

### QueryStringsConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| QueryStringBehavior | String | Yes | none, whitelist, all, allExcept |
| QueryStrings | List | Cond | List of query strings (required if whitelist/allExcept) |

### Example

```yaml
Resources:
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
          QueryStringsConfig:
            QueryStringBehavior: all
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | Policy ID |

## AWS::CloudFront::OriginRequestPolicy

Creates a policy for origin requests.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| OriginRequestPolicyConfig | OriginRequestPolicyConfig | Yes | Policy configuration |

### OriginRequestPolicyConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Policy name |
| CookiesConfig | CookiesConfig | Yes | Cookie configuration |
| HeadersConfig | HeadersConfig | Yes | Header configuration |
| QueryStringsConfig | QueryStringsConfig | Yes | Query string configuration |

### Example

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

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | Policy ID |

## AWS::CloudFront::ResponseHeadersPolicy

Creates a policy for response headers, useful for implementing security headers.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ResponseHeadersPolicyConfig | ResponseHeadersPolicyConfig | Yes | Policy configuration |

### ResponseHeadersPolicyConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Policy name |
| SecurityHeadersConfig | SecurityHeadersConfig | No | Security headers configuration |
| CorsConfig | CorsConfig | No | CORS configuration |
| CustomHeadersConfig | CustomHeadersConfig | No | Custom headers |
| ServerTimingHeadersConfig | ServerTimingHeadersConfig | No | Server-Timing header configuration |

### SecurityHeadersConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ContentTypeOptions | ContentTypeOptions | No | X-Content-Type-Options header |
| FrameOptions | FrameOptions | No | X-Frame-Options header |
| ReferrerPolicy | ReferrerPolicy | No | Referrer-Policy header |
| StrictTransportSecurity | StrictTransportSecurity | No | Strict-Transport-Security header |
| XSSProtection | XSSProtection | No | X-XSS-Protection header |

### ContentTypeOptions Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Override | Boolean | Yes | Whether to override existing headers |

### FrameOptions Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| FrameOption | String | Yes | DENY, SAMEORIGIN |
| Override | Boolean | Yes | Whether to override |

### ReferrerPolicy Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ReferrerPolicy | String | Yes | Referrer policy value |
| Override | Boolean | Yes | Whether to override |

### StrictTransportSecurity Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AccessControlMaxAgeSec | Integer | Yes | Max age in seconds |
| IncludeSubdomains | Boolean | No | Whether to include subdomains |
| Override | Boolean | Yes | Whether to override |
| Preload | Boolean | No | Whether to enable preload |

### XSSProtection Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ModeBlock | Boolean | No | Whether to block in block mode |
| Override | Boolean | Yes | Whether to override |
| Protection | Boolean | Yes | Whether to enable protection |

### CorsConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AccessControlAllowCredentials | Boolean | No | Whether to allow credentials |
| AccessControlAllowHeaders | AccessControlAllowHeaders | No | Allowed headers |
| AccessControlAllowMethods | AccessControlAllowMethods | No | Allowed methods |
| AccessControlAllowOrigins | AccessControlAllowOrigins | No | Allowed origins |
| AccessControlMaxAgeSec | Integer | No | Max age for preflight |
| AccessControlExposeHeaders | AccessControlExposeHeaders | No | Exposed headers |
| OriginOverride | Boolean | Yes | Whether to override origin header |

### Example

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
          AccessControlMaxAgeSec: 600
          OriginOverride: true
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | Policy ID |

## AWS::CloudFront::Function

Creates a CloudFront Function for lightweight edge operations.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AutoPublish | Boolean | No | Whether to auto-publish |
| FunctionCode | String | Yes | Function code |
| FunctionRuntime | String | Yes | Function runtime |
| Name | String | Yes | Function name |
| Comment | String | No | Comment |

### Supported Runtimes

| Runtime | Description |
|---------|-------------|
| cloudfront-js-1.0 | CloudFront Functions JavaScript |

### Example

```yaml
Resources:
  RewritePathFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-rewrite-path"
      FunctionCode: |
        function handler(event) {
          var request = event.request;
          var uri = request.uri;

          if (uri.endsWith('/')) {
            request.uri = uri.substring(0, uri.length - 1);
          }

          if (!uri.includes('.') && !uri.endsWith('/')) {
            request.uri = uri + '.html';
          }

          return request;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: Origin
            DomainName: !Ref OriginDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: Origin
          FunctionAssociations:
            - FunctionARN: !GetAtt RewritePathFunction.FunctionARN
              EventType: viewer-request
```

### Function Association Events

| Event | Description |
|-------|-------------|
| viewer-request | Before viewer request |
| viewer-response | After viewer response |
| origin-request | Before origin request |
| origin-response | After origin response |

### Attributes

| Attribute | Description |
|-----------|-------------|
| FunctionARN | Function ARN |

## AWS::WAFv2::WebACL

Creates a WAF Web ACL to protect CloudFront.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| DefaultAction | DefaultAction | Yes | Default action |
| Name | String | Yes | Web ACL name |
| Rules | List | No | List of rules |
| Scope | String | Yes | CLOUDFRONT or REGIONAL |
| VisibilityConfig | VisibilityConfig | Yes | Visibility configuration |

### DefaultAction Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Allow | AllowAction | No | Allow action |
| Block | BlockAction | No | Block action |

### VisibilityConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CloudWatchMetricsEnabled | Boolean | Yes | Whether to enable CloudWatch metrics |
| MetricName | String | Yes | Metric name |
| SampledRequestsEnabled | Boolean | Yes | Whether to enable sampling |

### Example

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
        - Name: AWSCommonRule
          Priority: 1
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AWSCommonRule
      VisibilityConfig:
        SampledRequestsEnabled: true
        CloudWatchMetricsEnabled: true
        MetricName: CloudFrontWAFACL
```

## AWS::GlobalAccelerator::EndpointGroup

Creates an endpoint group for VPC Origins.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| EndpointGroupRegion | String | Yes | Endpoint group region |
| EndpointConfigurations | List | No | Endpoint configurations |
| ListenerArn | String | Yes | Listener ARN |
| TrafficDialPercentage | Integer | No | Traffic percentage |

### EndpointConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| EndpointId | String | Yes | Endpoint ID |
| Weight | Integer | No | Weight for traffic routing |

### Example

```yaml
Resources:
  VPCOriginEndpoint:
    Type: AWS::GlobalAccelerator::EndpointGroup
    Properties:
      EndpointGroupRegion: !Ref VPCOriginRegion
      ListenerArn: !Ref AcceleratorListener
      EndpointConfigurations:
        - EndpointId: !Ref VPCEndpointService
          Weight: 128
```

## GeoRestriction Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Locations | List | Cond | List of country codes (whitelist/blacklist) |
| RestrictionType | String | Yes | none, blacklist, whitelist |

## LoggingConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Bucket | String | Yes | S3 bucket for logs |
| IncludeCookies | Boolean | No | Whether to include cookies |
| Prefix | String | No | Log prefix |

## RealTimeConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Endpoint | String | Yes | Kinesis stream ARN |
| Fields | List | Yes | Fields to include |
| RoleArn | String | Yes | IAM role ARN |

## Reference Intrinsic Functions

### !GetAtt

Returns the value of an attribute from a CloudFront resource.

```yaml
# Get distribution domain name
DistributionDomainName: !GetAtt CloudFrontDistribution.DomainName

# Get distribution ID
DistributionId: !Ref CloudFrontDistribution

# Get OAI canonical user ID
CanonicalUserId: !GetAtt CloudFrontOAI.S3CanonicalUserId

# Get S3 bucket regional domain name
BucketDomainName: !GetAtt StaticBucket.RegionalDomainName
```

### !Sub

Substitutes variables in a string.

```yaml
# With variable substitution
CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"

# Origin access identity path
OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
```

### !ImportValue

Imports values exported from other stacks.

```yaml
# Import from another stack
BucketDomainName: !ImportValue
  !Sub "${NetworkStackName}-StaticAssetsBucketRegionalDomainName"
```

## Limits and Quotas

### CloudFront Limits

| Resource | Default Limit |
|----------|---------------|
| Distributions per account | 200 |
| Origins per distribution | 25 |
| Cache behaviors per distribution | 25 |
| Certificates per account | 2000 |
| Maximum TTL | 31536000 seconds (1 year) |
| Request body size | 20 MB (edge), 5 MB (viewer) |
| Number of OAI | 100 per account |
| Custom domain length | 253 characters |

### CloudFront Functions Limits

| Resource | Limit |
|----------|-------|
| Execution time | 1 ms |
| Memory | 2 MB |
| Request/response size | 10 KB |
| Function code size | 10 KB |

### Lambda@Edge Limits

| Resource | Limit |
|----------|-------|
| Memory | 128 MB |
| Timeout | 30 seconds |
| Deployment package size | 1 MB |
| Response body size | 1 MB |

## Managed Cache Policies

AWS provides predefined managed policies:

| Policy ID | Name | Description |
|-----------|------|-------------|
| 658327ea-f89d-4fab-a63d-7e88639e58f6 | Managed-CachingOptimized | Optimized for caching |
| 5cc3b908-e619-4b99-88e5-2cf7a4592e4c | Managed-Elemental-MediaPackage | For MediaPackage |
| b2884449-e4de-46a7-ac21-5511b5d11b5f | Managed-Amplify | For Amplify |

## Managed Origin Request Policies

| Policy ID | Name | Description |
|-----------|------|-------------|
| 33f36d7e-f398-4d50-aaf9-1a26f4830ef3 | Managed-CORS-S3Origin | CORS for S3 |
| 10c336ab-3b4b-4e2b-a38b-5b4a20d0a1e2 | Managed-AllView | Forward all |

## Common Tags for CloudFront

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        Origins: []
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
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: team@example.com
        - Key: ManagedBy
          Value: CloudFormation
        - Key: CostCenter
          Value: "12345"
        - Key: Version
          Value: "1.0.0"
```
