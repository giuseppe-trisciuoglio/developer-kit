---
name: aws-cloudformation-ecs
description: Provides AWS CloudFormation patterns for ECS clusters, services, and task definitions. Use when creating ECS infrastructure with CloudFormation, configuring container definitions, scaling policies, service discovery, load balancing integration, and implementing template structure with Parameters, Outputs, Mappings, Conditions, cross-stack references, and blue/green deployments with CodeDeploy.
category: aws
tags: [aws, cloudformation, ecs, containers, docker, orchestration, infrastructure, iaac]
version: 2.2.0
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation ECS

## Overview

Create production-ready container infrastructure using AWS CloudFormation templates. This skill covers ECS clusters, services, task definitions, container configurations, scaling, service discovery, load balancing, and blue/green deployments with CodeDeploy.

## When to Use

Use this skill when:
- Creating new ECS clusters with CloudFormation
- Defining task definitions for Fargate or EC2 launch types
- Configuring ECS services with deployment strategies
- Integrating ECS with Application Load Balancer
- Implementing auto scaling for ECS services
- Configuring service discovery with Cloud Map
- Implementing blue/green deployments with CodeDeploy
- Implementing cross-stack references with export/import

## Instructions

1. **Define Cluster**: Create ECS cluster with `containerInsights` enabled
2. **Configure Task Definition**: Set CPU/Memory, container image, port mappings, log configuration, health checks
3. **Set Up Execution Role**: Create role with `AmazonECSTaskExecutionRolePolicy` for pulling images and logging
4. **Create Task Role**: Define role for container's application-level AWS access
5. **Create Service**: Configure desired count, deployment configuration (MaximumPercent, MinimumHealthyPercent)
6. **Set Up ALB Integration**: Configure target group (type: ip for Fargate), listener rules
7. **Configure Service Discovery**: Use Cloud Map namespace for service-to-service communication
8. **Implement Auto Scaling**: Create ScalableTarget and TargetTrackingScalingPolicy for CPU/memory
9. **Add Blue/Green**: Configure CodeDeploy deployment group with two target groups
10. **Export Outputs**: Export ClusterName, ServiceName, ALB DNS for cross-stack use

## Best Practices

### Security
- Use Fargate for serverless container management (no EC2 patching)
- Use task roles with least privilege (not execution role)
- Store secrets in Secrets Manager, reference via `secrets` in container definition
- Enable awslogs log driver for centralized logging
- Use private subnets with NAT for Fargate tasks

### Performance
- Right-size CPU/Memory for task definitions
- Use Application Auto Scaling with target tracking (70% CPU)
- Configure health check grace period to avoid premature termination
- Use ECS Service Connect or Cloud Map for service discovery

### Deployment
- Use blue/green with CodeDeploy for zero-downtime deployments
- Set MinimumHealthyPercent: 50, MaximumPercent: 200
- Configure circuit breaker with rollback enabled

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECS Fargate service with ALB

Resources:
  Cluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-cluster"
      ClusterSettings:
        - Name: containerInsights
          Value: enabled

  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-task"
      Cpu: "512"
      Memory: "1024"
      NetworkMode: awsvpc
      RequiresCompatibilities: [FARGATE]
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: !Ref ImageUri
          PortMappings:
            - ContainerPort: 8080
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  Service:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref Cluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
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
          SecurityGroups: [!Ref ServiceSG]
          Subnets: !Ref PrivateSubnets
      LoadBalancers:
        - ContainerName: app
          ContainerPort: 8080
          TargetGroupArn: !Ref TargetGroup

Outputs:
  ClusterName:
    Value: !Ref Cluster
    Export:
      Name: !Sub "${AWS::StackName}-ClusterName"
  ServiceName:
    Value: !GetAtt Service.Name
    Export:
      Name: !Sub "${AWS::StackName}-ServiceName"
```

## Constraints and Warnings

- **Fargate Limits**: CPU 0.25-4 vCPU; Memory 0.5-30 GB (valid combinations only)
- **Task Definition**: Max 10 containers per task definition
- **Service Limits**: Max 5000 tasks per service
- **ALB Integration**: Target type must be `ip` for Fargate (not `instance`)
- **Service Discovery**: Cloud Map namespace must be created before service
- **Blue/Green**: Requires two target groups and CodeDeploy configuration
- **Log Groups**: Must create log group before task runs or use `awslogs-create-group: true`
- **ECR Pull**: Execution role needs `ecr:GetAuthorizationToken` and `ecr:BatchGetImage`

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
