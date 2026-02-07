# AWS CloudFormation ECS - Examples

This file contains comprehensive examples for ECS patterns with CloudFormation.

## Example 1: Complete ECS Cluster with Fargate

Complete production-ready ECS cluster with Fargate launch type, ALB, and auto scaling.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production ECS cluster with Fargate, ALB, and auto scaling

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  PublicSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Public subnets for ALB

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Private subnets for ECS tasks

  ContainerName:
    Type: String
    Default: web-app

  ContainerImage:
    Type: String
    Default: nginx:latest

  ContainerPort:
    Type: Number
    Default: 80

  DesiredCount:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 20

  MaxCount:
    Type: Number
    Default: 10
    MinValue: 1
    MaxValue: 100

Mappings:
  EnvironmentConfig:
    dev:
      Cpu: "256"
      Memory: "512"
      CpuTarget: 60
      MemoryTarget: 70
      LogLevel: DEBUG
    staging:
      Cpu: "512"
      Memory: "1024"
      CpuTarget: 70
      MemoryTarget: 80
      LogLevel: INFO
    production:
      Cpu: "1024"
      Memory: "2048"
      CpuTarget: 70
      MemoryTarget: 80
      LogLevel: INFO

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  IsStaging: !Equals [!Ref Environment, staging]

Resources:
  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-${Environment}"
      ClusterSettings:
        - Name: containerInsights
          Value: enabled

  # Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}-${Environment}"
      RetentionInDays: !If [IsProduction, 90, 30]
      KmsKeyId: !Ref LogKmsKey

  # Task Execution Role
  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-task-execution-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-ecr-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - ecr:GetDownloadUrlForLayer
                  - ecr:BatchGetImage
                  - ecr:BatchCheckLayerAvailability
                Resource: !Ref EcrRepositoryArn
              - Effect: Allow
                Action:
                  - ecr:GetAuthorizationToken
                Resource: "*"
        - PolicyName: !Sub "${AWS::StackName}-secrets-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref DatabaseSecretArn
        - PolicyName: !Sub "${AWS::StackName}-logs-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: !GetAtt LogGroup.Arn

  # Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-task-${Environment}"
      Cpu: !FindInMap [EnvironmentConfig, !Ref Environment, Cpu]
      Memory: !FindInMap [EnvironmentConfig, !Ref Environment, Memory]
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      TaskRoleArn: !Ref TaskRole
      ContainerDefinitions:
        - Name: !Ref ContainerName
          Image: !Ref ContainerImage
          Cpu: !FindInMap [EnvironmentConfig, !Ref Environment, Cpu]
          Memory: !FindInMap [EnvironmentConfig, !Ref Environment, Memory]
          PortMappings:
            - ContainerPort: !Ref ContainerPort
              Protocol: tcp
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
            - Name: LOG_LEVEL
              Value: !FindInMap [EnvironmentConfig, !Ref Environment, LogLevel]
            - Name: SERVICE_NAME
              Value: !Ref ContainerName
          Secrets:
            - Name: DATABASE_URL
              ValueFrom: !Sub "${DatabaseSecretArn}:connection::"
            - Name: API_KEY
              ValueFrom: !Sub "${DatabaseSecretArn}:api_key::"
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: !Ref ContainerName
          HealthCheck:
            Command:
              - CMD-SHELL
              - curl -f http://localhost:8080/health || exit 1
            Interval: 30
            Timeout: 5
            Retries: 3
            StartPeriod: 60
          LinuxParameters:
            InitProcessEnabled: true
          DockerSecurityOptions:
            - !If [IsProduction, "no-new-privileges", !Ref AWS::NoValue]
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Task Role for application
  TaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-task-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-app-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                Resource: !Sub "${DataBucket.Arn}/*"
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                Resource: !GetAtt DataTable.Arn

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb-${Environment}"
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets: !Ref PublicSubnetIds
      Type: application
      LoadBalancerAttributes:
        - Key: idle_timeout.timeout_seconds
          Value: "60"
        - Key: routing.http2.enabled
          Value: "true"
        - Key: routing.http.drop_invalid_header_fields.enabled
          Value: "true"

  AlbSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-alb-sg-${Environment}"
      GroupDescription: Security group for ALB
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Target Groups
  TargetGroupBlue:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-tg-blue-${Environment}"
      Port: !Ref ContainerPort
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /health
      HealthCheckProtocol: HTTP
      HealthCheckPort: traffic-port
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
      Matcher:
        HttpCode: 200-499
      TargetType: ip
      IpAddressType: ipv4
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # ECS Service
  EcsService:
    Type: AWS::ECS::Service
    DependsOn: AlbListener
    Properties:
      ServiceName: !Sub "${AWS::StackName}-service-${Environment}"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: !Ref DesiredCount
      LaunchType: FARGATE
      DeploymentConfiguration:
        MaximumPercent: 200
        MinimumHealthyPercent: 50
        DeploymentCircuitBreaker:
          Enable: true
          Rollback: true
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: DISABLED
          SecurityGroups:
            - !Ref EcsSecurityGroup
          Subnets: !Ref PrivateSubnetIds
      LoadBalancers:
        - ContainerName: !Ref ContainerName
          ContainerPort: !Ref ContainerPort
          TargetGroupArn: !Ref TargetGroupBlue
      PropagateTags: SERVICE
      EnableExecuteCommand: true
      HealthCheckGracePeriodSeconds: 60
      Tags:
        - Key: Environment
          Value: !Ref Environment

  EcsSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-ecs-sg-${Environment}"
      GroupDescription: Security group for ECS service
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: !Ref ContainerPort
          ToPort: !Ref ContainerPort
          SourceSecurityGroupId: !Ref AlbSecurityGroup
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # ALB Listener
  AlbListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          ForwardConfig:
            TargetGroupStickinessConfig:
              Enabled: true
              DurationSeconds: 3600
            TargetGroups:
              - TargetGroupArn: !Ref TargetGroupBlue
                Weight: 100
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  # Auto Scaling
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: !Ref MaxCount
      MinCapacity: !Ref DesiredCount
      ResourceId: !Sub "service/${ECSCluster}/${EcsService}"
      RoleARN: !GetAtt AutoScalingRole.Arn
      ScalableDimension: ecs:service:DesiredCount
      ServiceNamespace: ecs

  CpuScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-cpu-scaling-${Environment}"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization
        TargetValue: !FindInMap [EnvironmentConfig, !Ref Environment, CpuTarget]
        ScaleInCooldown: 300
        ScaleOutCooldown: 60

  MemoryScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-memory-scaling-${Environment}"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageMemoryUtilization
        TargetValue: !FindInMap [EnvironmentConfig, !Ref Environment, MemoryTarget]
        ScaleInCooldown: 300
        ScaleOutCooldown: 60

  AutoScalingRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-autoscaling-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: application-autoscaling.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceAutoscaleRole

  # CloudWatch Alarms
  HighCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cpu-${Environment}"
      AlarmDescription: CPU utilization above threshold
      MetricName: CPUUtilization
      Namespace: AWS/ECS
      Dimensions:
        - Name: ClusterName
          Value: !Ref ECSCluster
        - Name: ServiceName
          Value: !Ref EcsService
      Statistic: Average
      Period: 60
      EvaluationPeriods: 2
      Threshold: 85
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref ScalingAlarmTopic
      OKActions:
        - !Ref ScalingAlarmTopic

  HighMemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-memory-${Environment}"
      AlarmDescription: Memory utilization above threshold
      MetricName: MemoryUtilization
      Namespace: AWS/ECS
      Dimensions:
        - Name: ClusterName
          Value: !Ref ECSCluster
        - Name: ServiceName
          Value: !Ref EcsService
      Statistic: Average
      Period: 60
      EvaluationPeriods: 2
      Threshold: 85
      ComparisonOperator: GreaterThanThreshold

  ScalingAlarmTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-alerts-${Environment}"
      Subscription:
        - Endpoint: !Ref AlertEmail
          Protocol: email

