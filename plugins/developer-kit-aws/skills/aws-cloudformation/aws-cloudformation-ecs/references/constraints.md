# AWS ECS Constraints and Limitations

## Resource Limits

### Task Definition and Container Limits

```yaml
# Maximum task definition size: 1 KB (CloudFormation)
# Maximum 10 containers per task definition
# Memory limits must be set for all containers
# CPU units must be set for all containers in Fargate

Parameters:
  ContainerCount:
    Type: Number
    Default: 1
    MaxValue: 10
    Description: Number of containers in task definition

Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: application
          Memory: 512
          Cpu: 256
        # Maximum 10 containers allowed
```

## Operational Constraints

### Service Update Limits

```yaml
# Services can only update to new task definitions
# Cannot modify existing task definitions
# Create new versions for updates

Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-task"
      ContainerDefinitions:
        - Name: application
          Image: !Ref ImageUrl
      # Always create new version for updates

  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDefinition
      # Service updates require new task definition version
```

### ENI and Network Constraints

```yaml
# awsvpc mode requires ENIs
# Each task consumes ENIs from subnet pool
# Plan ENI requirements for scaling

Resources:
  Service:
    Type: AWS::ECS::Service
    Properties:
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - !Ref PrivateSubnet1
            - !Ref PrivateSubnet2
          SecurityGroups:
            - !Ref SecurityGroup
          AssignPublicIp: DISABLED
      # Each task gets ENI from subnet pool
```

## Security Constraints

### Task IAM Roles

```yaml
# Task IAM roles must be assumable by ecs-tasks.amazonaws.com
# awsvpc mode required for Fargate

Resources:
  TaskExecutionRole:
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
```

## Cost Considerations

### Fargate Pricing

```yaml
# Fargate charges per vCPU and memory per hour
# Minimum charges apply (0.25 vCPU, 0.5 GB memory)

Parameters:
  TaskCPU:
    Type: String
    Default: 256
    AllowedValues:
      - 256    # 0.25 vCPU
      - 512    # 0.5 vCPU
      - 1024   # 1 vCPU
      - 2048   # 2 vCPU
      - 4096   # 4 vCPU
    Description: CPU units (affects cost)

  TaskMemory:
    Type: String
    Default: 512
    AllowedValues:
      - 512    # 0.5 GB
      - 1024   # 1 GB
      - 2048   # 2 GB
      - 3072   # 3 GB
      - 4096   # 4 GB
      - 5120   # 5 GB
      - 6144   # 6 GB
      - 7168   # 7 GB
      - 8192   # 8 GB
      - 9216   # 9 GB
      - 10240  # 10 GB
    Description: Memory (affects cost)
```

### Data Transfer Costs

```yaml
# Data transfer between tasks in different AZs incurs cross-AZ costs
# Use same AZ for communication when possible

Resources:
  Service:
    Type: AWS::ECS::Service
    Properties:
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - !Ref PrivateSubnetAZ1
            - !Ref PrivateSubnetAZ1  # Duplicate AZ for cost optimization
```

## Availability Constraints

### Fargate Spot Interruptions

```yaml
# Fargate Spot can interrupt tasks with 2-minute notice
# Implement graceful shutdown handling

Resources:
  Service:
    Type: AWS::ECS::Service
    Properties:
      CapacityProviderStrategy:
        - Base: 1
          CapacityProvider: FARGATE_SPOT
          Weight: 1
        - Base: 0
          CapacityProvider: FARGATE
          Weight: 0
      # Spot tasks can be interrupted with 2-minute notice
```

### Health Check Failures

```yaml
# Failing health checks can cause rapid task replacement
# Configure appropriate grace periods

Resources:
  Service:
    Type: AWS::ECS::Service
    Properties:
      HealthCheckGracePeriodSeconds: 60
      DeploymentController:
        DeploymentCircuitBreaker:
          Enable: true
          Rollback: true
      # Prevents rapid task replacement during startup
```

## Best Practices to Avoid Constraints

### Use Multiple AZs

```yaml
Resources:
  Service:
    Type: AWS::ECS::Service
    Properties:
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - !Ref PrivateSubnetAZ1
            - !Ref PrivateSubnetAZ2
            - !Ref PrivateSubnetAZ3
      # Spread tasks across AZs for high availability
```

### Optimize Image Size

```yaml
# Use multi-stage builds to reduce image size
# Smaller images = faster cold starts

# Dockerfile example:
# FROM node:20 AS build
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --production
# FROM node:20-alpine
# COPY --from=build /app/node_modules ./node_modules
# COPY . .
# CMD ["node", "index.js"]
```

### Implement Auto Scaling

```yaml
Resources:
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 10
      MinCapacity: 1
      ResourceId: !Sub "service/${ClusterName}/${ServiceName}"
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

## Quota Management

### Request Quota Increases

```yaml
# ENI limits, service limits, and concurrent execution limits can be increased
# Document requirements in stack outputs

Parameters:
  ExpectedENI:
    Type: Number
    Default: 50
    Description: Expected ENI usage (per subnet)

Outputs:
  QuotaIncreaseRequest:
    Description: Link to request quota increase
    Value: !Sub "https://console.aws.amazon.com/support/home#/case/create?issueType=service-limit-increase&serviceCode=amazon-ecs"
```
