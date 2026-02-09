# AWS CloudFormation VPC - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for VPC infrastructure.

## AWS::EC2::VPC

Creates an Amazon Virtual Private Cloud (VPC).

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CidrBlock | String | Yes | The IPv4 CIDR block for the VPC |
| EnableDnsHostnames | Boolean | No | Indicates whether instances launched in the VPC get DNS hostnames |
| EnableDnsSupport | Boolean | No | Indicates whether DNS resolution is supported in the VPC |
| InstanceTenancy | String | No | The tenancy options for instances launched into the VPC (default, dedicated, host) |
| Tags | List of Tag | No | Tags assigned to the VPC |

### Example

```yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      InstanceTenancy: default
      Tags:
        - Key: Name
          Value: my-vpc
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| CidrBlock | The CIDR block of the VPC |
| DefaultSecurityGroup | The default security group ID |
| Id | The VPC ID |

## AWS::EC2::Subnet

Creates a subnet in the specified VPC.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AvailabilityZone | String | Yes | The Availability Zone of the subnet |
| CidrBlock | String | Yes | The IPv4 CIDR block for the subnet |
| MapPublicIpOnLaunch | Boolean | No | Whether instances launched in this subnet receive a public IP |
| Tags | List of Tag | No | Tags assigned to the subnet |
| VpcId | String | Yes | The ID of the VPC |

### Example

```yaml
Resources:
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: public-subnet
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| AvailabilityZone | The Availability Zone of the subnet |
| CidrBlock | The CIDR block of the subnet |
| Id | The subnet ID |

## AWS::EC2::InternetGateway

Creates an internet gateway for use with a VPC.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Tags | List of Tag | No | Tags assigned to the internet gateway |

### Example

```yaml
Resources:
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: my-igw
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | The internet gateway ID |

## AWS::EC2::VPCGatewayAttachment

Attaches an internet gateway or a virtual private gateway to a VPC.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| InternetGatewayId | String | Cond | The ID of the internet gateway (use InternetGatewayId OR VpnGatewayId) |
| VpcId | String | Yes | The ID of the VPC |
| VpnGatewayId | String | Cond | The ID of the virtual private gateway |

### Example

```yaml
Resources:
  VPCGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway
```

## AWS::EC2::NatGateway

Creates a NAT gateway in the specified subnet.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AllocationId | String | Yes | The allocation ID of an Elastic IP address to associate with the NAT gateway |
| SubnetId | String | Yes | The subnet in which to create the NAT gateway |
| Tags | List of Tag | No | Tags assigned to the NAT gateway |

### Example

```yaml
Resources:
  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt EIP.AllocationId
      SubnetId: !Ref PublicSubnet
      Tags:
        - Key: Name
          Value: my-nat-gw
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | The NAT gateway ID |

## AWS::EC2::EIP

Allocates an Elastic IP address and associates it with an instance or network interface.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Domain | String | No | Indicates whether the EIP is for use in EC2-Classic or in a VPC (vpc or standard) |
| InstanceId | String | No | The ID of the instance |
| NetworkInterfaceId | String | No | The ID of the network interface |

### Example

```yaml
Resources:
  NatGatewayEIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: nat-gw-eip
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| AllocationId | The allocation ID of the Elastic IP address |
| PublicIp | The public IP address |

## AWS::EC2::RouteTable

Creates a route table for the specified VPC.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Tags | List of Tag | No | Tags assigned to the route table |
| VpcId | String | Yes | The ID of the VPC |

### Example

```yaml
Resources:
  RouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: my-route-table
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | The route table ID |

## AWS::EC2::Route

Creates a route in a route table within a VPC.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| DestinationCidrBlock | String | Cond | The IPv4 CIDR address block used for the destination match |
| DestinationIpv6CidrBlock | String | Cond | The IPv6 CIDR address block used for the destination match |
| EgressOnlyInternetGatewayId | String | Cond | The ID of the egress-only internet gateway |
| GatewayId | String | Cond | The ID of the internet gateway or virtual private gateway |
| InstanceId | String | Cond | The ID of the instance |
| NatGatewayId | String | Cond | The ID of the NAT gateway |
| NetworkInterfaceId | String | Cond | The ID of the network interface |
| RouteTableId | String | Yes | The ID of the route table |
| VpcPeeringConnectionId | String | Cond | The ID of a VPC peering connection |

### Example

```yaml
Resources:
  DefaultRoute:
    Type: AWS::EC2::Route
    DependsOn: VPCGatewayAttachment
    Properties:
      RouteTableId: !Ref RouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway
```

## AWS::EC2::SubnetRouteTableAssociation