Outputs:
  ClusterName:
    Description: Name of the ECS cluster
    Value: !Ref ECSCluster
    Export:
      Name: !Sub "${AWS::StackName}-ClusterName-${Environment}"

  ClusterArn:
    Description: ARN of the ECS cluster
    Value: !GetAtt ECSCluster.Arn
    Export:
      Name: !Sub "${AWS::StackName}-ClusterArn-${Environment}"

  ServiceName:
    Description: Name of the ECS service
    Value: !Ref EcsService

  ServiceArn:
    Description: ARN of the ECS service
    Value: !GetAtt EcsService.Arn

  LoadBalancerDnsName:
    Description: DNS name of the ALB
    Value: !GetAtt ApplicationLoadBalancer.DNSName

  LoadBalancerUrl:
    Description: URL of the ALB
    Value: !Sub "http://${ApplicationLoadBalancer.DNSName}"
```

## Example 2: Multi-Container Task with Sidecar

Task definition with main application container and Redis sidecar.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Multi-container task with application and Redis

Parameters:
  Environment:
    Type: String
    Default: production

  AppImage:
    Type: String
    Description: Application container image

Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: multi-container-task
      Cpu: "1024"
      Memory: "2048"
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        # Main Application Container
        - Name: app
          Image: !Ref AppImage
          Cpu: 512
          Memory: 1024
          PortMappings:
            - ContainerPort: 8080
              Protocol: tcp
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
            - Name: REDIS_HOST
              Value: localhost
            - Name: REDIS_PORT
              Value: "6379"
          Secrets:
            - Name: DATABASE_URL
              ValueFrom: !Ref DatabaseSecretArn
            - Name: JWT_SECRET
              ValueFrom: !Ref JwtSecretArn
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref AppLogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: app
          HealthCheck:
            Command:
              - CMD-SHELL
              - curl -f http://localhost:8080/actuator/health || exit 1
            Interval: 30
            Timeout: 5
            Retries: 3
            StartPeriod: 90
          DependsOn:
            - ContainerName: redis
              Condition: HEALTHY

        # Redis Sidecar Container
        - Name: redis
          Image: redis:7-alpine
          Cpu: 256
          Memory: 512
          PortMappings:
            - ContainerPort: 6379
              Protocol: tcp
          HealthCheck:
            Command:
              - CMD-SHELL
              - redis-cli ping | grep -q PONG
            Interval: 10
            Timeout: 5
            Retries: 3
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref RedisLogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: redis

        # Nginx Sidecar (Reverse Proxy)
        - Name: nginx
          Image: nginx:alpine
          Cpu: 128
          Memory: 256
          PortMappings:
            - ContainerPort: 80
              Protocol: tcp
          Environment:
            - Name: APP_HOST
              Value: localhost
            - Name: APP_PORT
              Value: "8080"
          DependsOn:
            - ContainerName: app
              Condition: HEALTHY
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref NginxLogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: nginx
          VolumesFrom:
            - SourceContainer: app
              ReadOnly: true

      Volumes:
        - Name: shared-data
        - Name: nginx-cache

  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-task-execution"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
      Policies:
        - PolicyName: SecretsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource:
                  - !Ref DatabaseSecretArn
                  - !Ref JwtSecretArn

  AppLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}/app"
      RetentionInDays: 30

  RedisLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}/redis"
      RetentionInDays: 30

  NginxLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}/nginx"
      RetentionInDays: 30
```

