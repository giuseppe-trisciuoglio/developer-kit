# Application Load Balancer Configuration

## Basic ALB

```yaml
Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${AWS::StackName}-alb
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      Type: application

  ApplicationTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${AWS::StackName}-tg
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      TargetType: instance
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-tg

  ApplicationListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref ApplicationTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP
```

## ALB with HTTPS

```yaml
Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${AWS::StackName}-alb
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2

  ApplicationTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${AWS::StackName}-tg
      Port: 443
      Protocol: HTTPS
      VpcId: !Ref VpcId
      TargetType: instance
      HealthCheckPath: /health
      HealthCheckProtocol: HTTPS

  ApplicationListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref ApplicationTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 443
      Protocol: HTTPS
      Certificates:
        - CertificateArn: !Ref CertificateArn

  ApplicationListenerHttpRedirect:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: redirect
          RedirectConfig:
            Host: "#{host}"
            Path: "/#{path}"
            Port: "443"
            Protocol: "HTTPS"
            Query: "#{query}"
            StatusCode: HTTP_301
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP
```

## ALB with Multiple Target Groups

```yaml
Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${AWS::StackName}-alb
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2

  ApiTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${AWS::StackName}-api-tg
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /actuator/health

  WebTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${AWS::StackName}-web-tg
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /health

  ApiListenerRule:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      Actions:
        - Type: forward
          TargetGroupArn: !Ref ApiTargetGroup
      Conditions:
        - Field: path-pattern
          Values:
            - /api/*
            - /v1/*
      ListenerArn: !Ref ApplicationListener
      Priority: 10

  WebListenerRule:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      Actions:
        - Type: forward
          TargetGroupArn: !Ref WebTargetGroup
      Conditions:
        - Field: path-pattern
          Values:
            - /*
      ListenerArn: !Ref ApplicationListener
      Priority: 100
```

## ALB with Cross-Zone Load Balancing

```yaml
Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${AWS::StackName}-alb
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      LoadBalancerAttributes:
        - Key: load_balancing.cross_zone.enabled
          Value: true
```

## Target Group Configuration

### Health Check Settings

```yaml
ApplicationTargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: !Sub ${AWS::StackName}-tg
    Port: 80
    Protocol: HTTP
    VpcId: !Ref VpcId
    TargetType: instance
    HealthCheckEnabled: true
    HealthCheckPath: /health
    HealthCheckProtocol: HTTP
    HealthCheckIntervalSeconds: 30
    HealthCheckTimeoutSeconds: 5
    HealthyThresholdCount: 2
    UnhealthyThresholdCount: 3
    Matcher:
      HttpCode: '200'
```

### Target Group with IP Targets

```yaml
ApplicationTargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: !Sub ${AWS::StackName}-tg
    Port: 80
    Protocol: HTTP
    VpcId: !Ref VpcId
    TargetType: ip
    HealthCheckPath: /health
```

### Target Group with Lambda Targets

```yaml
LambdaTargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: !Sub ${AWS::StackName}-lambda-tg
    TargetType: lambda
    Targets:
      - Id: !GetAtt LambdaFunction.Arn
```

## Listener Configuration

### Listener with Forward Action

```yaml
ApplicationListener:
  Type: AWS::ElasticLoadBalancingV2::Listener
  Properties:
    DefaultActions:
      - Type: forward
        TargetGroupArn: !Ref ApplicationTargetGroup
        ForwardConfig:
          TargetGroups:
            - TargetGroupArn: !Ref ApplicationTargetGroup
              Weight: 1
            - TargetGroupArn: !Ref BlueTargetGroup
              Weight: 0
    LoadBalancerArn: !Ref ApplicationLoadBalancer
    Port: 80
    Protocol: HTTP
```

### Listener with Redirect Action

```yaml
HttpListener:
  Type: AWS::ElasticLoadBalancingV2::Listener
  Properties:
    DefaultActions:
      - Type: redirect
        RedirectConfig:
          Protocol: HTTPS
          Port: '443'
          StatusCode: HTTP_301
    LoadBalancerArn: !Ref ApplicationLoadBalancer
    Port: 80
    Protocol: HTTP
```

### Listener with Fixed Response

```yaml
MaintenanceListener:
  Type: AWS::ElasticLoadBalancingV2::Listener
  Properties:
    DefaultActions:
      - Type: fixed-response
        FixedResponseConfig:
          ContentType: text/plain
          MessageBody: 'System under maintenance'
          StatusCode: 503
    LoadBalancerArn: !Ref ApplicationLoadBalancer
    Port: 80
    Protocol: HTTP
```

## Listener Rules

### Path-Based Routing

```yaml
ApiListenerRule:
  Type: AWS::ElasticLoadBalancingV2::ListenerRule
  Properties:
    Actions:
      - Type: forward
        TargetGroupArn: !Ref ApiTargetGroup
    Conditions:
      - Field: path-pattern
        Values:
          - /api/*
          - /v1/*
    ListenerArn: !Ref ApplicationListener
    Priority: 10
```

### Host-Based Routing

```yaml
ApiListenerRule:
  Type: AWS::ElasticLoadBalancingV2::ListenerRule
  Properties:
    Actions:
      - Type: forward
        TargetGroupArn: !Ref ApiTargetGroup
    Conditions:
      - Field: host-header
        Values:
          - api.example.com
    ListenerArn: !Ref ApplicationListener
    Priority: 10
```

### Multiple Conditions

```yaml
ApiListenerRule:
  Type: AWS::ElasticLoadBalancingV2::ListenerRule
  Properties:
    Actions:
      - Type: forward
        TargetGroupArn: !Ref ApiTargetGroup
    Conditions:
      - Field: path-pattern
        Values:
          - /api/*
      - Field: http-header
        HttpHeaderConfig:
          HttpHeaderName: X-API-Version
          Values:
            - v1
            - v2
    ListenerArn: !Ref ApplicationListener
    Priority: 10
```

## ALB Attributes

### Common Attributes

```yaml
ApplicationLoadBalancer:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Name: !Sub ${AWS::StackName}-alb
    LoadBalancerAttributes:
      - Key: idle_timeout.timeout_seconds
        Value: '60'
      - Key: deletion_protection.enabled
        Value: 'true'
      - Key: routing.http2.enabled
        Value: 'true'
      - Key: load_balancing.cross_zone.enabled
        Value: 'true'
```

### Access Logs

```yaml
ApplicationLoadBalancer:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Name: !Sub ${AWS::StackName}-alb
    LoadBalancerAttributes:
      - Key: access_logs.s3.enabled
        Value: 'true'
      - Key: access_logs.s3.bucket
        Value: !Ref AccessLogsBucket
      - Key: access_logs.s3.prefix
        Value: !Sub ${AWS::StackName}/
```

## Connection Settings

### Idle Timeout

```yaml
LoadBalancerAttributes:
  - Key: idle_timeout.timeout_seconds
    Value: '300'
```

### Deregistration Delay

```yaml
ApplicationTargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: !Sub ${AWS::StackName}-tg
    Port: 80
    Protocol: HTTP
    VpcId: !Ref VpcId
    HealthCheckPath: /health
    TargetGroupAttributes:
      - Key: deregistration_delay.timeout_seconds
        Value: '300'
      - Key: stickiness.enabled
        Value: 'true'
      - Key: stickiness.type
        Value: lb_cookie
      - Key: stickiness.duration_seconds
        Value: '3600'
```
