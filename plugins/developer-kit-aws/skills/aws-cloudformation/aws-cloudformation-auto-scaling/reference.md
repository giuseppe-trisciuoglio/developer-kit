# AWS CloudFormation Auto Scaling - Reference

This reference guide contains detailed information about AWS CloudFormation resources for Auto Scaling infrastructure.

## AWS::AutoScaling::AutoScalingGroup

Creates an Auto Scaling group.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AutoScalingGroupName | String | Yes | Name of the Auto Scaling group |
| MinSize | String | Yes | Minimum number of instances |
| MaxSize | String | Yes | Maximum number of instances |
| DesiredCapacity | String | No | Desired number of instances |
| LaunchConfigurationName | String | Cond | Launch configuration name |
| LaunchTemplate | LaunchTemplateSpecification | Cond | Launch template specification |
| MixedInstancesPolicy | MixedInstancesPolicy | No | Mixed instances policy |
| VPCZoneIdentifier | List of String | No | Subnet IDs for the group |
| AvailabilityZones | List of String | No | Availability zones |
| HealthCheckType | String | No | Health check type (EC2, ELB) |
| HealthCheckGracePeriod | Integer | No | Grace period in seconds |
| TerminationPolicies | List of String | No | Termination policy list |
| InstanceMaintenancePolicy | InstanceMaintenancePolicy | No | Instance maintenance policy |
| CapacityRebalance | Boolean | No | Enable capacity rebalance |
| ServiceLinkedRoleARN | String | No | Service-linked role ARN |
| MaxInstanceLifetime | Integer | No | Maximum instance lifetime in seconds |
| NewInstancesProtectedFromScaleIn | Boolean | No | Protect new instances |
| Tags | List of Tag | No | Tags for instances |

### LaunchTemplateSpecification Structure

```yaml
LaunchTemplate:
  LaunchTemplateId: String
  LaunchTemplateName: String
  Version: String
```

### MixedInstancesPolicy Structure

```yaml
MixedInstancesPolicy:
  InstancesDistribution:
    OnDemandAllocationStrategy: String
    OnDemandBaseCapacity: Integer
    OnDemandPercentageAboveBaseCapacity: Integer
    SpotAllocationStrategy: String
    SpotInstancePools: Integer
    SpotMaxPrice: String
  LaunchTemplate:
    LaunchTemplateId: String
    LaunchTemplateName: String
    Version: String
    Overrides:
      - InstanceType: String
        WeightedCapacity: String
```

### InstanceMaintenancePolicy Structure

```yaml
InstanceMaintenancePolicy:
  MinHealthyPercentage: Integer
  MaxHealthyPercentage: Integer
```

### Example

```yaml
Resources:
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg"
      MinSize: "2"
      MaxSize: "10"
      DesiredCapacity: "2"
      VPCZoneIdentifier: !Ref SubnetIds
      LaunchConfigurationName: !Ref MyLaunchConfiguration
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      TerminationPolicies:
        - OldestInstance
        - Default
      Tags:
        - Key: Environment
          Value: !Ref Environment
          PropagateAtLaunch: true
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | ARN of the Auto Scaling group |
| Name | Name of the Auto Scaling group |

## AWS::AutoScaling::LaunchConfiguration

Creates a launch configuration.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| LaunchConfigurationName | String | Yes | Name of the launch configuration |
| ImageId | String | Yes | AMI ID for instances |
| InstanceType | String | Yes | EC2 instance type |
| KeyName | String | No | Key pair name |
| SecurityGroups | List of String | No | Security group IDs |
| InstanceMonitoring | InstanceMonitoring | No | Monitoring configuration |
| SpotPrice | String | No | Spot price |
| UserData | String | No | User data script |
| AssociatePublicIpAddress | Boolean | No | Associate public IP |
| BlockDeviceMappings | List of BlockDeviceMapping | No | Block device mappings |
| EbsOptimized | Boolean | No | Enable EBS optimization |
| IamInstanceProfile | String | No | IAM instance profile |
| KernelId | String | No | Kernel ID |
| RamDiskId | String | No | RAM disk ID |
| SpotMarketOptions | SpotMarketOptions | No | Spot market options |

### InstanceMonitoring Structure

```yaml
InstanceMonitoring:
  Enabled: Boolean
```

### BlockDeviceMapping Structure

```yaml
BlockDeviceMappings:
  - DeviceName: String
    Ebs:
      DeleteOnTermination: Boolean
      Encrypted: Boolean
      Iops: Integer
      SnapshotId: String
      VolumeSize: Integer
      VolumeType: String
    NoDevice: Boolean
    VirtualName: String