## Example 3: Blue/Green Deployment

Complete blue/green deployment with CodeDeploy and traffic shifting.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::CodeDeployBlueGreen

Description: ECS blue/green deployment with CodeDeploy

Parameters:
  Environment:
    Type: String
    Default: production

  BlueImage:
    Type: String
    Description: Blue environment container image

  GreenImage:
    Type: String
    Description: Green environment container image

Resources:
  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-cluster"
      ClusterSettings:
        - Name: containerInsights
          Value: enabled

  # Task Definition (Blue)
  TaskDefinitionBlue:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-blue"
      Cpu: "512"
      Memory: "1024"
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        - Name: web
          Image: !Ref BlueImage
          Cpu: 256
          Memory: 512
          PortMappings:
            - ContainerPort: 80
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: blue

  # Task Definition (Green)
  TaskDefinitionGreen:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-green"
      Cpu: "512"
      Memory: "1024"
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        - Name: web
          Image: !Ref GreenImage
          Cpu: 256
          Memory: 512
          PortMappings:
            - ContainerPort: 80
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: green

  # Task Set (Blue)
  TaskSetBlue:
    Type: AWS::ECS::TaskSet
    Properties:
      Cluster: !Ref ECSCluster
      Service: !Ref ECSService
      TaskDefinition: !Ref TaskDefinitionBlue
      Scale:
        Unit: PERCENT
        Value: 100

  # Task Set (Green)
  TaskSetGreen:
    Type: AWS::ECS::TaskSet
    Properties:
      Cluster: !Ref ECSCluster
      Service: !Ref ECSService
      TaskDefinition: !Ref TaskDefinitionGreen
      Scale:
        Unit: PERCENT
        Value: 0

  # ECS Service
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${AWS::StackName}-service"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinitionBlue
      DesiredCount: 2
      LaunchType: FARGATE
      LoadBalancers:
        - ContainerName: web
          ContainerPort: 80
          TargetGroupArn: !Ref BlueTargetGroup

  # Target Groups
  BlueTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-blue-tg"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /health
      TargetType: ip

  GreenTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-green-tg"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /health
      TargetType: ip

  # Listeners
  ProductionListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref BlueTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  TestListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref BlueTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 8080
      Protocol: HTTP

  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb"
      Scheme: internet-facing
      Subnets: !Ref PublicSubnets
      SecurityGroups:
        - !Ref AlbSecurityGroup

  AlbSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-alb-sg"
      GroupDescription: ALB security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0

  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}"
      RetentionInDays: 30

  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-task-execution"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  # CodeDeploy Blue/Green Hook
