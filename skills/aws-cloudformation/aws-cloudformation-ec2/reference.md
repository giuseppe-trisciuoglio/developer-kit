# AWS CloudFormation EC2 - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for EC2 infrastructure.

## AWS::EC2::Instance

Creates an EC2 instance.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ImageId | String | Yes | The ID of the AMI |
| InstanceType | String | Yes | The instance type (e.g., t3.micro) |
| AvailabilityZone | String | No | The Availability Zone of the instance |
| BlockDeviceMappings | List | No | Block device mappings |
| EbsOptimized | Boolean | No | Whether instance is EBS-optimized |
| IamInstanceProfile | String | No | IAM instance profile name or ARN |
| InstanceId | String | No | For instance updates only |
| KeyName | String | No | Key pair name |
| Monitoring | Boolean | No | Whether detailed monitoring is enabled |
| NetworkInterfaces | List | No | Network interfaces |
| Placement | Placement | No | Placement settings |
| SecurityGroupIds | List | No | Security group IDs |
| SubnetId | String | No | Subnet ID |
| Tags | List of Tag | No | Tags assigned to the instance |
| Tenancy | String | No | Tenancy (default, dedicated, host) |
| UserData | String | No | User data script (base64 encoded) |

### Example

```yaml
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0ff8a95407f89df2f
      InstanceType: t3.micro
      KeyName: my-key-pair
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
      Tags:
        - Key: Name
          Value: my-instance
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| AvailabilityZone | The Availability Zone of the instance |
| PrivateDnsName | The private DNS name |
| PrivateIp | The private IP address |
| PublicDnsName | The public DNS name |
| PublicIp | The public IP address |

## AWS::EC2::SecurityGroup

Creates a security group.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| GroupDescription | String | Yes | A description of the security group |
| GroupName | String | No | The name of the security group |
| SecurityGroupEgress | List | No | Outbound rules |
| SecurityGroupIngress | List | No | Inbound rules |
| Tags | List of Tag | No | Tags assigned to the security group |
| VpcId | String | No | The VPC ID |

### Example

```yaml
Resources:
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2 instance
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16
```

### Security Group Ingress Patterns

```yaml
# Allow HTTP from anywhere
- IpProtocol: tcp
  FromPort: 80
  ToPort: 80
  CidrIp: 0.0.0.0/0

# Allow SSH from specific CIDR
- IpProtocol: tcp
  FromPort: 22
  ToPort: 22
  CidrIp: 10.0.0.0/16

# Allow from another security group
- IpProtocol: tcp
  FromPort: 8080
  ToPort: 8080
  SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup

# Allow all ICMP
- IpProtocol: icmp
  FromPort: -1
  ToPort: -1
  CidrIp: 10.0.0.0/16

# Allow all traffic from security group
- IpProtocol: -1
  SourceSecurityGroupId: !Ref DatabaseSecurityGroup
```

### Security Group Egress Patterns

```yaml
# Allow outbound HTTPS
- IpProtocol: tcp
  FromPort: 443
  ToPort: 443
  CidrIp: 0.0.0.0/0

# Allow all outbound traffic
- IpProtocol: -1
  FromPort: 0
  ToPort: 65535
  CidrIp: 0.0.0.0/0
```

## AWS::IAM::Role

Creates an IAM role.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AssumeRolePolicyDocument | PolicyDocument | Yes | Trust policy document |
| ManagedPolicyArns | List | No | ARNs of managed policies |
| Path | String | No | Path for the role |
| Policies | List | No | Inline policies |
| RoleName | String | No | Name of the role |

### Example

```yaml
Resources:
  Ec2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      Policies:
        - PolicyName: S3Access
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "arn:aws:s3:::my-bucket/*"
```

## AWS::IAM::InstanceProfile

Creates an instance profile.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| InstanceProfileName | String | No | Name of the instance profile |
| Path | String | No | Path for the instance profile |
| Roles | List | Yes | Roles to associate with the profile |

### Example

```yaml
Resources:
  Ec2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref Ec2Role
      InstanceProfileName: my-instance-profile
```

## AWS::ElasticLoadBalancingV2::LoadBalancer

Creates an Application Load Balancer.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | Name of the load balancer |
| Scheme | String | No | internet-facing or internal |
| SecurityGroups | List | No | Security group IDs |
| Subnets | List | Yes | Subnet IDs |
| Type | String | No | load balancer type |
| LoadBalancerAttributes | List | No | Load balancer attributes |

### Example

```yaml
Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: my-alb
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      Type: application
      LoadBalancerAttributes:
        - Key: idle_timeout.timeout_seconds
          Value: "60"
        - Key: deletion_protection.enabled
          Value: "false"
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| DNSName | DNS name of the load balancer |
| CanonicalHostedZoneID | Hosted zone ID |
| LoadBalancerName | Name of the load balancer |

