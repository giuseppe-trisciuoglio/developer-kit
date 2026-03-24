# CloudFront Origins Configuration

## S3 Origins

### S3 Origin with OAI (Legacy)

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront distribution with S3 origin

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

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "Static assets CDN"
        Enabled: true
        IPV6Enabled: true
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
```

### S3 Origin with Origin Access Control (OAC)

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
            S3OriginConfig:
              OriginAccessIdentity: ""
            # For OAC, use OriginAccessControl instead of S3OriginConfig
            # but CloudFormation supports both
```

## ALB Origins

### Application Load Balancer Origin

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with ALB origin

Resources:
  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb"
      Scheme: internet-facing
      SecurityGroups:
        - !Ref ALBSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      Type: application

  # ALB Security Group
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: ALB security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref CloudFrontSecurityGroup
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref CloudFrontSecurityGroup

  # CloudFront Security Group (for ALB ingress)
  CloudFrontSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: CloudFront security group for ALB
      VpcId: !Ref VPCId
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          DestinationSecurityGroupId: !Ref ALBSecurityGroup
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          DestinationSecurityGroupId: !Ref ALBSecurityGroup

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront with ALB origin"
        Enabled: true
        Origins:
          - Id: ALBOrigin
            DomainName: !GetAtt ApplicationLoadBalancer.DNSName
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
              OriginSSLProtocols:
                - TLSv1.2
        DefaultCacheBehavior:
          TargetOriginId: ALBOrigin
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
            Headers:
              - Origin
              - Access-Control-Request-Method
              - Access-Control-Request-Headers
            Cookies:
              Forward: all
            QueryStringSettings:
              - Name: "*"
          MinTTL: 0
          DefaultTTL: 0
          MaxTTL: 0
```

## API Gateway Origins

### REST API Origin

```yaml
Resources:
  # REST API
  RestApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "${AWS::StackName}-api"
      Description: API Gateway for CloudFront origin

  # API Resource
  ApiResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref RestApi
      ParentId: !GetAtt RestApi.RootResourceId
      PathPart: v1

  # API Method
  ApiMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref RestApi
      ResourceId: !Ref ApiResource
      HttpMethod: GET
      AuthorizationType: NONE
      Integration:
        Type: HTTP_PROXY
        IntegrationHttpMethod: GET
        Uri: !Sub "http://${LoadBalancerDNSName}/api"

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: ApiOrigin
            DomainName: !Sub "${RestApi}.execute-api.${AWS::Region}.amazonaws.com"
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
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
          ForwardedValues:
            QueryString: true
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 0
          MaxTTL: 0
```

### HTTP API Origin

```yaml
Resources:
  # HTTP API
  HttpApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: !Sub "${AWS::StackName}-http-api"
      ProtocolType: HTTPS
      Target: !Ref LoadBalancerDNSName

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: HttpApiOrigin
            DomainName: !GetAtt HttpApi.ApiEndpoint
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: HttpApiOrigin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
            - OPTIONS
            - PUT
            - POST
            - PATCH
            - DELETE
          ForwardedValues:
            QueryString: true
            Headers:
              - Authorization
              - Content-Type
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 0
          MaxTTL: 0
```

## Lambda@Edge Origins

### Lambda Function Origin

```yaml
Resources:
  # Lambda@Edge Function
  LambdaEdgeFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-lambda-edge"
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/edge-function.zip
      Handler: index.handler
      Runtime: nodejs20.x
      Role: !GetAtt LambdaEdgeRole.Arn

  # Lambda Version for Lambda@Edge
  LambdaEdgeVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref LambdaEdgeFunction
      Description: Lambda@Edge version

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: LambdaOrigin
            DomainName: !Sub "${LambdaFunction}.execute-api.${AWS::Region}.amazonaws.com"
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: LambdaOrigin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          LambdaFunctionAssociations:
            - FunctionARN: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${LambdaEdgeFunction}:${LambdaEdgeVersion}"
              EventType: origin-request
          Compress: true
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
```

## VPC Origins

### VPC Origin with Global Accelerator

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudFront with VPC Origin

Resources:
  # VPC Origin Endpoint
  VPCOriginEndpoint:
    Type: AWS::GlobalAccelerator::EndpointGroup
    Properties:
      EndpointGroupRegion: !Ref VPCOriginRegion
      ListenerArn: !Ref AcceleratorListener
      EndpointConfigurations:
        - EndpointId: !Ref VPCEndpointService
          Weight: 128

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront with VPC Origin"
        Enabled: true
        IPV6Enabled: true
        Origins:
          - Id: VPCOrigin
            DomainName: !Ref VPCOriginDomain
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
              OriginKeepaliveTimeout: 60
              OriginReadTimeout: 30
        DefaultCacheBehavior:
          TargetOriginId: VPCOrigin
          ViewerProtocolPolicy: https-only
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
            Headers:
              - "*"
            Cookies:
              Forward: all
          MinTTL: 0
          DefaultTTL: 3600
          MaxTTL: 86400
```

## Custom Origins

### Custom HTTP Origin

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: CustomOrigin
            DomainName: api.example.com
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
              OriginSSLProtocols:
                - TLSv1.2
              OriginReadTimeout: 30
              OriginKeepaliveTimeout: 5
```

### Custom Origin with Health Checks

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: CustomOrigin
            DomainName: api.example.com
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
            OriginCustomHeaders:
              - HeaderName: X-Custom-Header
                HeaderValue: custom-value
              - HeaderName: X-Forwarded-For
                HeaderValue: !Ref AWS::StackName
```

## Multiple Origins Configuration

### Multi-Origin with Path Patterns

```yaml
Resources:
  # S3 Bucket for static assets
  StaticAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "static-assets-${AWS::AccountId}-${AWS::Region}"

  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${StaticAssetsBucket}"

  # Application Load Balancer for API
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-api-alb"
      Scheme: internet-facing
      SecurityGroups:
        - !Ref ALBSecurityGroup
      Subnets: !Ref PublicSubnets
      Type: application

  # Lambda function origin
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: image-processor
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/processor.zip
      Handler: index.handler
      Runtime: nodejs20.x

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "Multi-origin CloudFront distribution"
        Enabled: true
        IPV6Enabled: true
        DefaultRootObject: index.html
        Origins:
          # Static assets origin
          - Id: StaticAssetsOrigin
            DomainName: !GetAtt StaticAssetsBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
          # API origin
          - Id: ApiOrigin
            DomainName: !GetAtt ApplicationLoadBalancer.DNSName
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
          # Lambda origin
          - Id: LambdaOrigin
            DomainName: !Sub "${LambdaFunction}.execute-api.${AWS::Region}.amazonaws.com"
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          # Default: static assets
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
            Compress: true
            ForwardedValues:
              QueryString: true
              Headers:
                - Accept
                - Accept-Language
                - Authorization
              Cookies:
                Forward: all
            MinTTL: 0
            DefaultTTL: 0
            MaxTTL: 0
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
```