Hooks:
  BlueGreenHook:
    Type: AWS::CodeDeploy::BlueGreen
    Properties:
      TrafficRoutingConfig:
        Type: TimeBasedCanary
        TimeBasedCanary:
          StepPercentage: 15
          BakeTimeMins: 5
      AdditionalOptions:
        TerminationWaitTimeInMinutes: 5
      ServiceRole: !Ref CodeDeployRoleArn
      Applications:
        - Target:
            Type: AWS::ECS::Service
            LogicalID: ECSService
          ECSAttributes:
            TaskDefinitions:
              - TaskDefinitionBlue
              - TaskDefinitionGreen
            TaskSets:
              - TaskSetBlue
              - TaskSetGreen
            TrafficRouting:
              ProdTrafficRoute:
                Type: AWS::ElasticLoadBalancingV2::Listener
                LogicalID: ProductionListener
              TestTrafficRoute:
                Type: AWS::ElasticLoadBalancingV2::Listener
                LogicalID: TestListener
              TargetGroups:
                - BlueTargetGroup
                - GreenTargetGroup

  CodeDeployRoleArn:
    Value: !Sub "arn:aws:iam::${AWS::AccountId}:role/service-role/AmazonCodeDeployRoleForECS"
```

## Example 4: Service Discovery with Cloud Map

ECS service with service discovery using AWS Cloud Map.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECS service with service discovery

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  # Private DNS Namespace
  ServiceDiscoveryNamespace:
    Type: AWS::ServiceDiscovery::PrivateDnsNamespace
    Properties:
      Name: !Sub "${Environment}.internal"
      Vpc: !Ref VpcId
      Description: !Sub "Service discovery namespace for ${Environment}"

  # Service with service discovery
  ServiceDiscoveryService:
    Type: AWS::ServiceDiscovery::Service
    Properties:
      Name: api-service
      NamespaceId: !Ref ServiceDiscoveryNamespace
      DnsConfig:
        RoutingPolicy: LATENCY
        DnsRecords:
          - Type: A
            TTL: 60
          - Type: SRV
            TTL: 60
      HealthCheckConfig:
        Type: HTTP
        ResourcePath: /health
        FailureThreshold: 2
      Description: API service discovery

  # ECS Service with service registry
  EcsService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${AWS::StackName}-service"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 3
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: DISABLED
          SecurityGroups:
            - !Ref EcsSecurityGroup
          Subnets: !Ref PrivateSubnets
      ServiceRegistries:
        - RegistryArn: !GetAtt ServiceDiscoveryService.Arn
          Port: 8080
          ContainerName: api
          ContainerPort: 8080

Outputs:
  ServiceDiscoveryArn:
    Description: ARN of the service discovery service
    Value: !GetAtt ServiceDiscoveryService.Arn

  ServiceDiscoveryName:
    Description: DNS name of the service
    Value: !Sub "api-service.${Environment}.internal"
```