```

### SpotMarketOptions Structure

```yaml
SpotMarketOptions:
  SpotPrice: String
  BlockDurationMinutes: Integer
  ValidUntil: String
  InstanceInterruptionBehavior: String
```

### Example

```yaml
Resources:
  MyLaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      LaunchConfigurationName: !Sub "${AWS::StackName}-lc"
      ImageId: !Ref AmiId
      InstanceType: t3.micro
      KeyName: !Ref KeyName
      SecurityGroups:
        - !Ref SecurityGroup
      InstanceMonitoring:
        Enabled: true
      UserData: !Base64 |
        #!/bin/bash
        yum update -y
```

## AWS::EC2::LaunchTemplate

Creates a launch template.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| LaunchTemplateName | String | Yes | Name of the launch template |
| LaunchTemplateData | LaunchTemplateData | Yes | Template data |
| TagSpecifications | List of TagSpecification | No | Tag specifications |

### LaunchTemplateData Structure

```yaml
LaunchTemplateData:
  ImageId: String
  InstanceType: String
  KeyName: String
  SecurityGroupIds: List of String
  SecurityGroups: List of String
  InstanceMarketOptions: InstanceMarketOptions
  Monitoring: Monitoring
  Placement: Placement
  NetworkInterfaces: List of NetworkInterface
  TagSpecifications: List of TagSpecification
  UserData: String
  DisableApiTermination: Boolean
  EbsOptimized: Boolean
  IamInstanceProfile: IamInstanceProfile
  InstanceInitiatedShutdownBehavior: String
  KernelId: String
  RamDiskId: String
```

### Monitoring Structure

```yaml
Monitoring:
  Enabled: Boolean
```

### InstanceMarketOptions Structure

```yaml
InstanceMarketOptions:
  MarketType: String
  SpotOptions:
    SpotPrice: String
    BlockDurationMinutes: Integer
    ValidUntil: String
    InstanceInterruptionBehavior: String
    MaxPrice: String
```

### Example

```yaml
Resources:
  MyLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub "${AWS::StackName}-lt"
      LaunchTemplateData:
        ImageId: !Ref AmiId
        InstanceType: t3.micro
        KeyName: !Ref KeyName
        SecurityGroupIds:
          - !Ref SecurityGroup
        Monitoring:
          Enabled: true
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub "${AWS::StackName}-instance"
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| LatestVersionNumber | Latest version number of the launch template |

## AWS::AutoScaling::ScalingPolicy

Creates a scaling policy.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PolicyName | String | Yes | Name of the scaling policy |
| PolicyType | String | Yes | Policy type |
| AdjustmentType | String | Cond | Adjustment type |
| ScalingAdjustment | Integer | Cond | Scaling adjustment |
| Cooldown | Integer | Cond | Cooldown period |
| MetricAggregationType | String | No | Metric aggregation type |
| StepAdjustments | List of StepAdjustment | No | Step adjustments |
| StepScalingPolicyConfiguration | StepScalingPolicyConfiguration | Cond | Step scaling config |
| TargetTrackingConfiguration | TargetTrackingConfiguration | Cond | Target tracking config |
| AutoScalingGroupName | String | Yes | ASG name |

### Policy Types

| Type | Description |
|------|-------------|
| SimpleScaling | Simple scaling policy |
| StepScaling | Step scaling policy |
| TargetTrackingScaling | Target tracking scaling policy |

### Adjustment Types

| Type | Description |
|------|-------------|
| ChangeInCapacity | Change in capacity |
| PercentChangeInCapacity | Percentage change in capacity |
| ExactCapacity | Exact capacity |

### StepAdjustment Structure

```yaml
StepAdjustments:
  - MetricIntervalLowerBound: Double
    MetricIntervalUpperBound: Double
    ScalingAdjustment: Integer
```

### TargetTrackingConfiguration Structure

```yaml
TargetTrackingConfiguration:
  PredefinedMetricSpecification: PredefinedMetricSpecification
  CustomizedMetricSpecification: MetricSpecification
  TargetValue: Double
  DisableScaleIn: Boolean
  ScaleInCooldown: Integer
  ScaleOutCooldown: Integer
```

### PredefinedMetricSpecification Structure

```yaml
PredefinedMetricSpecification:
  PredefinedMetricType: String
  ResourceLabel: String
```

### Predefined Metric Types