Associates a subnet with a route table.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| RouteTableId | String | Yes | The ID of the route table |
| SubnetId | String | Yes | The ID of the subnet |

### Example

```yaml
Resources:
  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref RouteTable
      SubnetId: !Ref Subnet
```

## AWS::EC2::SecurityGroup

Creates a security group.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| GroupDescription | String | Yes | A description of the security group |
| GroupName | String | No | The name of the security group |
| SecurityGroupEgress | List of IpPermission | No | Outbound rules for the security group |
| SecurityGroupIngress | List of IpPermission | No | Inbound rules for the security group |
| Tags | List of Tag | No | Tags assigned to the security group |
| VpcId | String | No | The ID of the VPC |

### Example

```yaml
Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: My security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: my-sg
```

### Security Group Ingress Example

```yaml
Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group with various rules
      VpcId: !Ref VPC
      SecurityGroupIngress:
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
        # Allow PostgreSQL from security group
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref OtherSecurityGroup
        # Allow all ICMP
        - IpProtocol: icmp
          FromPort: -1
          ToPort: -1
          CidrIp: 10.0.0.0/16
```

## AWS::EC2::VPCEndpoint

Creates a VPC endpoint.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PrivateDnsEnabled | Boolean | No | Indicates whether to associate a private hosted zone with the specified VPC |
| RouteTableIds | List of String | Cond | The IDs of the route tables for the endpoint (Gateway endpoint only) |
| SecurityGroupIds | List of String | Cond | The IDs of the security groups for the endpoint (Interface endpoint only) |
| ServiceName | String | Yes | The service name |
| SubnetIds | List of String | Cond | The IDs of the subnets for the endpoint (Interface endpoint only) |
| VpcEndpointType | String | No | The type of endpoint (Interface or Gateway) |
| VpcId | String | Yes | The ID of the VPC |

### Example - Gateway Endpoint

```yaml
Resources:
  S3GatewayEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPC
      ServiceName: !Sub com.amazonaws.${AWS::Region}.s3
      RouteTableIds:
        - !Ref PrivateRouteTable
```

### Example - Interface Endpoint

```yaml
Resources:
  SecretsManagerEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPC
      ServiceName: !Sub com.amazonaws.${AWS::Region}.secretsmanager
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      PrivateDnsEnabled: true
```

## AWS::EC2::VPCPeeringConnection

Creates a VPC peering connection between two VPCs.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PeerVpcId | String | Yes | The ID of the VPC with which you are creating the peering connection |
| PeerOwnerId | String | No | The AWS account ID of the owner of the peer VPC |
| PeerRegion | String | No | The region of the peer VPC (required for cross-region peering) |
| Tags | List of Tag | No | Tags assigned to the VPC peering connection |
| VpcId | String | Yes | The ID of the requester VPC |

### Example

```yaml
Resources:
  VPCPeeringConnection:
    Type: AWS::EC2::VPCPeeringConnection
    Properties:
      VpcId: !Ref VPC
      PeerVpcId: !Ref PeerVpcId
      PeerOwnerId: !Ref PeerOwnerId
      Tags:
        - Key: Name
          Value: peering-connection
```

## AWS::EC2::NetworkAcl

Creates a network ACL in a VPC.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Tags | List of Tag | No | Tags assigned to the network ACL |
| VpcId | String | Yes | The ID of the VPC |

### Example

```yaml
Resources:
  NetworkAcl:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: my-nacl
```

## AWS::EC2::NetworkAclEntry

Creates an entry in a network ACL.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CidrBlock | String | Cond | The IPv4 CIDR range for the rule (use CidrBlock OR Ipv6CidrBlock) |
| Egress | Boolean | No | Whether this rule applies to egress traffic |
| Ipv6CidrBlock | String | Cond | The IPv6 CIDR range for the rule |
| NetworkAclId | String | Yes | The ID of the network ACL |
| PortRange | PortRange | Cond | The port range for the rule (TCP/UDP protocols only) |
| Protocol | Integer | Yes | The protocol number (-1 for all) |
| RuleAction | String | Yes | Whether to allow or deny traffic (allow or deny) |
| RuleNumber | Integer | Yes | The rule number (1-32766) |

### Example

```yaml
Resources:
  NetworkAclEntry:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref NetworkAcl
      RuleNumber: 100
      Protocol: 6
      RuleAction: allow
      CidrBlock: 0.0.0.0/0
      PortRange:
        From: 80
        To: 443
```

## AWS::EC2::CustomerGateway

Creates a customer gateway.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| BgpAsn | Integer | Yes | The customer gateway's Border Gateway Protocol (BGP) Autonomous System Number |
| IpAddress | String | Yes | The customer gateway's IP address |
| Tags | List of Tag | No | Tags assigned to the customer gateway |
| Type | String | Yes | The type of customer gateway (ipsec.1) |