## Example 5: Scheduled Tasks

Scheduled task definition using EventBridge rules.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Scheduled ECS task with EventBridge

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  # Task Definition for batch job
  BatchTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: batch-job-task
      Cpu: "2048"
      Memory: "4096"
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        - Name: batch-job
          Image: !Ref JobImage
          Cpu: 2048
          Memory: 4096
          Command:
            - /app/batch-process.sh
            - "--date"
            - !Ref ProcessingDate
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
            - Name: LOG_LEVEL
              Value: INFO
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref BatchLogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: batch
          ReadonlyRootFilesystem: true
          Privileged: false

  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-batch-execution"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  # EventBridge Rule for scheduled execution
  ScheduledRule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub "${AWS::StackName}-daily-batch"
      Description: Triggers batch job daily at 2 AM
      ScheduleExpression: "cron(0 2 * * ? *)"
      State: ENABLED
      Targets:
        - Id: BatchTask
          Arn: !Ref EcsTaskArn
          RoleArn: !Ref EventsRoleArn
          EcsParameters:
            TaskDefinitionArn: !Ref BatchTaskDefinition
            TaskCount: 1
            LaunchType: FARGATE
            NetworkConfiguration:
              AwsvpcConfiguration:
                AssignPublicIp: DISABLED
                SecurityGroups:
                  - !Ref BatchSecurityGroup
                Subnets: !Ref PrivateSubnets
            PlatformVersion: LATEST

  EventsRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-events-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: EventsEcsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - ecs:RunTask
                Resource: !Ref BatchTaskDefinition
              - Effect: Allow
                Action:
                  - ecs:StopTask
                  - ecs:DescribeTasks
                Resource: "*"
              - Effect: Allow
                Action:
                  - iam:PassRole
                Resource: !Ref TaskExecutionRole

  BatchLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}/batch"
      RetentionInDays: 90

  BatchSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-batch-sg"
      GroupDescription: Security group for batch tasks
      VpcId: !Ref VpcId

Outputs:
  ScheduledRuleArn:
    Description: ARN of the scheduled rule
    Value: !GetAtt ScheduledRule.Arn
