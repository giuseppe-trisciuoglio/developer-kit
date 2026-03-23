---
name: aws-cloudformation-auto-scaling
description: Provides AWS CloudFormation patterns for Auto Scaling including EC2, ECS, and Lambda. Use when creating Auto Scaling groups, launch configurations, launch templates, scaling policies, lifecycle hooks, and predictive scaling. Covers template structure with Parameters, Outputs, Mappings, Conditions, cross-stack references, and best practices for high availability and cost optimization.
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

### 1. Define Parameters

Specify capacity and instance settings with AWS-specific parameter types:

```yaml
Parameters:
  MinSize:
    Type: Number
    Default: 2
    Description: Minimum number of instances

  MaxSize:
    Type: Number
    Default: 10
    Description: Maximum number of instances

  DesiredCapacity:
    Type: Number
    Default: 2
    Description: Desired number of instances

  InstanceType:
    Type: AWS::EC2::Instance::Type
    Default: t3.micro
    Description: EC2 instance type

  AmiId:
    Type: AWS::EC2::Image::Id
    Description: AMI ID for instances

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Subnets for Auto Scaling group
```

### 2. Create Launch Configuration

Define instance launch settings:

```yaml
Resources:
  MyLaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      LaunchConfigurationName: !Sub "${AWS::StackName}-lc"
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyName
      SecurityGroups:
        - !Ref InstanceSecurityGroup
      InstanceMonitoring: Enabled
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
```

### 3. Create Auto Scaling Group

Specify min/max/desired capacity and networking:

```yaml
Resources:
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg"
      MinSize: !Ref MinSize
      MaxSize: !Ref MaxSize
      DesiredCapacity: !Ref DesiredCapacity
      VPCZoneIdentifier: !Ref SubnetIds
      LaunchConfigurationName: !Ref MyLaunchConfiguration
      TargetGroupARNs:
        - !Ref MyTargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Environment
          Value: !Ref Environment
          PropagateAtLaunch: true
```

### 4. Configure Load Balancer Integration

Set up ALB for traffic distribution:

```yaml
Resources:
  MyTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-tg"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPCId
      HealthCheckPath: /
      TargetType: instance

  MyLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb"
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
```

### 5. Add Scaling Policies

Implement target tracking scaling:

```yaml
Resources:
  TargetTrackingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-target-tracking"
      PolicyType: TargetTrackingScaling
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70
        DisableScaleIn: false
```

### 6. Configure Lifecycle Hooks

Implement hooks for graceful instance management:

```yaml
Resources:
  LifecycleHookTermination:
    Type: AWS::AutoScaling::LifecycleHook
    Properties:
      LifecycleHookName: !Sub "${AWS::StackName}-termination-hook"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      LifecycleTransition: autoscaling:EC2_INSTANCE_TERMINATING
      HeartbeatTimeout: 300
      NotificationTargetARN: !Ref SNSTopic
      RoleARN: !Ref LifecycleHookRole
```

### 7. Set Up Monitoring

Configure CloudWatch alarms for scaling triggers:

```yaml
Resources:
  HighCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cpu"
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref MyAutoScalingGroup
      Statistic: Average
      Period: 60
      EvaluationPeriods: 3
      Threshold: 70
      ComparisonOperator: GreaterThanThreshold
```

### 8. Configure Outputs and Cross-Stack References

Export ASG configuration for other stacks:

```yaml
Outputs:
  AutoScalingGroupName:
    Description: Name of the Auto Scaling Group
    Value: !Ref MyAutoScalingGroup
    Export:
      Name: !Sub "${AWS::StackName}-AutoScalingGroupName"

  AutoScalingGroupArn:
    Description: ARN of the Auto Scaling Group
    Value: !GetAtt MyAutoScalingGroup.AutoScalingGroupArn
    Export:
      Name: !Sub "${AWS::StackName}-AutoScalingGroupArn"
```

## Best Practices

### High Availability

- Distribute instances across multiple AZs
- Use ALB with health checks for automatic routing
- Implement lifecycle hooks for graceful shutdown
- Configure appropriate termination policies
- Use mixed instances policies for diversity
- Set appropriate health check grace periods

### Cost Optimization

- Use Spot Instances for fault-tolerant workloads
- Implement right-sizing of instances
- Configure aggressive scale-in policies
- Use scheduled scaling for predictable patterns
- Monitor and optimize regularly
- Set appropriate minimum capacity to avoid over-provisioning

### Monitoring

- Create CloudWatch Alarms for key metrics
- Implement scaling policies based on metrics
- Use lifecycle hooks for logging and analytics
- Configure SNS notifications for scaling events
- Implement detailed monitoring for troubleshooting
- Use multiple scaling policies for optimal response

### Security

- Use IAM roles with least privilege permissions
- Encrypt EBS volumes with KMS
- Configure restrictive security groups
- Use VPC with appropriate subnets
- Implement Parameter Store for sensitive configuration
- Avoid broad managed policies (use specific permissions)
- Configure appropriate instance profiles

## References

For detailed implementation guidance, see:

- **[constraints.md](references/constraints.md)** - Resource limits (ASG limits, scaling policy limits, lifecycle hook limits), scaling constraints (cooldown periods, health check grace periods, min/max capacity), operational constraints (mixed instances policy, predictive scaling, instance refresh), security constraints (IAM roles, service-linked roles, KMS permissions), and cost considerations (Spot instance termination, over-provisioning, scaling frequency)

## Related Resources

- [Auto Scaling Documentation](https://docs.aws.amazon.com/autoscaling/)
- [AWS CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/)
- [Auto Scaling Best Practices](https://docs.aws.amazon.com/autoscaling/plans/userguide/auto-scaling-best-practices.html)
- [Application Auto Scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/what-is-application-auto-scaling.html)
