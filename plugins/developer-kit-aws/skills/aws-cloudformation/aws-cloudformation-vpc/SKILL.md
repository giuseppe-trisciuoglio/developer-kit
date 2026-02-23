---
name: aws-cloudformation-vpc
description: Provides AWS CloudFormation patterns for VPC infrastructure. Use when creating VPCs, Subnets, Route Tables, NAT Gateways, Internet Gateways, and implementing template structure with Parameters, Outputs, Mappings, Conditions, and cross-stack references.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation VPC Infrastructure

## Overview

Create production-ready VPC infrastructure using AWS CloudFormation templates. This skill covers VPC components (Subnets, Route Tables, NAT Gateways, Internet Gateways), VPC endpoints, peering, and cross-stack references for modular infrastructure.

## When to Use

Use this skill when:
- Creating new VPCs with public and private subnets
- Configuring route tables for internet and NAT connectivity
- Setting up Internet Gateways and NAT Gateways
- Implementing VPC endpoints for private AWS service access
- Creating VPC peering connections
- Designing reusable, modular CloudFormation templates
- Creating Outputs for cross-stack references

## Instructions

1. **Define VPC Parameters**: Specify CIDR block (e.g., 10.0.0.0/16), enable DNS support and hostnames
2. **Create Subnets**: Configure public and private subnets across at least 2 AZs with non-overlapping CIDRs
3. **Set Up Internet Gateway**: Create IGW and attach to VPC for public subnet internet access
4. **Configure NAT Gateways**: Create NAT GW in each public subnet with Elastic IP for private subnet outbound
5. **Create Route Tables**: Public RT routes 0.0.0.0/0 to IGW; Private RT routes 0.0.0.0/0 to NAT GW
6. **Associate Subnets**: Associate each subnet with appropriate route table
7. **Add VPC Endpoints**: Create Gateway endpoints (S3, DynamoDB) and Interface endpoints (other services)
8. **Configure NACLs**: Add Network ACLs as additional security layer (stateless)
9. **Set Up Flow Logs**: Enable VPC Flow Logs to CloudWatch Logs or S3 for monitoring
10. **Export Outputs**: Export VpcId, SubnetIds, SecurityGroupIds for cross-stack references

## Best Practices

### Design
- Use /16 CIDR for VPC, /24 for subnets (256 addresses minus 5 reserved)
- Create at least 2 AZs for high availability
- Separate public, private, and data subnets
- Plan CIDR blocks to avoid overlap with peered VPCs

### Security
- Use private subnets for databases and application servers
- Public subnets only for ALBs, NAT GWs, and bastion hosts
- Implement VPC endpoints to avoid internet routing for AWS services
- Enable VPC Flow Logs for network auditing
- Use NACLs as defense-in-depth (not primary security)

### Cost
- Use Gateway VPC endpoints (S3, DynamoDB) - free
- Share NAT Gateways across AZs in non-production environments
- Use one NAT GW per AZ in production for HA
- Consider VPC endpoint policies to restrict access

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: VPC with public and private subnets in 2 AZs

Parameters:
  VpcCidr:
    Type: String
    Default: 10.0.0.0/16

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-vpc"

  InternetGateway:
    Type: AWS::EC2::InternetGateway
  IGWAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs ""]
      MapPublicIpOnLaunch: true
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs ""]

  NatEIP:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc
  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatEIP.AllocationId
      SubnetId: !Ref PublicSubnet1

  PublicRT:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
  PublicRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PublicRT
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway
  PublicSubnet1RTA:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRT

  PrivateRT:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
  PrivateRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRT
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway
  PrivateSubnet1RTA:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRT

  S3Endpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPC
      ServiceName: !Sub "com.amazonaws.${AWS::Region}.s3"
      RouteTableIds:
        - !Ref PrivateRT

Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub "${AWS::StackName}-VpcId"
  PrivateSubnets:
    Value: !Ref PrivateSubnet1
    Export:
      Name: !Sub "${AWS::StackName}-PrivateSubnets"
  PublicSubnets:
    Value: !Ref PublicSubnet1
    Export:
      Name: !Sub "${AWS::StackName}-PublicSubnets"
```

## Constraints and Warnings

- **VPC CIDR**: Max /16 (65,536 IPs), min /28 (16 IPs); cannot change after creation
- **Subnets**: 5 IPs reserved per subnet by AWS; max 200 subnets per VPC
- **NAT Gateway**: ~$0.045/hour + data processing charges; single point of failure per AZ
- **VPC Endpoints**: Interface endpoints charge hourly + per GB; Gateway endpoints are free
- **Route Tables**: Max 200 routes per table; only one IGW per VPC
- **Peering**: Non-transitive; max 125 peering connections per VPC; CIDRs cannot overlap
- **Flow Logs**: Cannot modify after creation; add latency to log delivery
- **Elastic IPs**: Max 5 per region (can request increase); charges when not associated

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
