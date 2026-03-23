# CloudFront Advanced Features

## CloudFront Functions

### Viewer Request Function

```yaml
Resources:
  # CloudFront Function
  RewritePathFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-rewrite-path"
      FunctionCode: |
        function handler(event) {
          var request = event.request;
          var uri = request.uri;

          // Remove trailing slash
          if (uri.endsWith('/')) {
            request.uri = uri.substring(0, uri.length - 1);
          }

          // Add .html extension for HTML pages
          if (!uri.includes('.') && !uri.endsWith('/')) {
            request.uri = uri + '.html';
          }

          // Clean query string for static assets
          if (uri.match(/\.(jpg|jpeg|png|gif|css|js|ico|svg|woff2)$/)) {
            request.querystring = {};
          }

          return request;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          TargetOriginId: StaticAssetsOrigin
          FunctionAssociations:
            - FunctionARN: !GetAtt RewritePathFunction.FunctionARN
              EventType: viewer-request
```

### Viewer Response Function

```yaml
Resources:
  SecurityHeadersFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-security-headers"
      FunctionCode: |
        function handler(event) {
          var response = event.response;

          // Add security headers
          response.headers['strict-transport-security'] = { value: 'max-age=31536000; includeSubDomains; preload' };
          response.headers['x-content-type-options'] = { value: 'nosniff' };
          response.headers['x-frame-options'] = { value: 'DENY' };
          response.headers['x-xss-protection'] = { value: '1; mode=block' };
          response.headers['referrer-policy'] = { value: 'strict-origin-when-cross-origin' };

          // Add CORS headers
          response.headers['access-control-allow-origin'] = { value: 'https://example.com' };
          response.headers['access-control-allow-methods'] = { value: 'GET, HEAD, OPTIONS' };
          response.headers['access-control-allow-headers'] = { value: '*' };

          return response;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true
```

### Origin Request Function

```yaml
Resources:
  OriginRequestFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-origin-request"
      FunctionCode: |
        function handler(event) {
          var request = event.request;

          // Add custom headers to origin
          request.headers['x-origin-id'] = { value: 'cloudfront' };
          request.headers['x-request-id'] = { value: Math.random().toString(36).substring(2, 15) };

          // Clean Accept-Encoding header
          var acceptEncoding = request.headers['accept-encoding'];
          if (acceptEncoding) {
            acceptEncoding.value = acceptEncoding.value.replace(/\*,\s*/g, '').trim();
          }

          return request;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true
```

## Lambda@Edge Functions

### Lambda@Edge for Authentication

```yaml
Resources:
  # Lambda@Edge Function
  LambdaEdgeFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-auth"
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/edge-auth.zip
      Handler: index.handler
      Runtime: nodejs20.x
      Role: !GetAtt LambdaEdgeRole.Arn
      Timeout: 5

  # Lambda Version for Lambda@Edge
  LambdaEdgeVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref LambdaEdgeFunction
      Description: Lambda@Edge version

  LambdaEdgeRole:
    Type: AWS::IAM::Role
    Properties:
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

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          TargetOriginId: ApiOrigin
          LambdaFunctionAssociations:
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${LambdaEdgeFunction}:${LambdaEdgeVersion}"
              EventType: viewer-request
```

### Lambda@Edge for URL Rewriting

```yaml
Resources:
  URLRewriteFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: url-rewrite
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/url-rewrite.zip
      Handler: index.handler
      Runtime: nodejs20.x
      Role: !Ref LambdaEdgeRole
      MemorySize: 128
      Timeout: 5

  URLRewriteVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref URLRewriteFunction

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          TargetOriginId: ApiOrigin
          LambdaFunctionAssociations:
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${URLRewriteFunction}:${URLRewriteVersion}"
              EventType: origin-request
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${URLRewriteFunction}:${URLRewriteVersion}"
              EventType: viewer-response
```

## Geo-Restrictions

### Country-Based Restriction

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

### Custom Geo-Restriction with Lambda@Edge

```yaml
Resources:
  GeoRestrictionFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: geo-restriction
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/geo-restriction.zip
      Handler: index.handler
      Runtime: nodejs20.x
      Role: !Ref LambdaEdgeRole
      Environment:
        Variables:
          ALLOWED_COUNTRIES: "US,CA,GB,DE,FR"

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          TargetOriginId: ApiOrigin
          LambdaFunctionAssociations:
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${GeoRestrictionFunction}:${GeoRestrictionVersion}"
              EventType: viewer-request
```