## AWS::ElasticLoadBalancingV2::TargetGroup

Creates a target group for ALB.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | Name of the target group |
| Port | Number | Yes | Port on which targets receive traffic |
| Protocol | String | Yes | Protocol for the target group |
| VpcId | String | Yes | VPC ID |
| HealthCheckIntervalSeconds | Number | No | Health check interval |
| HealthCheckPath | String | No | Health check path |
| HealthCheckPort | String | No | Health check port |
| HealthCheckProtocol | String | No | Health check protocol |
| HealthCheckTimeoutSeconds | Number | No | Health check timeout |
| HealthyThresholdCount | Number | No | Healthy threshold count |
| UnhealthyThresholdCount | Number | No | Unhealthy threshold count |
| TargetType | String | No | Target type (instance, ip, lambda) |
| Targets | List | No | Targets to register |

### Example

```yaml
Resources:
  ApplicationTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: my-tg
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPC
      TargetType: instance
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
```

## AWS::ElasticLoadBalancingV2::Listener

Creates a listener for ALB.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| DefaultActions | List | Yes | Default actions for the listener |
| LoadBalancerArn | String | Yes | ARN of the load balancer |
| Port | Number | Yes | Port on which the load balancer is listening |
| Protocol | String | Yes | Protocol for the listener |
| Certificates | List | No | Certificates for HTTPS |

### Example

```yaml
Resources:
  ApplicationListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref ApplicationTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  HttpsListener:
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
```

## AWS::ElasticLoadBalancingV2::ListenerRule

Creates a listener rule for ALB routing.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Actions | List | Yes | Actions for the rule |
| Conditions | List | Yes | Conditions for the rule |
| ListenerArn | String | Yes | ARN of the listener |
| Priority | Number | Yes | Priority of the rule |

### Example

```yaml
Resources:
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

## AWS::EC2::SpotFleet

Creates a SPOT fleet request.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| SpotFleetRequestConfigData | SpotFleetRequestConfigData | Yes | Configuration for the request |

### SpotFleetRequestConfigData Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AllocationStrategy | String | No | Strategy for allocating SPOT instances |
| IamFleetRole | String | Yes | IAM role for SPOT fleet |
| SpotPrice | String | No | Maximum SPOT price |
| TargetCapacity | Number | Yes | Target capacity |
| TerminateInstancesWithExpiration | Boolean | No | Terminate on expiration |
| Type | String | No | Request type |
| LaunchSpecifications | List | Yes | Launch specifications |

### Example

```yaml
Resources:
  SpotFleet:
    Type: AWS::EC2::SpotFleet
    Properties:
      SpotFleetRequestConfigData:
        TargetCapacity: 10
        IamFleetRole: !GetAtt SpotFleetRole.Arn
        AllocationStrategy: capacityOptimized
        SpotPrice: "0.05"
        Type: request
        LaunchSpecifications:
          - ImageId: !Ref AmiId
            InstanceType: t3.micro
            SubnetId: !Ref SubnetId
```

## AWS::EC2::NetworkInterface

Creates a network interface.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Description | String | No | Description of the network interface |
| GroupSet | List | No | Security group IDs |
| SubnetId | String | Yes | Subnet ID |

### Example

```yaml
Resources:
  NetworkInterface:
    Type: AWS::EC2::NetworkInterface
    Properties:
      SubnetId: !Ref SubnetId
      Description: My network interface
      GroupSet:
        - !Ref SecurityGroup
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| PrimaryPrivateIpAddress | Primary private IP address |
| SecondaryPrivateIpAddresses | Secondary private IP addresses |

## AWS::AutoScaling::LaunchConfiguration

Creates a launch configuration for Auto Scaling.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ImageId | String | Yes | ID of the AMI |
| InstanceType | String | Yes | Instance type |
| AssociatePublicIpAddress | Boolean | No | Associate public IP |
| EbsOptimized | Boolean | No | EBS optimized |
| IamInstanceProfile | String | No | IAM instance profile |
| InstanceMonitoring | Boolean | No | Instance monitoring |
| SecurityGroups | List | No | Security groups |
| UserData | String | No | User data script |