| Type | Description |
|------|-------------|
| ASGAverageCPUUtilization | ASG average CPU utilization |
| ASGAverageNetworkIn | ASG average network in |
| ASGAverageNetworkOut | ASG average network out |
| ALBRequestCountPerTarget | ALB request count per target |

### Example

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

  StepScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-step-scaling"
      PolicyType: StepScaling
      AdjustmentType: PercentChangeInCapacity
      Cooldown: 300
      StepAdjustments:
        - MetricIntervalLowerBound: 0
          MetricIntervalUpperBound: 10000
          ScalingAdjustment: 200
      AutoScalingGroupName: !Ref MyAutoScalingGroup
```

## AWS::AutoScaling::LifecycleHook

Creates a lifecycle hook.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| LifecycleHookName | String | Yes | Name of the lifecycle hook |
| AutoScalingGroupName | String | Yes | ASG name |
| LifecycleTransition | String | Yes | Lifecycle transition |
| HeartbeatTimeout | Integer | No | Heartbeat timeout in seconds |
| NotificationTargetARN | String | No | SNS topic ARN |
| RoleARN | String | No | IAM role ARN |
| DefaultResult | String | No | Default result (CONTINUE, ABANDON) |

### Lifecycle Transitions

| Transition | Description |
|------------|-------------|
| autoscaling:EC2_INSTANCE_LAUNCHING | Instance is launching |
| autoscaling:EC2_INSTANCE_TERMINATING | Instance is terminating |

### Example

```yaml
Resources:
  LifecycleHookLaunch:
    Type: AWS::AutoScaling::LifecycleHook
    Properties:
      LifecycleHookName: !Sub "${AWS::StackName}-launch-hook"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      LifecycleTransition: autoscaling:EC2_INSTANCE_LAUNCHING
      HeartbeatTimeout: 900
      NotificationTargetARN: !Ref SnsTopic
      RoleARN: !GetAtt LifecycleRole.Arn
```

## AWS::AutoScaling::ScheduledAction

Creates a scheduled action.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ScheduledActionName | String | Yes | Name of the scheduled action |
| AutoScalingGroupName | String | Yes | ASG name |
| MinSize | String | No | Minimum size |
| MaxSize | String | No | Maximum size |
| DesiredCapacity | String | No | Desired capacity |
| StartTime | String | No | Start time (ISO 8601) |
| EndTime | String | No | End time (ISO 8601) |
| Recurrence | String | No | Recurrence (cron expression) |

### Example

```yaml
Resources:
  ScheduledScaleUp:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      ScheduledActionName: !Sub "${AWS::StackName}-morning-scale-up"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      MinSize: "5"
      MaxSize: "15"
      DesiredCapacity: "5"
      Recurrence: "0 8 * * *"
```

## AWS::ApplicationAutoScaling::ScalableTarget

Creates a scalable target for Application Auto Scaling.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| MaxCapacity | Integer | Yes | Maximum capacity |
| MinCapacity | Integer | Yes | Minimum capacity |
| ResourceId | String | Yes | Resource identifier |
| RoleARN | String | Yes | IAM role ARN |
| ScalableDimension | String | Yes | Scalable dimension |
| ServiceNamespace | String | Yes | Service namespace |

### Scalable Dimensions

| Dimension | Description |
|-----------|-------------|
| ecs:service:DesiredCount | ECS service desired count |
| ec2:spot-fleet-request:TargetCapacity | Spot fleet target capacity |
| dynamodb:table:ReadCapacityUnits | DynamoDB read capacity |
| dynamodb:table:WriteCapacityUnits | DynamoDB write capacity |
| dynamodb:index:ReadCapacityUnits | DynamoDB index read capacity |
| dynamodb:index:WriteCapacityUnits | DynamoDB index write capacity |
| lambda:function:ProvisionedConcurrency | Lambda provisioned concurrency |

### Service Namespaces

| Namespace | Service |
|-----------|---------|
| ecs | ECS |
| ec2 | EC2 |
| dynamodb | DynamoDB |
| lambda | Lambda |
| comprehend | Comprehend |

### Resource ID Formats

| Service | Resource ID Format |
|---------|-------------------|
| ECS | service/cluster-name/service-name |
| Lambda | function:function-name:version-or-alias |
| DynamoDB | table/table-name |
| DynamoDB Index | table/table-name/index/index-name |

### Example

```yaml
Resources:
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 10
      MinCapacity: 2
      ResourceId: !Sub "service/${EcsCluster}/${EcsService}"
      RoleARN: !GetAtt ScalingRole.Arn
      ScalableDimension: ecs:service:DesiredCount
      ServiceNamespace: ecs
