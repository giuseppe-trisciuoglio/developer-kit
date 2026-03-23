# CloudFormation EC2 Constraints and Warnings

## Resource Limits

- **Instance Limits**: Maximum number of EC2 instances per region varies by account
- **ENI Limits**: Each instance type has maximum ENI limits
- **Security Groups**: Maximum 500 security groups per VPC
- **EBS Volumes**: Maximum number of EBS volumes per account is 20 by default

## Instance Constraints

- **Instance Type Availability**: Not all instance types available in all regions/AZs
- **Instance Replacement**: Changing instance type requires instance replacement
- **Tenancy Changes**: Changing between default and dedicated tenancy requires replacement
- **Host Resource Group**: Dedicated Hosts have specific allocation and utilization constraints

## Storage Constraints

- **EBS Volume Limits**: EBS volume size varies by volume type (gp3 up to 16 TB)
- **IOPS Limits**: Provisioned IOPS (io1/io2) has specific IOPS per GB limits
- **Snapshot Costs**: EBS snapshots incur storage costs even after source volume deletion
- **Throughput**: Volume throughput limits vary by volume type and size

## Network Constraints

- **ENI Limits**: Each instance type has maximum ENI and IP address per ENI limits
- **Public IP Assignment**: Public IP addresses are released on instance stop
- **Elastic IP Limits**: Each account has limited number of Elastic IPs
- **Security Group Rules**: Maximum 60 inbound and 60 outbound rules per security group

## Security Constraints

- **Key Pairs**: Key pairs cannot be recovered if lost; instance access lost
- **IAM Roles**: Instance profile roles cannot be changed after instance creation
- **Password Authentication**: Password authentication for EC2 is disabled by default; use key pairs
- **Metadata Service**: IMDSv2 should be enabled; IMDSv1 has security vulnerabilities

## Cost Considerations

- **Instance Costs**: Instances incur costs while running; stopped instances may still incur EBS costs
- **EBS Costs**: EBS volumes incur costs per GB-month even if not attached
- **Data Transfer**: Data transfer out to internet incurs significant costs
- **Load Balancer Costs**: ALBs/ELBs/NLBs incur hourly and per-GB data processing costs
- **Elastic IP**: Unattached Elastic IPs incur small hourly costs

## Availability Constraints

- **Spot Instances**: Spot instances can be terminated with 2-minute notice
- **Reserved Instances**: Reserved instances require commitment and have specific term limits
- **Availability Zones**: Not all instance types available in all AZs
- **Capacity Limits**: On-Demand capacity limits may prevent launching instances during high demand

## CloudFormation-Specific Constraints

- **Stack Size**: Maximum 500 resources per stack
- **Template Size**: Maximum 51,200 bytes for templates uploaded directly to CloudFormation
- **Parameter Limits**: Maximum 200 parameters per template
- **Mapping Limits**: Maximum 100 mappings per template
- **Output Limits**: Maximum 60 outputs per template
- **Resource Naming**: Some resources require unique names within an account/region

## Troubleshooting Common Issues

### Instance Launch Failures

- **Invalid AMI ID**: Verify AMI exists in the target region
- **Insufficient Capacity**: Try different instance type or AZ
- **Security Group Rules**: Ensure necessary ports are open
- **Key Pair Missing**: Verify key pair exists in the region
- **IAM Permissions**: Check EC2 role has required permissions

### Network Connectivity Issues

- **Subnet Configuration**: Verify subnet has route to internet gateway
- **Security Group Ingress**: Check inbound rules allow required traffic
- **Network ACLs**: Ensure NACLs allow traffic
- **Public IP Assignment**: Verify subnet has `MapPublicIpOnLaunch` enabled

### Stack Update Failures

- **Resource Conflicts**: Check for name collisions with existing resources
- **Dependency Issues**: Verify all referenced resources exist
- **IAM Permissions**: Ensure CloudFormation has necessary permissions
- **Rollback Configuration**: Consider disabling rollback for debugging

## Best Practices for Avoiding Constraints

### Capacity Planning

```yaml
# Use multiple instance types for Spot Fleet
LaunchSpecifications:
  - InstanceType: t3.micro
    ImageId: !Ref AmiId
    WeightedCapacity: 1
  - InstanceType: t3.small
    ImageId: !Ref AmiId
    WeightedCapacity: 2
  - InstanceType: t3a.micro
    ImageId: !Ref AmiId
    WeightedCapacity: 1
```

### Multi-AZ Deployment

```yaml
# Deploy instances across multiple AZs
Resources:
  Instance1:
    Type: AWS::EC2::Instance
    Properties:
      AvailabilityZone: !Select [0, !GetAZs '']
      SubnetId: !Ref Subnet1

  Instance2:
    Type: AWS::EC2::Instance
    Properties:
      AvailabilityZone: !Select [1, !GetAZs '']
      SubnetId: !Ref Subnet2
```

### Cost Optimization

```yaml
# Use Spot Instances for non-critical workloads
Parameters:
  UseSpotInstances:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false

Conditions:
  UseSpot: !Equals [!Ref UseSpotInstances, true]

Resources:
  SpotInstance:
    Type: AWS::EC2::SpotFleet
    Condition: UseSpot
    Properties:
      SpotFleetRequestConfigData:
        AllocationStrategy: capacity-optimized
```

### Security Hardening

```yaml
# Enable IMDSv2 for enhanced security
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      MetadataOptions:
        HttpTokens: required
        HttpPutResponseHopLimit: 1
        HttpEndpoint: enabled
```

## Monitoring and Alerts

Set up CloudWatch alarms for critical metrics:

```yaml
# CPU Utilization Alarm
CPUAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmDescription: Alarm if CPU > 90%
    MetricName: CPUUtilization
    Namespace: AWS/EC2
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 90
    ComparisonOperator: GreaterThanThreshold

# Status Check Alarm
StatusCheckAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmDescription: Alarm for instance status checks
    MetricName: StatusCheckFailed
    Namespace: AWS/EC2
    Statistic: Average
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
```
