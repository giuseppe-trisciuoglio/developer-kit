# CloudFront Constraints and Limitations

## Resource Limits

### Distribution Limits

```yaml
# Account-level limits (default, can be increased)
Parameters:
  ExpectedDistributions:
    Type: Number
    Default: 200
    MinValue: 1
    MaxValue: 200
    Description: Expected number of CloudFront distributions
```

**Important Limits:**
- **200 distributions** per AWS account (soft limit, can be increased)
- **25 origins** maximum per distribution
- **25 cache behaviors** maximum per distribution
- **10 custom headers** maximum per origin
- **4 alternate domain names** per distribution with IAM certificate
- **300 alternate domain names** per distribution with ACM certificate

### Origin Limits

```yaml
# Maximum origins configuration example
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          # Up to 25 origins allowed
          - Id: Origin1
            DomainName: bucket1.s3.amazonaws.com
          - Id: Origin2
            DomainName: bucket2.s3.amazonaws.com
          # ... (maximum 25 origins)
```

### Cache Behavior Limits

```yaml
# Maximum cache behaviors configuration
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CacheBehaviors:
          # Up to 25 cache behaviors allowed
          - PathPattern: "/api/v1/*"
            TargetOriginId: ApiOrigin
            # ... behavior config
          # ... (maximum 25 behaviors)
```

## DNS and Certificate Constraints

### ACM Certificate Region Requirement

```yaml
# CloudFront requires ACM certificates in us-east-1 ONLY
# Even if distribution is in other regions

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        ViewerCertificate:
          # Certificate MUST be in us-east-1
          AcmCertificateArn: arn:aws:acm:us-east-1:123456789012:certificate/abcd1234
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only

# Cross-region certificate reference
Conditions:
  UseUsEast1Certificate: !Equals [!Ref AWS::Region, us-east-1]
```

### Custom Domain Validation

```yaml
Parameters:
  DomainName:
    Type: String
    Description: Custom domain name
    AllowedPattern: "[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*"
    ConstraintDescription: Must be a valid domain name
    MinLength: 4
    MaxLength: 253

  # Validate domain before use
  DomainValidation:
    Type: String
    Default: "validated"
    AllowedValues:
      - validated
      - pending
      - failed
```

### Alternate Domain Names Limits

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        # Maximum depends on certificate type
        DomainNames:
          - cdn.example.com
          - www.example.com
          - static.example.com
          - api.example.com
          # Maximum: 4 with IAM cert, 300 with ACM cert
```

### DNS Propagation Constraints

```yaml
# DNS changes can take up to 24-48 hours
# Consider TTL settings for DNS records

Parameters:
  DNSTTL:
    Type: Number
    Default: 300
    MinValue: 60
    MaxValue: 86400
    Description: DNS record TTL in seconds

# Route53 health check for domain validation
Resources:
  DomainHealthCheck:
    Type: AWS::Route53::HealthCheck
    Properties:
      HealthCheckConfig:
        Port: 443
        Type: HTTPS
        ResourcePath: /health
        FullyQualifiedDomainName: !Ref DomainName
        RequestInterval: 30
        FailureThreshold: 3
```

## Operational Constraints

### Invalidation Limits

```yaml
# Maximum invalidation requests in progress: 15
Parameters:
  MaxInvalidations:
    Type: Number
    Default: 15
    MinValue: 1
    MaxValue: 15
    Description: Maximum concurrent invalidations