### Example

```yaml
Resources:
  CustomerGateway:
    Type: AWS::EC2::CustomerGateway
    Properties:
      BgpAsn: 65001
      IpAddress: 203.0.113.1
      Type: ipsec.1
      Tags:
        - Key: Name
          Value: my-cgw
```

## AWS::EC2::VPNGateway

Creates a virtual private gateway.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Tags | List of Tag | No | Tags assigned to the virtual private gateway |
| Type | String | Yes | The type of VPN gateway (ipsec.1) |

### Example

```yaml
Resources:
  VPNGateway:
    Type: AWS::EC2::VPNGateway
    Properties:
      Type: ipsec.1
      Tags:
        - Key: Name
          Value: my-vpn-gw
```

## AWS::EC2::VPNConnection

Creates a VPN connection between a virtual private gateway and a customer gateway.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CustomerGatewayId | String | Yes | The ID of the customer gateway |
| StaticRoutesOnly | Boolean | No | Whether to use static routes only |
| Tags | List of Tag | No | Tags assigned to the VPN connection |
| Type | String | Yes | The type of VPN connection (ipsec.1) |
| VpnGatewayId | String | Yes | The ID of the virtual private gateway |

### Example

```yaml
Resources:
  VPNConnection:
    Type: AWS::EC2::VPNConnection
    Properties:
      CustomerGatewayId: !Ref CustomerGateway
      VpnGatewayId: !Ref VPNGateway
      Type: ipsec.1
      StaticRoutesOnly: true
      Tags:
        - Key: Name
          Value: my-vpn
```

## AWS::EC2::FlowLog

Creates a flow log for a VPC, subnet, or network interface.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| DeliverLogsPermissionArn | String | Cond | The ARN of the IAM role that permits AWS to publish flow logs |
| LogDestinationType | String | No | The type of log destination (cloud-watch-logs, s3, kinesis-data-firehose) |
| LogGroupName | String | Cond | The name of the log group for CloudWatch Logs |
| LogDestination | String | Cond | The destination for the log data (S3 bucket or Kinesis Data Firehose ARN) |
| ResourceId | String | Yes | The ID of the subnet, VPC, or network interface |
| ResourceType | String | Yes | The type of resource (VPC, Subnet, NetworkInterface) |
| TrafficType | String | Yes | The type of traffic to log (ACCEPT, REJECT, ALL) |

### Example - CloudWatch Logs

```yaml
Resources:
  FlowLogsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: vpc-flow-logs.amazonaws.com
            Action: sts:AssumeRole

  FlowLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/vpc/flow-logs

  FlowLog:
    Type: AWS::EC2::FlowLog
    Properties:
      ResourceId: !Ref VPC
      ResourceType: VPC
      TrafficType: ALL
      LogDestinationType: cloud-watch-logs
      LogGroupName: !Ref FlowLogGroup
      DeliverLogsPermissionArn: !GetAtt FlowLogsRole.Arn
```

## Intrinsic Functions Reference

### !Ref

Returns the value of the specified parameter or resource.

```yaml
# Reference a parameter
VpcId: !Ref VPCId

# Reference a resource (returns the physical ID)
VpcId: !Ref VPC
```

### !GetAtt

Returns the value of an attribute from a resource.

```yaml
# Get the allocation ID from an EIP
AllocationId: !GetAtt EIP.AllocationId

# Get the CIDR block from a VPC
CidrBlock: !GetAtt VPC.CidrBlock
```

### !Sub

Substitutes variables in an input string with their values.

```yaml
# With variable substitution
Name: !Sub ${AWS::StackName}-vpc

# Without variable substitution
Name: !Sub "literal-string"
```

### !Join

Combines a list of values into a single value.

```yaml
# Join with comma
SubnetIds: !Join [",", [!Ref Subnet1, !Ref Subnet2, !Ref Subnet3]]
```

### !Select

Returns a single object from a list of objects.

```yaml
# Select first AZ
AvailabilityZone: !Select [0, !GetAZs '']

# Select specific subnet CIDR
CidrBlock: !Select [0, !Ref SubnetCidrs]
```

### !FindInMap

Returns the value corresponding to keys in a two-level map.

```yaml
# Find in mapping
ImageId: !FindInMap [RegionMap, !Ref AWS::Region, HVM64]
```

### !If

Returns one value if the specified condition is true and another value if the condition is false.

```yaml
# Conditional value
SubnetId: !If [IsProduction, !Ref ProdSubnet, !Ref DevSubnet]
```