### Example

```yaml
Resources:
  LaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      IamInstanceProfile: !Ref InstanceProfile
      SecurityGroups:
        - !Ref SecurityGroup
```

## AWS::AutoScaling::AutoScalingGroup

Creates an Auto Scaling group.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| LaunchConfigurationName | String | Cond | Launch configuration name |
| LaunchTemplate | LaunchTemplate | Cond | Launch template |
| MaxSize | String | Yes | Maximum size |
| MinSize | String | Yes | Minimum size |
| DesiredCapacity | String | No | Desired capacity |
| VPCZoneIdentifier | List | No | Subnet IDs |
| TargetGroupARNs | List | No | Target group ARNs |
| HealthCheckType | String | No | Health check type (EC2 or ELB) |
| HealthCheckGracePeriod | Number | No | Grace period in seconds |
| TerminationPolicies | List | No | Termination policies |

### Example

```yaml
Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: my-asg
      LaunchConfigurationName: !Ref LaunchConfiguration
      MinSize: "2"
      MaxSize: "10"
      DesiredCapacity: "2"
      VPCZoneIdentifier:
        - !Ref Subnet1
        - !Ref Subnet2
      TargetGroupARNs:
        - !Ref TargetGroupArn
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
```

## AWS::AutoScaling::ScalingPolicy

Creates a scaling policy.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AutoScalingGroupName | String | Yes | Name of ASG |
| PolicyType | String | No | Policy type |
| TargetTrackingConfiguration | TargetTrackingConfiguration | Cond | Target tracking config |
| StepAdjustment | List | No | Step adjustments |

### Example

```yaml
Resources:
  ScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70.0
```

## AWS::CloudWatch::Alarm

Creates a CloudWatch alarm.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AlarmName | String | No | Name of the alarm |
| AlarmDescription | String | No | Description |
| MetricName | String | Yes | Metric name |
| Namespace | String | Yes | Namespace |
| Dimensions | List | No | Dimensions |
| Statistic | String | No | Statistic |
| Period | Number | No | Period in seconds |
| EvaluationPeriods | Number | Yes | Evaluation periods |
| Threshold | Number | Yes | Threshold |
| ComparisonOperator | String | Yes | Comparison operator |
| AlarmActions | List | No | Actions on alarm |
| OKActions | List | No | Actions on OK |

### Example

```yaml
Resources:
  CpuHighAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-cpu-high
      AlarmDescription: CPU utilization exceeds 80%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref Ec2Instance
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SnsTopic
```

## AWS::SNS::Topic

Creates an SNS topic for notifications.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| TopicName | String | No | Name of the topic |

### Example

```yaml
Resources:
  AlarmTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${AWS::StackName}-alarms
```

## Intrinsic Functions Reference

### !Ref

Returns the value of the specified parameter or resource.

```yaml
# Reference a parameter
InstanceType: !Ref InstanceType

# Reference a resource (returns the physical ID)
InstanceId: !Ref Ec2Instance
```

### !GetAtt

Returns the value of an attribute from a resource.

```yaml
# Get public IP
PublicIp: !GetAtt Ec2Instance.PublicIp

# Get role ARN
RoleArn: !GetAtt Ec2Role.Arn

# Get ALB DNS name
DnsName: !GetAtt ApplicationLoadBalancer.DNSName
```

### !Sub

Substitutes variables in an input string with their values.

```yaml
# With variable substitution
Name: !Sub ${AWS::StackName}-instance

# Without variable substitution
Name: !Sub "literal-string"
```

### !Join

Combines a list of values into a single value.

```yaml
# Join with comma
SubnetIds: !Join [",", [!Ref Subnet1, !Ref Subnet2]]
```

### !Select

Returns a single object from a list of objects.

```yaml
# Select first AZ
AvailabilityZone: !Select [0, !GetAZs '']

# Select from list
SubnetId: !Select [0, !Ref SubnetIds]
```

### !FindInMap

Returns the value corresponding to keys in a two-level map.

```yaml
# Find in mapping
ImageId: !FindInMap [RegionMap, !Ref AWS::Region, HVM64]
```

### !If

Returns one value if the specified condition is true and another if false.

```yaml
# Conditional value
SubnetId: !If [IsProduction, !Ref ProdSubnet, !Ref DevSubnet]
```

### !Equals

Compares two values.

```yaml
# Condition
IsProduction: !Equals [!Ref Environment, production]
```

### !ImportValue

Returns the value of an output exported by another stack.

