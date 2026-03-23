---
name: aws-cloudformation-ecs
description: Provides AWS CloudFormation patterns for ECS clusters, task definitions, services, container definitions, auto scaling, blue/green deployments, CodeDeploy integration, ALB integration, service discovery, monitoring, logging, template structure, parameters, outputs, and cross-stack references. Use when creating ECS clusters with CloudFormation, configuring Fargate and EC2 launch types, implementing blue/green deployments, managing auto scaling, integrating with ALB and NLB, and implementing ECS best practices.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation ECS

## Overview

Create production-ready ECS infrastructure using AWS CloudFormation templates. This skill covers ECS clusters, task definitions, services, container definitions, auto scaling, blue/green deployments, CodeDeploy integration, ALB integration, service discovery, monitoring, logging, best practices for parameters, outputs, and cross-stack references.

## When to Use

Use this skill when:
- Creating ECS clusters with CloudFormation
- Configuring Fargate and EC2 launch types
- Implementing task definitions and container definitions
- Managing ECS services with ALB/NLB integration
- Implementing blue/green deployments with CodeDeploy
- Configuring auto scaling for ECS services
- Setting up service discovery with Cloud Map
- Managing container image repositories with ECR
- Implementing monitoring, logging, and tracing
- Organizing ECS infrastructure with parameters and outputs
- Implementing capacity providers and scaling strategies

## Instructions

Follow these steps to create ECS infrastructure with CloudFormation:

### 1. Define ECS Cluster Parameters

Specify launch type, networking, and capacity settings:

```yaml
Parameters:
  LaunchType:
    Type: String
    Default: FARGATE
    AllowedValues:
      - EC2
      - FARGATE
    Description: ECS launch type

  ContainerPort:
    Type: Number
    Default: 80
    Description: Container port

  TaskCPU:
    Type: String
    Default: 256
    AllowedValues:
      - 256
      - 512
      - 1024
      - 2048
      - 4096
    Description: Task CPU units

  TaskMemory:
    Type: String
    Default: 512
    AllowedValues:
      - 512
      - 1024
      - 2048
      - 3072
      - 4096
      - 5120
      - 6144
      - 7168
      - 8192
      - 9216
      - 10240
    Description: Task memory in MB
```

### 2. Create ECS Cluster

Define the cluster infrastructure:

```yaml
Resources:
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-cluster"
      ClusterSettings:
        - Name: containerInsights
          Value: enabled
      CapacityProviders:
        - FARGATE
        - FARGATE_SPOT
      DefaultCapacityProviderStrategy:
        - CapacityProvider: FARGATE
          Weight: 1
        - CapacityProvider: FARGATE_SPOT
          Weight: 0
```

### 3. Create Task Definition

Define container configurations:

```yaml
Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-task"
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: !Ref TaskCPU
      Memory: !Ref TaskMemory
      ExecutionRoleArn: !Ref ExecutionRole
      TaskRoleArn: !Ref TaskRole
      ContainerDefinitions:
        - Name: application
          Image: !Ref ImageUrl
          PortMappings:
            - ContainerPort: !Ref ContainerPort
              Protocol: tcp
          Environment:
            - Name: LOG_LEVEL
              Value: INFO
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs
          Memory: !Ref TaskMemory
```

### 4. Configure Execution Roles

Set up IAM roles for task execution:

```yaml
Resources:
  ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  TaskRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: S3Access
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "${DataBucket.Arn}/*"
```

### 5. Create ECS Service

Define the service configuration:

```yaml
Resources:
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${AWS::StackName}-service"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - !Ref PrivateSubnet1
            - !Ref PrivateSubnet2
          SecurityGroups:
            - !Ref SecurityGroup
          AssignPublicIp: DISABLED
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: application
          ContainerPort: !Ref ContainerPort
```

### 6. Configure Load Balancer

Set up ALB for traffic distribution:

```yaml
Resources:
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb"
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPC
      TargetType: ip

  Listener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - TargetGroupArn: !Ref TargetGroup
          Type: forward
      LoadBalancerArn: !Ref LoadBalancer
      Port: 80
      Protocol: HTTP
```

### 7. Implement Auto Scaling

Configure Application Auto Scaling:

```yaml
Resources:
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 10
      MinCapacity: 1
      ResourceId: !Sub "service/${ECSCluster}/${ECSService}"
      ScalableDimension: ecs:service:DesiredCount
      ServiceNamespace: ecs

  ScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-scaling"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 70.0
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization
```

### 8. Configure Monitoring

Enable CloudWatch Container Insights:

```yaml
Resources:
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}"
      RetentionInDays: 7

  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-cluster"
      ClusterSettings:
        - Name: containerInsights
          Value: enabled
```

## Best Practices

### Cluster Configuration

- Use Fargate for simplified infrastructure management
- Spread services across multiple AZs for high availability
- Enable Container Insights for monitoring
- Use capacity providers for cost optimization (Fargate Spot)
- Configure appropriate vCPU and memory based on workload requirements
- Implement graceful shutdown for task termination

### Task Definition Management

- Use specific versions for immutable deployments
- Keep task definitions under 1 KB for CloudFormation limit
- Define resource limits (CPU, memory) for all containers
- Use environment variables for configuration
- Implement health checks for container applications
- Store container images in ECR for security

### Service Deployment

- Use blue/green deployments for zero-downtime updates
- Configure deployment circuit breakers for automatic rollback
- Set appropriate health check grace periods
- Implement rolling updates with minimum healthy percentage
- Use CodeDeploy for complex deployment strategies
- Test task definitions in development environment first

### Security

- Use awsvpc network mode for Fargate
- Apply least privilege IAM policies to task roles
- Encrypt data in transit using TLS/SSL
- Use private subnets for application tasks
- Rotate secrets and credentials regularly
- Scan container images for vulnerabilities
- Implement security group rules for network traffic

### Scaling and Performance

- Use auto scaling based on CPU, memory, or custom metrics
- Configure appropriate minimum and maximum capacity
- Use Fargate Spot for cost savings on interruptible workloads
- Optimize container image size for faster startup
- Use Application Load Balancer for traffic distribution
- Implement service discovery for inter-service communication

### Monitoring and Logging

- Enable CloudWatch Container Insights for metrics
- Configure CloudWatch Logs for application logs
- Set up CloudWatch alarms for service metrics
- Use X-Ray tracing for distributed tracing
- Monitor task placement and resource utilization
- Implement centralized logging with CloudWatch Logs Insights

## References

For detailed implementation guidance, see:

- **[constraints.md](references/constraints.md)** - Resource limits (task definition size, container limits, memory limits, CPU limits), operational constraints (service updates, ENI limits, task start time, scaling delays), security constraints (IAM roles, network mode, security groups, secrets rotation), cost considerations (Fargate pricing, data transfer, ECR storage, monitoring), deployment constraints (blue/green requirements, CodeDeploy integration, rollbacks, task drift), and availability constraints (Fargate Spot, multi-AZ, health checks, service discovery)

## Related Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [ECS Task Definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)
- [ECS Services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
- [AWS CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/)
- [ECS Blue/Green Deployments](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-steps-ecs.html)
- [CloudFormation Stack Policies](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/protect-stack-resources.html)
- [CloudFormation Drift Detection](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/detect-drift-stack.html)
- [CloudFormation Change Sets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html)
