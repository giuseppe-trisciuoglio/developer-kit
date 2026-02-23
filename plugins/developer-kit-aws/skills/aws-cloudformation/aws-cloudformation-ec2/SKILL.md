---
name: aws-cloudformation-ec2
description: Provides AWS CloudFormation patterns for EC2 instances, Security Groups, IAM roles, and load balancers. Use when creating EC2 instances, SPOT instances, Security Groups, IAM roles for EC2, Application Load Balancers (ALB), Target Groups, and implementing template structure with Parameters, Outputs, Mappings, Conditions, and cross-stack references.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation EC2 Infrastructure

## Overview

Create production-ready EC2 infrastructure using AWS CloudFormation templates. This skill covers EC2 instances (On-Demand and SPOT), Security Groups, IAM roles and instance profiles, Application Load Balancers (ALB), Target Groups, and cross-stack references for modular infrastructure as code.

## When to Use

Use this skill when:
- Creating new EC2 instances (On-Demand or SPOT)
- Configuring Security Groups for network access control
- Creating IAM roles and instance profiles for EC2
- Setting up Application Load Balancers (ALB) with target groups
- Implementing template Parameters with AWS-specific types
- Creating Outputs for cross-stack references
- Organizing templates with Mappings and Conditions

## Instructions

1. **Define Instance Parameters**: Specify instance type (`AWS::EC2::Instance::Type`), AMI ID (`AWS::EC2::Image::Id`), key pair
2. **Configure Security Groups**: Create ingress/egress rules referencing source security groups over CIDRs when possible
3. **Set Up IAM Roles**: Create instance profile with least-privilege policies for AWS service access
4. **Configure EBS Volumes**: Define block device mappings with encryption, IOPS, and volume type
5. **Implement User Data**: Add bootstrap scripts with `Fn::Base64` for initialization
6. **Add ALB Integration**: Create ALB, target group, listener, and health checks
7. **Use Spot Instances**: Configure SpotFleet or LaunchTemplate with spot options for cost savings
8. **Enable Monitoring**: Enable detailed monitoring and CloudWatch agent
9. **Use SSM Parameters**: Reference latest AMI via `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>`
10. **Export Outputs**: Export instance IDs, security group IDs, ALB DNS for cross-stack use

## Best Practices

### Security
- Use IAM roles instead of access keys on instances
- Restrict security group rules to specific CIDRs/security groups
- Encrypt all EBS volumes with KMS
- Use SSM Session Manager instead of SSH
- Enable IMDSv2 (HttpTokens: required)

### Performance
- Use appropriate instance families for workload type
- Enable EBS optimization for I/O-intensive workloads
- Use placement groups for low-latency networking
- Consider Graviton instances for cost-performance

### Cost
- Use Spot instances for fault-tolerant workloads
- Right-size instances based on CloudWatch metrics
- Use Reserved Instances or Savings Plans for steady-state

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: EC2 instance with ALB

Parameters:
  AmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64
  InstanceType:
    Type: String
    Default: t3.micro

Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      IamInstanceProfile: !Ref InstanceProfile
      SecurityGroupIds:
        - !Ref SecurityGroup
      SubnetId: !Ref SubnetId
      MetadataOptions:
        HttpTokens: required
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: 20
            VolumeType: gp3
            Encrypted: true

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: EC2 instance security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref AlbSg

  InstanceRole:
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
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref InstanceRole

Outputs:
  InstanceId:
    Value: !Ref Instance
    Export:
      Name: !Sub "${AWS::StackName}-InstanceId"
```

## Constraints and Warnings

- **Instance Limits**: Default vCPU limits per region vary by instance family
- **EBS Limits**: Max 64 TiB per volume; IOPS limits vary by volume type
- **Security Groups**: Max 5 SGs per ENI; max 60 inbound + 60 outbound rules per SG
- **Spot Instances**: Can be terminated with 2-minute notice; not for stateful workloads
- **User Data**: Max 16 KB; runs only on first boot unless configured otherwise
- **IMDSv2**: Always enable HttpTokens: required to prevent SSRF attacks
- **Key Pairs**: Cannot be created via CloudFormation; must pre-exist

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