Resources:
  # Invalidation via Lambda or custom resource
  CacheInvalidation:
    Type: Custom::CacheInvalidation
    Properties:
      ServiceToken: !GetAtt InvalidationFunction.Arn
      DistributionId: !Ref CloudFrontDistribution
      Paths: /index.html /images/* /api/v1/*
```

### Deployment Time Constraints

```yaml
# Distribution deployment can take up to 30 minutes
# Plan deployments accordingly

Parameters:
  DeploymentTimeout:
    Type: Number
    Default: 30
    MinValue: 5
    MaxValue: 30
    Description: Maximum deployment time in minutes

Resources:
  CloudFrontStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TimeoutInMinutes: !Ref DeploymentTimeout
      TemplateURL: !Sub "https://${ArtifactBucket}.s3.amazonaws.com/cloudfront.yaml"
```

### Cache Invalidation Constraints

```yaml
# Batch invalidation limits
Parameters:
  InvalidationPaths:
    Type: CommaDelimitedList
    Description: Comma-separated list of paths to invalidate
    # Maximum: 1000 paths per invalidation
    # Maximum: 15 invalidations in progress

Resources:
  # Use custom resource for invalidation
  InvalidationCustomResource:
    Type: Custom::CloudFrontInvalidation
    Properties:
      ServiceToken: !Ref InvalidationToken
      DistributionId: !Ref CloudFrontDistribution
      CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
      Paths: !Join [" ", !Ref InvalidationPaths]
```

### Edge Location Caching

```yaml
# Changes at origins may not be reflected immediately
# Configure appropriate cache TTLs

Resources:
  StaticAssetsCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: static-assets-policy
        # Long TTL for static content
        DefaultTTL: 86400      # 24 hours
        MaxTTL: 31536000       # 1 year
        MinTTL: 86400          # 24 hours

  # Consider using cache invalidation for immediate updates
```

## Security Constraints

### HTTPS Enforcement

```yaml
# Modern browsers block HTTP-only content on HTTPS pages
# Always redirect to HTTPS

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          # Required for HTTPS pages
          ViewerProtocolPolicy: redirect-to-https
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only
```

### Content Security Policy Headers

```yaml
# CSP headers can break functionality if misconfigured
# Test thoroughly before implementing

Resources:
  SecurityHeadersPolicy:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: security-headers
        CustomHeadersConfig:
          Items:
            # Test CSP headers in non-production first
            - Header: Content-Security-Policy
              Value: "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.example.com"
              Override: true
```

### WAF Integration Constraints

```yaml
# WAF rules add latency and may block legitimate traffic
# Monitor WAF logs and adjust rules accordingly

Resources:
  CloudFrontWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: waf-acl
      Scope: CLOUDFRONT
      DefaultAction:
        Allow: {}
      Rules:
        # Carefully configure rate limiting
        - Name: RateLimitRule
          Priority: 1
          Statement:
            RateBasedStatementKey:
              AggregateKeyType: IP
              Limit: 2000  # Adjust based on traffic patterns
          Action:
            Block: {}
```

### Origin Access Control Constraints

```yaml
# OAI/OAC prevents direct S3 access
# Complicates testing and local development

Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # For testing, consider separate bucket policies or CloudFront signed URLs
```

## Cost Considerations

### Data Transfer Out Costs

```yaml
# CloudFront charges for data transfer out to internet
# Costs vary significantly by region

Parameters:
  EstimatedMonthlyTransferGB:
    Type: Number
    Default: 1000
    MinValue: 0
    Description: Estimated monthly data transfer in GB

# Budget alert for CloudFront costs
Resources:
  CloudFrontBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetLimit:
          Amount: 100
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          Service:
            - Amazon CloudFront
```

### Regional Price Classes

```yaml
# Use PriceClass to optimize costs
# PriceClass_200: Lowest cost (limited edge locations)
# PriceClass_100: Medium cost
# PriceClass_All: All edge locations (highest cost)

Parameters:
  PriceClass:
    Type: String
    Default: PriceClass_All
    AllowedValues:
      - PriceClass_All
      - PriceClass_100
      - PriceClass_200
    Description: CloudFront price class for cost optimization

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        PriceClass: !Ref PriceClass
```

### Lambda@Edge Cost Considerations

```yaml
# Lambda@Edge functions add significant per-invocation cost
# Consider CloudFront Functions for simpler use cases

Parameters:
  EnableLambdaEdge:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false
    Description: Enable Lambda@Edge (adds cost)

Conditions:
  UseLambdaEdge: !Equals [!Ref EnableLambdaEdge, true]

Resources:
  # Prefer CloudFront Functions when possible
  RewritePathFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: rewrite-path
      FunctionCode: |
        function handler(event) {
          var request = event.request;
          return request;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true
```

### HTTPS Request Costs

```yaml
# HTTPS requests have higher CPU utilization cost
# Consider for high-traffic distributions

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        ViewerCertificate:
          # Minimum TLS version affects cost
          MinimumProtocolVersion: TLSv1.2_2021
```

## Quota Increase Requests

```yaml
# Default quotas can be increased via AWS Support
# Use CloudFormation to track quota requests

Parameters:
  RequestedDistributionQuota:
    Type: Number
    Default: 200
    Description: Requested distribution quota increase

  RequestedOriginQuota:
    Type: Number
    Default: 25
    Description: Requested origins per distribution quota

# Document quota requests in stack outputs
Outputs:
  QuotaIncreaseRequest:
    Description: Link to request quota increase
    Value: !Sub "https://console.aws.amazon.com/support/home#/case/create?issueType=service-limit-increase&serviceCode=cloudfront"
```

## Best Practices to Avoid Constraints

### Use Multiple Distributions

```yaml
# Instead of one large distribution, use multiple
# Each distribution can have 25 origins and 25 cache behaviors

Resources:
  StaticAssetsDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        # S3 origins for static assets

  ApiDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        # ALB/API Gateway origins for API

  MediaDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        # Media-specific origins and caching
```

### Use CloudFront Functions

```yaml
# CloudFront Functions are cheaper than Lambda@Edge
# Use for simple request/response manipulation

Resources:
  SecurityHeadersFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: security-headers
      FunctionCode: |
        function handler(event) {
          var response = event.response;
          response.headers['strict-transport-security'] = { value: 'max-age=31536000' };
          return response;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true
```

### Implement Cache Invalidation Strategy

```yaml
# Plan invalidation strategy to avoid hitting limits
# Use versioned paths for cache busting

Parameters:
  AssetVersion:
    Type: String
    Default: v1
    Description: Asset version for cache busting

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          # Long TTL for versioned assets
          DefaultTTL: 31536000
          MaxTTL: 31536000
```