```yaml
# Import value
VpcId: !ImportValue ${NetworkStackName}-VpcId
```

## Instance Types

### Common Instance Types

| Family | Types | Use Case |
|--------|-------|----------|
| t3 | nano, micro, small, medium, large, xlarge | General purpose |
| m5 | large, xlarge, 2xlarge, 4xlarge | General purpose |
| m6i | large, xlarge, 2xlarge, 4xlarge | General purpose |
| c5 | large, xlarge, 2xlarge, 4xlarge | Compute optimized |
| c6i | large, xlarge, 2xlarge, 4xlarge | Compute optimized |
| r5 | large, xlarge, 2xlarge, 4xlarge | Memory optimized |
| r6i | large, xlarge, 2xlarge, 4xlarge | Memory optimized |
| i3 | large, xlarge, 2xlarge, 4xlarge | Storage optimized |
| g4dn | xlarge, 2xlarge, 4xlarge | GPU |

### Burstable Performance Instances

The t3 family provides baseline CPU performance with the ability to burst:

```yaml
Parameters:
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.nano
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large
      - t3.xlarge
      - t3.2xlarge
```

## Common AMI IDs

### Amazon Linux 2 (HVM)

| Region | x86_64 | ARM64 |
|--------|--------|-------|
| us-east-1 | ami-0ff8a95407f89df2f | ami-0a0c776d80e2a1f3c |
| us-west-2 | ami-0a0c776d80e2a1f3c | ami-0a0c776d80e2a1f3c |
| eu-west-1 | ami-0ff8a95407f89df2f | ami-0a0c776d80e2a1f3c |

### Using SSM Parameter

```yaml
Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2
```

## Limits and Quotas

### EC2 Limits

| Resource | Default Limit |
|----------|---------------|
| Instances per region | 20 |
| Volumes per instance | 26 |
| ENIs per instance | Varies by type |
| Security groups per VPC | 500 |
| Rules per security group | 60 inbound + 60 outbound |

### ALB Limits

| Resource | Default Limit |
|----------|---------------|
| Listeners per load balancer | 10 |
| Rules per listener | 25 (default) / 100 (increased) |
| Targets per target group | 1000 |
| Load balancers per region | 50 |

### IAM Limits

| Resource | Default Limit |
|----------|---------------|
| Roles per account | 1000 |
| Instance profiles per account | 500 |
| Policies per account | 1500 |

## Tags Best Practices

### Recommended Tagging Strategy

```yaml
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-instance
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Project
          Value: !Ref ProjectName
        - Key: ManagedBy
          Value: CloudFormation
        - Key: CostCenter
          Value: !Ref CostCenter
        - Key: Owner
          Value: !Ref Owner
```

### Common Tags

| Tag Key | Description | Example Values |
|---------|-------------|----------------|
| Name | Human-readable name | production-web-01 |
| Environment | Deployment environment | development, staging, production |
| Project | Project name | my-project |
| Owner | Team or individual | team@example.com |
| ManagedBy | Managing tool | CloudFormation |
| CostCenter | Budget allocation | 12345 |
| Version | Resource version | 1.0.0 |
| Application | Application name | myapp |

## CloudWatch Metrics for EC2

### Basic Metrics

| Metric | Description |
|--------|-------------|
| CPUUtilization | CPU utilization percentage |
| DiskReadOps | Disk read operations |
| DiskWriteOps | Disk write operations |
| NetworkIn | Network bytes in |
| NetworkOut | Network bytes out |
| StatusCheckFailed | Status check failures |

### Detailed Monitoring Metrics

| Metric | Description |
|--------|-------------|
| CPUCreditUsage | CPU credits used |
| CPUCreditBalance | CPU credits available |
| DiskReadBytes | Bytes read from disk |
| DiskWriteBytes | Bytes written to disk |
| NetworkPacketsIn | Packets in |
| NetworkPacketsOut | Packets out |

## Best Practices Summary

1. **Use SSM parameters** for AMI IDs to get latest patches automatically
2. **Use IAM roles** instead of embedding credentials
3. **Use security groups** for instance-level access control
4. **Use ALB** for distributing traffic to multiple instances
5. **Enable detailed monitoring** for production instances
6. **Use Auto Scaling** for high availability and cost optimization
7. **Tag resources** consistently for cost allocation and management
8. **Use Spot instances** for cost-sensitive, fault-tolerant workloads
9. **Separate concerns** using multiple security groups
10. **Use cross-stack references** for modular architectures