## Price Class Optimization

### Price Class Configuration

```yaml
Parameters:
  PriceClass:
    Type: String
    Default: PriceClass_All
    AllowedValues:
      - PriceClass_All          # All edge locations
      - PriceClass_100         # North America, Europe, Asia, Middle East, Africa
      - PriceClass_200          # Lowest cost - limited locations

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        PriceClass: !Ref PriceClass
```

### Environment-Based Price Class

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        PriceClass: !If [IsProduction, PriceClass_All, PriceClass_200]
```

## Compression

### Gzip and Brotli Compression

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          Compress: true
          CachePolicyId: !GetAtt CompressionCachePolicy.Id

  CompressionCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: compression-policy
        DefaultTTL: 86400
        MaxTTL: 31536000
        MinTTL: 0
        ParametersInCacheKeyAndForwardedToOrigin:
          EnableAcceptEncodingBrotli: true
          EnableAcceptEncodingGzip: true
```

## Real-Time Logs

### Kinesis Data Stream Logs

```yaml
Resources:
  # Kinesis Data Stream
  CloudFrontLogsStream:
    Type: AWS::Kinesis::Stream
    Properties:
      Name: !Sub "${AWS::StackName}-cloudfront-logs"
      ShardCount: 1
      RetentionPeriodHours: 24

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

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
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
```

### S3 Access Logs

```yaml
Resources:
  # S3 Bucket for access logs
  AccessLogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "cloudfront-logs-${AWS::AccountId}-${AWS::Region}"
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256

  # Bucket policy for CloudFront logs
  AccessLogsBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref AccessLogsBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: s3:PutObject
            Resource: !Sub "${AccessLogsBucket.Arn}/*"
            Condition:
              StringEquals:
                aws:SourceAccount: !Ref AWS::AccountId

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Logging:
          Bucket: !Ref AccessLogsBucket
          Prefix: cloudfront-logs/
          IncludeCookies: false
```

## Custom Error Pages

### Custom Error Responses

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CustomErrorResponses:
          - ErrorCode: 403
            ErrorCachingMinTTL: 10
            ErrorCachingMaxTTL: 300
            ResponseCode: 200
            ResponsePagePath: /index.html
          - ErrorCode: 404
            ErrorCachingMinTTL: 10
            ErrorCachingMaxTTL: 300
            ResponseCode: 200
            ResponsePagePath: /index.html
          - ErrorCode: 500
            ErrorCachingMinTTL: 0
            ErrorCachingMaxTTL: 30
            ResponseCode: 200
            ResponsePagePath: /error.html
```

## Function Associations

### Multiple Function Associations

```yaml
Resources:
  ViewerRequestFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: viewer-request-func
      FunctionCode: |
        function handler(event) {
          // Function code
        }
      Runtime: cloudfront-js-1.0

  OriginResponseFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: origin-response-func
      FunctionCode: |
        function handler(event) {
          // Function code
        }
      Runtime: cloudfront-js-1.0

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          TargetOriginId: Origin
          FunctionAssociations:
            - FunctionARN: !GetAtt ViewerRequestFunction.FunctionARN
              EventType: viewer-request
            - FunctionARN: !GetAtt OriginResponseFunction.FunctionARN
              EventType: origin-response
```

## Lambda@Edge with Replication

### Lambda Edge with Replication

```yaml
Resources:
  # Lambda@Edge function (us-east-1 required)
  LambdaEdgeFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-edge-function"
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/edge-function.zip
      Handler: index.handler
      Runtime: nodejs20.x
      Role: !GetAtt LambdaEdgeRole.Arn

  # Lambda@Edge version
  LambdaEdgeVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref LambdaEdgeFunction

  # CloudFront distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          TargetOriginId: ApiOrigin
          LambdaFunctionAssociations:
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${LambdaEdgeFunction}:${LambdaEdgeVersion}"
              EventType: origin-request
```

## Origin Shield

### Origin Shield Configuration

```yaml
Resources:
  OriginShield:
    Type: AWS::CloudFront::OriginAccessControl
    Properties:
      OriginAccessControlConfig:
        Name: !Sub "${AWS::StackName}-origin-shield"
        OriginAccessControlOrigin:
          OriginAccessControlOriginRegions:
            - US_EAST_1
            - US_WEST_2
            - EU_WEST_1
          SigningProtocols:
            - https

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: OriginShieldOrigin
            DomainName: !Ref OriginShieldDomain
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
```