### !Equals

Compares two values and returns true if the values are equal.

```yaml
# Condition
IsProduction: !Equals [!Ref Environment, production]
```

### !And

Returns true if all specified conditions are true.

```yaml
# Multiple conditions
ShouldDeploy: !And [!Condition UseNat, !Condition IsProduction]
```

### !Or

Returns true if any specified condition is true.

```yaml
# Any condition
ShouldDeploy: !Or [!Condition IsProduction, !Condition UseNat]
```

### !Not

Returns true if the specified condition is false.

```yaml
# Negation
NotDevelopment: !Not [!Equals [!Ref Environment, development]]
```

### !ImportValue

Returns the value of an output exported by another stack.

```yaml
# Import value
VpcId: !ImportValue ${NetworkStackName}-VpcId
```

### !GetAZs

Returns a list of Availability Zones for the specified region.

```yaml
# Get all AZs in current region
AvailabilityZones: !GetAZs ''
```

## Common CIDR Blocks

### Private IPv4 Address Ranges

| CIDR Block | Range | Typical Use |
|------------|-------|-------------|
| 10.0.0.0/8 | 10.0.0.0 - 10.255.255.255 | Large private networks |
| 172.16.0.0/12 | 172.16.0.0 - 172.31.255.255 | Medium private networks |
| 192.168.0.0/16 | 192.168.0.0 - 192.168.255.255 | Small private networks |

### Recommended VPC CIDR Blocks

| VPC Size | CIDR Block | Usable IPs |
|----------|------------|------------|
| /16 | 10.0.0.0/16 | 65,536 |
| /17 | 10.0.0.0/17 | 32,768 |
| /18 | 10.0.0.0/18 | 16,384 |
| /19 | 10.0.0.0/19 | 8,192 |
| /20 | 10.0.0.0/20 | 4,096 |
| /21 | 10.0.0.0/21 | 2,048 |
| /22 | 10.0.0.0/22 | 1,024 |
| /24 | 10.0.0.0/24 | 256 |

### Subnet sizing for 10.0.0.0/16 VPC

| Subnet Type | CIDR Block | Size | Usable IPs |
|-------------|------------|------|------------|
| Public | 10.0.1.0/24 | /24 | 251 |
| Private | 10.0.10.0/24 | /24 | 251 |
| Public | 10.0.2.0/24 | /24 | 251 |
| Private | 10.0.11.0/24 | /24 | 251 |
| Public | 10.0.3.0/24 | /24 | 251 |
| Private | 10.0.12.0/24 | /24 | 251 |

## AWS Service Endpoints

### Common S3 Gateway Endpoints

| Region | Service Name |
|--------|--------------|
| us-east-1 | com.amazonaws.us-east-1.s3 |
| us-west-2 | com.amazonaws.us-west-2.s3 |
| eu-west-1 | com.amazonaws.eu-west-1.s3 |

### Common Interface Endpoints

| Service | Service Name Pattern |
|---------|---------------------|
| Secrets Manager | com.amazonaws.{region}.secretsmanager |
| SSM | com.amazonaws.{region}.ssm |
| CloudWatch Logs | com.amazonaws.{region}.logs |
| ECR API | com.amazonaws.{region}.ecr.api |
| ECR DKR | com.amazonaws.{region}.ecr.dkr |
| SQS | com.amazonaws.{region}.sqs |
| SNS | com.amazonaws.{region}.sns |

## Limits and Quotas

### VPC Limits

| Resource | Default Limit |
|----------|---------------|
| VPCs per region | 5 |
| Subnets per VPC | 200 |
| Route tables per VPC | 200 |
| Routes per route table | 50 |
| Security groups per VPC | 500 |
| Rules per security group | 60 (inbound) + 60 (outbound) |
| Network ACLs per VPC | 200 |
| Entries per network ACL | 20 (inbound) + 20 (outbound) |
| Internet gateways per region | 5 |
| NAT gateways per AZ | 5 |
| VPC peering connections per VPC | 50 |

## Tags Best Practices

### Recommended Tagging Strategy

```yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Project
          Value: !Ref ProjectName
        - Key: ManagedBy
          Value: CloudFormation
        - Key: CostCenter
          Value: !Ref CostCenter
```

### Common Tags

| Tag Key | Description | Example Values |
|---------|-------------|----------------|
| Name | Human-readable resource name | production-vpc |
| Environment | Deployment environment | development, staging, production |
| Project | Project name | my-project |
| Owner | Team or individual responsible | team@example.com |
| ManagedBy | Tool that manages the resource | CloudFormation |
| CostCenter | Budget allocation | 12345 |
| Version | Resource or application version | 1.0.0 |
