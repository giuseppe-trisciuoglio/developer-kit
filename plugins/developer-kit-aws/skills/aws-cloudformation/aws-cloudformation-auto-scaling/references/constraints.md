# AWS Auto Scaling Constraints and Limitations

## Resource Limits

### Auto Scaling Group Limits

```yaml
# Maximum 100 Auto Scaling Groups per region per AWS account
# Maximum 500 step adjustments in step scaling policy
# Lifecycle hooks limits vary by instance type

Parameters:
  MaxAutoScalingGroups:
    Type: Number
    Default: 50
    MaxValue: 100
    Description: Expected number of Auto Scaling Groups

Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg"
      MinSize: 1
      MaxSize: 10
      DesiredCapacity: 2
      # Cannot exceed 100 ASGs per region
```

## Scaling Constraints

### Cooldown Periods

```yaml
# Scaling cooldowns prevent rapid oscillations
# Can delay response to demand changes

Parameters:
  DefaultCooldown:
    Type: Number
    Default: 300
    Description: Default cooldown in seconds

  ScaleInCooldown:
    Type: Number
    Default: 300
    Description: Scale-in cooldown in seconds

Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      DefaultCooldown: !Ref DefaultCooldown
```

### Health Check Grace Period

```yaml
# Too short grace period may terminate bootstrapping instances
# Set appropriate grace period for application startup

Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      HealthCheckGracePeriod: 300
      HealthCheckType: ELB
      # Give instances time to start before health checks
```

## Operational Constraints

### Instance Termination

```yaml
# Scale-in terminates instances without graceful shutdown by default
# Implement lifecycle hooks for graceful shutdown

Resources:
  LifecycleHook:
    Type: AWS::AutoScaling::LifecycleHook
    Properties:
      LifecycleHookName: shutdown-hook
      AutoScalingGroupName: !Ref AutoScalingGroup
      LifecycleTransition: autoscaling:EC2_INSTANCE_TERMINATING
      HeartbeatTimeout: 300
      NotificationTargetARN: !Ref SNSTopic
      RoleARN: !Ref LifecycleHookRole
      # Enables graceful shutdown
```

### Mixed Instances Policy

```yaml
# Not all instance types support on-demand/Spot allocation
# Check instance type compatibility

Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MixedInstancesPolicy:
        InstancesDistribution:
          OnDemandBaseCapacity: 1
          OnDemandPercentageAboveBaseCapacity: 50
          SpotAllocationStrategy: capacity-optimized
        LaunchTemplate:
          LaunchTemplateSpecification:
            InstanceType: t3.micro
            # Verify instance type supports Spot
```

## Cost Considerations

### Spot Instance Termination

```yaml
# Spot instances can be terminated with 2-minute notice
# Not suitable for stateful workloads

Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MixedInstancesPolicy:
        InstancesDistribution:
          SpotAllocationStrategy: capacity-optimized
      # Spot instances can be interrupted
```

### Over-Provisioning

```yaml
# Setting minimum capacity too high leads to unnecessary costs
# Use predictive scaling for demand forecasting

Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MinSize: 1  # Avoid over-provisioning
      MaxSize: 10
```

## Best Practices to Avoid Constraints

### Use Multiple Scaling Policies

```yaml
# Combine different scaling strategies for optimal response

Resources:
  CPUPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: cpu-scaling
      AutoScalingGroupName: !Ref AutoScalingGroup
      ScalingAdjustmentType: ChangeInCapacity
      StepAdjustments:
        - MetricIntervalLowerBound: 30
          ScalingAdjustment: -1
        - MetricIntervalUpperBound: 70
          ScalingAdjustment: 1

  NetworkPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: network-scaling
      AutoScalingGroupName: !Ref AutoScalingGroup
      ScalingAdjustmentType: ChangeInCapacity
      StepAdjustments:
        - MetricIntervalLowerBound: 40
          ScalingAdjustment: 1
        - MetricIntervalUpperBound: 80
          ScalingAdjustment: -1
```

### Implement Predictive Scaling

```yaml
# Requires 24 hours of metric data before accurate predictions
# Use for predictable workload patterns

Resources:
  ScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: predictive-scaling
    PolicyType: PredictiveScaling
    AutoScalingGroupName: !Ref AutoScalingGroup
    PredictiveScalingConfiguration:
      MetricSpecification:
        - TargetValue: 1000
          PredefinedMetricSpecification:
            PredefinedMetricType: ASGAverageCPUUtilization
      SchedulingBufferTime: 300
```

### Configure Lifecycle Hooks

```yaml
# Enable graceful shutdown for stateful applications

Resources:
  TerminationHook:
    Type: AWS::AutoScaling::LifecycleHook
    Properties:
      LifecycleHookName: termination-hook
      AutoScalingGroupName: !Ref AutoScalingGroup
      LifecycleTransition: autoscaling:EC2_INSTANCE_TERMINATING
      HeartbeatTimeout: 300
      DefaultResult: CONTINUE
      NotificationTargetARN: !Ref SNSTopic
      RoleARN: !Ref LifecycleHookRole
```

## Quota Management

### Request Quota Increases

```yaml
# Auto Scaling group limits can be increased
# Service-linked roles may be required

Outputs:
  QuotaIncreaseRequest:
    Description: Link to request quota increase
    Value: !Sub "https://console.aws.amazon.com/support/home#/case/create?issueType=service-limit-increase&serviceCode=amazon-autoscaling"
```