```

## Example 6: Spot Capacity Provider

ECS cluster with spot instance capacity provider for cost optimization.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECS cluster with Spot capacity provider

Parameters:
  ClusterName:
    Type: String
    Default: spot-cluster

Resources:
  # Auto Scaling Group with Mixed Instances Policy
  CapacityAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${ClusterName}-capacity-asg"
      LaunchConfigurationName: !Ref SpotLaunchConfiguration
      MinSize: 1
      MaxSize: 10
      DesiredCapacity: 3
      VPCZoneIdentifier: !Ref PrivateSubnets
      MixedInstancesPolicy:
        InstancesDistribution:
          OnDemandAllocationStrategy: lowest-price
          OnDemandBaseCapacity: 0
          OnDemandPercentageAboveBaseCapacity: 0
          SpotAllocationStrategy: capacity-optimized
          SpotInstancePools: 5
        LaunchTemplate:
          LaunchTemplateSpecification:
            LaunchTemplateId: !Ref SpotLaunchTemplate
            Version: !GetAtt SpotLaunchTemplate.LatestVersionNumber
          Overrides:
            - InstanceType: t3.medium
              WeightedCapacity: 1
            - InstanceType: t3.large
              WeightedCapacity: 2
      Tags:
        - Key: Name
          Value: !Sub "${ClusterName}-instance"
          PropagateAtLaunch: true
        - Key: Cluster
          Value: !Ref ClusterName
          PropagateAtLaunch: true

  # Launch Template
  SpotLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub "${ClusterName}-spot-template"
      LaunchTemplateData:
        ImageId: !Ref AmiId
        InstanceType: t3.medium
        IamInstanceProfile:
          Name: !Ref EcsInstanceProfile
        SecurityGroupIds:
          - !Ref EcsSecurityGroup
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            echo "ECS_CLUSTER=${ClusterName}" >> /etc/ecs/ecs.config
            echo "ECS_BACKEND_HOST=${EcsBackendHost}" >> /etc/ecs/ecs.config
            echo "ECS_ENABLE_SPOT_INSTANCE_DRAINING=true" >> /etc/ecs/ecs.config
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub "${ClusterName}-spot-instance"
              - Key: Cluster
                Value: !Ref ClusterName

  # Capacity Provider
  SpotCapacityProvider:
    Type: AWS::ECS::CapacityProvider
    Properties:
      Name: !Sub "${ClusterName}-spot-cp"
      AutoScalingGroupProvider:
        AutoScalingGroupArn: !Ref CapacityAutoScalingGroup
        ManagedScaling:
          Status: ENABLED
          TargetCapacity: 80
          MinimumScalingStepSize: 1
          MaximumScalingStepSize: 5
        ManagedTerminationProtection: DISABLED

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Ref ClusterName
      ClusterSettings:
        - Name: containerInsights
          Value: enabled
      CapacityProviders:
        - !Ref SpotCapacityProvider

  # ECS Service using Spot capacity provider
  EcsService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${AWS::StackName}-service"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      CapacityProviderStrategy:
        - CapacityProvider: !Ref SpotCapacityProvider
          Weight: 1

  EcsInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub "${ClusterName}-instance-profile"
      Roles:
        - !Ref EcsInstanceRole

  EcsInstanceRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ClusterName}-instance-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role

  EcsSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${ClusterName}-ecs-sg"
      GroupDescription: ECS instance security group
      VpcId: !Ref VpcId
```

## Example 7: Service with DAEMON Scheduling Strategy

ECS service using DAEMON scheduling strategy for sidecar containers.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECS service with DAEMON scheduling strategy

Resources:
  # Log Router Sidecar (DAEMON scheduling)
  LogRouterTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: log-router
      Cpu: "256"
      Memory: "512"
      NetworkMode: Host
      RequiresCompatibilities:
        - EC2
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        - Name: log-router
          Image: amazon/aws-for-fluent-bit:stable
          Cpu: 256
          Memory: 512
          FirelensConfiguration:
            Type: fluentbit
            Options:
              enable-ecs-log-metadata: "true"
          Storage:
            - Type: emptyDir
              Size: 5
          LinuxParameters:
            Devices:
              - HostPath: /var/log
                ContainerPath: /var/log/host
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: log-router
          ReadonlyRootFilesystem: false
          Privileged: false

  LogRouterService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${AWS::StackName}-log-router"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref LogRouterTaskDefinition
      SchedulingStrategy: DAEMON
      DeploymentConfiguration:
        MaximumPercent: 100
        MinimumHealthyPercent: 0
      PlacementConstraints:
        - Type: memberOf
          Expression: "attribute:ecs.availability-zone in (${az1}, ${az2}, ${az3})"

  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-task-execution"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
      Policies:
        - PolicyName: LogsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"