```

## AWS::ApplicationAutoScaling::ScalingPolicy

Creates a scaling policy for Application Auto Scaling.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PolicyName | String | Yes | Name of the scaling policy |
| PolicyType | String | Yes | Policy type |
| ScalingTargetId | String | Yes | Scalable target ID |
| TargetTrackingScalingPolicyConfiguration | TargetTrackingScalingPolicyConfiguration | Cond | Target tracking config |
| StepScalingPolicyConfiguration | StepScalingPolicyConfiguration | Cond | Step scaling config |

### Example

```yaml
Resources:
  TargetTrackingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-target-tracking"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 70
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization
        ScaleInCooldown: 300
        ScaleOutCooldown: 60
```

## CloudWatch Metrics Reference

### Auto Scaling Metrics

| Metric | Description | Statistics |
|--------|-------------|------------|
| GroupMinSize | Minimum size of the group | Average, Maximum, Minimum |
| GroupMaxSize | Maximum size of the group | Average, Maximum, Minimum |
| GroupDesiredCapacity | Desired capacity of the group | Average, Maximum, Minimum |
| GroupInServiceInstances | Instances in service | Average, Maximum, Minimum |
| GroupPendingInstances | Instances pending | Average, Maximum, Minimum |
| GroupTerminatingInstances | Instances terminating | Average, Maximum, Minimum |
| GroupTotalInstances | Total instances | Average, Maximum, Minimum |

### EC2 Instance Metrics

| Metric | Description | Statistics |
|--------|-------------|------------|
| CPUUtilization | CPU utilization percentage | Average, Maximum, Minimum |
| NetworkIn | Network bytes received | Sum |
| NetworkOut | Network bytes sent | Sum |
| DiskReadOps | Disk read operations | Sum |
| DiskWriteOps | Disk write operations | Sum |
| DiskReadBytes | Disk read bytes | Sum |
| DiskWriteBytes | Disk write bytes | Sum |

### ALB Metrics

| Metric | Description | Statistics |
|--------|-------------|------------|
| RequestCount | Number of requests | Sum |
| TargetResponseTime | Target response time | Average |
| UnHealthyHostCount | Unhealthy target count | Average |
| HealthyHostCount | Healthy target count | Average |

## IAM Policy Examples

### Auto Scaling Service-Linked Role

```yaml
Resources:
  AutoScalingRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-asg-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: autoscaling.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AutoScalingServiceRolePolicy
```

### Custom Auto Scaling Policy

```yaml
Resources:
  CustomScalingRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-custom-scaling"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: application-autoscaling.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-scaling-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - autoscaling:DescribeAutoScalingGroups
                  - autoscaling:DescribeScalingActivities
                  - autoscaling:DescribeScheduledActions
                Resource: "*"
              - Effect: Allow
                Action:
                  - autoscaling:SetDesiredCapacity
                  - autoscaling:TerminateInstanceInAutoScalingGroup
                Resource: !Ref AutoScalingGroupArn
```

## Limits and Quotas

### Auto Scaling Limits

| Resource | Default Limit |
|----------|---------------|
| Auto Scaling groups per region | 200 |
| Launch configurations per region | 200 |
| Scaling policies per Auto Scaling group | 50 |
| Scheduled actions per Auto Scaling group | 125 |
| Lifecycle hooks per Auto Scaling group | 50 |

### Instance Limits

| Resource | Default Limit |
|----------|---------------|
| Instances per Auto Scaling group | 1000 |
| Spot instance pools | 20 |
| Max Spot price | On-demand price |

### Application Auto Scaling Limits

| Resource | Default Limit |
|----------|---------------|
| Scalable targets per region | 200 |
| Scalable targets per service namespace | 50 |

## Common Tags for Auto Scaling

```yaml
Resources:
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      Tags:
        - Key: Environment
          Value: !Ref Environment
          PropagateAtLaunch: true
        - Key: Project
          Value: !Ref ProjectName
          PropagateAtLaunch: true
        - Key: Owner
          Value: team@example.com
          PropagateAtLaunch: true
        - Key: ManagedBy
          Value: CloudFormation
          PropagateAtLaunch: true
        - Key: CostCenter
          Value: "12345"
          PropagateAtLaunch: true
        - Key: Version
          Value: "1.0.0"
          PropagateAtLaunch: true
```
