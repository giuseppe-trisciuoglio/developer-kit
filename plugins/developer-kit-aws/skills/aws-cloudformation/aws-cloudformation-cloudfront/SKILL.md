---
name: aws-cloudformation-cloudfront
description: Provides AWS CloudFormation patterns for CloudFront distributions, origins (ALB, S3, Lambda@Edge, VPC Origins), CacheBehaviors, Functions, SecurityHeaders, parameters, Outputs and cross-stack references. Use when creating CloudFront distributions with CloudFormation, configuring multiple origins, implementing caching strategies, managing custom domains with ACM, configuring WAF, and optimizing performance.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation CloudFront CDN

## Overview

Create production-ready CDN infrastructure using AWS CloudFormation templates. This skill covers CloudFront distributions, multiple origins (ALB, S3, Lambda@Edge, VPC Origins), CacheBehaviors, Functions, SecurityHeaders, and best practices for parameters, outputs, and cross-stack references.

## When to Use

Use this skill when:
- Creating new CloudFront distributions with CloudFormation
- Configuring multiple origins (ALB, S3, API Gateway, Lambda@Edge, VPC Origins)
- Implementing caching strategies with CacheBehaviors and Cache Policies
- Configuring custom domains with ACM certificates
- Implementing SecurityHeaders (CSP, HSTS, XSS protection)
- Configuring CloudFront Functions and Lambda@Edge
- Managing Geo-restrictions and Price Classes
- Integrating WAF with CloudFront
- Implementing cross-stack references with export/import

## Instructions

1. **Define Distribution Parameters**: Specify domain names, ACM certificates (must be in us-east-1), and price class
2. **Configure Origins**: Add S3 buckets (with OAI/OAC), ALBs, API Gateway, or custom origins
3. **Set Up Default Cache Behavior**: Configure viewer protocol policy, allowed/cached methods, compression
4. **Add Cache Policies**: Create custom cache policies or use managed policies for TTL and forwarding rules
5. **Add Origin Request Policies**: Control which headers, cookies, and query strings forward to origin
6. **Configure Security Headers**: Add ResponseHeadersPolicy with HSTS, X-Frame-Options, CSP, CORS
7. **Add CloudFront Functions**: Implement viewer-request/response functions for URL rewriting, redirects
8. **Configure Lambda@Edge**: Add origin-request/response functions for complex logic
9. **Integrate WAF**: Add WAFv2 WebACL with managed rules, rate limiting, SQL injection protection
10. **Set Up Monitoring**: Configure access logs to S3 and real-time logs to Kinesis

## Best Practices

### Security
- Always use HTTPS with minimum TLS 1.2
- Use WAF for protection against common attacks (OWASP)
- Limit origin access with OAI/OAC for S3
- Use Signed URLs for private content
- Implement rate limiting

### Performance
- Use appropriate PriceClass to optimize costs
- Enable compression (Gzip/Brotli)
- Use CloudFront Functions for lightweight operations (vs Lambda@Edge)
- Optimize header forwarding
- Consider Origin Shield to reduce load on origins

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with S3 origin and security headers

Resources:
  OAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${AWS::StackName}"

  Distribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        HttpVersion: http2and3
        IPV6Enabled: true
        DefaultRootObject: index.html
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt Bucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${OAI}"
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods: [GET, HEAD]
          CachedMethods: [GET, HEAD]
          Compress: true
          CachePolicyId: !Ref CachePolicy
          ResponseHeadersPolicyId: !Ref SecurityHeaders
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only

  CachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-cache"
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

  SecurityHeaders:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: !Sub "${AWS::StackName}-security"
        SecurityHeadersConfig:
          StrictTransportSecurity:
            AccessControlMaxAgeSec: 31536000
            IncludeSubdomains: true
            Override: true
          ContentTypeOptions:
            Override: true
          FrameOptions:
            FrameOption: DENY
            Override: true

Outputs:
  DistributionDomainName:
    Value: !GetAtt Distribution.DomainName
    Export:
      Name: !Sub "${AWS::StackName}-DomainName"
```

## Constraints and Warnings

- **ACM Certificates**: Must be in us-east-1 for CloudFront regardless of distribution region
- **Distribution Limits**: Max 200 distributions per account, 25 origins per distribution
- **Cache Behaviors**: Max 25 cache behaviors per distribution
- **Invalidation Limits**: Max 15 invalidation requests in progress at once
- **Deployment Time**: Distribution deployment can take up to 30 minutes
- **Lambda@Edge**: Must be deployed in us-east-1, adds per-invocation cost
- **Data Transfer**: CloudFront charges for data transfer out to internet
- **DNS Propagation**: DNS changes can take up to 24 hours to propagate globally

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
