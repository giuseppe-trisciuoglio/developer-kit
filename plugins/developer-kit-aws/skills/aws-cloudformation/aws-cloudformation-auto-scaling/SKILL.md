---
name: aws-cloudformation-auto-scaling
description: Provides AWS CloudFormation patterns for Auto Scaling including EC2, ECS, and Lambda. Use when creating Auto Scaling groups, launch configurations, launch templates, scaling policies, lifecycle hooks, and predictive scaling. Covers template structure with Parameters, Outputs, Mappings, Conditions, cross-stack references, and best practices for high availability and cost optimization.
category: aws
tags: [aws, cloudformation, auto-scaling, ec2, ecs, lambda, infrastructure, iaac, scaling]
version: 2.2.0
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation Auto Scaling

## Overview

Create production-ready Auto Scaling infrastructure using AWS CloudFormation templates. This skill covers Auto Scaling Groups for EC2, ECS, and Lambda, launch configurations, launch templates, scaling policies, lifecycle hooks, and best practices for high availability and cost optimization.

## When to Use

Use this skill when:
- Creating Auto Scaling Groups for EC2 instances
- Configuring Launch Configurations or Launch Templates
- Implementing scaling policies (step, target tracking, simple)
- Adding lifecycle hooks for lifecycle management
- Creating scaling for ECS services
- Implementing Lambda provisioned concurrency scaling
- Organizing templates with Parameters, Outputs, Mappings, Conditions
- Implementing cross-stack references with export/import
- Using mixed instances policies for diversity

## Instructions

Follow these steps to create Auto Scaling infrastructure with CloudFormation:

1. **Define Parameters**: Use AWS-specific parameter types for validation (e.g., `AWS::EC2::Image::Id`, `List<AWS::EC2::Subnet::Id>`, SSM parameter references)
2. **Configure Launch Resources**: Create LaunchConfiguration or LaunchTemplate with proper instance settings, security groups, UserData, and monitoring
3. **Create Auto Scaling Group**: Specify min/max/desired capacity, associate with launch resource, set VPCZoneIdentifier for multi-AZ
4. **Add Scaling Policies**: Implement target tracking (CPU/network/ALB), step scaling with CloudWatch alarms, or simple scaling policies
5. **Configure Health Checks**: Set up ELB or EC2 health checks with appropriate grace periods (typically 300s)
6. **Add Lifecycle Hooks**: Implement hooks for custom actions during EC2_INSTANCE_LAUNCHING and EC2_INSTANCE_TERMINATING transitions
7. **Set Up Monitoring**: Configure CloudWatch alarms for CPU, network, request count, latency, and unhealthy hosts
8. **Use Cross-Stack References**: Export ASG names and ARNs for other stacks to import via `!ImportValue`
9. **Apply Conditions**: Use conditions for environment-specific scaling (dev/staging/production)
10. **Schedule Scaling**: Add scheduled actions for predictable traffic patterns using cron expressions

## Best Practices

### High Availability
- Distribute instances across multiple AZs
- Use ALB with health checks for automatic routing
- Implement lifecycle hooks for graceful shutdown
- Configure appropriate termination policies
- Use mixed instances policies for diversity

### Cost Optimization
- Use Spot Instances for fault-tolerant workloads
- Implement right-sizing of instances
- Configure aggressive scale-in policies
- Use scheduled scaling for predictable patterns

### Security
- Use IAM roles with minimum permissions (avoid broad managed policies)
- Encrypt EBS volumes with KMS
- Configure restrictive security groups
- Use VPC with appropriate subnets
- Use parameter store for sensitive configuration

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Auto Scaling group with target tracking

Parameters:
  AmiId:
    Type: AWS::EC2::Image::Id
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub "${AWS::StackName}-lt"
      LaunchTemplateData:
        ImageId: !Ref AmiId
        InstanceType: t3.micro
        Monitoring:
          Enabled: true

  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg"
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 2
      VPCZoneIdentifier: !Ref SubnetIds
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300

  TargetTrackingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-cpu-tracking"
      PolicyType: TargetTrackingScaling
      AutoScalingGroupName: !Ref AutoScalingGroup
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70

Outputs:
  AutoScalingGroupName:
    Value: !Ref AutoScalingGroup
    Export:
      Name: !Sub "${AWS::StackName}-ASGName"
```

## Constraints and Warnings

- **ASG Limits**: Max 200 Auto Scaling Groups per region per account
- **Cooldown Periods**: Prevent rapid scale-in/scale-out oscillations but can delay response
- **Health Check Grace Period**: Too short may terminate instances still bootstrapping
- **Mixed Instances Policy**: Not all instance types support on-demand/Spot allocation
- **Predictive Scaling**: Requires at least 24 hours of metric data
- **Spot Instances**: Can be terminated with 2-minute notice; not for stateful workloads
- **IAM Roles**: Auto Scaling requires IAM roles with appropriate permissions for lifecycle hooks

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
